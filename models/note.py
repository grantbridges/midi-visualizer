from dataclasses import dataclass

# ----

'''
A Note corresponds to a single midi note value.
It contains relevant MIDI note data.
'''
@dataclass
class Note:
    pitch: int
    velocity: int # 0-127
    start: float # note start in seconds
    end: float # note end in seconds

    @property
    def duration(self):
        return self.end - self.start
