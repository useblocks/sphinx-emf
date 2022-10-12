"""Create need objects from an EMF ECore M2/M1 model with pyecore."""

import logging
import os
from typing import Any, Callable, Dict, List, Literal, Tuple, Union

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pyecore.ecore import EEnumLiteral, EOrderedSet

from sphinx_emf.ecore.io_ecore import load
from sphinx_emf.utils import get_xmi_id, is_field_allowed, is_type_allowed, natural_sort_in_place


logger = logging.getLogger(__name__)


def set_need_field(
    ecore_value,
    definition: Union[str, Tuple[str, Callable[[str, str, List[str], Dict[str, Any]], str]]],
    need,
):
    """Read an MAP_EMF_CLASSES_2_NEEDS definition and set the field in the given need accordingly."""
    if isinstance(definition, str):
        need[definition] = ecore_value
    elif isinstance(definition, List):
        # invoke user defined hook
        hook_out = definition[1](ecore_value)
        need[definition] = hook_out
    else:
        raise ValueError(f"Unexpected definition type {type(definition)} for ECore value {ecore_value}")


def get_field_definition(
    definition: Dict[str, Any], emf_field_name
) -> Tuple[str, Union[str, None, Tuple[str, Callable[[str, Any, Dict[str, Any]], str]]]]:
    """
    Look for the field in a MAP_EMF_CLASSES_2_NEEDS[...] definition.

    It can either be in 'options' or 'content'.
    """
    sections = ["options", "content"]
    found_section = None
    tar_definition = None
    for section in sections:
        if emf_field_name in definition[section]:
            found_section = section
            tar_definition = definition[section][emf_field_name]
    if not found_section:
        raise ValueError(f"Cannot find field {emf_field_name} in definition {definition}")
    return found_section, tar_definition


def set_need_value(
    need_definition: Union[str, Tuple[str, Callable[[str, Any, Dict[str, Any]], str]]],
    emf_field_name,
    emf_item,
    context,
) -> Tuple[str, str]:
    """
    Set a need field value based on a MAP_EMF_CLASSES_2_NEEDS definition.

    The need dictionary is modified in-place.
    """
    emf_value = getattr(emf_item, emf_field_name)
    if isinstance(need_definition, str):
        need_value = str(emf_value)  # convert it, could be an ECore Enum or Boolean
        return need_definition, need_value
    transformer_result = need_definition[1](emf_value, emf_item, context)
    return need_definition[0], transformer_result


def walk_ecore_tree(item, need, context, config):
    """Recursively walk the ECore model from a root element and populate a root need."""
    item_type = item.__class__.__name__
    if not is_type_allowed(item, config):
        return

    xmi_id = get_xmi_id(item)
    need_map = config.emf_classes_2_needs[item_type]  # map of ECore field names to need names

    # build fields list to analyze, order is the appearance in need_map
    sorted_emf_fields = list(need_map["options"].keys()) + list(need_map["content"].keys())
    fields = ["_internal_id"] + sorted_emf_fields
    # make items unique while keeping order
    fields = sorted(set(fields), key=lambda x: fields.index(x))  # pylint: disable=unnecessary-lambda

    # generate needs id
    if isinstance(need_map["id"], str):
        need["id"] = getattr(item, need_map["id"])
    elif isinstance(need_map["id"], Callable):
        need["id"] = need_map["id"](item, context)
    else:
        raise ValueError(f"Unknown type {type(need_map['id'])} for key 'id' of ECore type {item_type}")

    # set type
    need["type"] = need_map["type"]

    # set title
    if isinstance(need_map["title"], str):
        need["title"] = getattr(item, need_map["title"])
    elif isinstance(need_map["title"], Callable):
        need["title"] = need_map["title"](item, context)
    else:
        raise ValueError(f"Unknown type {type(need_map['title'])} for key 'title' of ECore type {item_type}")
    if not need["title"]:
        need["title"] = need["id"]

    # create space for fields
    need["extra_options"] = {}
    need["link_options"] = {}
    need["direct_content"] = {}
    need["nested_content"] = {}

    # update context with new IDs
    context["id_map_needs_2_ecore"][need["id"]] = xmi_id
    context["id_map_ecore_2_needs"][xmi_id] = need["id"]

    for field_name in fields:
        if not is_field_allowed(item, field_name, config):
            continue
        value = getattr(item, field_name)
        if value is None:
            # do not transfer this to needs
            continue
        section, definition = get_field_definition(need_map, field_name)
        if isinstance(value, (str, EEnumLiteral, bool, int)):
            # option or content types, stored as strings
            # store the value on the need dictionary as per the MAP_EMF_CLASSES_2_NEEDS definition
            need_field_name, need_value = set_need_value(definition, field_name, item, context)
            if section == "options":
                need["extra_options"][need_field_name] = need_value
            else:
                need["direct_content"][need_field_name] = need_value
        elif isinstance(value, EOrderedSet):
            # need links or nested needs
            # sort the items to get reproducible RST output
            natural_sort_in_place(value.items, config)
            list_needs: List[Dict[str, Any]] = []
            for inner_item in value.items:
                new_need = {}
                walk_ecore_tree(inner_item, new_need, context, config)
                if new_need:
                    list_needs.append(new_need)
            if list_needs:
                if value.is_cont:
                    # containment -> UML composition -> nested need
                    if definition not in need["nested_content"]:
                        need["nested_content"][definition] = []
                    need["nested_content"][definition].extend(list_needs)
                else:
                    # reference -> UML aggregation -> need link
                    need["link_options"][definition] = [local_need["id"] for local_need in list_needs]
        else:
            raise ValueError(f"Unexpected field type {type(value)} for id {xmi_id}")


def write_rst(config) -> None:
    """Load model and write need objects."""
    # history is not used
    roots = load(config)
    dir_this_file = os.path.dirname(os.path.realpath(__file__))
    env = Environment(
        loader=FileSystemLoader(searchpath=os.path.join(dir_this_file, "base_templates")),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.add_extension("jinja2.ext.do")  # enable usage of {% do %}
    for root in roots:
        need_root: Dict[str, Any] = {}
        context: Dict[Literal["id_map_ecore_2_needs", "id_map_needs_2_ecore"], Any] = {
            "id_map_ecore_2_needs": {},
            "id_map_needs_2_ecore": {},
        }
        walk_ecore_tree(root, need_root, context, config)
        if not os.path.exists(config.emf_output_directory):
            # create the output directory
            os.makedirs(config.emf_output_directory, exist_ok=True)

        need_template = env.get_template("need.rst.j2")
        need_template_out = need_template.render(need=need_root, indent=config.emf_rst_indent)
        output_file_name = f"{root.__class__.__name__}_out.rst"
        with open(os.path.join(config.emf_output_directory, output_file_name), "w", encoding="utf-8") as file_handler:
            file_handler.write(need_template_out)
    # for template_path in TEMPLATES:
    #     template_dir = os.path.dirname(template_path)
    #     template_file_name = os.path.basename(template_path)
    #     tool_j2 = env.get_template(template_file_name)
    #     tool_j2_out = tool_j2.render(need_root=need_root, indent=RST_INDENT)
    #     if not template_file_name.endswith(".rst.j2"):
    #         raise ValueError(f"Template path must end on .rst.j2, given {template_path}")
    #     output_file_name = template_file_name[:-3]
    #     with open(os.path.join(OUTPUT_DIRECTORY, output_file_name), "w", encoding="utf-8") as file_handler:
    #         file_handler.write(tool_j2_out)


def read_rst() -> None:
    """Load model and read need objects from RST."""
