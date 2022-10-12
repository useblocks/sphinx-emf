"""
CLI interface to sphinx-emf.

Usecase is to read M1/M2 models and generate need RST files.
"""

from importlib.machinery import SourceFileLoader
import logging
import sys
from typing import Callable, Dict, List

import click
from pydantic import ValidationError

from sphinx_emf.config.model import SphinxEmfConfig
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
    log.info(f"Loading {confpy_path=}")

    try:
        confpy = SourceFileLoader("conf", confpy_path).load_module()
    except SyntaxError as exc:
        log.error("Error importing config file")
        log.error(exc)
        sys.exit(1)

    config = validate_config(confpy)
    write_rst(config)


def validate_config(confpy):
    """Run pydantic on emf_* fields of conf.py."""
    allowed_types = (int, str, List, Dict, Callable)
    all_fields = dir(confpy)
    emf_fields = {}
    for field in all_fields:
        if field.startswith("emf_"):
            value = getattr(confpy, field)
            if isinstance(value, (allowed_types)):
                emf_fields[field] = value
    try:
        config = SphinxEmfConfig(**emf_fields)
    except ValidationError as exc:
        log.error("Config validation failed")
        log.error(exc)
        sys.exit(1)
    log.info("Config validation successful")
    return config


if __name__ == "__main__":
    run(["tests/data/prod/config_sphinx_emf.py"])
