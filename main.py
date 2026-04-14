from typing import List
# import pygame
# import PIL
import pretty_midi

from utility.midi_util import MidiUtil

INPUT_FILE = 'input/MIDI Test.midi'

pm = pretty_midi.PrettyMIDI(INPUT_FILE)

MidiUtil.print_midi_data(pm)