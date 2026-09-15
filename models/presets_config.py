from dataclasses import dataclass, field
import json
import logging
from pathlib import Path
from typing import List
from utility.file_util import FileUtil

from models.track_preset import TrackPreset
logger = logging.getLogger("PresetsConfig")

# ----

'''
History
  1 - Initial version
'''
PRESETS_CONFIG_SCHEMA_VERSION = 1
PRESETS_CONFIG_FILE_NAME = "presets.json"

@dataclass
class PresetsConfig:
    '''
    App-level presets config container
    '''
    track_presets: List[TrackPreset] = field(default_factory=list)

    @staticmethod
    def _config_path() -> Path:
        return Path(FileUtil.get_app_data_dir()) / PRESETS_CONFIG_FILE_NAME

    def save(self) -> None:
        path = self._config_path()
        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            logger.debug(f"Save | Saving presets config")

            data = {
                "schema_version": PRESETS_CONFIG_SCHEMA_VERSION,
                "track_presets": [
                    track_preset.save()
                    for track_preset in self.track_presets
                ],
            }

            with path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception:
            logger.exception("Save | Unable to save user settings")
    
    def load(self) -> None:
        path = self._config_path()

        if not path.exists():
            logger.info("Load | No presets config found on disk - using default")
            return

        logger.info(f"Load | Loading presets config from \"{str(path)}\"")

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            schema_version = data["schema_version"]

            self.track_groups = [
                TrackPreset.load(track_presets_data, schema_version)
                for track_presets_data in data["track_presets"]
            ]

            logger.info(f"Load | Loaded presets config")

        except Exception:
            logger.exception(f"Load | Unable to load presets config - using default")

# module-level singleton instance
presets_config = PresetsConfig()