"""Read M1 model with pyecore using the M2 model."""
from pyecore.resources import URI, ResourceSet
from pyecore.resources.xmi import XMIResource

from sphinx_emf.config.model import SphinxEmfConfig


def load(config: SphinxEmfConfig):
    """Read a M1 EMF file with its M2 ECore model using pyecore."""
    rset = ResourceSet()

    # load M2 model
    resource = rset.get_resource(URI(config.emf_path_m2_model))
    mm_root = resource.contents[0]
    rset.metamodel_registry[mm_root.nsURI] = mm_root

    if config.emf_pre_read_hook is not None:
        # option to run user specific code (like add M2 )
        config.emf_pre_read_hook(rset)

    # At this point, the .ecore is loaded in the 'rset' as a metamodel
    # load the M1 model
    resource = rset.get_resource(URI(config.emf_path_m1_model))

    model_root = resource.contents[0]
    model_root_history = resource.contents[1]
    return model_root, model_root_history


def save(model_root, model_root_history, out_path):
    """Save the M1 model back out - the history NS will be saved at the node."""
    resource_out = XMIResource(URI(out_path), use_uuid=True)
    resource_out.append(model_root)  # We add the root to the resource
    resource_out.append(model_root_history)
    resource_out.save()  # will save the result in 'my/path.xmi'


if __name__ == "__main__":
    # just an example how to use the functions
    root, history = load("path_m1", "path_m2")
    save(root, history, "out_path.tca")
