Dynamic Wormhole Only + Config Options Patch

This ZIP is ONLY for:
- Dynamic Wormhole backend
- one Open Wormhole button
- popup choice:
  - Standard Wormhole
  - Dynamic Wormhole
  - Black Hole
- config.htm options through JSON config keys:
  - Use Dynamic Wormhole
  - Use Dynamic Wormhole For Incoming

It does NOT change:
- TMC2209 parameters
- Stepper parameters
- MotorHat/TMC selection
- volume meter
- DHD test
- incoming history
- other custom UI sections

Install:
  cd /home/pi
  unzip dynamic_wormhole_only_with_config_patch.zip
  cd dynamic_wormhole_only_with_config_patch
  sudo ./install.sh /home/pi/sg1_v4
  sudo systemctl restart stargate.service

After installing:
  Open config.htm and look for:
  - Use Dynamic Wormhole
  - Use Dynamic Wormhole For Incoming

Restore:
  sudo rsync -a --delete /home/pi/sg1_v4_backup_dynamic_wormhole_only_YYYYMMDD_HHMMSS/ /home/pi/sg1_v4/
