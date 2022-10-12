"""Utils to generate need RST code."""

import re

from sphinx_emf.config.model import SphinxEmfConfig


def is_type_allowed(item, config: SphinxEmfConfig):
    """Determine whether the ECore item is valid for import."""
    item_type = item.__class__.__name__
    if item_type not in config.emf_classes_2_needs:
        # item has no definition in class -> need map
        return False
    if config.emf_allowed_classes:
        if item_type not in config.emf_allowed_classes:
            return False
    if item_type in config.emf_denied_classes:
        return False
    if item_type in config.emf_allowed_values:
        for field_name, values in config.emf_allowed_values[item_type].items():
            field_value = getattr(item, field_name, None)
            if field_value not in values:
                return False
    if item_type in config.emf_denied_values:
        for field_name, values in config.emf_denied_values[item_type].items():
            field_value = getattr(item, field_name, None)
            if field_value in values:
                return False
    return True


def get_xmi_id(item):
    """
    Return xmi:id field from ECore model.

    This is a wrapper as ECore does not expose that to its API.
    """
    return item._internal_id  # pylint: disable=protected-access


def is_field_allowed(item, field_name, config: SphinxEmfConfig):
    """Determine whether a certain ECore item field is valid for import."""
    if field_name == "_internal_id":
        return True
    item_type = item.__class__.__name__
    field_types = ["options", "content"]
    field_known = False
    for field_type in field_types:
        if field_type in config.emf_classes_2_needs[item_type]:
            if field_name in config.emf_classes_2_needs[item_type][field_type]:
                field_known = True
                break
    if not field_known:
        return False
    return True


def natural_sort_in_place(list_to_sort, config: SphinxEmfConfig):
    """Sort a list by a given attribute naturally (correctly handling numbers)."""

    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split("([0-9]+)", getattr(key, config.emf_sort_field))]

    if config.emf_sort_field:
        # only sort if emf_sort_field has a value
        list_to_sort.sort(key=alphanum_key)
