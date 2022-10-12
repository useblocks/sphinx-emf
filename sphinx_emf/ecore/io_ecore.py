"""Read M1 model with pyecore using the M2 model."""
from pyecore.resources import URI, ResourceSet
from pyecore.resources.xmi import XMIOptions, XMIResource

from sphinx_emf.config.model import SphinxEmfConfig


def load_m1(config: SphinxEmfConfig):
    """Read a M1 EMF file with its M2 ECore model using pyecore."""
    rset = load_m2(config)

    # At this point, the .ecore is loaded in the 'rset' as a metamodel
    # load the M1 model
    resource = rset.get_resource(URI(config.emf_path_m1_model))

    if config.emf_post_read_hook is not None:
        # option to run user specific code (like remove model roots)
        model_roots = config.emf_post_read_hook(resource)
    else:
        model_roots = resource.contents
    return model_roots


def load_m2(config: SphinxEmfConfig) -> ResourceSet:
    """Read an M2 EMF using pyecore."""
    rset = ResourceSet()

    # load M2 model
    resource = rset.get_resource(URI(config.emf_path_m2_model))
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root

    if config.emf_pre_read_hook is not None:
        # option to run user specific code (like add classes not in M2)
        config.emf_pre_read_hook(rset)

    return rset


def save_m1(model_roots, output_path: str):
    """Save the M1 model back out - the history NS will be saved at the node."""
    resource_out = XMIResource(URI(output_path), use_uuid=True)
    for root in model_roots:
        resource_out.append(root)
    resource_out.save(
        options={
            XMIOptions.SERIALIZE_DEFAULT_VALUES: True,
            XMIOptions.OPTION_USE_XMI_TYPE: True,
        }
    )
