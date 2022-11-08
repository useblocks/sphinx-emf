"""
CLI interface to sphinx-emf.

Usecase is to read ECore metamodels and XMI models and generate need RST files.
"""

import importlib
import logging
import sys

import click

from sphinx_emf.config.model import SphinxEmfCliConfig
from sphinx_emf.config.validate import validate_config
from sphinx_emf.main import write_rst


log = logging.getLogger("sphinx_emf.cli")


@click.command()
@click.argument(
    "confpy_path",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
)
def run(confpy_path):
    """Import settings from conf.py argument and run the EMF importer."""
    log_format = "[%(levelname)5s] %(name)s - %(message)s"
    logging.basicConfig(level=logging.DEBUG, format=log_format)
    log.info(f"Loading confpy_path={confpy_path}")

    try:
        # creates a new module spec
        confpy_spec = importlib.util.spec_from_file_location("conf", confpy_path)
        # create a new module from the spec
        confpy = importlib.util.module_from_spec(confpy_spec)
        # execute the module in its own namespace
        confpy_spec.loader.exec_module(confpy)
    except SyntaxError as exc:
        log.error("Error importing config file")
        log.error(exc)
        sys.exit(1)

    config = validate_config(confpy, log, SphinxEmfCliConfig)
    write_rst(config)


if __name__ == "__main__":
    run(["tests/data/prod/config_sphinx_emf.py"])
