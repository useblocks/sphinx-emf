"""Builders for sphinx-emf."""

import os
import re
from typing import Dict, Iterable, Optional, Set

from docutils import nodes
from pyecore.ecore import EEnumLiteral, EObject, EOrderedSet
from pyecore.valuecontainer import BadValueError
from sphinx.builders import Builder

from sphinx_emf.config.invert import get_emf_class_from_need
from sphinx_emf.ecore.io_ecore import load_m2, save_m1
from sphinx_emf.sphinx_logging import get_logger


logger = get_logger(__name__)


class EmfBuilder(Builder):
    """Generate ECore M1 model from RST needs."""

    name = "emf"
    format = "xmi"  # noqa: F841
    file_suffix = ".ecore"  # noqa: F841
    links_suffix = None  # noqa: F841

    def write_doc(self, docname: str, doctree: nodes.document) -> None:
        """Needed by Sphinx, it does nothing."""
        del docname
        del doctree

    def finish(self) -> None:
        """Generate the M1 model."""
        env = self.env
        config = env.config

        need_id_2_need = env.needs_all_needs
        m2_rset = load_m2(config)
        mm_root = m2_rset.resources[config.emf_path_m2_model].contents[0]

        root_instances = []
        for emf_root in config.emf_model_roots:
            # get the root need
            root_need = None
            for need in need_id_2_need.values():
                need_emf_type = get_emf_class_from_need(need, config.emf_class_2_need_def, mm_root)
                if emf_root == need_emf_type:
                    root_need = need
                    break
            if root_need is None:
                raise RuntimeError(f"Could not find need for EMF root {emf_root}")
            e_class = mm_root.getEClassifier(emf_root)
            if e_class is None:
                logger.error(f"Cannot find ECore class for classifier {emf_root}")
                continue

            e_instance = e_class()
            root_instances.append(e_instance)
            need_id_2_ecore: Dict[str, EObject] = {root_need["id"]: e_instance}
            walk_create_ecore(
                root_need,
                e_instance,
                need_id_2_need,
                config.emf_class_2_need_def,
                mm_root,
                need_id_2_ecore,
            )
            # replace _isset with a list to get reproducible attribute order
        for instance in root_instances:
            overwrite_isset(instance)

        out_path = os.path.join(self.outdir, "ecore_m1.xmi")
        save_m1(root_instances, out_path)
        logger.info("EMF M1 model successfully exported")

    def get_outdated_docs(self) -> Iterable[str]:
        """Needed by Sphinx, it does nothing."""
        return []

    def prepare_writing(self, _docnames: Set[str]) -> None:
        """Needed by Sphinx, it does nothing."""

    def write_doc_serialized(self, _docname: str, _doctree: nodes.document) -> None:
        """Needed by Sphinx, it does nothing."""

    def cleanup(self) -> None:
        """Needed by Sphinx, it does nothing."""

    def get_target_uri(self, _docname: str, _typ: Optional[str] = None) -> str:
        """Needed by Sphinx, it does nothing."""
        return ""


def walk_create_ecore(need, e_instance, need_id_2_need, emf_class_2_need_def, mm_root, need_id_2_ecore):
    """Recursively walk the needs and create ECore instances."""
    curr_emf_type = get_emf_class_from_need(need, emf_class_2_need_def, mm_root)
    definitions = emf_class_2_need_def[curr_emf_type]
    # stores a flag for each emf field indicating whether the field has a transformer (== is an exact copy)
    emf_field_is_exact_copy = {}
    for definition in definitions["emf_to_need_options"]:
        emf_field, need_field = definition[0], definition[1]
        if emf_field in emf_field_is_exact_copy:
            if not emf_field_is_exact_copy[emf_field]:
                if len(definition) != 2:
                    # value was written inexactly previously, but this instance is not better (also not exact)
                    continue
            else:
                # previously written value is already exact
                continue
        # if true it means it was a 1:1 copy, else a transformer was involved
        emf_field_is_exact_copy[emf_field] = len(definition) == 2
        emf_value = getattr(e_instance, emf_field)
        if not need[need_field]:
            # not setting an empty or None field
            continue
        if emf_value is None:
            setattr(e_instance, emf_field, need[need_field])
        elif isinstance(emf_value, str):
            setattr(e_instance, emf_field, str(need[need_field]))
        elif isinstance(emf_value, bool):
            # if sphinx-emf is used as roundtrip, the import will have the
            # string values "[Tt]rue"/"[Ff]alse" set on need options
            setattr(e_instance, emf_field, need[need_field].lower() == "true")
        elif isinstance(emf_value, int):
            setattr(e_instance, emf_field, int(need[need_field]))
        elif isinstance(emf_value, EEnumLiteral):
            enum_value = emf_value.eEnum.from_string(need[need_field])
            if enum_value is None:
                logger.warning(
                    f"need {need['id']}: cannot convert '{need[need_field]}' to Enum for field {emf_field}, skipping"
                    " need"
                )
                continue
            setattr(e_instance, emf_field, enum_value)
        elif isinstance(emf_value, EOrderedSet):
            for link_need_id in need[need_field]:
                linked_need = need_id_2_need[link_need_id]
                if link_need_id in need_id_2_ecore:
                    local_e_instance = need_id_2_ecore[link_need_id]
                else:
                    nested_need_class = emf_value.feature.eType
                    local_e_instance = nested_need_class()
                    need_id_2_ecore[linked_need["id"]] = local_e_instance
                    emf_value.append(local_e_instance)
                walk_create_ecore(
                    linked_need,
                    local_e_instance,
                    need_id_2_need,
                    emf_class_2_need_def,
                    mm_root,
                    need_id_2_ecore,
                )
        else:
            raise ValueError(f"Unexpected EMF field type {type(emf_value)} for need id {need['id']}")
    for definition in definitions["emf_to_need_content"]:
        emf_field, need_field = definition[0], definition[1]
        if emf_field in emf_field_is_exact_copy:
            if not emf_field_is_exact_copy[emf_field]:
                if len(definition) != 2:
                    # value was written inexactly previously, but this instance is not better (also not exact)
                    continue
            else:
                # previously written value is already exact
                continue
        # if true it means it was a 1:1 copy, else a transformer was involved
        emf_field_is_exact_copy[emf_field] = len(definition) == 2
        emf_value = getattr(e_instance, emf_field)
        raw_rst_value = get_content_field_from_raw_rst(need["content"], need_field)
        if not raw_rst_value and not isinstance(emf_value, EOrderedSet):
            # not setting an empty or None field, however for EOrderedSet it is expected
            continue
        if emf_value is None:
            setattr(e_instance, emf_field, raw_rst_value)
        elif isinstance(emf_value, str):
            setattr(e_instance, emf_field, raw_rst_value)
        elif isinstance(emf_value, bool):
            # if sphinx-emf is used as roundtrip, the import will have the
            # string values "[Tt]rue"/"[Ff]alse" set on need options
            if raw_rst_value.lower() == "true":
                setattr(e_instance, emf_field, True)
            elif raw_rst_value.lower() == "false":
                setattr(e_instance, emf_field, False)
            else:
                logger.warning(
                    f"Cannot convert direct content field {need_field} to bool for need id {need['id']},"
                    f" actual value: '{raw_rst_value}'"
                )
        elif isinstance(emf_value, int):
            try:
                value = int(raw_rst_value)
                setattr(e_instance, emf_field, value)
            except ValueError:
                logger.warning(
                    f"Cannot convert direct content field {need_field} to int for need id {need['id']},"
                    f" actual value: '{raw_rst_value}'"
                )
        elif isinstance(emf_value, EEnumLiteral):
            enum_value = emf_value.eEnum.from_string(raw_rst_value)
            if enum_value is None:
                logger.warning(
                    f"need {need['id']}: cannot convert '{need[need_field]}' to Enum for field {emf_field}, skipping"
                    " need"
                )
                continue
            setattr(e_instance, emf_field, enum_value)
        elif isinstance(emf_value, EOrderedSet):  # does not use raw_rst_value, no need to check for emptiness
            # find all needs that have the current need as parent and analyze those as well
            for nested_need in need_id_2_need.values():
                if nested_need["parent_need"] == need["id"]:
                    expected_emf_class = emf_value.feature.eType.name
                    nested_need_emf_type = get_emf_class_from_need(nested_need, emf_class_2_need_def, mm_root)
                    nested_need_class = mm_root.getEClassifier(nested_need_emf_type)
                    if nested_need_class is None:
                        logger.error(f"Cannot find ECore class for classifier {nested_need_emf_type}")
                        continue
                    nested_need_super_classes = [x.name for x in nested_need_class.eSuperTypes.items]
                    if not (
                        expected_emf_class == nested_need_emf_type or expected_emf_class in nested_need_super_classes
                    ):
                        # the nested need is neither directly the right class nor does the super classes match the
                        # expected emf class
                        continue

                    if nested_need["id"] in need_id_2_ecore:
                        local_e_instance = need_id_2_ecore[nested_need["id"]]
                    else:
                        local_e_instance = nested_need_class()

                    try:
                        emf_value.append(local_e_instance)
                    except BadValueError as exc:
                        logger.warning(
                            f"need {need['id']}: cannot append nested need {nested_need['id']} (EMF type"
                            f" '{nested_need_emf_type}', field '{emf_field}'), skipping nested need"
                        )
                        logger.warning(f"need {need['id']}: {exc}")
                        continue
                    walk_create_ecore(
                        nested_need,
                        local_e_instance,
                        need_id_2_need,
                        emf_class_2_need_def,
                        mm_root,
                        need_id_2_ecore,
                    )
        else:
            raise ValueError(f"Unexpected EMF field type {type(emf_value)} for need id {need['id']}")


def overwrite_isset(instance: EObject):
    """Replace emf_value._isset with a sorted list to get reproducable attribute order."""
    if hasattr(instance, "_isset"):
        if instance._isset:  # pylint: disable=protected-access
            instance._isset = sorted(instance._isset, key=lambda x: (x.name))  # pylint: disable=protected-access
    for field in dir(instance):
        value = getattr(instance, field)
        if isinstance(value, EOrderedSet) and value.is_cont:
            for sub_instance in value.items:
                overwrite_isset(sub_instance)


def get_content_field_from_raw_rst(content, content_direct_field):
    """
    Get the RST content from a raw RST need body.

    The fields must be in the form::

        **Description**
        This is some text for description

        **Comment**
        This is a comment

        .. nested-need:: This is a nested need not considered by this function
        :id: NEED_2

    It shall parse all bold fields and the below content.
    """
    ret_str = ""
    lines = content.split("\n")
    block_open = False
    for line in lines:
        # determine start/stop conditions
        if line == f"**{content_direct_field}**":
            block_open = True
            continue
        if re.match(r"^.. [a-zA-Z0-9\-_]+::", line):
            # a directive started
            break
        if block_open and re.match(r"^\*\*.+\*\*$", line):
            # another field started
            break
        if block_open:
            # add to the string
            ret_str += f"\n{line}"
    trimmed = ret_str.strip()
    if trimmed:
        return trimmed
    return None
