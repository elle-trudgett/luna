import logging

from rich.logging import RichHandler

LOGGER = logging.getLogger("luna")


def configure_logging() -> None:
    log_format = "%(message)s"
    logging.basicConfig(level=logging.WARNING, format=log_format, datefmt="[%X]", handlers=[RichHandler()])

    log = logging.getLogger("luna")
    log.setLevel(logging.DEBUG)

    LOGGER.info("Logging initialized")
