# Button Test

A standalone diagnostic ROM, separate from the Birdie Juice game executable.
Plain GBDK C renders one text screen and polls the eight standard Game Boy inputs:
Up, Down, Left, Right, A, B, Start, and Select.

HELD shows YES while a button is held. SEEN retains OK after it is pressed.
The counter reaches 8/8 and displays ALL BUTTONS OK! once every input has been
seen. Reboot to clear the results. The Chromatic system Menu button is not a
Game Boy cartridge input and is not included.

No graphics assets, game engine, sound, external RAM, saves, or ROM bank switching.
The ROM is monochrome-compatible and runs on Game Boy Color/Chromatic.
This diagnostic stays inside the plugin's currently authorized Birdie Juice
workspace; it does not modify the golf project or replace its ROM.

Build using ModRetro `rom_build` with `sourcePath` set to this folder's absolute
`main.c`, `colorMode: "dmg"`, and `outputPath: "build/button-test.gb"`.
Use the exact returned ROM path for inspection, emulator checks, and flashing.
Standalone C builds are tested through the plugin's emulator; its GB Studio
`web_preview` workflow does not export standalone C programs.

## Install comparisons

The original 32 KiB diagnostic successfully flashed and the user confirmed it
worked on the physical Chromatic on November 18, 2026.

The first color-flag-only comparison flashed successfully, but the user reported
a white screen. The original test did not initialize CGB palettes. PyBoy showed
red text from its startup palette, masking this dependency; a readable emulator
screen alone did not establish correct hardware initialization.

The current source explicitly calls `set_default_palette()` on CGB hardware.
Build it with `colorMode: "gbc-only"` to
`build/button-comparison/01b-color-initialized.gb`. This corrected checkpoint
passed all eight inputs over 264 emulator frames with black text on white.
Physical confirmation is required before advancing to the later checkpoints.

Run `python3 diagnostics/button-test/make_comparisons.py` from the game folder
to produce four corrected images in `build/button-comparison/`. The generator
requires the exact corrected baseline hash and preserves the old comparison
files and `manifest.json`; new files use the `b` suffix and
`manifest-initialized.json`.
The emitted manifest identifies each exact file and its changes:

1. Establish a color-only baseline with explicit palette initialization.
2. Add Birdie's MBC5+rumble+RAM+battery type and 32 KiB RAM declaration.
3. Expand to 128 KiB using 0xFF padding and update the declared ROM size.
4. Replace unused padding at 0x2000 onward with Birdie's bytes, increasing
   programming workload while preserving the complete button-test program.

Header and global checksums are recomputed. The original four were inspected and tested
in CGB-mode PyBoy for 264 frames each: boot 120, then each of eight buttons held
12 frames followed by 6 neutral frames. Each reached ALL BUTTONS OK!.
The corrected later variants require fresh emulator checks before installation.
These variants do not execute banked golf code or exercise external RAM.
They isolate installation properties, not runtime bank/RAM functionality.

Physical installation results, rather than emulator success, are needed to
determine which change affects the writer. Stop the comparison sequence at the
first failed install and retain its original operation status. Do not equate
one failure with proof of a particular cause; intermittent writes remain possible.
