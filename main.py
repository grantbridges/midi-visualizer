from typing import List
import pygame
# import PIL
import sys
import pretty_midi
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

pygame.init()

# Window setup
WIDTH, HEIGHT = 800, 600
PADDING = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Test Window")

running = True

while running:
    # Handle events (close window)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw
    screen.fill(Color.WHITE)

    BAR_WIDTH_STRETCH_MULT = 100
    BAR_HEIGHT = 10
    for track in tracks:
        for n in track.notes:
            x = PADDING + n.start * BAR_WIDTH_STRETCH_MULT
            width = n.duration * BAR_WIDTH_STRETCH_MULT
            y = MidiUtil.pitch_to_y(n.pitch, pitch_min, pitch_max, HEIGHT, PADDING) - BAR_HEIGHT
            height = BAR_HEIGHT

            pygame.draw.rect(screen, track.color, (x, y, width, height))

            pygame.draw.line(screen, Color.BLACK, (WIDTH / 2, 0), (WIDTH / 2, HEIGHT), 1)

    # Update display
    pygame.display.flip()

pygame.quit()
sys.exit()