from dataclasses import dataclass
from common import Color, Const
from models import VisConfig
import pygame as pg
import os

'''
Window for showing preview midi visualization animation while editing.
Leverages pygame for animation rendering.
'''
@dataclass
class PreviewWindow:
    def start(self, vis_config: VisConfig, mp3_filepath: str, start_time_offset: int):
        (pitch_min, pitch_max) = vis_config.get_pitch_bounds()
        (time_min, time_max) = vis_config.get_time_bounds()

        # show on right monitor (Grant local debug setup)
        os.environ['SDL_VIDEO_WINDOW_POS'] = '2200,200'
        pg.init()
        pg.mixer.init()
        pg.mixer.music.load(mp3_filepath)

        # constants
        PIXELS_PER_SECOND = 200
        PAD = Const.SCREEN_PADDING
        PLAYHEAD_X = Const.SCREEN_WIDTH / 2 # line where notes cross when they play

        # Initial time offset, in seconds
        # Defaults to the time needed to have all the midi data just to the right
        # edge of the screen. Can also override this to any positive second value
        # to start midi/playback at some part of the piece.
        time_offset = time_min - (Const.SCREEN_WIDTH - PLAYHEAD_X) / PIXELS_PER_SECOND + start_time_offset

        screen = pg.display.set_mode((Const.SCREEN_WIDTH, Const.SCREEN_HEIGHT))
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
                        return

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
                if x >= 0 and x <= (Const.SCREEN_WIDTH + 25):
                    pg.draw.line(screen, Color.DARKER_GRAY, (x, 0), (x, Const.SCREEN_HEIGHT), 1)

            # draw midi bars
            still_has_notes = False
            for track in vis_config.tracks:
                for note in track.notes:
                    # x and width calc
                    x = PLAYHEAD_X + (note.start - current_time) * track.bar_pixels_per_second
                    w = note.duration * track.bar_pixels_per_second
                    x_right = x + w

                    if x > Const.SCREEN_WIDTH:
                        # note hasn't entered visible area yet - skip rendering
                        still_has_notes = True
                        continue

                    # y and height calc
                    t = (note.pitch - pitch_min) / (pitch_max - pitch_min)
                    y_min = PAD
                    y_max = Const.SCREEN_HEIGHT - PAD
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
                return

            # draw playhead line that notes will cross when they "play"
            pg.draw.line(screen, Color.LIGHT_GRAY, (PLAYHEAD_X, 0), (PLAYHEAD_X, Const.SCREEN_HEIGHT), 1)

            m, s = divmod(int(current_ms / 1000), 60)
            self._draw_text(screen, f'{m:02d}:{s:02d}', 20, 20, Color.LIGHT_GRAY, 18)

            # update display
            pg.display.flip()

            # sleep then iterate frame count
            clock.tick(Const.FPS)
            current_frame += 1
    
    # text helper
    def _draw_text(self, screen: pg.Surface, text, x, y, color, font_size):
        font = pg.font.Font(Const.PRIMARY_FONT, font_size)
        text_object = font.render(text, True, color)
        text_rect = text_object.get_rect()
        text_rect.left = x
        text_rect.top = y
        screen.blit(text_object, text_rect)