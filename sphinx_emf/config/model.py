"""Pydantic model of sphinx-emf configuration parameters."""
from typing import Any, Callable, Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, StrictStr, conint
from pyecore.resources import ResourceSet


class SphinxEmfConfig(BaseModel):
    """sphinx-emf config model."""

    emf_path_m1_model: StrictStr
    emf_path_m2_model: StrictStr
    emf_output_directory: StrictStr
    emf_rst_indent: conint(strict=True, gt=0) = 3
    emf_allowed_classes: List[StrictStr] = []
    emf_denied_classes: List[StrictStr] = []
    emf_allowed_values: Dict[StrictStr, Dict[StrictStr, List[StrictStr]]] = {}
    emf_denied_values: Dict[StrictStr, Dict[StrictStr, List[StrictStr]]] = {}
    emf_remove_unlinked_types: List[StrictStr] = []
    emf_pre_read_hook: Optional[Callable[[ResourceSet], ResourceSet]] = None
    emf_post_read_hook: Optional[Callable] = None
    emf_classes_2_needs: Dict[
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
    emf_sort_field: StrictStr = None
