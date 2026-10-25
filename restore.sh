#!/usr/bin/env bash
set -euo pipefail

TARGET="${1:-/home/pi/sg1_v4}"
if [[ "$TARGET" == "--target" ]]; then
  TARGET="${2:-/home/pi/sg1_v4}"
fi

fail() { echo "ERROR: $1" >&2; exit 1; }

[ -d "$TARGET" ] || fail "Target folder not found: $TARGET"

if ! sudo -n true 2>/dev/null; then
  echo "This restore needs sudo because stargate files may be owned by root."
  sudo true
fi

BACKUP="$(ls -dt "${TARGET}"_backup_dynamic_wormhole_only_* 2>/dev/null | head -n 1 || true)"
[ -n "$BACKUP" ] || fail "No Dynamic Wormhole backup found: ${TARGET}_backup_dynamic_wormhole_only_*"
[ -d "$BACKUP" ] || fail "Backup folder does not exist: $BACKUP"

echo "Restoring Dynamic Wormhole files from:"
echo "  $BACKUP"

if [[ "${STARGATE_ADDON_NO_RESTART:-0}" != "1" ]]; then
  sudo systemctl stop stargate.service || true
fi

for rel in \
  "classes/StargateMilkyWay/wormhole_manager.py" \
  "classes/StargateMilkyWay/wormhole_pattern_manager.py" \
  "classes/web_server.py" \
  "web/debug.htm" \
  "config/milkyway-config.json" \
  "config/defaults-milkyway/config.json.dist"
do
  if [ -e "$BACKUP/$rel" ]; then
    sudo mkdir -p "$(dirname "$TARGET/$rel")"
    sudo rm -rf "$TARGET/$rel"
    sudo cp -a "$BACKUP/$rel" "$TARGET/$rel"
    echo "Restored: $rel"
  else
    echo "Skipped missing backup file: $rel"
  fi
done

# This file belongs only to the add-on, so an older SG1 v4 backup normally
# does not contain it. Remove it during restore instead of leaving dead code.
if [ ! -e "$BACKUP/classes/StargateMilkyWay/dynamic_wormhole_runtime.py" ]; then
  sudo rm -f "$TARGET/classes/StargateMilkyWay/dynamic_wormhole_runtime.py"
  echo "Removed add-on file: classes/StargateMilkyWay/dynamic_wormhole_runtime.py"
fi

sudo find "$TARGET/classes" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
if [[ "${STARGATE_ADDON_NO_RESTART:-0}" != "1" ]]; then
  sudo systemctl start stargate.service
else
  echo "Stargate restart deferred by add-on manager."
fi

echo "=== DYNAMIC WORMHOLE RESTORE COMPLETE ==="
