"""Create need objects from an EMF ECore M2/M1 model with pyecore."""
import logging
import os
from typing import Any, Dict, List, Literal

from jinja2 import Environment, FileSystemLoader, select_autoescape
from pyecore.ecore import EEnumLiteral, EOrderedSet

from sphinx_emf.config.model import SphinxEmfConfig
from sphinx_emf.ecore.io_ecore import load_m1
from sphinx_emf.utils import get_xmi_id, is_field_allowed, is_type_allowed, natural_sort_in_place


logger = logging.getLogger(__name__)


def emf_2_need_value(emf_class_2_need_def_entry, emf_item, context) -> str:
    """
    Return the (optionally transformed) EMF value to be set on a need.

    Using a definition from emf_class_2_need_def.
    """
    emf_value = getattr(emf_item, emf_class_2_need_def_entry[0])
    if len(emf_class_2_need_def_entry) == 2:
        return str(emf_value)  # convert it, could be an ECore Enum or Boolean
    transformer_result = emf_class_2_need_def_entry[2](emf_value, emf_item, context)
    return transformer_result


def reduce_tree(need, emf_type, output_needs: List[Any], context, config) -> bool:
    """
    Recursively walk the need tree and write the given emf_type items to output_needs.

    It also changes the structure as need["nested_content"] does not contain those anymore.

    :returns: True if the need is kept and False if it is moved.
    """
    # evaluate need first before going down the nested needs tree;
    # if an element is moved to another output file, it should be done with all children
    curr_emf_type = need["emf_type"]
    if curr_emf_type == emf_type:
        return False

    list_emf_types_remove = []

    # go through the children now
    for list_emf_type, nested_needs in need["nested_content"].items():
        reduced_list = []
        for inner_need in nested_needs:
            keep_need = reduce_tree(inner_need, emf_type, output_needs, context, config)
            if keep_need:
                reduced_list.append(inner_need)
            else:
                output_needs.append(inner_need)
        need["nested_content"][list_emf_type] = reduced_list
        if not reduced_list:
            list_emf_types_remove.append(list_emf_type)

    for list_emf_type_remove in list_emf_types_remove:
        del need["nested_content"][list_emf_type_remove]

    return True


def remove_unlinked(need, context, config) -> bool:
    """
    Remove all need objects that are not linked as per emf_remove_unlinked_types.

    Context holds all actually linked need ids.

    :returns: True if the need is used else False
    """
    # go through the chidren first, then evaluate the need itself
    for emf_type, nested_needs in need["nested_content"].items():
        reduced_list = []
        for inner_need in nested_needs:
            keep_need = remove_unlinked(inner_need, context, config)
            if keep_need:
                reduced_list.append(inner_need)
        need["nested_content"][emf_type] = reduced_list

    # evaluate need
    emf_type = need["emf_type"]
    if emf_type in context["remove_unlinked_type_2_linked_need_ids"]:
        if need["internal"]["id"] not in context["remove_unlinked_type_2_linked_need_ids"][emf_type]:
            # this need id was not linked from anywhere - release it
            # also the children are not considered anymore
            return False
    return True


def get_cat(field_name):
    """
    Return the target need field category for a field name.

    This function just exists to distinguish internal fields from extra_options.
    """
    if field_name in ["id", "type", "title"]:
        return "internal"
    return "extra_options"


def walk_ecore_tree(item, need, context, config):
    """Recursively walk the ECore model from a root element and populate a root need."""
    item_type = item.__class__.__name__
    if not is_type_allowed(item, config):
        return []

    more_root_needs = []

    xmi_id = get_xmi_id(item)
    need_map = config.emf_class_2_need_def[item_type]  # map of ECore field names to need names

    # transform the dictionary to remove need_static and align with below need object that is passed to Jinja2
    all_definitions = {
        "options": need_map["emf_to_need_options"],
        "content": need_map["emf_to_need_content"],
    }

    # create space for fields
    need["emf_type"] = item_type
    need["internal"] = {}  # stores id, type, title
    need["extra_options"] = {}
    need["link_options"] = {}
    need["direct_content"] = {}
    need["nested_content"] = {}

    for need_field, value in need_map["need_static"].items():
        need[get_cat(need_field)][need_field] = value

    for section, definitions in all_definitions.items():
        for definition in definitions:
            emf_field, need_field = definition[0], definition[1]
            if not is_field_allowed(item, emf_field, config):
                continue

            try:
                value = getattr(item, emf_field)
            except AttributeError as exc:
                logger.warning(f"xmi:id {xmi_id}: Cannot get field {emf_field}, skipping it")
                logger.warning(f"xmi:id {xmi_id}: {exc}")
                continue
            if value is None:
                # do not transfer this to needs
                continue

            if isinstance(value, (str, EEnumLiteral, bool, int)):
                # option or content types, stored as strings
                # store the value on the need dictionary as per the MAP_EMF_CLASS_2_NEED_DEF definition
                need_value = emf_2_need_value(definition, item, context)
                if section == "options":
                    need[get_cat(need_field)][need_field] = need_value
                else:
                    need["direct_content"][need_field] = need_value
            elif isinstance(value, EOrderedSet):
                # need links or nested needs
                # sort the items to get reproducible RST output
                natural_sort_in_place(value.items, config)
                # emf_type to new need that is part of the EOrderedSet
                list_needs: List[Dict[str, Any]] = []
                for inner_item in value.items:
                    new_need = {}
                    new_root_needs = walk_ecore_tree(inner_item, new_need, context, config)
                    more_root_needs.extend(new_root_needs)
                    if new_need:
                        list_needs.append(new_need)
                if list_needs:
                    if value.is_cont:
                        if section == "content":
                            # containment -> UML composition -> nested need
                            # SN will add the need is it is part of a need content as a nested directive
                            if need_field not in need["nested_content"]:
                                need["nested_content"][need_field] = []
                            need["nested_content"][need_field].extend(list_needs)
                        else:
                            # ECore containment, but defined as link -> SN will not see the nodes
                            # -> add then as additional root needs
                            more_root_needs.extend(list_needs)
                            need["link_options"][need_field] = [
                                local_need["internal"]["id"] for local_need in list_needs
                            ]
                            for local_need in list_needs:
                                emf_type = local_need["emf_type"]
                                if emf_type in context["remove_unlinked_type_2_linked_need_ids"]:
                                    context["remove_unlinked_type_2_linked_need_ids"][emf_type].add(
                                        local_need["internal"]["id"]
                                    )
                    else:
                        # reference -> UML aggregation -> need link
                        # the linked need itself will be handled in another tree of the root need
                        need["link_options"][need_field] = [local_need["internal"]["id"] for local_need in list_needs]
                        for local_need in list_needs:
                            emf_type = local_need["emf_type"]
                            if emf_type in context["remove_unlinked_type_2_linked_need_ids"]:
                                context["remove_unlinked_type_2_linked_need_ids"][emf_type].add(
                                    local_need["internal"]["id"]
                                )
            else:
                raise ValueError(f"Unexpected field type {type(value)} for id {xmi_id}")

    # check whether all mandatory fields are set, if not this is a user config error or input data error
    mandatory_missing = False
    for mandatory_field in ["title", "id", "type"]:
        if mandatory_field not in need["internal"]:
            logger.warning(f"'{mandatory_field}' not set for need {need}, skipping need")
            mandatory_missing = True

    if mandatory_missing:
        need = None

    return more_root_needs


def write_rst(config: SphinxEmfConfig) -> None:
    """Load model and write need objects."""
    # history is not used
    roots = load_m1(config)
    dir_this_file = os.path.dirname(os.path.realpath(__file__))
    jinja_searchpaths = [os.path.join(dir_this_file, "base_templates")]
    if config.emf_templates_dir:
        jinja_searchpaths.append(config.emf_templates_dir)
    env = Environment(
        loader=FileSystemLoader(searchpath=jinja_searchpaths),
        autoescape=select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.add_extension("jinja2.ext.do")  # enable usage of {% do %}
    default_handled = False

    for root in roots:
        root_need: Dict[str, Any] = {}
        context: Dict[
            Literal["ecore_id_2_need_id", "need_id_2_ecore_id", "remove_unlinked_type_2_linked_need_ids"], Any
        ] = {"remove_unlinked_type_2_linked_need_ids": {}}
        if config.emf_remove_unlinked_types:
            context["remove_unlinked_type_2_linked_need_ids"] = {
                emf_type: set() for emf_type in config.emf_remove_unlinked_types
            }
        more_root_needs: List[Dict[str, Any]] = walk_ecore_tree(root, root_need, context, config)

        # remove all unlinked needs as defined in the config;
        # all needs in more_root_needs are definitively linked
        remove_unlinked(root_need, context, config)

        all_root_needs = [root_need] + more_root_needs

        default_config = None  # handle this at the end
        output: Dict[str, Dict[str, Any]] = {}  # stores all needs for each output path
        for output_config in config.emf_rst_output_configs:
            if "default" in output_config:
                default_config = output_config
                continue
            needs_to_write: List[Any] = []
            output[output_config["path"]] = {
                "needs": needs_to_write,
            }
            for need_type in output_config["emf_types"]:
                for root in all_root_needs:
                    keep_root = reduce_tree(root, need_type, needs_to_write, context, config)
                    if not keep_root:
                        needs_to_write.append(root)
        if default_config and not default_handled:
            output[default_config["path"]] = {
                "needs": [root_need],
            }
            default_handled = True
        for output_path, value in output.items():
            if not value["needs"]:
                # no export if list is empty
                continue
            needs_template = env.get_template("needs.rst.j2")

            # add function to Jinja2 context to allow template existence checks
            template_dir = config.emf_templates_dir or ""

            @static_vars(template_dir=template_dir)  # pylint: disable=cell-var-from-loop
            def template_exists(template_name):
                target = os.path.join(template_exists.template_dir, template_name)  # pylint: disable=cell-var-from-loop
                return os.path.exists(target) and os.path.isfile(target)

            env.globals["exists"] = template_exists

            template_name = os.path.basename(output_path).split(".")[0]
            needs_template_out = needs_template.render(
                needs=value["needs"],
                indent=config.emf_rst_indent,
                template_name=template_name,  # needed for inject header and footer
            )
            create_dirs(output_path)
            logger.info(f"Writing output file {output_path}")
            with open(output_path, "w", encoding="utf-8") as file_handler:
                file_handler.write(needs_template_out)


def create_dirs(file_path: str):
    """Create all directories to a (non-existent) file."""
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        # create the directory
        os.makedirs(directory, exist_ok=True)


def static_vars(**kwargs):
    """Decorate functions to inject variables."""

    def decorate(func):
        for key, value in kwargs.items():
            setattr(func, key, value)
        return func

    return decorate
