from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from utility.file_util import FileUtil

# ----

'''
History
  1 - Initial version
'''
USER_SETTINGS_SCHEMA_VERSION = 1
USER_SETTINGS_FILENAME = "user_settings.json"

'''
User Settings data container
'''
@dataclass
class UserSettings:
    # TODO store info about last accessed project

    # preview area displays
    show_time_display: bool = True
    show_track_names: bool = True

    @staticmethod
    def _settings_path() -> Path:
        return Path(FileUtil.get_app_data_dir()) / USER_SETTINGS_FILENAME

    def save(self) -> None:
        path = self._settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "schema_version": USER_SETTINGS_SCHEMA_VERSION,
            **asdict(self),
        }

        print(f"UserSettings | Saving user settings")

        with path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def load(self) -> None:
        path = self._settings_path()

        if not path.exists():
            print("UserSettings | No user settings found on disk - using default")
            return
        
        print(f"UserSettings | Loading user settings from \"{str(path)}\"")

        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        schema_version = data.get("schema_version", 1)

        self.show_time_display = data.get(
            "show_time_display",
            self.show_time_display
        )

        self.show_track_names = data.get(
            "show_track_names",
            self.show_track_names
        )


# module-level singleton instance
user_settings = UserSettings()