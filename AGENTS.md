# Agent instructions

This repository holds multiple independent ModRetro Chromatic games. Follow the folder conventions in `README.md`.

- Use the installed ModRetro skills for authoring, pixel art, ROM debugging, dependency setup, or device work as applicable.
- Begin with `session_status`. Select the intended game's absolute `.gbsproj` path before project operations. Read that game's README and any local `AGENTS.md`.
- For sibling games, the plugin workspace must cover the repository root. Preserve configured access boundaries.
- Create each game in a new root-level folder. Use `project_create_blank` for blank games or `project_create` for samples. Select the created project explicitly.
- Keep edits and outputs inside the target game's folder. Reuse the plugin's shared managed toolchain.
- Inspect focused resources before editing. Prefer semantic plugin tools with current revisions. Preserve native formats, resource IDs, unknown fields, plugins, palettes, and existing tracked ROMs.
- Build the target game with `rom_build`. Pass its returned absolute `outputPath` to inspection and emulator tools. Relative build paths resolve inside the selected game.
- For playable changes, open `web_preview` early in Codex's built-in browser. Update it after successful builds without interrupting human play, saves, or recordings.
- Test changed behavior on the exact built ROM with `emulator_run`, bounded `emulator_step` inputs, and `emulator_observe`. Retain recordings when useful. If browser access fails, report it and continue headless gameplay tests.
- Before switching projects, close task-owned emulator sessions and resolve active saves or recordings. Preserve other sessions.
- Report the game, ROM, inputs, frames, and observed results. Distinguish source inspection, compilation, emulator behavior, and physical hardware evidence.
