"""Extension entry point for Sphinx."""
from typing import Any, Dict

from sphinx_emf.builder import EmfBuilder
from sphinx_emf.sphinx_logging import get_logger


VERSION = "0.1.0"


def setup(app) -> Dict[str, Any]:  # noqa: F841  # used by Sphinx when registering the plugin
    """Set up the extension."""
    log = get_logger(__name__)
    log.info("Setting up sphinx-emf extension")

    app.add_builder(EmfBuilder)

    # configurations
    # types are not given as pydantic is used to check the config in detail (see config/model.py)
    app.add_config_value(name="emf_path_m1_model", default=None, rebuild="html")
    app.add_config_value(name="emf_path_m2_model", default=None, rebuild="html")
    app.add_config_value(name="emf_rst_indent", default=3, rebuild="html")
    app.add_config_value(name="emf_allowed_classes", default=[], rebuild="html")
    app.add_config_value(name="emf_denied_classes", default=[], rebuild="html")
    app.add_config_value(name="emf_allowed_values", default={}, rebuild="html")
    app.add_config_value(name="emf_denied_values", default={}, rebuild="html")
    app.add_config_value(name="emf_remove_unlinked_types", default=[], rebuild="html")
    app.add_config_value(name="emf_pre_read_hook", default=[], rebuild="html")
    app.add_config_value(name="emf_post_read_hook", default=[], rebuild="html")
    app.add_config_value(name="emf_class_2_need_def", default={}, rebuild="html")
    app.add_config_value(name="emf_sort_field", default=None, rebuild="html")
    app.add_config_value(name="emf_model_roots", default=[], rebuild="html")

    return {
        "version": VERSION,  # identifies the version of our extension
        "parallel_read_safe": True,  # support parallel modes
        "parallel_write_safe": True,
    }
