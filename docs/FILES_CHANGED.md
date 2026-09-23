# Files Changed

## Added

- `classes/StargateMilkyWay/dynamic_wormhole_runtime.py`

## Patched in-place

- `classes/StargateMilkyWay/wormhole_manager.py` — targeted hooks and configurable timer correction
- `classes/StargateMilkyWay/wormhole_pattern_manager.py` — one marked runtime integration hook
- `classes/web_server.py`
- `web/debug.htm`
- `config/milkyway-config.json`
- `config/defaults-milkyway/config.json.dist`

The installer never replaces complete SG1 v4 core files. If an expected
integration point cannot be identified unambiguously, installation stops and
the dated backup remains available.

## Not touched

- retro CSS
- crosshair
- TMC2209 parameters
- stepper parameters
- DHD test
- volume meter
- incoming history
