# SG1 Dynamic Wormhole Patch

## Stellar Archive maintenance

This repository includes maintenance contract v1. Install and bounded restore
can be launched by Stellar Archive without an automatic service restart.

[![Downloads](https://img.shields.io/github/downloads/matelv-x/Dynamic-Wormhole/total?label=downloads)](https://github.com/matelv-x/Dynamic-Wormhole/releases)

Lightweight Dynamic Wormhole add-on for Kristian/Jonnerd SG1 v4 images.

The installer is surgical: it keeps the existing SG1 v4 core files and adds
only the Dynamic Wormhole integration hooks. It does not replace complete
`wormhole_manager.py` or `wormhole_pattern_manager.py` files.

<img width="1343" height="175" alt=" Dynamic" src="https://github.com/user-attachments/assets/5e5b7457-563b-4be0-aca8-4972ef7af26a" />


## Install

## Method 1 — GitHub Clone (Recommended)

```bash
cd /home/pi
rm -rf Dynamic-Wormhole
git clone https://github.com/matelv-x/Dynamic-Wormhole.git
cd Dynamic-Wormhole
chmod +x install.sh restore.sh
sudo ./install.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## Method 2 — ZIP Download

1. Download and extract the ZIP archive into:

/home/pi/Dynamic-Wormhole

2. Then run:

```bash
cd /home/pi/Dynamic-Wormhole
chmod +x install.sh restore.sh
sudo ./install.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## Restore / uninstall

```bash
cd /home/pi/Dynamic-Wormhole
sudo ./restore.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## What it changes

- Adds dynamic wormhole and black-hole effects.
- Limits the dynamic LED refresh rate to reduce CPU/thread pressure on Pi 3.
- Runs an independent 5-second Kawoosh opening phase before a normal or dynamic wormhole animation begins.
- Leaves the separate Lamp Mode `Kawoosh Loop` option available.
- Adds Debug UI popup selector.
- Injects required endpoint/config changes where needed.
- Preserves unrelated SG1 v4, hardware, timing, audio, LAN and UI changes.
- Reads normal and Black Hole durations from `config.htm` before every connection.
- Converts configured minutes to seconds exactly once; no fixed connection times are embedded.
- Refuses to modify core files when the expected SG1 v4 integration points cannot be identified safely.
- Can be run repeatedly without duplicating hooks.

The installer creates a dated backup before editing. It copies only the new
add-on-owned `dynamic_wormhole_runtime.py`; existing SG1 v4 source files receive
small marked or structurally validated edits.

## Attribution and originality

Original base project: StargateProject SG1 https://github.com/jonnerd154/StargateProject-software.

Additional source/idea credit: Feature idea by matelv-x/Codex over StargateProject wormhole LED code.
