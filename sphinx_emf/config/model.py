"""Pydantic model of Sphinx-EMF configuration parameters."""
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pydantic import BaseModel, StrictBool, StrictStr, conint
from pyecore.ecore import EObject
from pyecore.resources import ResourceSet
from pyecore.resources.xmi import XMIResource
from typing_extensions import TypedDict


# solution as per https://mypy.readthedocs.io/en/stable/runtime_troubles.html#using-new-additions-to-the-typing-module
if sys.version_info >= (3, 8):
    from typing import Literal
else:
    from typing_extensions import Literal


class Class2NeedDefSettings(TypedDict, total=False):
    """Definition for :attr:`Class2NeedDefValues.settings`."""

    remove_if_unlinked: StrictBool
    """
    Remove the EMF type if it is not linked by other EMF types.

    The idea of this parameter is to prevent importing ECore objects that are not needed (linked) by the main objects
    of interest. All ECore instances can be a link target in one way or another:

    - they are a nested containment of another ECore instance
    - they are linked by another ECore instance

    If this setting is ``True``, root ECore instances are ignored during import.
    The parameter :attr:`remove_ignored_link_sources` can be used to further specify the behavior.
    """

    remove_ignored_link_sources: List[StrictStr]
    """
    List of EMF types whose outgoing links are ignored when removing elements.

    The setting is only relevant if :attr:`remove_if_unlinked` is True.

    The setting can be used to also ignore (remove) elements that are contained in the listed types
    as nested elements or that are linked by the listed elements types. The elements will only be removed
    if they are not linked by other element types not listed here.

    The main use case of the feature is to ignore containment links when removing ECore objects.
    Almost all ECore objects are contained by another ECore object.
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
    When converting back from RST to XMI, the ECore containment information from the ECore metamodel is used
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

    Any simple ECore type (bool, int, str, enum) leads to a highlighted section in the
    need body with the tuple[1] prepended as bold text.
    Any ECore list type (``EOrderedSet``) produces a list of nested needs, so new need directives are
    added to the current need's body. See also the description of :attr:`emf_to_need_options` about modeling
    of ECore list fields as linked needs or nested needs.

    Example:

    .. code-block:: python

        from sphinx_emf.user_hooks.escape_rst import to_rst

        def escape_rst(value: str, ecore_item: Any, context: Dict[str, Any]) -> str:
          del ecore_item
          del context
          escaped_value = to_rst(value)
          return escaped_value

        emf_class_2_need_def = {
          "Story": {
            "need_static": {
              "type": "story",
            },
            "emf_to_need_options": [
              ("Name", "title"),
              ("_iternal_id", "id", gen_needs_id),
            ],
            "emf_to_need_content": [
              ("Description", "Description"),
              ("LongDescription", "Long Description", escape_rst),
              ("Requirements", "Requirements"),
            ],
          },
        }

    .. code-block:: rst

        .. story:: The alphabet story
           :id: STORY_abc

           **Description** Names all letters.

           **Long Description**

           Special care for:

           - the sort order and
           - not to forget a letter

           **Requirements**

           .. requirement:: Must be sorted
              :id: REQ_sorted

           .. requirement:: Must not forget a letter
              :id: REQ_forget

    The transformer has the same parameters and return type as in :attr:`emf_to_need_options`.
    It can only be used for simple ECore types (bool, int, str, enum).

    .. note::
        In above example an ECore class called ``Requirement`` is missing in ``emf_class_2_need_def``.
        It is needed to tell Sphinx-EMF how to represent the nested ``requirement`` need types.
        It is skipped to keep the example short.

    .. note::
        XMI does not specify any highlighting language such as Markdown, RestructuredText or
        HTML for plain text (multiline) fields.
        Therefore text fields cannot be copied 1:1 to RST as strings like ``the *.json files`` are
        not valid RST. The ``*`` needs to be escaped. Sphinx-EMF provides a function to transform
        plain text to RST. See above example how to import and use it. The function handles the following
        scenarios:

        #. all incomplete inline literals are escaped
        #. lists are correctly formatted
        #. paragraphs are correctly formatted, line breaks lead to lines prepended with '| '

        You may also decide to store RST directly to XMI. This however needs custom escaping
        of ``"`` as it is the start/stop sequence of values.

    Any ECore field that does not appear here and also not in :attr:`emf_to_need_options`
    will be ignored.
    """

    settings: Class2NeedDefSettings


class SphinxEmfCommonConfig(BaseModel):
    """Common configuration for both CLI (XMI -> RST) and builder (RST -> XMI)."""

    emf_path_ecore: StrictStr
    """Path to the ECore metamodel."""

    emf_pre_xmi_read_hook: Optional[Callable[[ResourceSet], ResourceSet]] = None
    """
    Function that shall be called before reading the XMI model.

    Input parameter is the ECore metamodel ``ResourceSet``.
    Must return the ECore metamodel ``ResourceSet`` again after modifying it.

    This can be used to add custom model parts that are not part of the ECore metamodel.
    """

    emf_post_xmi_read_hook: Optional[Callable[[XMIResource], List[Any]]] = None
    """
    Function that shall be called after reading the XMI model.

    Input paramter is the XMI model ``XMIResource``.
    Must return a list of XMI model roots.

    The main use case is the removal of unused XMI model roots.
    """

    emf_class_2_need_def: Dict[StrictStr, Class2NeedDefValues] = {}
    """
    Main configuration mapping from EMF ECore classes to need types.

    Keys are ECore class names, values are instances of :class:`Class2NeedDefValues`.
    Example:

    .. code-block:: python

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

    For more explanation see :class:`Class2NeedDefValues`.
    """


class SphinxEmfCliConfig(SphinxEmfCommonConfig):
    """Sphinx-EMF config model for the CLI that converts from XMI to RST."""

    emf_path_xmi: StrictStr
    """Path to the ECore XMI model."""

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

    This is needed to distribute ECore types from one XMI to multiple RST files.

    .. note::
        Any ECore type that goes to another file than its parent must be part of
        :attr:`Class2NeedDefValues.emf_to_need_options` of its original ECore parent.
        It cannot be be a nested need as it is located in a different file.

    It is a list of dictionaries with the following keys:

    * ``path`` (``str``) RST output file path
    * ``emf_types`` (``List[str]``) list of ECore types for the file;
      must exist if ``default`` is not given or ``False`` [optional]
    * ``default`` (``bool``) if ``True`` the file will be the target for all remaining ECore classes [optional]

    .. note:: ``"default": True`` can only be set for one dictionary in the list

    .. note:: ``emf_types`` must be unique across all list entries

    .. note:: The list order is important as it defines which elements are moved first - with all its nested needs.
    """

    # see https://github.com/pydantic/pydantic/issues/239
    #     https://github.com/pydantic/pydantic/issues/156
    # for why ignoring the type error seems to be the best solution
    emf_rst_indent: conint(strict=True, gt=0) = 3  # type: ignore
    """Amount of leading spaces for each RST code indentation level."""

    emf_rst_write_default_values: StrictBool = False
    """
    Serialize XMI default values to RST need objects.

    If ``False``, need extra options and need content fields will not get created if the ECore field is not explicitly
    set in XMI.

    If ``True``, need extra options and need content fields get created with the default value even when the field is
    not explicitely set in XMI. For ``EBoolean`` types, if not given in the ECore metamodel as ``defaultValueLiteral``,
    the default value is ``False``.
    """

    emf_allowed_classes: List[StrictStr] = []
    """
    List of EMF class names that should be allowed for importing.

    The filter fields

    - :attr:`emf_allowed_classes`
    - :attr:`emf_denied_classes`
    - :attr:`emf_allowed_values`
    - :attr:`emf_denied_values`

    are evaluated with the following logic for each object instance in order:

    - discard the object if

      - :attr:`emf_allowed_classes` is not empty and
      - the object class does not appear in :attr:`emf_allowed_classes`

    - discard the object if

      - the object class appears in :attr:`emf_denied_classes`

    - discard the object if

      - the class name appears in :attr:`emf_allowed_values` and
      - the values of the object fields don't appear in :attr:`emf_allowed_values`

    - discard the object if

      - the class name appears in :attr:`emf_denied_values` and
      - the values of the object fields appear in :attr:`emf_denied_values`

    - if the logic reaches this point and the object is not discarded, it will be imported
    """
    emf_denied_classes: List[StrictStr] = []
    """
    List of EMF class names that should be denied for importing.

    For the filter evaluation logic see :attr:`emf_allowed_classes`.
    """
    emf_allowed_values: Dict[StrictStr, Dict[StrictStr, List[StrictStr]]] = {}
    """
    Map EMF class names to EMF field names to allowed values of the fields.

    For the filter evaluation logic see :attr:`emf_allowed_classes`.
    """
    emf_denied_values: Dict[StrictStr, Dict[StrictStr, List[StrictStr]]] = {}
    """
    Map EMF class names to EMF field names to denied values of the fields.

    For the filter evaluation logic see :attr:`emf_allowed_classes`.
    """

    emf_sort_field: StrictStr = None
    """
    Sort ECore instances by this field to get reproducible RST output.

    This affects containment links as well as non-containment links.

    Set to ``None`` to disable sorting.
    """

    emf_templates_dir: StrictStr = None
    """
    Path to a directory containing user defined Jinja2 templates to be injected into RST output.

    They have access to all variables the Sphinx-EMF base template have access.
    When using those it is helpful to debug Sphinx-EMF and inspect available variables in the various templates.

    The file names must follow a specific pattern to be recognized. Variable definition:

    - ``<template-name>`` RST output file name without extension
    - ``<need-type>`` is a need type
    - ``<need-field>`` is a need field; can be an extra-option, extra-link, direct content or nested content
    - ``<nested-need-type>`` is one instance of a nested need type in a ``<need-type>`` content area
    - ``<nested-needs-title>`` is the title of all nested needs (of a single type) in a ``<need-type>`` content area

    All file names must end on ``.rst.j2``.

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
    Generate the title for nested needs as given in :attr:`Class2NeedDefValues.emf_to_need_content` tuple[1].

    The setting exist as it might not be wanted because documentation readers will directly spot the nested need
    contents without a title. Also a template as documented in :attr:`emf_templates_dir` can be used to
    set a custom title.
    """


class SphinxEmfBuilderConfig(SphinxEmfCommonConfig):
    """Sphinx-EMF config model for the Sphinx builder that converts from RST to XMI."""

    emf_model_roots: List[StrictStr] = []
    """List of model roots, ordered as they shall appear in the exported XMI model."""

    emf_sort_xmi_attributes: StrictBool = False
    """Sort attributes of XMI ECore classes by name."""

    emf_xmi_output_name: StrictStr = "model.xmi"
    """
    Output name for the XMI file.

    Directory is always the builder output, commonly ``_build/emf``.
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
