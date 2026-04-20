from dataclasses import dataclass
from enum import Enum
# import PIL
import sys
import pretty_midi
from editor import EditorWindow
from models import VisConfig

from PySide6.QtWidgets import QApplication

# ----

TRACK_NAME = 'Puppet Master'
#TRACK_NAME = 'MIDI Test'
INPUT_MIDI_FILE = f'input/{TRACK_NAME}.midi'
INPUT_MP3_FILE = f'input/{TRACK_NAME}.mp3'
INPUT_CONFIG_FILE = f'input/{TRACK_NAME}.mvc'

START_TIME_OFFSET = 0 # seconds

@dataclass
class App:
    vis_config: VisConfig = None

    def start(self):
        print(f"Starting MIDI Visualizer app")

        # 1) Check if we already have a .mvc (midi visual config) file for this track
        self.vis_config = VisConfig.load(INPUT_CONFIG_FILE)

        if self.vis_config is None:
            # 2) Generate new vis_config from midi file
            print(f"Generating new config for \"{TRACK_NAME}\"")
            midi_data = pretty_midi.PrettyMIDI(INPUT_MIDI_FILE)
            self.vis_config = VisConfig.create_from_midi_data(TRACK_NAME, midi_data)

            # 2.1) Save out as initial generated file
            self.vis_config.save(INPUT_CONFIG_FILE)

        # 3) Start app in requested mode
        q_app = QApplication(sys.argv)
        editor = EditorWindow(self.vis_config, INPUT_CONFIG_FILE)
        editor.show()
        sys.exit(q_app.exec())

App().start()