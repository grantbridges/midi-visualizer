from typing import List
# import pygame
# import PIL
import pretty_midi

from models import Track
from utility import MidiUtil

INPUT_FILE = 'input/MIDI Test.midi'

midi_data = pretty_midi.PrettyMIDI(INPUT_FILE)

tracks: List[Track] = MidiUtil.create_tracks_from_prettymidi(midi_data)

for t in tracks:
    print(f'Track {t.name}: {len(t.notes)} notes')