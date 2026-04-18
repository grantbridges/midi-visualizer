
from typing import List
import pretty_midi

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