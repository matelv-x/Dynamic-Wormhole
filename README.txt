Dynamic Wormhole Only + Config Options Patch

The installer is surgical. It does not replace complete SG1 v4 core files.

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
  git clone https://github.com/matelv-x/Dynamic-Wormhole.git
  cd Dynamic-Wormhole
  sudo ./install.sh /home/pi/sg1_v4
  sudo systemctl restart stargate.service

After installing:
  Open config.htm and look for:
  - Use Dynamic Wormhole
  - Use Dynamic Wormhole For Incoming

Restore:
  cd /home/pi/Dynamic-Wormhole
  sudo ./restore.sh /home/pi/sg1_v4
