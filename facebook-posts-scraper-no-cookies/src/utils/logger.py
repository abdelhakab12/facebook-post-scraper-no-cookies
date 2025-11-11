thonimport logging
import sys
from typing import Optional

_LOGGING_CONFIGURED = False

def setup_logging(level: str = "INFO") -> None:
    """
    Configure root logging with a sensible default format.

    Calling this multiple times is safe; subsequent calls will update
    the log level without re-adding handlers.
    """
    global _LOGGING_CONFIGURED

    numeric_level = getattr(logging, level.upper(), logging.INFO)

    if not _LOGGING_CONFIGURED:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)

        root_logger = logging.getLogger()
        root_logger.setLevel(numeric_level)
        root_logger.handlers.clear()
        root_logger.addHandler(handler)

        _LOGGING_CONFIGURED = True
    else:
        logging.getLogger().setLevel(numeric_level)

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger instance. If setup_logging has not been called yet,
    this will configure basic logging implicitly.
    """
    if not _LOGGING_CONFIGURED:
        setup_logging("INFO")
    return logging.getLogger(name)