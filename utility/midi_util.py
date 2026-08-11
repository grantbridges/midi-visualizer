from typing import List
import pretty_midi

import logging
logger = logging.getLogger("MidiUtil")

class MidiUtil:
    def __new__(cls):
        raise TypeError("MidiUtil is static")

    @staticmethod
    def log_midi_data(midi_data: pretty_midi.PrettyMIDI) -> None:
        instruments: List[pretty_midi.Instrument] = midi_data.instruments

        log_str = f"Loaded MIDI with {len(instruments)} instrument track(s)\n"

        tempo_times, tempi = midi_data.get_tempo_changes()
        log_str += "Tempo changes:"
        for time, tempo in zip(tempo_times, tempi):
            log_str += f"time={time:.3f}s tempo={tempo:.2f} BPM"
        log_str += ""

        for i, instrument in enumerate(instruments):
            instrument_name = instrument.name or "(no name)"
            notes: List[pretty_midi.Note] = instrument.notes

            program_name = pretty_midi.program_to_instrument_name(instrument.program)

            log_str += f"Instrument {i}\n"
            log_str += f"  Name:      {instrument_name}\n"
            log_str += f"  Program:   {instrument.program} ({program_name})\n"
            log_str += f"  Is drum:   {instrument.is_drum}\n"
            log_str += f"  Note count:{len(instrument.notes)}\n"

            if not instrument.control_changes:
                log_str += f"  No CC data\n"
            else:
                log_str += f"  CC events: {len(instrument.control_changes)}\n"

                for cc in instrument.control_changes[:10]:
                    log_str += f"    CC{cc.number} value={cc.value} time={cc.time:.3f}s"

            for j, note in enumerate(notes):
                pitch_name = pretty_midi.note_number_to_name(note.pitch)
                duration = note.end - note.start

                log_str += (
                    f"    Note {j}: "
                    f"pitch={note.pitch} ({pitch_name}), "
                    f"velocity={note.velocity} "
                    f"start={note.start:.3f} "
                    f"end={note.end:.3f} "
                    f"duration={duration:.3f}\n"
                )

            log_str += ""

        logger.debug("%s", log_str)

    @staticmethod
    def midi_pitch_to_note(pitch: int) -> str:
        if not 0 <= pitch <= 127:
            logger.warning(f"Pitch to Note | Invalid MIDI pitch \"{pitch}\"")
            return ""
        
        NOTE_NAMES = [
            "C", "C#", "D", "D#", "E", "F",
            "F#", "G", "G#", "A", "A#", "B"
        ]

        note = NOTE_NAMES[pitch % 12]
        octave = (pitch // 12) - 1

        return f"{note}{octave}"