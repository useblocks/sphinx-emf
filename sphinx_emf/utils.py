"""Utils to generate need RST code."""

import re

from sphinx_emf.config.config_writer import (
    EMF_SORT_FIELD,
    MAP_EMF_CLASSES_2_NEEDS,
    MAP_FILTER_ALLOWED_EMF_CLASSES,
    MAP_FILTER_ALLOWED_EMF_VALUES,
    MAP_FILTER_DENIED_EMF_CLASSES,
    MAP_FILTER_DENIED_EMF_VALUES,
)


def is_type_allowed(item):
    """Determine whether the ECore item is valid for import."""
    item_type = item.__class__.__name__
    if item_type not in MAP_EMF_CLASSES_2_NEEDS:
        # item has no definition in class -> need map
        return False
    if MAP_FILTER_ALLOWED_EMF_CLASSES:
        if item_type not in MAP_FILTER_ALLOWED_EMF_CLASSES:
            return False
    if item_type in MAP_FILTER_DENIED_EMF_CLASSES:
        return False
    if item_type in MAP_FILTER_ALLOWED_EMF_VALUES:
        for field_name, values in MAP_FILTER_ALLOWED_EMF_VALUES[item_type].items():
            field_value = getattr(item, field_name, None)
            if field_value not in values:
                return False
    if item_type in MAP_FILTER_DENIED_EMF_VALUES:
        for field_name, values in MAP_FILTER_DENIED_EMF_VALUES[item_type].items():
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


def is_field_allowed(item, field_name):
    """Determine whether a certain ECore item field is valid for import."""
    if field_name == "_internal_id":
        return True
    item_type = item.__class__.__name__
    field_types = ["options", "content"]
    field_known = False
    for field_type in field_types:
        if field_type in MAP_EMF_CLASSES_2_NEEDS[item_type]:
            if field_name in MAP_EMF_CLASSES_2_NEEDS[item_type][field_type]:
                field_known = True
                break
    if not field_known:
        return False
    return True


def natural_sort_in_place(list_to_sort):
    """Sort a list by a given attribute naturally (correctly handling numbers)."""

    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum_key(key):
        return [convert(c) for c in re.split("([0-9]+)", getattr(key, EMF_SORT_FIELD))]

    if EMF_SORT_FIELD:
        # only sort if EMF_SORT_FIELD has a value
        list_to_sort.sort(key=alphanum_key)
