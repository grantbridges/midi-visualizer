from __future__ import annotations

import json
from dataclasses import dataclass, asdict, field
from pathlib import Path
from utility.file_util import FileUtil

import logging
logger = logging.getLogger("UserSettings")

# ----

'''
History
  1 - Initial version
'''
USER_SETTINGS_SCHEMA_VERSION = 1
USER_SETTINGS_FILENAME = "user_settings.json"

MAX_RECENT_PROJECTS_COUNT = 10
    
@dataclass
class UserSettings:
    '''
    User Settings data container
    '''
    # file info
    # persisted so we can reload last project on startup
    active_project_path: str | None = None
    recent_projects: list[str] = field(default_factory=list)

    # display settings
    fullscreen: bool = False

    # preview area displays
    show_time_display: bool = True
    show_track_groups: bool = False
    show_guides: bool = True
    show_pitches: bool = False
    mute_audio: bool = False
    loop_preview: bool = True

    @staticmethod
    def _settings_path() -> Path:
        return Path(FileUtil.get_app_data_dir()) / USER_SETTINGS_FILENAME

    def save(self) -> None:
        path = self._settings_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.debug(f"Save | Saving user settings")

            data = {
                "schema_version": USER_SETTINGS_SCHEMA_VERSION,
                "active_project_path": self.active_project_path,
                "recent_projects": self.recent_projects,
                "fullscreen": self.fullscreen,
                "show_time_display": self.show_time_display,
                "show_track_groups": self.show_track_groups,
                "show_guides": self.show_guides,
                "show_pitches": self.show_pitches,
                "mute_audio": self.mute_audio,
                "loop_preview": self.loop_preview,
            }
            
            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            logger.exception("Save | Unable to save user settings")

    def load(self) -> None:
        path = self._settings_path()

        if not path.exists():
            logger.info("Load | No user settings found on disk - using default")
            return

        logger.info(f"Load | Loading user settings from \"{str(path)}\"")

        try:
            with path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            schema_version = data.get("schema_version", 1)

            self.active_project_path = data["active_project_path"]
            self.recent_projects = data["recent_projects"]
            self.fullscreen = data["fullscreen"]
            self.show_time_display = data["show_time_display"]
            self.show_track_groups = data["show_track_groups"]
            self.show_guides = data["show_guides"]
            self.show_pitches = data["show_pitches"]
            self.mute_audio = data["mute_audio"]
            self.loop_preview = data["loop_preview"]

        except Exception:
            logger.exception("Load | Unable to load user settings - using default")

    def remove_from_recent_projects(self, filepath: str):
        # remove any existing occurrences of this project (by filepath)
        self.recent_projects = [x for x in self.recent_projects if x != filepath]

    def add_recent_project(self, filepath: str):
        '''
        Returns reference to newly added recent project
        '''
        self.remove_from_recent_projects(filepath)

        self.recent_projects.insert(0, filepath)

        while len(self.recent_projects) > MAX_RECENT_PROJECTS_COUNT:
            self.recent_projects.pop()

# module-level singleton instance
user_settings = UserSettings()