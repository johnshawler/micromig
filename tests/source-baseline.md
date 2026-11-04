# Source and native baseline scenarios

Identity: build/SHA256SUMS. Cold reset and clean XEX load for Atari. Cold boot
from build/mini-mig.adf for Amiga. No random behavior or saved state is involved.
Use PAL, record version/profile/ROM hashes and a timestamp for each actual run.

| Case | Reproducible scenario | Expected | Actual execution |
| --- | --- | --- | --- |
| Atari boot | Reset 48 KiB Atari 800 PAL, load XEX, wait 2 s | 32 ANTIC F checker lines, black border, silent | Not run |
| Atari fire | Hold joystick 0 fire 2 s | Border changes; channel 1 pure tone | Register-stub path passed; emulator not run |
| Atari release | Release fire 2 s | Black border, silence | Register-stub path passed; emulator not run |
| Atari repeat | Repeat fire/release twice, stop at 10 s | Stable picture and repeatable audio/input | Not run |
| Amiga boot | Cold boot ADF, wait 2 s | Four Copper color bands, silence | Not run |
| Amiga input/audio | Hold left mouse 2 s, release 2 s | Upper band green→red→green; tone→silence | Not run |
| Amiga repeat/reset | Repeat twice, reset | Stable bands/audio and clean reboot | Not run |

For actual runs save cold-boot, held and released screenshots independently;
record audio including silence→tone→silence; preserve emulator configuration and
startup log, map input events to emulated frames, and measure framebuffer/audio
output independently from register traces. No capture exists yet.

The original local trace runner executes 53 fixture instructions across init and
released/pressed/released register-stub scenarios. It does not model ANTIC DMA,
GTIA pixels/collisions, POKEY sound/timers, interrupts, scanline timing, or OS.
Passing it establishes binary control-flow and register writes only.
