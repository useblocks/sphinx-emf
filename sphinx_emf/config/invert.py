"""Invert emf_class_2_need_def dictionary."""

from sphinx_emf.config.model import emf_class_2_need_def_type


def invert_emf_class_2_need_def(emf_class_2_need_def: emf_class_2_need_def_type):
    """Invert the main config dictionary for the export ECore feature."""
    output = {}
    need_type_2_emf_def = {}
    for ecore_type, field_map in emf_class_2_need_def.items():
        need_type_2_emf_def[field_map["type"]] = {"type": ecore_type}
    output["need_type_2_emf_def"] = need_type_2_emf_def
    return output
