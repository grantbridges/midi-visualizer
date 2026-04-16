from dataclasses import dataclass

# ----

'''
A Note corresponds to a single midi note value.
It contains relevant MIDI note data.
'''
@dataclass
class Note:
    pitch: int = 50
    velocity: int = 70 # 0-127
    start: float = 0 # note start in seconds
    end: float = 1 # note end in seconds

    # draw fields
    alpha: int = 255

    @property
    def duration(self):
        return self.end - self.start
