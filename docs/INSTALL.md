# Installation Guide

```bash
cd /home/pi
unzip dynamic_wormhole_only_with_config_patch.zip
cd dynamic_wormhole_only_with_config_patch
sudo ./install.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

Check service:

```bash
sudo systemctl status stargate.service --no-pager
tail -n 80 /home/pi/sg1_v4/logs/milkyway.log
```
