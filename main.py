from enum import Enum
import pygame as pg
# import PIL
import sys
import os
import pretty_midi
from common.constants import Const
from models import VisConfig
from common import Color

# ----

class RunMode(str, Enum):
    # Animates MIDI in pygame window
    Test = "Test",
    # Generates MIDI animation to mp4
    Generate = "Generate"

run_mode = RunMode.Test
if len(sys.argv) > 1:
    run_mode = sys.argv[1]

print(f"Running script in {run_mode} mode")

if run_mode != RunMode.Test:
    print(f"Warning: {RunMode.Generate} mode not yet supported - exiting")
    quit()

TRACK_NAME = 'Puppet Master'
#TRACK_NAME = 'MIDI Test'
INPUT_MIDI_FILE = f'input/{TRACK_NAME}.midi'
INPUT_MP3_FILE = f'input/{TRACK_NAME}.mp3'
INPUT_CONFIG_FILE = f'input/{TRACK_NAME}.mvc'

START_TIME_OFFSET = 0 # seconds

# ----

# 1) Check if we already have a .mvc (midi visual config) file for this track
vis_config = VisConfig.load(INPUT_CONFIG_FILE)

if vis_config is None:
    # 2) Generate new vis_config from midi file
    print(f"Generating new config for \"{TRACK_NAME}\"")
    midi_data = pretty_midi.PrettyMIDI(INPUT_MIDI_FILE)
    vis_config = VisConfig.create_from_midi_data(TRACK_NAME, midi_data)

    # temp: dummy hardcoding of track settings
    # vis_config.play_audio = False
    # vis_config.tracks[0].color = Color.KAYLA_1
    # vis_config.tracks[0].bar_height = 10
    # vis_config.tracks[0].bar_pixels_per_second = 400
    # vis_config.tracks[1].color = Color.KAYLA_2
    # vis_config.tracks[1].bar_height = 5
    # vis_config.tracks[1].bar_pixels_per_second = 100

    # 2.1) Save out as initial generated file
    vis_config.save(INPUT_CONFIG_FILE)

# ----

# Animation start

(pitch_min, pitch_max) = vis_config.get_pitch_bounds()
(time_min, time_max) = vis_config.get_time_bounds()

# text helper
def draw_text(screen: pg.Surface, text, x, y, color, font_size):
    font = pg.font.Font(Const.PRIMARY_FONT, font_size)
    text_object = font.render(text, True, color)
    text_rect = text_object.get_rect()
    text_rect.left = x
    text_rect.top = y
    screen.blit(text_object, text_rect)

# show on right monitor (Grant local debug setup)
os.environ['SDL_VIDEO_WINDOW_POS'] = '2200,200'
pg.init()
pg.mixer.init()
pg.mixer.music.load(INPUT_MP3_FILE)

# constants
PIXELS_PER_SECOND = 200
SW = Const.SCREEN_WIDTH # shorthand for easier reading
SH = Const.SCREEN_HEIGHT
PAD = Const.SCREEN_PADDING
PLAYHEAD_X = SW / 2 # line where notes cross when they play

# Initial time offset, in seconds
# Defaults to the time needed to have all the midi data just to the right
# edge of the screen. Can also override this to any positive second value
# to start midi/playback at some part of the piece.
time_offset = time_min - (SW - PLAYHEAD_X) / PIXELS_PER_SECOND + START_TIME_OFFSET

screen = pg.display.set_mode((SW, SH))
pg.display.set_caption(Const.TITLE)
clock = pg.time.Clock()

current_frame = 0
audio_started = False

start_ms = pg.time.get_ticks()

# main animation loop
while True:
    # get all events currently in the queue and handle
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                pg.quit()
                raise SystemExit

    # calculate current time
    current_ms = pg.time.get_ticks()
    elapsed = (current_ms - start_ms) / 1000.0
    current_time = time_offset + elapsed

    # start audio once we're at the playhead
    if vis_config.play_audio == True:
        if not audio_started and current_time >= 0:
            pg.mixer.music.play(start = current_time)
            audio_started = True

    # draw background
    screen.fill(vis_config.bg_color)

    # draw time markers
    for i in range(int(time_min), int(time_max) + 1):
        x = PLAYHEAD_X + (i - current_time) * PIXELS_PER_SECOND
        if x >= 0 and x <= (SW + 25):
            pg.draw.line(screen, Color.DARKER_GRAY, (x, 0), (x, SH), 1)

    # draw midi bars
    still_has_notes = False
    for track in vis_config.tracks:
        for note in track.notes:
            # x and width calc
            x = PLAYHEAD_X + (note.start - current_time) * track.bar_pixels_per_second
            w = note.duration * track.bar_pixels_per_second
            x_right = x + w

            if x > SW:
                # note hasn't entered visible area yet - skip rendering
                still_has_notes = True
                continue

            # y and height calc
            t = (note.pitch - pitch_min) / (pitch_max - pitch_min)
            y_min = PAD
            y_max = SH - PAD
            y = (y_max + t * (y_min - y_max)) - track.bar_height / 2
            h = track.bar_height

            color = track.color
            if x <= PLAYHEAD_X:
                # turn white and start reducing alpha
                color = Color.WHITE
                note.alpha = 255 * (x_right / PLAYHEAD_X)
                note.alpha = max(0, min(255, note.alpha))  # clamp

            if x_right >= 0:
                # still visible - draw
                surf = pg.Surface((w, h), pg.SRCALPHA)
                surf.fill(Color.rgba(color, note.alpha))
                screen.blit(surf, (x, y))

                still_has_notes = True
            # else - note has fallen off screen, don't draw

    if not still_has_notes:
        # done
        pg.quit()
        raise SystemExit

    # draw playhead line that notes will cross when they "play"
    pg.draw.line(screen, Color.LIGHT_GRAY, (PLAYHEAD_X, 0), (PLAYHEAD_X, SH), 1)

    m, s = divmod(int(current_ms / 1000), 60)
    draw_text(screen, f'{m:02d}:{s:02d}', 20, 20, Color.LIGHT_GRAY, 18)

    # update display
    pg.display.flip()

    # sleep then iterate frame count
    clock.tick(Const.FPS)
    current_frame += 1