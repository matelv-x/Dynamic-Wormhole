#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-/home/pi/sg1_v4}"

if [[ "$TARGET" == "--target" ]]; then
  TARGET="${2:-/home/pi/sg1_v4}"
fi

if [[ "$TARGET" == */web ]]; then
  echo "ERROR: Use sg1_v4 root folder, not /web."
  echo "Correct: sudo ./install.sh /home/pi/sg1_v4"
  exit 1
fi

if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: Target folder not found: $TARGET"
  exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKUP="${TARGET}_backup_dynamic_wormhole_only_$(date +%Y%m%d_%H%M%S)"

echo "=== Creating backup ==="
cp -a "$TARGET" "$BACKUP"
echo "Backup created: $BACKUP"

echo "=== Installing Dynamic Wormhole only + config options ==="
cp "$SCRIPT_DIR/files/classes/StargateMilkyWay/wormhole_manager.py" \
   "$TARGET/classes/StargateMilkyWay/wormhole_manager.py"

cp "$SCRIPT_DIR/files/classes/StargateMilkyWay/wormhole_pattern_manager.py" \
   "$TARGET/classes/StargateMilkyWay/wormhole_pattern_manager.py"

echo "=== Patching only required dynamic wormhole parts ==="
python3 - "$TARGET" <<'PY'
import json
import re
import sys
from pathlib import Path

target = Path(sys.argv[1])

def read(p):
    return p.read_text(encoding="utf-8", errors="ignore")

def write(p, s):
    p.write_text(s, encoding="utf-8")

# ------------------------------------------------------------
# Config: only add dynamic wormhole options if missing.
# Do NOT touch stepper/TMC/MotorHat config.
# ------------------------------------------------------------
for p in [
    target / "config/milkyway-config.json",
    target / "config/defaults-milkyway/config.json.dist",
]:
    if not p.exists():
        print(f"WARNING: missing config file: {p}")
        continue

    data = json.loads(read(p))

    # These entries are what make the options appear in config.htm.
    if "use_dynamic_wormhole" not in data or not isinstance(data.get("use_dynamic_wormhole"), dict):
        data["use_dynamic_wormhole"] = {"value": False}
    data["use_dynamic_wormhole"]["desc"] = "True to use the dynamic animated wormhole effect instead of the original static wormhole patterns"
    data["use_dynamic_wormhole"]["type"] = "bool"

    if "use_dynamic_wormhole_for_incoming" not in data or not isinstance(data.get("use_dynamic_wormhole_for_incoming"), dict):
        data["use_dynamic_wormhole_for_incoming"] = {"value": False}
    data["use_dynamic_wormhole_for_incoming"]["desc"] = "True to force the dynamic animated wormhole effect for every incoming wormhole, even when use_dynamic_wormhole is false"
    data["use_dynamic_wormhole_for_incoming"]["type"] = "bool"

    write(p, json.dumps(data, indent=2))
    print(f"Patched config: {p}")

# ------------------------------------------------------------
# web_server.py: add /do/dynamic_wormhole_on endpoint only.
# Do NOT touch other endpoints or config validation.
# ------------------------------------------------------------
web_server = target / "classes/web_server.py"

if web_server.exists():
    s = read(web_server)

    # Universal endpoint injection:
    # - if dynamic_wormhole_on exists, keep it
    # - if blackhole_on exists, keep it
    # - if missing, add endpoint(s)
    # - use blackhole_on, wormhole_on, or wormhole_off as safe insertion marker
    endpoint_block = ""

    if "/do/dynamic_wormhole_on" not in s:
        endpoint_block += '''            elif self.path == "/do/dynamic_wormhole_on":
                if not self.stargate.wormhole_active:
                    self.stargate.black_hole = False
                    self.stargate.manual_dynamic_override = True
                    self.stargate.wormhole_active = True
                    data = { "success": True }
                else:
                    data = { "success": False, "message": "A wormhole is already established." }

'''

    if "/do/blackhole_on" not in s:
        endpoint_block += '''            elif self.path == "/do/blackhole_on":
                if not self.stargate.wormhole_active:
                    self.stargate.black_hole = True
                    self.stargate.manual_dynamic_override = None
                    self.stargate.wormhole_active = True
                    data = { "success": True }
                else:
                    data = { "success": False, "message": "A wormhole is already established." }

'''

    if endpoint_block:
        markers = [
            '            elif self.path == "/do/blackhole_on":',
            "            elif self.path == '/do/blackhole_on':",
            '            elif self.path == "/do/wormhole_on":',
            "            elif self.path == '/do/wormhole_on':",
            '            elif self.path == "/do/wormhole_off":',
            "            elif self.path == '/do/wormhole_off':",
        ]

        inserted = False
        for marker in markers:
            if marker in s:
                s = s.replace(marker, endpoint_block + marker, 1)
                inserted = True
                break

        if not inserted:
            raise SystemExit("ERROR: Could not find wormhole endpoint marker in web_server.py")

    write(web_server, s)
    print(f"Patched web_server.py: {web_server}")
else:
    raise SystemExit("ERROR: web_server.py not found")

# ------------------------------------------------------------
# debug.htm:
# one Open Wormhole button
# popup:
#   Standard Wormhole
#   Dynamic Wormhole
#   Black Hole
# ------------------------------------------------------------
debug_html = target / "web/debug.htm"

if debug_html.exists():
    s = read(debug_html)

    # Remove old injected script if installed before.
    s = re.sub(
        r'\n\s*<!-- DYNAMIC WORMHOLE ONLY PATCH START -->.*?<!-- DYNAMIC WORMHOLE ONLY PATCH END -->\s*\n',
        '\n',
        s,
        flags=re.S
    )

    # Remove standalone Dynamic Wormhole button if present.
    s = re.sub(
        r'\n\s*<button[^>]+action=["\']dynamic_wormhole_on["\'][^>]*>Dynamic Wormhole</button>\s*',
        '\n',
        s
    )

    new_section = '''        <h4>Wormhole Manual Control</h4>
        <button type="button" class="btn-secondary controlButton" id="openWormholeMenuButton">Open Wormhole</button>
        <button type="button" class="btn-secondary controlButton" action="wormhole_off">Close Wormhole</button>

        <div id="wormholePickerDialog" title="Select Wormhole Type" style="display:none;">
          <button type="button" class="btn-secondary wormholeChoiceButton" data-action="wormhole_on">Standard Wormhole</button><br><br>
          <button type="button" class="btn-secondary wormholeChoiceButton" data-action="dynamic_wormhole_on">Dynamic Wormhole</button><br><br>
          <button type="button" class="btn-secondary wormholeChoiceButton" data-action="blackhole_on">Black Hole</button>
        </div>'''

    pattern = r'        <h4>Wormhole Manual Control</h4>.*?\n\s*<hr\s*/>'
    m = re.search(pattern, s, flags=re.S)

    if m:
        s = s[:m.start()] + new_section + "\n\n        <hr />" + s[m.end():]
    else:
        raise SystemExit("ERROR: Could not find Wormhole Manual Control section in debug.htm")

    script = r'''
<!-- DYNAMIC WORMHOLE ONLY PATCH START -->
<script type="text/javascript">
  $(function() {
    $('#openWormholeMenuButton').off('click').off('click.dynamicWormholeOnly').on('click.dynamicWormholeOnly', function(e) {
      e.preventDefault();
      e.stopImmediatePropagation();

      $('#wormholePickerDialog').dialog({
        modal: true,
        width: 320,
        resizable: false
      });
    });

    $('.wormholeChoiceButton').off('click.dynamicWormholeOnly').on('click.dynamicWormholeOnly', function(e) {
      e.preventDefault();
      e.stopImmediatePropagation();

      var actionName = $(this).data('action');
      $('#wormholePickerDialog').dialog('close');

      $.post('stargate/do/' + actionName)
        .fail(function() {
          $("<div>Failed to start wormhole.</div>").dialog();
        });
    });
  });
</script>
<!-- DYNAMIC WORMHOLE ONLY PATCH END -->
'''

    if "</body>" in s:
        s = s.replace("</body>", script + "\n</body>", 1)
    else:
        s += script

    write(debug_html, s)
    print(f"Patched debug.htm: {debug_html}")
else:
    raise SystemExit("ERROR: debug.htm not found")

PY

echo "=== Syntax check ==="
python3 -m py_compile \
  "$TARGET/classes/StargateMilkyWay/wormhole_manager.py" \
  "$TARGET/classes/StargateMilkyWay/wormhole_pattern_manager.py" \
  "$TARGET/classes/web_server.py"

echo "=== Done ==="
echo "Restart with: sudo systemctl restart stargate.service"
echo "Restore backup with: sudo rsync -a --delete $BACKUP/ $TARGET/"
