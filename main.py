from typing import List
import pygame as pg
# import PIL
import sys
import pretty_midi
from common.constants import Const
from models import Track
from common import Color
from utility import MidiUtil

# ----

INPUT_FILE = 'input/MIDI Test.midi'

# Import data
midi_data = pretty_midi.PrettyMIDI(INPUT_FILE)
MidiUtil.print_midi_data(midi_data)

# Initialize models
tracks: List[Track] = MidiUtil.create_tracks_from_prettymidi(midi_data)

# temp: dummy hardcoding of track colors
tracks[0].color = Color.RED
tracks[1].color = Color.BLUE

for t in tracks:
    print(f'Track {t.name}: {len(t.notes)} notes')

(pitch_min, pitch_max) = MidiUtil.get_pitch_bounds(tracks)
print(f'Pitch bounds: {pitch_min} to {pitch_max}')

(start, end) = MidiUtil.get_time_bounds(tracks)
print(f'Time bounds: {start:.3f} to {end:.3f}')

# ----

# Animation start

pg.init()

# constants
BAR_WIDTH_STRETCH_MULT = 200
BAR_HEIGHT = 10
SW = Const.SCREEN_WIDTH # shorthand for easier reading
SH = Const.SCREEN_HEIGHT
PAD = Const.SCREEN_PADDING

screen = pg.display.set_mode((SW, SH))
pg.display.set_caption(Const.TITLE)
clock = pg.time.Clock()

current_frame = 0
initial_x = SW
x_vel = 10 # pixels per frame

# main animation loop
while True:
    # get all events currently in the queue and handle
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                pg.quit()
                raise SystemExit

    # Draw
    screen.fill(Color.WHITE)

    # draw midi bars
    for track in tracks:
        for n in track.notes:
            x = initial_x + n.start * BAR_WIDTH_STRETCH_MULT - current_frame * x_vel
            y = MidiUtil.pitch_to_y(n.pitch, pitch_min, pitch_max, SH, PAD) - BAR_HEIGHT / 2
            w = n.duration * BAR_WIDTH_STRETCH_MULT
            h = BAR_HEIGHT

            surf = pg.Surface((w, h), pg.SRCALPHA)
            alpha = max(0, 255 - current_frame * 2) # temp: POC for changing alpha
            surf.fill(Color.rgba(track.color, alpha))
            screen.blit(surf, (x, y))

    # center vertical line
    pg.draw.line(screen, Color.LIGHT_GRAY, (SW / 2, 0), (SW / 2, SH), 1)

    # update display
    pg.display.flip()

    # sleep then iterate frame count
    clock.tick(Const.FPS)
    current_frame += 1