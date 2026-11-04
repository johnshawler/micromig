# Environment preparation

The proposed requirements target Debian 13 amd64 with FS-UAE and Atari800. `setup.py plan` performs no network request; `setup.py install` requires root and the configured signed fixed-snapshot package sources. It does not rewrite source URLs or circumvent network controls. `startup.py` exits nonzero when readiness is incomplete and runs original fixture checks. A full dependency lock can be recorded only after installation succeeds.

`isolation_probe.py` is an original file/process isolation diagnostic. It is not proof of emulator isolation or a published Codex environment. Use separate per-task configuration, writable files and displays when validating source and target emulators. Keep proprietary firmware outside the repository.
