"""PyEcore functions to read/write XMI models using ECore metamodels."""
import re

from pyecore.resources import URI, ResourceSet
from pyecore.resources.xmi import XMIOptions, XMIResource

from sphinx_emf.config.model import SphinxEmfCliConfig, SphinxEmfCommonConfig


def load_xmi(config: SphinxEmfCliConfig):
    """Read a XMI file with its ECore metamodel using pyecore."""
    rset = load_ecore(config)

    # At this point, the .ecore is loaded in the 'rset' as a metamodel
    # load the XMI model
    resource = rset.get_resource(URI(config.emf_path_xmi))

    if config.emf_post_xmi_read_hook is not None:
        # option to run user specific code (like remove model roots)
        model_roots = config.emf_post_xmi_read_hook(resource)
    else:
        model_roots = resource.contents
    return model_roots


def load_ecore(config: SphinxEmfCommonConfig) -> ResourceSet:
    """Read an ECore metamodel using pyecore."""
    rset = ResourceSet()

    # load metamodel
    resource = rset.get_resource(URI(config.emf_path_ecore))
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root

    if config.emf_pre_xmi_read_hook is not None:
        # option to run user specific code (like add classes not in the metamodel)
        config.emf_pre_xmi_read_hook(rset)

    return rset


def save_xmi(model_roots, output_path: str):
    """Save the XMI model back out - the history NS will be saved at the node."""
    resource_out = XMIResource(URI(output_path), use_uuid=True)
    for root in model_roots:
        resource_out.append(root)
    resource_out.save(
        options={
            XMIOptions.SERIALIZE_DEFAULT_VALUES: False,
            # XMIOptions.OPTION_USE_XMI_TYPE: True,
        },
    )
    modify_line_breaks(output_path)


def modify_line_breaks(path: str):
    """Reformat written XML file to wrap attributes on new lines."""
    with open(path, encoding="utf-8") as f_pointer:
        data = f_pointer.read()

    element_to_newline_pattern = r"^( *)(<[\w:]+) "
    element_to_newline_replace = r"\1\2\n\1    "

    data = re.sub(element_to_newline_pattern, element_to_newline_replace, data, flags=re.MULTILINE)

    attribute_to_newline_pattern = r"^( +)([^\"<]+\"[^\"]+\") "
    attribute_to_newline_replace = r"\1\2\n\1"
    old_data = data
    while True:
        new_data = re.sub(attribute_to_newline_pattern, attribute_to_newline_replace, old_data, flags=re.MULTILINE)
        if new_data == old_data:
            break
        old_data = new_data
    with open(path, mode="w", encoding="utf-8") as f_pointer:
        f_pointer.write(new_data)
