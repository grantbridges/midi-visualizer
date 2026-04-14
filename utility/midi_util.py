
from typing import List
import pretty_midi

from models import Note, Track

class MidiUtil:
    @staticmethod
    def print_midi_data(midi_data: pretty_midi.PrettyMIDI) -> None:
        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        print(f"Loaded MIDI with {len(instruments)} instrument track(s)\n")

        for i, instrument in enumerate(instruments):
            instrument_name = instrument.name or "(no name)"
            notes: List[pretty_midi.Note] = instrument.notes

            program_name = pretty_midi.program_to_instrument_name(instrument.program)

            print(f"Instrument {i}")
            print(f"  Name:      {instrument_name}")
            print(f"  Program:   {instrument.program} ({program_name})")
            print(f"  Is drum:   {instrument.is_drum}")
            print(f"  Note count:{len(instrument.notes)}")    

            for j, note in enumerate(notes):
                pitch_name = pretty_midi.note_number_to_name(note.pitch)
                duration = note.end - note.start

                print(
                    f"    Note {j}: "
                    f"pitch={note.pitch} ({pitch_name}), "
                    f"velocity={note.velocity}, "
                    f"start={note.start:.3f}, "
                    f"end={note.end:.3f}, "
                    f"duration={duration:.3f}"
                )

            print()

    @staticmethod
    def get_pitch_bounds(midi_data: pretty_midi.PrettyMIDI) -> tuple[int, int]:
        min_pitch = min(
            note.pitch
            for instrument in midi_data.instruments
            for note in instrument.notes
        )

        max_pitch = max(
            note.pitch
            for instrument in midi_data.instruments
            for note in instrument.notes
        )

        return (min_pitch, max_pitch)
    
    @staticmethod
    def create_tracks_from_prettymidi(midi_data: pretty_midi.PrettyMIDI) -> List[Track]:
        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        tracks: List[Track] = []

        for inst in instruments:
            notes: List[Note] = []

            for note in inst.notes:
                notes.append(Note(note.pitch, note.velocity, note.start, note.end))

            inst_name = inst.name or "(no name)"
            tracks.append(Track(inst_name, notes))

        return tracks