import sys

from loguru import logger

from . import const, env


def configure(remove_existing=True):
    log_filepath = const.DIRS.user_log_path / "app.log"

    if remove_existing:
        logger.remove()

    if env.get("DEBUG", "0") == "1":
        stderr_level = "DEBUG"
    else:
        stderr_level = env.get("LOG_STDERR_LEVEL", "ERROR")

    if stderr_level:
        logger.add(sys.stderr, level=stderr_level)

    logger.add(
        log_filepath,
        level=env.get("LOG_FILE_LEVEL", "WARNING"),
        rotation=env.get("LOG_FILE_ROTATION", "00:00"),
    )

    logger.trace(f"Writing logs to {log_filepath}")
