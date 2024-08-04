import os
import shutil
from typing import Optional

from dotenv import load_dotenv
from loguru import logger

load_dotenv()


def get(name: str, default: Optional[str] = None) -> str:
    logger.trace(f"env.get called with name '{name}' and default '{default}'")
    if os.getenv(name):
        return os.environ[name]

    if default:
        return default
    else:
        raise Exception(f"{name} environment variable is not set.")


DEBUG_APP = get("DEBUG", "0") == "1"
DEBUG_GUITK = get("DEBUG_GUITK", "0") == "1"

FFMPEG_PRESENT = shutil.which("ffmpeg") is not None
