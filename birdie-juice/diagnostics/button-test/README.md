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
