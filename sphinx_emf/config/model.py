"""Pydantic model of sphinx-emf configuration parameters."""
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, StrictBool, StrictStr, conint
from pyecore.ecore import EObject
from pyecore.resources import ResourceSet
from pyecore.resources.xmi import XMIResource
from typing_extensions import TypedDict


try:
    from typing import Literal
except ImportError:
    from typing_extensions import Literal


class Class2NeedDefSettings(TypedDict, total=False):
    """Definition for :attr:`Class2NeedDefValues.settings`."""

    remove_if_unlinked: StrictBool
    """Remove the EMF type if it is not linked by other EMF types."""

    remove_ignored_link_sources: List[StrictStr]
    """
    List of EMF types whose outgoing links are ignored when removing elements.

    The setting is only relevant if :attr:`remove_if_unlinked` is True.
    The setting can be used to remove elements that are contained in other types
    as nested elements (which is also a link source), but should still be removed
    if not explicitely linked by other elements.
    """


class Class2NeedDefValues(TypedDict, total=False):
    """Definition for :attr:`SphinxEmfCommonConfig.emf_class_2_need_def`."""

    need_static: Dict[StrictStr, StrictStr]
    """
    Static needs options given as key-value pairs.

    This is commonly used to set the need ``type``.
    Example:

    .. code-block:: python

        {
          'need_static': { 'type': 'story' }
        }

    .. uml::

        @startuml
        class "need 'story'" as need {
            str type = 'story'
        }
        class "ECore 'Story'" as ecore {
        }
        note left of need::type
            <code>
            emf_class_2_need_def = {
              "Story": {
                "need_static": {
                  "type": "story",
                },
              },
            }
        end note
        @enduml
    """

    emf_to_need_options: List[
        Union[
            Tuple[StrictStr, StrictStr],  # direct EMF field reading
            # transformer: value, ecore_item, context
            Tuple[StrictStr, StrictStr, Callable[[StrictStr, EObject, Dict[StrictStr, Any]], StrictStr]],
        ]
    ]
    """
    Define how ECore field names are copied to need extra options and links.

    Any simple ECore type (bool, int, str, enum) leads to a
    `needs extra option <https://sphinxcontrib-needs.readthedocs.io/en/latest/configuration.html#needs-extra-options>`_.
    ECore list types (``EOrderedSet``) produce a
    `needs extra link <https://sphinxcontrib-needs.readthedocs.io/en/latest/configuration.html#needs-extra-links>`_.

    Any ECore field that does not appear here and also not in :attr:`emf_to_need_content`
    will be ignored.

    Tuple entries:

    0. ECore field name
    1. need extra option/link name
    2. transformer function [optional]

    The ECore field name tuple[0] will be transformed to the need extra option or need extra link given in
    tuple[1].

    Any ECore values that lead to `need extra options` will be converted to string types.

    Any Ecore list values lead to `need extra links`, even when the ECore definition is a containment (nested object).
    When converting back from RST to XMI, the ECore containment information from the ECore M2 model is used
    to transform a needs link correctly back to an ECore containment. This makes it possible to change the link
    modeling for Sphinx-Needs. Users may want to write certain need types to dedicated files which makes it impossible
    to model them as UML composition (containment) - which in the Sphinx-Needs world - is realized as nested needs.

    The transformer function is only allowed for simple types that lead to `need extra options`.
    The function must support the following parameters:

    * ``value`` ECore field value of tuple[0] field name
    * ``ecore_item`` full ECore object; can be used to access other ECore fields
    * ``context`` empty dicionary, will be the same instance for all invocations
      of transformers; and can be used to hold context information across invocations

    The function must return a ``str`` type.

    A use case for transformers is to generate unique need IDs from ECore fields. Example:

    .. code-block:: python

        def gen_needs_id(value: str, ecore_item: Any, context: Dict[str, Any]) -> str:
          need_prefixes = {
            'Story': 'STORY_',
            'Requirement': 'REQ_',
          }
          prefix = need_prefixes[ecore_item.__class__.__name__]
          need_id = prefix + value.upper()
          return need_id

        emf_class_2_need_def = {
          "Story": {
            "need_static": {
              "type": "story",
            },
            "emf_to_need_options": [
              ("Name", "title"),  # need title: direct copy the 'Name' field
              ("_iternal_id", "id", gen_needs_id),  # need id: use a transformer
            ],
          },
        }

    .. note:: pyecore stores the XMI unique identifiers in the field ``_internal_id`` which can also be used.

    .. uml::

        @startuml
        class "need 'story'" as need {
            str type = 'story'
            str id = 'STORY_abc'
            str title = 'The alphabet story'
        }
        class "ECore 'Story'" as ecore {
            str _internal_id = 'abc'
            str Name = 'The alphabet story'
        }
        circle "gen_needs_id()" as gen_needs_id

        ecore::_internal_id --> gen_needs_id
        gen_needs_id --> need::id
        ecore::Name --> need::title

        note as n1
            <code>
            emf_class_2_need_def = {
              "Story": {
                "need_static": {
                  "type": "story",
                },
                "emf_to_need_options": [
                  ("Name", "title"),
                  ("_iternal_id", "id", gen_needs_id),
                ],
              },
            }
        end note
        @enduml

        .. note::
            The mandatory need fields ``id``, ``type`` and ``title`` must appear in one the configuration
            sections :attr:`need_static` or :attr:`emf_to_need_options`.

    """

    emf_to_need_content: List[
        Union[
            Tuple[StrictStr, StrictStr],  # direct EMF field reading
            # transformer: value, ecore_item, context
            Tuple[StrictStr, StrictStr, Callable[[StrictStr, EObject, Dict[StrictStr, Any]], StrictStr]],
        ]
    ]
    """
    Define how ECore field names are copied to the need content area.

    Tuple entries:

    0. ECore field name
    1. need content title
    2. transformer function [optional]

    Any simple ECore type (bool, int, str, enum) leads to a highlighted section of the
    need body. ECore list types (``EOrderedSet``) produce a nested need.

    Example:

    .. code-block:: python

        emf_class_2_need_def = {
          "Story": {
            "need_static": {
              "type": "story",
            },
            "emf_to_need_content": [
              ("Name", "title"),  # need title: direct copy the 'Name' field
              ("_iternal_id", "id", gen_needs_id),  # need id: use a transformer
            ],
          },
        }

    .. code-block:: rst

        .. story:: Title
           :id: STORY_abc

           **Description** The alphabet story.

    ECore list types (``EOrderedSet``) produce a nested need, so a new needs directive in the
    current need's body. See also the description of :attr:`emf_to_need_options` about modeling
    of ECore list fields as linked needs or nested needs.

    Any ECore field that does not appear here and also not in :attr:`emf_to_need_options`
    will be ignored.
    """

    settings: Class2NeedDefSettings


class SphinxEmfCommonConfig(BaseModel):
    """Common configuration for both CLI (XMI -> RST) and builder (RST -> XMI)."""

    emf_path_m2_model: StrictStr
    """Ecore M2 model."""

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

    emf_class_2_need_def: Dict[StrictStr, Class2NeedDefValues] = {}
    """
    Main configuration mapping from EMF ECore classes to need types.

    Key are ECore class names, value are instances of :class:`Class2NeedDefValues`.
    """


class SphinxEmfCliConfig(SphinxEmfCommonConfig):
    """sphinx-emf config model for the CLI that converts from XMI to RST."""

    emf_path_m1_model: StrictStr
    """ECore M1 model."""

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

    emf_sort_field: StrictStr = None
    """
    Sort ECore instances by this field to get reproducible RST output.

    Set to None to disable sorting.
    """

    emf_templates_dir: StrictStr = None
    """
    Path to a directory containing user defined Jinja2 templates to be injected into RST output.

    They have access to all variables the base template has access.

    The file names must follow a pattern to be recognized. Variable definition:

    - ``<need-type>`` is a need type.
    - ``<need-field>`` is a need field, can be an extra-option, extra-link, direct content or nested content.

    All file names must end on .rst.j2.
    Templates have 3 types:

    - ``pre`` injected before the item
    - ``post`` injected after the item
    - ``wrap`` wraps the item, so the need/content gets indented (useful for nested directives like dropdowns)

    Patterns:

    - ``<template-name>_header`` before all content in RST output file (see emf_rst_output_configs, without .rst)
    - ``<template-name>_footer`` after all content in RST output file (see emf_rst_output_configs, without .rst)
    - ``<need-type>_pre`` before the neeed
    - ``<need-type>_post`` after the need
    - ``<need-type>_wrap`` wraps the generated need
    - ``<need-type>_options_fields_pre`` before all extra options
    - ``<need-type>_options_fields_post`` after all extra options
    - ``<need-type>_options_links_pre`` before all link options
    - ``<need-type>_options_links_post`` after all link options
    - ``<need-type>_content_direct_pre`` before all direct content
    - ``<need-type>_content_direct_post`` after all direct content
    - ``<need-type>_content_direct_wrap`` wraps all direct content
    - ``<need-type>_content_direct_pre_<need-field>`` before a direct content needs field/section
    - ``<need-type>_content_direct_post_<need-field>`` after a direct content needs field/section
    - ``<need-type>_content_direct_wrap_<need-field>`` wraps a direct content needs field/section
    - ``<need-type>_content_nested_pre`` before all nested content
    - ``<need-type>_content_nested_post`` after all nested content
    - ``<need-type>_content_nested_wrap`` wraps all nested content
    - ``<need-type>_content_nested_pre_<nested-need-type>`` before each instance of a nested needs type
    - ``<need-type>_content_nested_post_<nested-need-type>`` after each instance of a nested needs type
    - ``<need-type>_content_nested_wrap_<nested-need-type>`` wraps each instance of a nested needs type
    - ``<need-type>_content_nested_pre_all_<nested-needs-title>`` before all instances of a nested needs type
    - ``<need-type>_content_nested_post_all_<nested-needs-title>`` after all instances of a nested needs type
    - ``<need-type>_content_nested_wrap_all_<nested-needs-title>`` wraps all instances of a nested needs type
    """

    emf_show_nested_need_title: StrictBool = True
    """
    Generate the title for nested needs as given in emf_class_2_need_def.

    Set it under emf_class_2_need_def -> <emf-type> -> emf_to_need_content -> (<emf-fild>, <title>)
    """


class SphinxEmfBuilderConfig(SphinxEmfCommonConfig):
    """sphinx-emf config model for the Sphinx builder that converts from RST to XMI."""

    emf_model_roots: List[StrictStr] = []
    """List of model roots, ordered as they shall appear in the exported M1 model."""

    emf_sort_xmi_attributes: StrictBool = False
    """Sort attributes of XMI ECore classes by name."""

    emf_xmi_output_name: StrictStr = "m1_model.xmi"
    """
    Output name for XMI file.

    Directory is always the builder output (default _build/emf)
    """

    emf_convert_rst_to_plain: StrictBool = True
    r"""
    Flag indicating whether to convert RST sequences to plain text.

    The following sequences will be handled:


    * explicit line breaks on start of line :literal:`| \ ` will be removed
    * ``\*`` will be converted to ``*``
    * ``\``` will be converted to `````
    * ``\\`` will be converted to ``\``
    """
