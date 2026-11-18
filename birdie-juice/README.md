# Birdie Juice

A top-down golf game for Game Boy Color and ModRetro Chromatic.
Play the Sunrise Nine, a full round with two par 3s, five par 4s, and two par 5s.
The course totals par 36.

Choose a driver, 5 wood, 7 iron, wedge, or putter.
Adjust the aim and power, then send the ball toward the flag.
The crosshair shows the intended landing point.

## Controls

| Control | Action |
| --- | --- |
| Left / Right | Rotate the aim |
| Up / Down | Increase / decrease power |
| A | Hit the ball, start a round, or advance after a hole |
| B | Select the next club or close a menu |
| Select | Select the previous club |
| Start | Open the scorecard, or open help from the title |

In the browser export, use the arrow keys, Z for A, X for B, Enter for Start, and Shift for Select.
The game aims toward the cup after each shot. You can change that aim before the next shot.
Power ranges from 5% to 100%.

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

Rough reduces carry for the driver, wood, and iron. Bunkers halve their carry.
The wedge keeps its carry in sand and rough. The putter rolls along the ground and can enter the cup along its path.
Water and out-of-bounds landings add one penalty stroke and return the ball to its previous position.
Trees return a blocked landing to the previous position without an extra penalty stroke.
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

The test plays all nine holes through controller inputs and reads matching build symbols for assertions.
It also exercises menus, club selection, water penalties, bunker carry, pickup, and a new round.
Screenshots, input journals, and `report.json` go into `artifacts/playtests/`.

## Source files

`project/` contains the native scenes, actors, settings, and palettes.
`assets/` contains the editable backgrounds, sprites, font, and dialogue frame.
`plugins/birdie-golf/` adds a game-specific scene type for golf physics and scoring, using GB Studio's supported extension format.

`course/holes.json` defines the layouts, terrain, tees, cups, and pars.
`tools/generate_course.py` regenerates course assets, native scene resources, and course lookup data from that file.
It requires Pillow and replaces those generated files, so preserve editor changes before running it.
Edit gameplay in `plugins/birdie-golf/engine/src/states/golf.c` and menus in `engine/src/core/birdie_ui.c` within that extension.

The course artwork, sprites, golf rules, and HUD font were created for Birdie Juice.
The baseline dialogue font and frame come from the ModRetro original starter.
The included `LICENSE` preserves the native project's upstream notice.
