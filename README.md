# ModRetro Chromatic Games

A collection of games for my ModRetro Chromatic, built with the
[ModRetro Chromatic Plugin](plugin://modretro-chromatic@openai-curated-remote).
Each game lives in its own folder and remains editable in GB Studio.

[Birdie Juice](birdie-juice/README.md) is a nine-hole, par-36 golf game.
Its game README includes direct compiler commands and automated playtests.
`setup-check/` contains the starter used to test the shared toolchain.

## Repository layout

Use a short, lowercase, hyphenated folder name for each game at the repository root.
Keep each game's source, assets, extensions, and generated files inside that folder.
Keep the repository root for shared documentation and repository configuration.

```text
modretro-chromatic-games/
├── README.md
├── AGENTS.md
├── birdie-juice/         # Nine-hole golf game
├── setup-check/          # Starter used to test the toolchain
│   ├── project.gbsproj   # GB Studio project descriptor
│   ├── project/          # Native .gbsres resources
│   ├── assets/
│   ├── plugins/          # Game-specific extensions
│   └── build/            # Generated ROMs and browser exports
└── <next-game>/
```

Each game needs a README with its concept, controls, and build/playtest notes.
Game-specific agent instructions belong in that game's `AGENTS.md` when needed.
Keep generated `build/`, `artifacts/`, `captures/`, and `save-states/` files out of commits unless intentionally retained.

## Working on a game

1. Configure the plugin's `GB_STUDIO_WORKSPACE_ROOT` to this repository's absolute path before its server starts.
2. Use `session_status` to inspect the selected project and workspace boundary.
3. For a new game, use `project_create_blank` or `project_create` with `template: "starter"` for a sample.
4. Select the intended game's `.gbsproj` with `project_select` before edits or builds.
5. Build with `rom_build`, preview with `web_preview`, and test gameplay with the `emulator_*` tools.

A workspace set to the repository root allows the plugin to work with sibling game folders.
Selecting a project alone authorizes only that game's directory.
Finish active play, recordings, and saves before switching games, because selection closes the previous browser preview.

## Shared tools

The installed plugin, compiler, and emulator dependencies are shared across games and stay outside this repository.
Use `toolchain_doctor` to inspect them and `toolchain_prepare` to prepare missing `build` or `emulator` components.
The GB Studio desktop editor is optional for the plugin workflow.

Use [AGENTS.md](AGENTS.md) for the agent workflow and the installed plugin's skills for detailed authoring, art, debugging, and hardware guidance.
