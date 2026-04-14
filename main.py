from typing import List
# import pygame
# import PIL
import pretty_midi
from models import Track
from utility import MidiUtil

# ----

INPUT_FILE = 'input/MIDI Test.midi'

# Import data
midi_data = pretty_midi.PrettyMIDI(INPUT_FILE)
# MidiUtil.print_midi_data(midi_data)

# Initialize models
tracks: List[Track] = MidiUtil.create_tracks_from_prettymidi(midi_data)

for t in tracks:
    print(f'Track {t.name}: {len(t.notes)} notes')

(pitch_min, pitch_max) = MidiUtil.get_pitch_bounds(tracks)
print(f'Pitch bounds: {pitch_min} to {pitch_max}')

(start, end) = MidiUtil.get_time_bounds(tracks)
print(f'Time bounds: {start:.3f} to {end:.3f}')

# TODO
# Draw notes for each instrument in a canvas (pygame), converting pitch & time to coordinates