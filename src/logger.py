import sys

from aiologger import Logger
from aiologger.formatters.base import Formatter

from aiologger.handlers.streams import AsyncStreamHandler
from aiologger.levels import LogLevel

logger: Logger


def setup_logger():
    logger = Logger(name="api_logger")

    formatter = Formatter(
        fmt="{asctime} | {levelname} | {message}",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="{",
    )

    stream_handler = AsyncStreamHandler(stream=sys.stdout)
    stream_handler.formatter = formatter
    logger.add_handler(stream_handler)

    logger.level = LogLevel.INFO

    return logger


logger = setup_logger()
