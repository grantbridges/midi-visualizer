from __future__ import annotations
from dataclasses import dataclass
from PySide6.QtCore import QSettings
from common import Const


import logging
logger = logging.getLogger("UserSettings")


@dataclass
class UserSettings:
    '''
    User Settings data container
    '''
    # file info
    # persisted so we can reload last project on startup
    active_project_path: str | None = None

    # preview area displays
    show_time_display: bool = True
    show_track_groups: bool = False
    show_guides: bool = True
    show_pitches: bool = False
    mute_audio: bool = False
    loop_preview: bool = True

    @staticmethod
    def _qsettings() -> QSettings:
        return QSettings(Const.ORG_NAME, Const.APP_NAME)

    def save(self) -> None:
        logger.debug("Saving user settings")

        settings = self._qsettings()

        settings.setValue("project/active_project_path", self.active_project_path)

        settings.setValue("preview/show_time_display", self.show_time_display)
        settings.setValue("preview/show_track_groups", self.show_track_groups)
        settings.setValue("preview/show_guides", self.show_guides)
        settings.setValue("preview/show_pitches", self.show_pitches)
        settings.setValue("preview/mute_audio", self.mute_audio)
        settings.setValue("preview/loop_preview", self.loop_preview)

        settings.sync()

    def load(self) -> None:
        logger.info("Loading user settings")

        settings = self._qsettings()

        self.active_project_path = settings.value("project/active_project_path", None, type=str)

        self.show_time_display = settings.value("preview/show_time_display", self.show_time_display, type=bool)
        self.show_track_groups = settings.value("preview/show_track_groups",self.show_track_groups, type=bool)
        self.show_guides = settings.value( "preview/show_guides",self.show_guides,type=bool)
        self.show_pitches = settings.value("preview/show_pitches",self.show_pitches,type=bool)
        self.mute_audio = settings.value("preview/mute_audio", self.mute_audio, type=bool)
        self.loop_preview = settings.value("preview/loop_preview", self.loop_preview, type=bool)

# module-level singleton instance
user_settings = UserSettings()