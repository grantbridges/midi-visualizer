See [v1.0.0-beta](https://github.com/grantbridges/midi-visualizer/releases/tag/v1.0.0-beta) release for installer instructions and quick-start guide.

### Updates

- Added Track Presets to support reuse of pitch min/max overrides across projects. Manage track presets and apply them from buttons on top-right of Tracks table.
- Added Track Group presets to support reuse of track group configurations across different projects. Manage track group presets and apply them from buttons on top-right of Track Groups table.
- Improved move up/down interaction on Tracks and Track Group tables - now supports bulk moving as well
- Added "minimum supported OS" message on startup if using an older incompatible Mac OS
- Added ability to delete tracks
- Update from MIDI workflow no longer removes tracks missing from new import - only handles adds and udpates
- Various UI tweaks and cleanup

#### Bug Fixes

- Fixed issue where mouse scrollwheel would change track group dropdowns on Tracks table
- Removed useless "Round Edges" checkbox on Note Effects tab - "Edge Rounding" slider now does everything
- Now show an error on project load if unable to load supporting
