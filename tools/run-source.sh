#!/bin/sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
: "${ATARI_CONFIG:?Set ATARI_CONFIG to your private Atari800 config with lawfully obtained OS ROMs}"
[ -f "$ATARI_CONFIG" ] || { echo 'Atari800 configuration missing' >&2; exit 1; }
command -v atari800 >/dev/null || { echo 'Atari800 not installed; see README prerequisites' >&2; exit 1; }
exec atari800 -config "$ATARI_CONFIG" -atari -pal -run "$root/build/atari-original.xex"
