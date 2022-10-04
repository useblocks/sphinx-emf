"""Entry point to the app."""

import logging

from sphinx_emf.logger import config_logger


logger = logging.getLogger(__name__)


def run() -> None:
    """Set up logger and execute main function."""
    config_logger()
    logger.info("This program should have never been built.")


if __name__ == "__main__":
    run()
