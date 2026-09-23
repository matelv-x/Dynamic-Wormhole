# Installation Guide

```bash
cd /home/pi
git clone https://github.com/matelv-x/Dynamic-Wormhole.git
cd Dynamic-Wormhole
sudo ./install.sh /home/pi/sg1_v4
sudo systemctl restart stargate.service
```

Check service:

```bash
sudo systemctl status stargate.service --no-pager
tail -n 80 /home/pi/sg1_v4/logs/milkyway.log
```

The installer preserves existing core files and applies only validated Dynamic
Wormhole hooks. Normal and Black Hole durations continue to come from
`config.htm`.
