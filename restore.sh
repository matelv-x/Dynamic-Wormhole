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

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Removing only Dynamic Wormhole integration blocks."

if [[ "${STARGATE_ADDON_NO_RESTART:-0}" != "1" ]]; then
  sudo systemctl stop stargate.service || true
fi

sudo python3 "$SCRIPT_DIR/scripts/unpatch_core.py" "$TARGET"
sudo python3 "$SCRIPT_DIR/scripts/uninstall_overlay.py" "$TARGET"
sudo python3 -m py_compile "$TARGET/classes/StargateMilkyWay/wormhole_manager.py" "$TARGET/classes/StargateMilkyWay/wormhole_pattern_manager.py" "$TARGET/classes/web_server.py"

sudo find "$TARGET/classes" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
if [[ "${STARGATE_ADDON_NO_RESTART:-0}" != "1" ]]; then
  sudo systemctl start stargate.service
else
  echo "Stargate restart deferred by add-on manager."
fi

echo "=== DYNAMIC WORMHOLE RESTORE COMPLETE ==="
