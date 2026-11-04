#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
: "${KICKSTART:?Set KICKSTART to a private lawfully obtained A500 Kickstart path}"
[ -f "$KICKSTART" ] || { echo 'Kickstart file missing' >&2; exit 1; }
command -v fs-uae >/dev/null || { echo 'FS-UAE not installed; see README prerequisites' >&2; exit 1; }
[ -f "$root/build/mini-mig.adf" ] || { echo 'Run make first' >&2; exit 1; }
mkdir -p "$root/evidence/fs-uae"
exec fs-uae "$root/config/mini-mig.fs-uae" \
  --base-dir="$root/evidence/fs-uae" --kickstart-file="$KICKSTART" \
  --floppy-drive-0="$root/build/mini-mig.adf" --joystick-port-0-mode=mouse
