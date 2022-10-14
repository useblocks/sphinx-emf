"""Pydantic model of sphinx-emf configuration parameters."""
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, StrictBool, StrictStr, conint
from pyecore.resources import ResourceSet
from pyecore.resources.xmi import XMIResource


class SphinxEmfConfig(BaseModel):
    """sphinx-emf config model."""

    emf_rst_output_configs: List[
        Dict[
            Literal["path", "emf_types", "default"],
            Union[
                StrictStr,  # for path
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

    emf_model_roots: List[StrictStr] = []
    """List of model roots as they shall appear in the root of the exported M1 model."""

    emf_templates_dir: StrictStr = None
    """
    Path to a directory containing user defined Jinja2 templates to be injected into RST output.

    They have access to all variables the base template has access.

    The file names must follow a pattern to be recognized. Variable definition:
    - <need-type> is a need type.
    - <need-field> is a need field, can be an extra-option, extra-link, direct content or nested content.

    All file names must end on .rst.j2.
    Templates have 3 types:
    - pre  -> injected before the item
    - post  -> injected after the item
    - wrap  -> wraps the item, so the need/content gets indented (useful for nested directives like dropdowns)

    Patterns:
    - <need-type>_pre  -> before the neeed
    - <need-type>_post  -> after the need
    - <need-type>_wrap  -> wraps the generated need
    - <need-type>_pre_extra_options  -> before all extra options
    - <need-type>_post_extra_options  -> after all extra options
    - <need-type>_pre_link_options  -> before all link options
    - <need-type>_post_link_options  -> after all link options
    - <need-type>_pre_direct_content  -> before all direct content
    - <need-type>_post_direct_content  -> after all direct content
    - <need-type>_wrap_direct_content  -> wraps all direct content
    - <need-type>_pre_direct_content_<need-field>  -> before a direct content needs field/section
    - <need-type>_post_direct_content_<need-field>  -> after a direct content needs field/section
    - <need-type>_wrap_direct_content_<need-field>  -> wraps a direct content needs field/section
    - <need-type>_pre_nested_content  -> before all nested content
    - <need-type>_post_nested_content  -> after all nested content
    - <need-type>_wrap_nested_content  -> wraps all nested content
    - <need-type>_pre_nested_content_<need-type>  -> before all instances of a nested needs type
    - <need-type>_post_nested_content_<need-type>  -> after all instances of a nested needs type
    - <need-type>_wrap_nested_content_<need-type>  -> wraps all instances of a nested needs type
    - <need-type>_pre_nested_content_every_<need-type>  -> before each instance of a nested needs type
    - <need-type>_post_nested_content_every_<need-type>  -> after each instance of a nested needs type
    - <need-type>_wrap_nested_content_every_<need-type>  -> wraps each instance of a nested needs type
    """
