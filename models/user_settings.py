from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from pathlib import Path

from utility.file_util import FileUtil

# ----

'''
History
  1 - Initial version
  2 - Added "show guides" and "mute audio"
  3 - Added "show pitches"
  4 - Renamed to "show_track_groups"
'''
USER_SETTINGS_SCHEMA_VERSION = 4
USER_SETTINGS_FILENAME = "user_settings.json"

'''
User Settings data container
'''
@dataclass
class UserSettings:
    # TODO store info about last accessed project

    # preview area displays
    show_time_display: bool = True
    show_track_groups: bool = True
    show_guides: bool = True
    show_pitches: bool = True
    mute_audio: bool = True

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

        self.show_time_display = data["show_time_display"]

        if schema_version >= 2:
            self.show_guides = data["show_guides"]
            self.mute_audio = data["mute_audio"]

        if schema_version >= 3:
            self.show_pitches = data["show_pitches"]

        if schema_version >= 4:
            self.show_track_groups = data["show_track_groups"]
        else:
            self.show_track_groups = data["show_track_names"]


# module-level singleton instance
user_settings = UserSettings()