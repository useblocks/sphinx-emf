"""Basic log configuration."""
import logging


def config_logger() -> None:
    """Define a basic log format and sets log level to DEBUG."""
    log_format = "[%(levelname)5s] %(name)s - %(message)s"
    logging.basicConfig(format=log_format, level=logging.DEBUG)
