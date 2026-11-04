# Micro MIG

Reusable Atari 8-bit-to-Amiga harness, previously called Mini Mig. The requested destination is OCS with 512 KB RAM. The provisional baseline is a PAL A500-class 68000 with 512 KiB Chip RAM and no Slow/Fast RAM. **This is a diagnostic baseline, not a game conversion or a published Codex environment.**

## Build and test

From the repository root:

```sh
make check
```

Only Python 3's standard library and make are needed. `tools/build.py` emits an original native ADF and an original Atari XEX using readable fixed-opcode emitters. The independent checks verify structure, checksums and 53 instructions of bounded released/pressed/released behavior. They are not hardware emulation. Optional third-party reference source is not executed by this path.

## Native and source-system runs

```sh
KICKSTART=/private/path/to/A500-Kickstart.rom ./tools/run-native.sh
ATARI_CONFIG=/private/path/to/atari800.cfg ./tools/run-source.sh
```

Install FS-UAE and Atari800 through permitted official package routes, configure a working display/audio environment and supply required private firmware/configuration. No proprietary ROM is bundled. `config/mini-mig.fs-uae` explicitly requests OCS, 512 KiB Chip and zero Slow/Fast memory; verify effective settings in emulator logs.

The native fixture shows colored Copper bands; holding the left mouse button changes a band and requests a Paula tone. The independent Atari fixture shows ANTIC checker lines; joystick fire requests a colored border and POKEY tone. These are separate diagnostics, not a matched game translation or fidelity claim. Reset/exit to stop the native takeover fixture.

## Environment preparation and status

`python3 environment/setup.py plan` prints the proposed Debian 13 amd64 package install plan without installing. The `install` action requires root, the fixed configured snapshot and permitted registry access. `python3 environment/startup.py` checks dependencies and reruns original fixture checks. No full resolved package lock exists until installation succeeds.

The existing development delivery reported passing structural and bounded original-fixture checks. FS-UAE, Atari800, audio/video behavior, two-task isolation and Codex environment publication were not verified. That development environment encountered package-registry access and setup-privilege blockers. See `PUBLICATION.md` for checks performed on this import. Repository publication does not resolve those runtime blockers.

## Licenses and source scope

Original build/test scripts, launchers, configuration and preparation scripts are imported from the existing Micro MIG delivery. No new blanket license is assigned. Optional Atari800 reference excerpts retain their GPL-2.0-or-later notices and COPYING; py65 retains BSD-3-Clause LICENSE.txt; the Altirra replacement-OS notice is preserved under its original path. `optional/manifest.json` records upstream commits, paths and hashes. Optional source is reference material only, not a bundled emulator. Generated disks, binaries, private firmware and workspace logs are excluded.
