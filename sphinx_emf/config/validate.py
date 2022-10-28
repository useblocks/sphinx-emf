"""Validate sphinx-emf config with pydantic."""

import sys
from typing import Callable, Dict, List

from pydantic import ValidationError


def validate_config(confpy, logger, pydantic_class):
    """Run pydantic on emf_* fields of conf.py."""
    allowed_types = (int, str, List, Dict, Callable)
    all_fields = dir(confpy)
    emf_fields = {}
    for field in all_fields:
        if field.startswith("emf_"):
            value = getattr(confpy, field)
            if isinstance(value, (allowed_types)):
                emf_fields[field] = value
    try:
        config = pydantic_class(**emf_fields)
    except ValidationError as exc:
        logger.error("Config validation failed")
        logger.error(exc)
        sys.exit(1)
    logger.info("Config validation successful")
    return config
