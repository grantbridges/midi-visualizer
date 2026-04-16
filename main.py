from typing import List
import pygame as pg
# import PIL
import sys
import os
import pretty_midi
from common.constants import Const
from models import Track, Note
from common import Color
from utility import MidiUtil

# ----

INPUT_MIDI_FILE = 'input/MIDI Test.midi'
#INPUT_MP3_FILE = 'input/MIDI Test.mp3'

# Import data
midi_data = pretty_midi.PrettyMIDI(INPUT_MIDI_FILE)
# MidiUtil.print_midi_data(midi_data)

# Initialize models
tracks: List[Track] = MidiUtil.create_tracks_from_prettymidi(midi_data)

# temp: dummy hardcoding of track settings
tracks[0].color = Color.RED
tracks[0].bar_height = 10
tracks[0].bar_width_mult = 400
tracks[1].color = Color.BLUE
tracks[1].bar_height = 5
tracks[1].bar_width_mult = 200

for t in tracks:
    print(f'Track {t.name}: {len(t.notes)} notes')

(pitch_min, pitch_max) = MidiUtil.get_pitch_bounds(tracks)
print(f'Pitch bounds: {pitch_min} to {pitch_max}')

(time_min, time_max) = MidiUtil.get_time_bounds(tracks)
print(f'Time bounds: {time_min:.3f} to {time_max:.3f}')

# ----

# Animation start

# show on right monitor (Grant local debug setup)
#os.environ['SDL_VIDEO_WINDOW_POS'] = '2200,200'
pg.init()

# constants
PIXELS_PER_SECOND = 200
SW = Const.SCREEN_WIDTH # shorthand for easier reading
SH = Const.SCREEN_HEIGHT
PAD = Const.SCREEN_PADDING
PLAYHEAD_X = SW / 2 # line where notes cross when they play

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

    # draw
    screen.fill(Color.DARK_GRAY)

    time_offset = time_min - (SW - PLAYHEAD_X) / PIXELS_PER_SECOND
    current_time = time_offset + current_frame / Const.FPS

    # draw midi bars
    drew_notes = False
    for track in tracks:
        for note in track.notes:
            # x and width calc
            x = PLAYHEAD_X + (note.start - current_time) * track.bar_width_mult
            w = note.duration * track.bar_width_mult

            # y and height calc
            t = (note.pitch - pitch_min) / (pitch_max - pitch_min)
            y_min = PAD
            y_max = SH - PAD
            y = (y_max + t * (y_min - y_max)) - track.bar_height / 2
            h = track.bar_height

            color = track.color
            if x <= PLAYHEAD_X:
                color = Color.WHITE
                note.alpha = 255 * ((x + w) / PLAYHEAD_X)
                note.alpha = max(0, min(255, note.alpha))  # clamp

            if note.alpha > 0:
                # draw
                surf = pg.Surface((w, h), pg.SRCALPHA)
                surf.fill(Color.rgba(color, note.alpha))
                screen.blit(surf, (x, y))

                drew_notes = True

    if not drew_notes:
        # done
        pg.quit()
        raise SystemExit

    # draw playhead line that notes will cross when they "play"
    pg.draw.line(screen, Color.LIGHT_GRAY, (PLAYHEAD_X, 0), (PLAYHEAD_X, SH), 1)

    # update display
    pg.display.flip()

    # sleep then iterate frame count
    clock.tick(Const.FPS)
    current_frame += 1