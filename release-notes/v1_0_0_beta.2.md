#### Updates

- Can now group multiple selected track rows with Groups dropdown in tracks table
- Can now override min and max pitch for tracks (helping out my keyswitch homies)
- Added "Solo" checkbox on tracks for soloing individual tracks (along with existing solo-by-group option)
- New toggle for "enhance colors" on note styling to control coloring with gradient or solid color
- Added MIDI note corner rounding controls
- Misc. UI improvements:
  - Added "linked sliders" for a few inputs (e.g. Pitch Min/Max) for mutually limited values (where min can't be higher than max)
  - Updated highlight coloring throughout app to better match Illustri title coloring
  - Updated icons in a couple of spots

#### Bug Fixes

- Fixed issue on Mac where Illustri app icon would enlarge in toolbar while running app

# Illustri MIDI Studio

Bring your compositions to the next level with **Illustri MIDI Studio**, a free MIDI video stylization app available now on both Windows and Mac.

**Open Beta Release** - _bugs and incomplete features may be present. Please report issues encountered so they can be addressed._

<img width="640" height="360" alt="Puppet Master Trim" src="https://github.com/user-attachments/assets/271f2ef1-59c9-4034-b499-703dca03bf5a" />

### Installing Illustri

Download the correct installer for your operating system below:

- MAC (Silicon): `illustri-macos-arm64.dmg`
- MAC (Intel): `illustri-macos-x86_64.dmg`
- Windows: `IllustriMIDIStudio-Setup.exe`

⚠️ **Note**: Installers are not yet signed during the open beta testing period, so you will receive "Unknown Publisher" security warnings when running for the first time. Source code is openly available on this beta release for the sake of transparency, but will not be available in future production releases (once signed). To get past the security flagging:

- Mac: Try to run the application once, ignore the warning, then open Apple menu > System Settings > Privacy & Security. Scroll down to the security section and click Open Anyway.
- Windows: Click "More Info", then "Run Anyway".

### Getting Started

Export a .midi/.mid file from your DAW of choice - sample MIDI export guides:

- [Logic Pro](https://support.apple.com/guide/logicpro/export-midi-regions-lgcp77376cad/mac)
- [Cubase](https://www.steinberg.help/r/cubase-pro/15.0/en/cubase_nuendo/topics/vst_instruments/vst_instruments_exporting_instrument_tracks_as_midi_files_c.html)
- [FL Studio](https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/fformats_save_export.htm)

Create a new Illustri project by dropping the midi file onto the app window (or clicking "New Project" in the file menu to browse for the file).

### Using Illustri to Stylize your Track

**General Tab**
Set high-level settings of the project, such as orientation, overall scaling/positioning, and time offsets.

**Tracks**
See all tracks from imported .midi file. Add one or multiple at a time to track groups for further styling and ordering.

**Track Groups**
Set order (groups at top are drawn on top), color, styling, visibility, offsets, and more for each track group.

**Note Effects**
Set effects for note playback, such as sparks, fade in/out, and highlight/glow. These effects apply to all notes, but some effects can be turned on or off on a group basis on the Track Groups tab.

**Background**
Set background mode for track - color, image, or video. For video, a downscaled version is loaded in for preview, but full resolution will be rendered on export.

**Audio**
Optionally add an audio file to sync with midi playback and a visual waveform.

### Export

Click "Export..." in the file menu to begin export process - select output format from `mp4`, `mov`, or `webm`, and set the desired resolution and FPS. **Note:** The rendering process is very CPU intensive due to requiring image generation and processing for every frame of the exported video. Try lowering resolution or output FPS to an acceptable level if export performance is an issue.
