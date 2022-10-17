"""Invert emf_class_2_need_def dictionary."""
import logging
from typing import Any, Dict, Optional

from pyecore.ecore import EClass


logger = logging.getLogger(__name__)


def get_emf_class_from_need(need: Dict[str, Any], emf_class_2_need_def, mm_root) -> Optional[str]:
    """
    Try to derive the ECore class from a need type.

    3 strategies are used:

    1. Check whether whether one of the emf_class_2_need_def need_static settings for 'type' matches
    2. Check whether the need type matches any lower case key in emf_class_2_need_def
    3. Check whether the need type matches any lower case ECore EClass name of the meta model

    If none is successful, the function returns None.
    """
    # first look in need_static
    for emf_type, definitions in emf_class_2_need_def.items():
        if "type" in definitions["need_static"]:
            if definitions["need_static"]["type"] == need["type"]:
                return emf_type
    # now match the dictionary key
    all_emf_types = list(emf_class_2_need_def.keys())
    for emf_type in all_emf_types:
        if emf_type.lower() == need["type"]:
            return emf_type
    # now go through all EClass items in the meta model
    for item in mm_root.eClassifiers.items:
        if item.name.lower() == need["type"] and isinstance(item, EClass):
            return item.name
    logger.error(f"Cannot derive the ECore class for need id '{need['id']}' (type '{need['type']}')")
    return None
