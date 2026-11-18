# Birdie Juice

- Build directly with `node tools/build.mjs all`. Use ModRetro for device operations when requested.
- Run `tools/playtest.py` with Python that has PyBoy and Pillow. Build the ROM first so its symbols match.
- Keep nine holes totaling par 36: two par 3s, five par 4s, and two par 5s.
- Keep golf rules in the project-local `birdie-golf` extension. Preserve ordinary native scene-transition events on the aim actors.
- Treat `course/holes.json` as the layout source. The generator replaces native course resources and assets. Preserve editor changes before regeneration.
- Keep builds and test evidence in the ignored `build/` and `artifacts/` folders.
