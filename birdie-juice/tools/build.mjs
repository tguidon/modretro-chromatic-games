import { existsSync, mkdirSync, copyFileSync } from "node:fs";
import { homedir, platform } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";

const root = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const dataRoot = platform() === "darwin"
  ? join(homedir(), "Library", "Application Support", "modretro-chromatic")
  : platform() === "win32"
    ? join(process.env.LOCALAPPDATA, "modretro-chromatic")
    : join(process.env.XDG_DATA_HOME || join(homedir(), ".local", "share"), "modretro-chromatic");
const setupRoot = process.env.GB_STUDIO_SETUP_ROOT || dataRoot;
const cli = process.env.GB_STUDIO_CLI || join(setupRoot, "toolchain", ".local", "vendor", "gb-studio", "out", "cli", "gb-studio-cli.js");
if (!existsSync(cli)) throw new Error("GB Studio CLI is missing. Set GB_STUDIO_CLI to your installed gb-studio-cli.js.");
const target = process.argv[2] || "all";
if (!["rom", "web", "all"].includes(target)) throw new Error("Usage: node tools/build.mjs [rom|web|all]");
const tmp = join(root, "build", "tmp");
mkdirSync(tmp, { recursive: true });
for (const kind of target === "all" ? ["rom", "web"] : [target]) {
  const destination = join(root, "build", kind === "rom" ? "birdie-juice.gbc" : "web");
  const result = spawnSync(process.execPath, [cli, `make:${kind}`, join(root, "project.gbsproj"), destination, "--verbose"], {
    cwd: root, env: { ...process.env, TMPDIR: tmp, TMP: tmp, TEMP: tmp }, stdio: "inherit",
  });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status || 1);
  if (kind === "rom") {
    for (const file of ["birdie-juice.noi", "birdie-juice.map", "birdie-juice.sym"]) {
      const source = join(tmp, "_gbsbuild", "build", "rom", file);
      if (existsSync(source)) copyFileSync(source, join(root, "build", file));
    }
  }
  console.log(`Built ${destination}`);
}
