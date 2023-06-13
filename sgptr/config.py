import os
from pathlib import Path
from tempfile import gettempdir
from typing import Any

from click import UsageError

CONFIG_FOLDER = os.path.expanduser("~/.config")
SHELL_GPT_CONFIG_FOLDER = Path(CONFIG_FOLDER) / "shell_gptr"
SHELL_GPT_CONFIG_PATH = SHELL_GPT_CONFIG_FOLDER / ".sgptrc"
CACHE_PATH = Path(gettempdir()) / "shell_gptr_cache"

# TODO: Refactor ENV variables with SGPT_ prefix.
DEFAULT_CONFIG = {
    # TODO: Refactor it to CHAT_STORAGE_PATH.
    "CACHE_PATH": os.getenv("CACHE_PATH", str(CACHE_PATH)),
    "CACHE_LENGTH": int(os.getenv("CACHE_LENGTH", "100")),
    "REQUEST_TIMEOUT": int(os.getenv("REQUEST_TIMEOUT", "60")),
    "API_HOST": os.getenv("API_HOST", "http://34.94.199.195:7070"),
    "DEFAULT_COLOR": os.getenv("DEFAULT_COLOR", "magenta"),
    "DEFAULT_EXECUTE_SHELL_CMD": os.getenv("DEFAULT_EXECUTE_SHELL_CMD", "false"),
    # New features might add their own config variables here.
}


class Config(dict):  # type: ignore
    def __init__(self, config_path: Path, **defaults: Any):
        self.config_path = config_path

        if self._exists:
            self._read()
            has_new_config = False
            for key, value in defaults.items():
                if key not in self:
                    has_new_config = True
                    self[key] = value
            if has_new_config:
                self._write()
        else:
            config_path.parent.mkdir(parents=True, exist_ok=True)
            super().__init__(**defaults)
            self._write()

    @property
    def _exists(self) -> bool:
        return self.config_path.exists()

    def _write(self) -> None:
        with open(self.config_path, "w", encoding="utf-8") as file:
            string_config = ""
            for key, value in self.items():
                string_config += f"{key}={value}\n"
            file.write(string_config)

    def _read(self) -> None:
        with open(self.config_path, "r", encoding="utf-8") as file:
            for line in file:
                if not line.startswith("#"):
                    key, value = line.strip().split("=")
                    self[key] = value

    def get(self, key: str) -> str:  # type: ignore
        # Prioritize environment variables over config file.
        value = os.getenv(key) or super().get(key)
        if not value:
            raise UsageError(f"Missing config key: {key}")
        return value


cfg = Config(SHELL_GPT_CONFIG_PATH, **DEFAULT_CONFIG)
