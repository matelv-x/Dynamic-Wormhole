# SG1 Dynamic Wormhole Patch

Lightweight Dynamic Wormhole add-on for Kristian/Jonnerd SG1 v4 images.

This repository is private while it is being checked and verified.

## Install

Clone or unzip this add-on into `/home/pi`, then run:

```bash
cd /home/pi
rm -rf Dynamic-Wormhole
git clone https://github.com/matelv-x/Dynamic-Wormhole.git
cd Dynamic-Wormhole
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
- Adds Debug UI popup selector.
- Injects required endpoint/config changes where needed.

## Attribution and originality

Original base project: StargateProject SG1 software from the BuildAStargate/Jordan/Kristian/Jonnerd project lineage.

Additional source/idea credit: Feature idea by Marcin/Codex over StargateProject wormhole LED code.

How much is copied or changed: Medium script/overlay patch with robust insertion logic.
