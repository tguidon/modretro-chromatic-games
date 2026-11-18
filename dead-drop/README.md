# Dead Drop

An original Game Boy Color stealth operation for ModRetro Chromatic. Infiltrate
MV Meridian, steal its weapons manifest, sabotage the guidance shipment, and
escape without sinking the tanker. Inspired by the patient observation,
infiltration, limited ammunition, and close approaches of classic spy games;
all characters, story, maps, and new artwork are original.

## Play

Open `project.gbsproj` through the ModRetro plugin or GB Studio 4.3.2.
The cartridge is `build/dead-drop.gbc`; the latest official browser export is
`build/web-combat` (the earlier `build/web` export is retained).
This is a color-only cartridge, not an original monochrome Game Boy game.

| Control | Action |
| --- | --- |
| D-pad | Move and face |
| A | Knife at close range |
| Hold A near a mint terminal | Establish a three-second link, then interact |
| B | Fire the silenced pistol in the facing direction |
| Select | Toggle crouching; crawl through grated passages |
| Start | Pause and show the current mission objective |

Browser keys: arrows, Z = A, X = B, P = Select, Enter = Start. Press A to
advance radio messages. If a guard is within knife range, A attacks first;
release A and hold again to start a terminal link.

The pistol fires one round per press, up to 112 pixels, and cover stops shots.
A shot is audible only to nearby guards. Knives are silent, but attacking an
alert guard can cost health. Ammunition is limited; avoid patrols when possible.

Pistol attacks show a directional recoil pose, bright muzzle flash, travelling
shot streak, and impact spark at a guard or cover. Knife attacks have distinct
wind-up, sweeping-blade, and follow-through poses with a large visible arc.
Both animations play on misses; terminal links do not trigger knife swings.

Dotted markers show guard facing, not the complete detection cone. Dark bays
and crouching reduce detection. Solid cover blocks sight. SEEN is suspicion;
ALERT is pursuit. Break line of sight and stay hidden to lose a patrol.
Enemies continue moving during terminal links. Dialogue and pause stop combat.

Every sector entrance is an in-session checkpoint. Defeat restores five health
and at least six rounds at that entrance; collected objectives and eliminated
guards persist. Supply caches are single-use. Checkpoints are RAM-only: resetting
or closing the cartridge starts a new mission. Browser save states can preserve
an exact running build; they are not compatible across changed ROMs.

## One mission, three acts

There are **28 playable compartments plus the title scene**, 40 × 36 tiles each.
The main route has 24 compartments, plus four side areas. The required return
journey brings the main mission to roughly 40 compartment visits.

1. **Infiltrate:** boarding platform → aft winch deck → container spine → customs
   → crew passage → mess → security. Copy the access card.
2. **Identify:** service trunk → ballast → pump → engine → generator. Black out
   the cargo lights. Continue through lower hold, tank catwalk, archive, radio,
   officers' quarters, and bridge. Copy the manifest and arming codes.
3. **Sabotage and escape:** return south to pump control and plant the coolant
   charge, then north one room to arm the engine regulator. The manifest causes
   new security teams to enter engineering. Return north through the bridge,
   unlock the cipher vault, plant the third charge in missile cargo, erase the
   launch uplink, and escape through foredeck, crane gantry, and lifeboat.

Side hatches: crew passage → ventilation; mess → infirmary; security → armory;
officers' quarters → chart room. Ventilation links to ballast after acquiring
the access card. Optional intel is in the archive, radio room, and chart room.
Collecting all three changes the debrief.

**Pacing target:** 15–30 minutes for a first, exploratory stealth run. This is a
design target, not a measured human playtest result. A guided emulator run using
known routes reached the ending in about 11.5 minutes of emulated time, including
briefings, failed approaches, and checkpoint recovery. Skipping optional
rooms and knowing the routes can shorten the mission substantially.

## Native implementation

- Editable distributed `.gbsproj` / `.gbsres` scenes, actors, triggers, dialogue,
  palette resources, collision maps, and objective variables.
- A project-local `STEALTH` scene mode in `plugins/dead-drop/engine` provides
  smooth movement, ray-tested vision, suspicion, patrols, pursuit, combat,
  crouch passages, sound, HUD, live terminal links, and session checkpoints.
- A small visual-script event calls explicit runtime commands. No engine eject,
  global toolchain changes, or standalone substitute cartridge is used.
- Original hand-authored tile and sprite recipes in `tools/author_art.py`.
  Seven environmental palettes plus the engine's reserved UI palette, distinct
  operative/guard/sight palettes, animated directional sprites, and compartment
  set pieces. The original minimal starter font and UI remain included.
- `tools/author_combat.py`, also called by the art recipe, preserves the original
  walking frames and adds directional combat poses and effects. Editable frames
  and timing notes are in `design/combat`; `combat_fx.c` animates the existing
  shared effect actor without changing combat damage or ammunition rules.
- `tools/author_world.py` reconstructs this game's deterministic authored world.
  It is an authoring recipe, not a migration for user-edited scenes. Preserve
  subsequent manual scene edits before deliberately regenerating.
- `tools/check_world.py` checks standing-route connectivity, side-door access,
  collision dimensions, and actor counts. It does not emulate the cartridge.

## Build and verify

Use the shared managed ModRetro toolchain. Do not install a second compiler.

1. `session_status`, then `project_select` with this absolute `project.gbsproj`.
2. `rom_build` with `outputPath: "build/dead-drop.gbc"` and optional
   `captureDebugArtifacts: true`.
3. Pass the returned absolute `outputPath` to `rom_inspect` and `emulator_run`.
4. Use `web_preview` for the official Binjgb player, exclusively in Codex's
   built-in browser. Preserve active human play before refreshing.
5. Test with bounded `emulator_step` inputs and inert `emulator_observe`.

Run source checks with `python3 tools/check_world.py`. Art regeneration requires
Pillow, available in the shared toolchain's existing emulator Python environment.
The imported sprite/background `.gbsres` files are committed native resources;
asset imports do not need to be repeated.

See `PLAYTEST.md` for exact build identity, input/frame evidence and limitations.
Generated ROMs, exports, recordings, and debug artifacts remain inside this game
folder and are ignored by Git. Source changes are on the `spy-game` branch.
