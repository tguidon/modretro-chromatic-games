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
The user subsequently confirmed this corrected image worked on the Chromatic.

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
Each corrected later variant also passed the same 264-frame emulator sequence,
flashed successfully, and received physical confirmation from the user.
These variants do not execute banked golf code or exercise external RAM.
They isolate installation properties, not runtime bank/RAM functionality.

Physical installation results, rather than emulator success, are needed to
determine which change affects the writer. Stop the comparison sequence at the
first failed install and retain its original operation status. Do not equate
one failure with proof of a particular cause; intermittent writes remain possible.

## First 8 KiB isolation

All four corrected comparisons passed on the physical Chromatic. Checkpoint 4
contains Birdie's exact last 120 KiB, so all remaining file differences are in
offsets 0x0000–0x1FFF. This narrows the file comparison; it does not establish that
those bytes caused the earlier verification failures. Intermittent writes remain
possible. Do not change the production game on that inference alone.

Run `python3 diagnostics/button-test/isolate_prefix.py` from the game folder.
This pins both inputs by SHA-256 and prepares the next cumulative comparisons:

5. `05-birdie-header.gb` copies Birdie's title/header fields into checkpoint 4.
   Only 13 bytes change: 11 title bytes, the header checksum, and one global
   checksum byte. The complete header at 0x100–0x14D matches Birdie; the valid
   global checksum at 0x14E–0x14F depends on the remaining diagnostic content.
6. `06-birdie-prefix-padding.gb` additionally copies Birdie's bytes into the
   diagnostic's unused 0x10AB–0x1FFF padding. All test code is preserved. Only
   3,750 differing byte positions then remain, entirely below 0x10AB.

The generator asserts the allowed changed ranges and preserves the input ROMs.
Inspect and emulator-test each exact generated ROM before installation; keep
physical checkpoints between writes. The output manifest describes prepared
images, not completed tests. Retain subsequent observations and operation results
under `artifacts/button-comparison/`.

The Birdie linker symbols place the earlier failing offset 0x232 inside
`_script_cmds` (starting at 0x206), its script command table. That locates a failed
readback byte; it does not indicate a runtime script error. Both original
verification failures occurred during installation, before verified gameplay.

## Installation outcome (November 18, 2026)

Checkpoints 5 and 6 both flashed successfully and the user confirmed all eight
buttons worked on the physical Chromatic. Following those controls, checkpoint 7
flashed the exact previously failing native Birdie ROM successfully:

- ROM SHA-256: `90f92dad08b36b092b1dbb9818dfe56412bdbe0b9558f14c438fa5b09c7bfefd`
- Size: 131,072 bytes; no ROM modifications between its failed and successful attempts.
- Successful operation: `28eb9167c548bdb72bbca331af48e875e09ab988dabd0aa28b659bcfee983c97`
- Vendor CLI 1.2.1 reported success and closed with exit code 0.

The earlier installation failure did not reproduce. This does not identify its
cause or prove that the comparison sequence repaired anything. No production
ROM patch is justified by these install results. The user then confirmed Birdie
booted and they played the first hole on the physical Chromatic. Its exact-image
emulator regression passed all 17 checks across 15,901 frames, including a full
nine-hole round; that complete round has not been verified on physical hardware.
Detailed operation and user-report evidence is retained in
`artifacts/button-comparison/` and `artifacts/rom-audit/`.

Comparing the original failed native write with the successful write through the
public operation records found identical vendor command arguments (including
ROM path and expected hash), executable path, CLI version 1.2.1, target
darwin-arm64, plugin session, and USB bus/port/player enumeration. The failed
write read 0xFF instead of 0x00 at offset 0x232; the successful write verified.
Between those attempts, diagnostic writes and user power-cycles changed the
cartridge contents and device history. That supports investigating a
state-dependent or intermittent write/readback condition, but does not identify
its cause or establish that the diagnostic sequence repaired anything. Preserve
the working installation. The detailed comparison is retained as
`artifacts/button-comparison/failed-versus-successful-write.json`.
