# Birdie Juice

A golf game for Game Boy Color and ModRetro Chromatic, with an overhead course
view and a separate illustrated swing camera.
Play the Sunrise Nine, a full round with two par 3s, five par 4s, and two par 5s.
The course totals par 36.

Choose a driver, 5 wood, 7 iron, wedge, or putter.
Plan your aim and target power on the map, then time a three-press swing:
press A to start the meter, A to set power, and A again as the returning cursor
crosses the green diamond. Early and late contact changes direction and distance.
The crosshair estimates calm-air carry; wind, bounce, and rollout change the result.

## Controls

| Control | Action |
| --- | --- |
| Left / Right | Rotate the aim |
| Up / Down | Set the target power shown by the marker |
| A | Start meter → set power → time contact; also start/advance a round |
| B | Select the next club or close a menu |
| Select | Select the previous club |
| Start | Open the scorecard, or open help from the title |

During the rising power meter, B cancels without taking a stroke. Once power is
locked, missing the returning accuracy window produces a mishit.

In the plugin browser player, use the arrow keys, Z for A, X for B, Enter for Start,
and P for Select (the standalone GB Studio export also supports Shift).
The game aims toward the cup after each shot. You can change that aim before the next shot.
Target power ranges from 5% to 100%; the timed meter sets the actual shot power.
The HUD shows approximate yards remaining and nominal carry at the selected power.

## Course and rules

| Hole | Name | Par |
| --- | --- | --- |
| 1 | Morning Dew | 4 |
| 2 | Short Squeeze | 3 |
| 3 | Dogleg Punch | 5 |
| 4 | Sand Wedge | 4 |
| 5 | Creekside | 4 |
| 6 | Island Lime | 3 |
| 7 | Long Pour | 5 |
| 8 | Orchard Run | 4 |
| 9 | Last Call | 4 |
| Total | Sunrise Nine | 36 |

Morning Dew now has a creek crossing and a smaller green guarded by bunkers.
The Dogleg Punch grove blocks a low driver shortcut; Island Lime rewards a lay-up
below the creek before the approach. Long Pour has a longer tee-to-pin distance.

Air shots use velocity, gravity, club-specific loft, and wind. A ground shadow
separates the airborne ball from its position on the course. Fairway and green
landings bounce; rough and sand absorb the impact. Rolling friction depends on
the surface. Rough reduces driver, wood, and iron carry by a quarter; bunkers halve
it. The wedge keeps its carry from those lies.

Green chevrons point downhill. Putts curve with that slope, and downhill putts
travel farther. Aim uphill and choose power carefully: a fast ball can run across
the cup. Water landings and out-of-bounds shots add one penalty stroke and return
the ball to its previous safe lie. Low shots deflect off trees without an extra
penalty. A ball trapped inside a tree footprint returns to the previous lie.
The game records a maximum of 12 strokes per hole, then picks up the ball.

The scorecard records all nine holes and the total score relative to par.
After the last hole, press A on the scorecard to start a new round.
Round progress stays in memory until you restart the ROM or start another round.

## Build and playtest

Open `project.gbsproj` in GB Studio 4.3.2 to edit the native project.
This game builds directly with the installed GB Studio CLI. It does not require the ModRetro MCP tools.
From this folder, run:

```sh
node tools/build.mjs all
```

Use `rom` or `web` instead of `all` to build one target.
Outputs are `build/birdie-juice.gbc` and `build/web/`.
The build script uses the shared managed compiler by default.
Set `GB_STUDIO_CLI` to your `gb-studio-cli.js` path to use another installation.

To play in a browser, serve the official export over HTTP:

```sh
python3 -m http.server 8765 --bind 127.0.0.1 --directory build/web
```

Open `http://127.0.0.1:8765/` in the browser.
For automated tests, use Python with PyBoy 2.7.0 and Pillow installed:

```sh
python3 tools/playtest.py
```

The test plays all nine holes through controller inputs and reads matching build
symbols for assertions, without memory writes or teleports. It also exercises
timed and missed swings, cancellation, gravity, bounce, curved putts, water and
OB penalties, bunker carry, tree deflection, pickup, and a new round.
Screenshots, exact input journals, and `report.json` go into
`artifacts/playtests/regression/`. Plugin builds should request debug artifacts;
direct builds produce the `.sym` file used as a fallback.

To test another exact export, supply its matching build symbols and a separate
evidence directory, for example after `node tools/build.mjs all`:

```sh
python3 tools/playtest.py --rom build/web/rom/birdie-juice.gbc --symbols build/birdie-juice.sym --output artifacts/playtests/web
```

Power-limit checks also cover D-pad adjustments after a timed swing, ensuring
the target stays between 5% and 100% and the meter can be cancelled at either limit.

## Source files

`project/` contains the native scenes, actors, settings, and palettes.
`assets/` contains the editable backgrounds, sprites, font, and dialogue frame.
`plugins/birdie-golf/` adds a game-specific scene type for golf physics and scoring, using GB Studio's supported extension format.

`course/holes.json` defines the layouts, terrain, tees, cups, pars, wind, and green slopes.
Its `contours` define curved fairway centerlines (`x`, `y`, radius) and closed
green, bunker, and water outlines in screen pixels. `tools/course_shapes.py`
rasterizes these into a shared two-pixel surface map for artwork and ball physics.
The legacy tile rows retain tree footprints and provide a coarse layout reference.
Generated `course/art/hole_*_terrain.png` masks store surface codes 0–5, and the
banked `birdie_terrain_*.c` files pack two surface cells per byte for the ROM.
`tools/generate_course.py` regenerates course assets, native scene resources, and course lookup data from that file.
It requires Pillow and replaces those generated files, so preserve editor changes before running it.
`tools/course_art.py` draws the original course tiles and palettes.
`tools/generate_shot_art.py` produces the mountain panorama and four swing poses;
run it after changing shot artwork. Its editable source previews live in `course/art/`.

Edit the game state machine in `plugins/birdie-golf/engine/src/states/golf.c`,
physics in `engine/src/core/birdie_physics.c`, and menus in
`engine/src/core/birdie_ui.c` within that extension.

The shot camera reserves 109 panorama tiles, three meter tiles, and 16 animated
pose tiles in CGB VRAM bank 1 at `0x9000`. Course art stays below 128 tiles in bank 0,
leaving the separate 64-tile HUD font intact. Sprite objects occupy their ordinary
engine allocation. The panorama is illustrated scenery; the map shows the actual
hole geometry and ball trajectory.

The course artwork, sprites, golf rules, and HUD font were created for Birdie Juice.
The baseline dialogue font and frame come from the ModRetro original starter.
The included `LICENSE` preserves the native project's upstream notice.
