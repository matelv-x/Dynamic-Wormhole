#!/usr/bin/env python3
from pathlib import Path
import json
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/pi/sg1_v4")

for relative in ("config/milkyway-config.json", "config/defaults-milkyway/config.json.dist"):
    path = root / relative
    if path.is_file():
        data = json.loads(path.read_text(encoding="utf-8"))
        data.pop("use_dynamic_wormhole", None)
        data.pop("use_dynamic_wormhole_for_incoming", None)
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

server = root / "classes/web_server.py"
text = server.read_text(encoding="utf-8")
for endpoint in ("dynamic_wormhole_on", "blackhole_on"):
    text = re.sub(
        rf"\n            elif self\.path == [\"']/do/{endpoint}[\"']:\n.*?"
        r"(?=\n            elif self\.path ==)",
        "\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
server.write_text(text, encoding="utf-8")

debug = root / "web/debug.htm"
text = debug.read_text(encoding="utf-8", errors="replace")
text = re.sub(r"\n\s*<!-- DYNAMIC WORMHOLE ONLY PATCH START -->.*?<!-- DYNAMIC WORMHOLE ONLY PATCH END -->\s*\n", "\n", text, flags=re.DOTALL)
text = re.sub(
    r"        <h4>Wormhole Manual Control</h4>.*?\n\s*<hr\s*/>",
    '        <h4>Wormhole Manual Control</h4>\n'
    '        <button type="button" class="btn-secondary controlButton" action="wormhole_on">Open Wormhole</button>\n'
    '        <button type="button" class="btn-secondary controlButton" action="wormhole_off">Close Wormhole</button>\n\n'
    '        <hr />',
    text,
    count=1,
    flags=re.DOTALL,
)
debug.write_text(text, encoding="utf-8")
(root / "classes/StargateMilkyWay/dynamic_wormhole_runtime.py").unlink(missing_ok=True)
