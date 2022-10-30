"""Extension entry point for Sphinx."""
from typing import Any, Dict

from sphinx.application import Sphinx
from sphinx.config import Config

from sphinx_emf.builder import EmfBuilder
from sphinx_emf.config.model import SphinxEmfBuilderConfig
from sphinx_emf.config.validate import validate_config
from sphinx_emf.sphinx_logging import get_logger


VERSION = "0.1.0"


def setup(app) -> Dict[str, Any]:  # noqa: F841  # used by Sphinx when registering the plugin
    """Set up the extension."""
    log = get_logger(__name__)
    log.info("Setting up sphinx-emf extension")

    app.add_builder(EmfBuilder)

    app.connect("config-inited", check_configuration)

    # configurations
    # types are not given as pydantic is used to check the config in detail (see config/model.py)
    app.add_config_value(name="emf_path_m2_model", default=None, rebuild="html")
    app.add_config_value(name="emf_pre_read_hook", default=None, rebuild="html")
    app.add_config_value(name="emf_post_read_hook", default=None, rebuild="html")
    app.add_config_value(name="emf_class_2_need_def", default={}, rebuild="html")
    app.add_config_value(name="emf_model_roots", default=[], rebuild="html")
    app.add_config_value(name="emf_sort_xmi_attributes", default=False, rebuild="html")
    app.add_config_value(name="emf_xmi_output_name", default="m1_model.xmi", rebuild="html")

    return {
        "version": VERSION,  # identifies the version of our extension
        "parallel_read_safe": True,  # support parallel modes
        "parallel_write_safe": True,
    }


def check_configuration(_app: Sphinx, config: Config):
    """Check all configuration needed by the builder with pydantic."""
    logger = get_logger(__name__)
    validate_config(config, logger, SphinxEmfBuilderConfig)
