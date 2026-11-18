# Dead Drop validation

## Current cartridge: combat animation update

- ROM: `build/dead-drop.gbc`, built with the shared native GB Studio 4.3.2 CLI.
- SHA-256: `bc7c5b1fc864da6cb1500479bbc16d864001dc7d80f847a5154e614bea71aa61`.
- 524,288 bytes; valid CGB-only MBC5 cartridge; no C compiler warnings.
- Exact-ROM PyBoy 2.7.0 recording: `captures/combat-animation`, frames 0–1,942.
- Actual gameplay excerpt: `artifacts/combat-animation.gif`, frames 1,144–1,392.

Bounded public `emulator_step` controller inputs verified:

| Frames | Input and observed result |
| --- | --- |
| 947–967 | B for 20 frames: upward muzzle flash, recoil, travelling streak, impact, guard hit, ammunition 12 → 11 |
| 991–1,009 | A near terminal: LINK appears, with no knife arc |
| 1,101–1,121 | A for 20 frames away from terminal: knife wind-up, broad sweep and follow-through on a miss |
| 1,122–1,392 | Right/down/left facing inputs, A for 12 frames and B for 16 frames with neutral releases: matching directional effects, cover impact, return to walking pose |
| 1,392–1,632 | Eight B presses with releases, then dry B for 24 frames: ammunition reaches zero, dry fire produces no false flash or tracer |
| 1,662–1,942 | A for 280 frames at supply terminal: live link then health/ammunition supply dialogue, no knife animation |

The official updated browser export was generated in `build/web-combat`.
Automatic approval review blocked opening its new localhost URL, citing the
built-in-browser-only restriction. Existing browser play was preserved; the
new export was not visually verified in a browser. Native ROM tests completed
and the temporary emulator session was closed with recordings retained.

No physical Chromatic test or repeat of the entire mission was performed for
this presentation update. The following sections retain earlier mission and
patrol evidence with their original ROM identities.

## Previous cartridge: patrol correction

- Native project: `project.gbsproj`, GB Studio 4.3.2 shared managed CLI.
- ROM: `build/dead-drop.gbc`.
- SHA-256: `ba01a50803f4c9fd35e8e83849340f9a78f6f33d0b04fa7a6812d82a52930464`.
- 524,288 bytes; CGB-only; MBC5; Nintendo logo and header checksum valid.
- Build completed with no C warnings. The CLI emits its known Node DEP0190
  dependency warning.

## Full mission run

Recorded in `captures/complete-route` using PyBoy 2.7.0 and the public ModRetro
`emulator_run`, `emulator_step`, `emulator_observe`, and read-only debug tools.
The model chose bounded ordinary controller inputs. There were no memory writes,
teleports, injected objective flags, save-state skips, or alternate starting scenes.

Exact walkthrough ROM SHA-256:
`032a2f45503cbcb29348aabc46420c9cc6c983679206f26362a2bf31609de4db`.
This differs from the previous patrol-correction cartridge only in the later guard-placement correction
and corresponding native build output. The full mission was not replayed after
that final placement correction; the affected patrol was checked separately.

Selected observed milestones (absolute native emulator frames):

| Frame | Observed result |
| ---: | --- |
| 947 | Title → briefing → boarding; player at the intended entrance |
| 1,314 | Held A for a live terminal link; first supply cache dialogue |
| 2,119 | North hatch reached Aft Winch Deck |
| 10,717 | Access-card dialogue; native access-card flag confirmed set |
| 16,107 | Generator interaction; native blackout flag confirmed set |
| 21,400 | Manifest and arming-code dialogue after a crouched terminal link |
| 26,804 | Returned through eight compartments to Pump Control |
| 27,118 | Coolant-charge dialogue and flag |
| 28,237 | Regulator-charge dialogue and flag |
| 34,655 | Cipher cracked after both engineering charges were armed |
| 35,970 | Final guidance charge placed |
| 37,586 | Uplink erased; all required objective flags confirmed |
| 40,468 | Lifeboat extraction dialogue, all five end conditions confirmed |
| 40,973 | “DEAD DROP COMPLETE. THANK YOU FOR PLAYING.” |
| 41,225 | Returned to the title screen |

Input patterns included D-pad holds up to 220 frames per movement segment,
neutral one-frame releases, B presses of 12–24 frames, A knife presses,
280-frame A holds for terminal links, Select taps for crouch, and 100-frame
A presses for dialogue pages. A known-route controller walker used only
read-only player coordinates to choose its next ordinary directional input.
It occasionally stopped on a wall or during a fade; subsequent observed frames
resolved these cases before continuing.

Observed behaviors include directional pistol hits and ammunition consumption,
close knife combat, cover collision, suspicion and alerts, damage, checkpoint
recovery with objective preservation, supply depletion, crouching, live terminal
links, native objective gates, the engineering return route, extraction and
return to title. Failed approaches were retained, including security-office,
generator, and archive attempts. Final human first-play pacing is unmeasured:
the guided run lasted roughly 11.5 emulated minutes, and skipped side rooms.

## Previous-build regression

`captures/final-regression` uses the patrol-correction SHA-256 above. Frames 0–2,146 cover
boot, briefing, an opening pistol hit, the boarding north-hatch transition,
Aft Winch Deck movement, and the corrected patrol.

One patrol in each of the nine rooms using the second formation previously
started inside the central machinery footprint. It was moved from tile (21,18)
to the clear lane at (21,20). On the final ROM its native position changed from
x=138.75 to x=168.375 at y=160 between frames 2,038 and 2,128, confirming movement
through the lane. A frame-2,146 OAM observation had six visible objects, peak four
objects on a scanline, and no scanlines over the ten-object hardware limit.
That is a sampled observation, not a whole-game performance guarantee.

## Source and visual checks

`python3 tools/check_world.py` passes:

- All 28 entrance → terminal → north-hatch standing routes are connected.
- All four side-door approaches are reachable.
- All 112 authored guard spawns are clear of solid cover and crouch-only vents.
- Every gameplay scene has the expected ten actor slots and 1,440 collision cells.

The native graphics analyzer reports no diagnostics for Lifeboat: 57 effective
background tiles, six used environmental palette slots, three object-palette
slots, and a 22-object authored OAM estimate including the player. These are
source estimates, distinct from the live OAM sample.

The official Binjgb export was opened in Codex's built-in browser. The title
screen was visually confirmed. Gameplay evidence above is from the exact native
PyBoy ROMs, not browser automation. Browser playback and native ROM builds have
separate build identities.

## Limits

- No physical Chromatic, cartridge flashing, or hardware audio test was performed.
- No human blind 15–30 minute playtest has been measured.
- Side-room transitions and all-intel debrief branches compile and have connected
  source routes, but were not included in the full runtime walkthrough.
- Checkpoints are session state. Cartridge SRAM persistence is not implemented.
- Audio is original hardware-register pulse/noise synthesis; emulator frame
  captures do not establish listening quality or real-device timing.

All task-owned PyBoy sessions were closed after retaining their recordings.
