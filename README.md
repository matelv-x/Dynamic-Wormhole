# Dynamic Wormhole

Adds dynamic wormhole and black-hole LED effects.

This repository is private while it is being checked and verified.

## Install

```bash
cd /home/pi/Stargate-Final_Patches
rm -rf Dynamic-Wormhole
git clone https://github.com/matelv-x/Dynamic-Wormhole.git
cd Dynamic-Wormhole
chmod +x *.sh
sudo ./install.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## Restore / uninstall

```bash
cd /home/pi/Stargate-Final_Patches/Dynamic-Wormhole
chmod +x restore.sh
sudo ./restore.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

## What it changes

- Adds dynamic blue wormhole and black-hole animation behavior.
- Adds debug actions for normal, dynamic and black-hole wormhole tests.
- Adds config support for dynamic wormhole behavior.

## Attribution and originality

Original base project: StargateProject SG1 software from the BuildAStargate/Jordan/Kristian/Jonnerd project lineage.

Additional source/idea credit: Inspired by Kristian/Jonnerd StargateProject wormhole LED behavior and Marcin/Codex animation work.

How much is copied or changed: Medium patch. It modifies selected wormhole manager, config and debug files rather than replacing the whole project.

The included `*.patch` file, when present, shows the exact text-level changes against the base software used while packaging.
