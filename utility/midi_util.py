
from typing import List
import pretty_midi
from models import VisConfig, Track, Note

class MidiUtil:
    def __new__(cls):
        raise TypeError("MidiUtil is static")

    @staticmethod
    def print_midi_data(midi_data: pretty_midi.PrettyMIDI) -> None:
        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        print(f"Loaded MIDI with {len(instruments)} instrument track(s)\n")

        tempo_times, tempi = midi_data.get_tempo_changes()
        print("Tempo changes:")
        for time, tempo in zip(tempo_times, tempi):
            print(f"time={time:.3f}s tempo={tempo:.2f} BPM")
        print()

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
    def get_pitch_bounds(tracks: List[Track]) -> tuple[int, int]:
        min_pitch = min(
            note.pitch
            for track in tracks
            for note in track.notes
        )

        max_pitch = max(
            note.pitch
            for track in tracks
            for note in track.notes
        )

        return (min_pitch, max_pitch)
    
    @staticmethod
    def get_time_bounds(tracks: List[Track]) -> tuple[int, int]:
        start = min(
            note.start
            for track in tracks
            for note in track.notes
        )

        end = max(
            note.end
            for track in tracks
            for note in track.notes
        )

        return (start, end)
    
    @staticmethod
    def create_vis_config_from_prettymidi(midi_data: pretty_midi.PrettyMIDI) -> VisConfig:
        vis_config = VisConfig()

        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        for inst in instruments:
            notes: List[Note] = []

            for note in inst.notes:
                notes.append(Note(note.pitch, note.velocity, note.start, note.end))

            inst_name = inst.name or "(no name)"
            vis_config.tracks.append(Track(name=inst_name, notes=notes))

        return vis_config