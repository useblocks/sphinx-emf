"""Pydantic model of sphinx-emf configuration parameters."""
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, StrictBool, StrictStr, conint
from pyecore.resources import ResourceSet
from pyecore.resources.xmi import XMIResource


class SphinxEmfConfig(BaseModel):
    """sphinx-emf config model."""

    emf_rst_output_configs: List[
        Dict[
            Literal["path", "emf_types", "default", "headline"],
            Union[
                StrictStr,  # for path / headline
                List[StrictStr],  # for emf_types
                StrictBool,  # for default
            ],
        ],
    ]
    """
    Mapping of ECore types to output files.

    'path' is mandatory for all.
    Only one list item may contain 'default'.
    All others must have 'emf_types'. 'emf_types' must be unique across the full config param.

    The list order is important as it defines which elements are moved first - with all its nested needs.
    """
    emf_path_m1_model: StrictStr
    """ECore M1 model."""
    emf_path_m2_model: StrictStr
    """Ecore M2 model."""
    emf_output_directory: StrictStr
    """
    Output directory for the RST files.

    Deprecated.
    """
    # see https://github.com/pydantic/pydantic/issues/239
    #     https://github.com/pydantic/pydantic/issues/156
    # for why ignoring seems to be the best solution
    emf_rst_indent: conint(strict=True, gt=0) = 3  # type: ignore
    """Amount of leading spaces for each RST code indentation level."""

    # The following 4 are fiter dictionaries, logic:
    # - for each object instance executed in order
    #   - discard the object if
    #     - MAP_FILTER_ALLOWED_EMF_CLASSES is not empty and
    #     - the object class does not appear in MAP_FILTER_ALLOWED_EMF_CLASSES
    #   - discard the object if
    #     - the object class appears in MAP_FILTER_DENIED_EMF_CLASSES
    #   - discard the object if
    #     - the class name appears in MAP_FILTER_ALLOWED_EMF_VALUES and
    #     - the values of the object fields don't appear in MAP_FILTER_ALLOWED_EMF_VALUES
    #   - discard the object if
    #     - the class name appears in MAP_FILTER_DENIED_EMF_VALUES and
    #     - the values of the object fields appear in MAP_FILTER_DENIED_EMF_VALUES
    emf_allowed_classes: List[StrictStr] = []
    """List of EMF classes that should be allowed for importing."""
    emf_denied_classes: List[StrictStr] = []
    """List of EMF classes that should be denied for importing."""
    emf_allowed_values: Dict[StrictStr, Dict[StrictStr, List[StrictStr]]] = {}
    """Map EMF classes to EMF field names to allowed values of the fields."""
    emf_denied_values: Dict[StrictStr, Dict[StrictStr, List[StrictStr]]] = {}
    """Map EMF classes to EMF field names to denied values of the fields."""

    emf_remove_unlinked_types: List[StrictStr] = []
    """ECore class names that should be removed if not linked from anywhere."""

    emf_pre_read_hook: Optional[Callable[[ResourceSet], ResourceSet]] = None
    """
    Function that should be called on the ResourceSet before reading the M1 model.

    Must return the ResourceSet again after modifying it.
    """

    emf_post_read_hook: Optional[Callable[[XMIResource], List[Any]]] = None
    """
    Function that should be called on the M1 XMIResource after creating it.

    Must return the list of ECore model roots (which is the main use case for this).
    """

    emf_class_2_need_def: Dict[
        StrictStr,  # ECore class
        Dict[
            Literal["emf_type", "id", "type", "title", "prefix", "options", "content"],
            Union[
                StrictStr,  # for id, type, prefix
                Callable[[Any, Dict[StrictStr, Any]], StrictStr],  # for id transformer
                Tuple[StrictStr, Callable[[StrictStr, Any, Dict[StrictStr, Any]], StrictStr]],  # for title transformer
                Dict[  # for options and content
                    StrictStr,  # for 1:1 mapping
                    Union[
                        StrictStr,  # for 1:1 mapping
                        None,  # for nested needs in content
                        Tuple[StrictStr, Callable[[StrictStr, Any, Dict[StrictStr, Any]], StrictStr]],
                    ],
                ],
            ],
        ],
    ] = {}
    """
    Map EMF class names to need definitions.

    The needs definition consists of:
    - id: str: copy from this EMF field; callable: generate it
    - type: str: taken literally as the need type
    - title: str: copy from this EMF field; callable: generate it
    - options: map EMF field names
    - content: map EMF field names to need content sections (will be converted to RST)
    """

    emf_sort_field: StrictStr = None
    """Sort ECore instances by this field to get reproducible RST output."""
