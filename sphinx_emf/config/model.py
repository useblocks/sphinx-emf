"""Pydantic model of sphinx-emf configuration parameters."""
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, StrictBool, StrictStr, conint
from pyecore.resources import ResourceSet
from pyecore.resources.xmi import XMIResource


emf_class_2_need_def_type = Dict[  # pylint: disable=invalid-name
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
]


class SphinxEmfConfig(BaseModel):
    """sphinx-emf config model."""

    emf_output_files: List[
        Dict[
            Literal["path", "emf_types", "default"],
            Union[
                StrictStr,  # for path
                List[StrictStr],  # for emf_types
                StrictBool,  # for default
            ],
        ],
    ]
    """Mapping of ECore types to output files."""
    emf_path_m1_model: StrictStr
    """ECore M1 model."""
    emf_path_m2_model: StrictStr
    """Ecore M2 model."""
    emf_output_directory: StrictStr
    # see https://github.com/pydantic/pydantic/issues/239
    #     https://github.com/pydantic/pydantic/issues/156
    # for why ignoring seems to be the best solution
    emf_rst_indent: conint(strict=True, gt=0) = 3  # type: ignore
    emf_allowed_classes: List[StrictStr] = []
    emf_denied_classes: List[StrictStr] = []
    emf_allowed_values: Dict[StrictStr, Dict[StrictStr, List[StrictStr]]] = {}
    emf_denied_values: Dict[StrictStr, Dict[StrictStr, List[StrictStr]]] = {}
    emf_remove_unlinked_types: List[StrictStr] = []
    emf_pre_read_hook: Optional[Callable[[ResourceSet], ResourceSet]] = None
    emf_post_read_hook: Optional[Callable[[XMIResource], List[Any]]] = None
    """Return list of ECore model roots."""
    emf_class_2_need_def: emf_class_2_need_def_type = {}
    emf_sort_field: StrictStr = None
