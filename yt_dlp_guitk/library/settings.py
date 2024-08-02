import json
from enum import Enum
from pathlib import Path
from typing import Optional

from .const import DIRS
from .log import logger


class Settings(Enum):
    OUTPUT_DIRECTORY = "OUTPUT_DIRECTORY"

    def get(self) -> any:
        return _get_setting(self)

    def set(self, value: any):
        _set_setting(self, value)

    @classmethod
    def is_valid(cls, setting):
        if isinstance(setting, cls):
            setting = setting.value
        if setting not in cls.__members__:
            return False
        else:
            return True

    @staticmethod
    def get_dict() -> dict:
        settings = _load_user_settings()

        return settings


class _SettingsDict(dict):
    def __setitem__(self, key: Settings, value: any):
        if Settings.is_valid(key):
            super().__setitem__(Settings(key), value)
        else:
            raise KeyError(f"{key} is not a valid setting")

    def __getitem__(self, key: Settings) -> any:
        if isinstance(key, str):
            key = Settings(key.upper())

        return super().__getitem__(key)

    def dump(self) -> str:
        safe_dict = {setting.value: value for setting, value in self.items()}

        return json.dumps(safe_dict)

    def load(self, json_string: str):
        safe_dict: dict = json.loads(json_string)

        for key, value in safe_dict.items():
            if Settings.is_valid(key):
                self[key] = value


_default_settings = _SettingsDict()
_default_settings[Settings.OUTPUT_DIRECTORY] = str(DIRS.user_desktop_path.absolute())

_user_settings_filepath: Path = DIRS.user_data_path / "settings.json"
_user_settings: Optional[_SettingsDict] = None


def _load_user_settings():
    global _user_settings

    if _user_settings is not None:
        return _user_settings

    logger.debug("Loading user settings")
    _user_settings = _default_settings

    if _user_settings_filepath.exists():
        try:
            with open(_user_settings_filepath, "r") as f:
                _user_settings.load(f.read())
        except Exception:
            logger.warning("Error loading user settings from file")
    else:
        logger.debug("User settings do not exist yet, will save defaults")
        _save_settings(_user_settings)

    return _user_settings


def _save_settings(settings: _SettingsDict):
    logger.debug("Saving user settings")

    _user_settings_filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(_user_settings_filepath, "w") as f:
        f.write(settings.dump())


def _get_setting(setting: Settings) -> any:
    settings = _load_user_settings()

    return settings[setting]


def _set_setting(setting: Settings, value: any):
    settings = _load_user_settings()
    settings[setting] = value

    _save_settings(settings)
