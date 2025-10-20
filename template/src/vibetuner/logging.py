import logging
import sys
from enum import Enum
from pathlib import Path

from loguru import logger


class LogLevel(str, Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame is not None and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        # Format the message with module information inline
        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            f"[{record.name}] {record.getMessage()}",
        )


def setup_logging(
    level: str | int | None = LogLevel.INFO,
    log_file: str | Path | None = None,
    rotation: str = "10 MB",
    retention: str = "1 week",
) -> None:
    """Configure logging for the application.

    Args:
        level: Minimum logging level threshold
        log_file: Optional path to log file. If None, logs only to stderr
        rotation: When to rotate the log file
        retention: How long to keep log files

    """
    # Remove default handler
    logger.remove()

    if level is None:
        level = LogLevel.INFO

    # Define format for the logs
    format_string = (
        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{line}</cyan> - "
        "<level>{message}</level>"
    )

    # Add stderr handler with custom format
    logger.add(sys.stderr, level=level, format=format_string, colorize=True)

    # Add file handler if log_file is specified
    if log_file:
        logger.add(
            str(log_file),
            level=level,
            format=format_string,
            rotation=rotation,
            retention=retention,
            compression="zip",
        )

    # Intercept standard logging
    logging.basicConfig(handlers=[InterceptHandler()], level=0, force=True)

    # Optional: Capture warnings from warnings module
    logging.captureWarnings(True)

    logger.info("Logging configured successfully")
