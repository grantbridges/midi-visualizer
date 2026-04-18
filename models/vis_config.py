from typing import List, Tuple
from dataclasses import dataclass, field
import pretty_midi
from common.colors import Color
from models.track import Track, Note

# ----

'''
Top level construct containing all visualizing info
'''
@dataclass
class VisConfig:
    # properties
    bg_color: Tuple[int, int, int] = Color.DARKEST_GRAY
    play_audio: bool = True

    tracks: List[Track] = field(default_factory=list)

    def get_track_by_name(self, name: str) -> Track:
        return next((track for track in self.tracks if track.name == name), None)

    # Loads in all note data from midi (assumes tracks are already defined)
    def populate_notes_from_midi_data(self, midi_data: pretty_midi.PrettyMIDI):
        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        for inst in instruments:
            # ensure loaded instrument has a name - we use it for track indexing
            if not inst.name:
                print("Warning: Loaded instrument from MIDI data with no name - skipping")
                continue

            # get corresponding track by instrument name
            track = self.get_track_by_name(inst.name)
            if track == None:
                print(f"Warning: Loaded instrument {inst.name} from MIDI data with no match in VisConfig tracks - skipping")
                continue

            track.notes = []
            for note in inst.notes:
                track.notes.append(Note(note.pitch, note.velocity, note.start, note.end))
