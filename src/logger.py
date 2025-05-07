import logging
from pathlib import Path

DEFAULT_LOGGER_NAME = "party_app.log"
DEFAULT_LOG_DIR = Path("./logs")


def create_single_file_logger(
    logger_name: str = DEFAULT_LOGGER_NAME,
    log_path: Path = None,
    level: int = logging.INFO,
) -> logging.Logger:
    if log_path is None:
        log_path = DEFAULT_LOG_DIR / f"{logger_name}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(_create_formatted_file_handler(filepath=log_path, level=level))
    return logger


def _create_formatted_file_handler(filepath: Path, level: int) -> logging.FileHandler:
    file_handler = logging.FileHandler(filename=filepath, encoding="utf-8")
    file_handler.setLevel(level)

    file_formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s:%(module)s:%(message)s"
    )
    file_handler.setFormatter(file_formatter)

    return file_handler