#!/usr/bin/env python3
from pathlib import Path
import ast
import re
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else "/home/pi/sg1_v4")
manager = root / "classes/StargateMilkyWay/wormhole_manager.py"
pattern = root / "classes/StargateMilkyWay/wormhole_pattern_manager.py"

def clean(path, transform):
    original = path.read_text(encoding="utf-8")
    text = transform(original)
    ast.parse(text, filename=str(path))
    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"Cleaned: {path}")

def clean_manager(text):
    text = text.replace("\nKAWOOSH_OPEN_SECONDS = 5\nDYNAMIC_WORMHOLE_FRAME_SECONDS = 0.04\n", "")
    text = re.sub(
        r"        if not self\.stargate\.black_hole:\n"
        r"            kawoosh_end_time = time\(\) \+ KAWOOSH_OPEN_SECONDS\n.*?"
        r"            self\.log\.log\('Kawoosh opening phase finished'\)\n",
        "        self.animation_manager.animate_kawoosh()\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace("        self.animation_manager.pattern_manager.stop_dynamic_wormhole()\n\n        # Reset some state variables\n", "        # Reset some state variables\n")
    text = text.replace(
        "        self.animation_manager.pattern_manager.stop_dynamic_wormhole()\n\n"
        "        # Reset runtime values on the manager that actually owns the timers.\n",
        "        # Reset runtime values on the manager that actually owns the timers.\n",
    )
    text = text.replace("        self.stargate.manual_dynamic_override = None\n        self.stargate.wormhole_active = False", "        self.stargate.wormhole_active = False")
    text = re.sub(
        r"        # DYNAMIC WORMHOLE REFRESH HOOK START\n"
        r"        self\.refresh_runtime_config\(\)\n"
        r"        # DYNAMIC WORMHOLE REFRESH HOOK END\n\n",
        "",
        text,
        count=1,
    )
    text = re.sub(
        r"        manual_override = getattr\(self\.stargate, \"manual_dynamic_override\", None\)\n.*?"
        r"            self\.use_dynamic_wormhole = bool\(self\.cfg\.get\(\"use_dynamic_wormhole\"\)\) or incoming_dynamic_enabled\n\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"            if self\.use_dynamic_wormhole:\n.*?"
        r"            else:\n                self\.animation_manager\.do_random_transitions\(self\.stargate\.black_hole\)\n",
        "            self.animation_manager.do_random_transitions(self.stargate.black_hole)\n",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace("        self.animation_manager.pattern_manager.stop_dynamic_wormhole()\n        self.close_wormhole()\n", "        self.close_wormhole()\n")
    text = re.sub(r"\n# DYNAMIC WORMHOLE ADD-ON HOOK START\n.*?# DYNAMIC WORMHOLE ADD-ON HOOK END\n?", "", text, flags=re.DOTALL)
    for line in (
        '        self.use_dynamic_wormhole = self.cfg.get("use_dynamic_wormhole")\n',
        '        self.use_dynamic_wormhole_for_incoming = self.cfg.get("use_dynamic_wormhole_for_incoming")\n',
        "        self.animation_manager.pattern_manager.stop_dynamic_wormhole()\n",
        "        self.stargate.manual_dynamic_override = None\n",
    ):
        text = text.replace(line, "")
    text = re.sub(
        r"        self\.log\.log\(f'Opening Wormhole! black_hole=\{self\.stargate\.black_hole\}, dynamic=\{self\.use_dynamic_wormhole\}'\)\n",
        "        self.log.log(f'Opening Wormhole! black_hole={self.stargate.black_hole}')\n",
        text,
    )
    leftovers = (
        "use_dynamic_wormhole",
        "manual_dynamic_override",
        "stop_dynamic_wormhole",
        "dynamic_wormhole_step",
        "DYNAMIC_WORMHOLE_FRAME_SECONDS",
    )
    remaining = [marker for marker in leftovers if marker in text]
    if remaining:
        raise RuntimeError(f"Dynamic Wormhole markers remain in {manager}: {remaining}")
    return text

def clean_pattern(text):
    text = re.sub(r"\n# DYNAMIC WORMHOLE ADD-ON HOOK START\n.*?# DYNAMIC WORMHOLE ADD-ON HOOK END\n?", "\n", text, flags=re.DOTALL)
    for line in (
        "        self.wormhole_array = None\n",
        "        self.wormhole_start_time = None\n",
        "        self.last_random_ms = 0\n",
    ):
        text = text.replace(line, "", 1)
    for name in (
        "start_dynamic_wormhole",
        "stop_dynamic_wormhole",
        "dynamic_wormhole_step",
        "start_dynamic_black_hole",
        "stop_dynamic_black_hole",
        "dynamic_black_hole_step",
    ):
        text = re.sub(
            rf"(?ms)^    def {name}\(.*?(?=^    (?:@|def )|^class |\Z)",
            "",
            text,
            count=1,
        )
    remaining = [
        marker for marker in (
            "start_dynamic_wormhole",
            "stop_dynamic_wormhole",
            "dynamic_wormhole_step",
            "start_dynamic_black_hole",
            "stop_dynamic_black_hole",
            "dynamic_black_hole_step",
            "DYNAMIC WORMHOLE ADD-ON HOOK",
        )
        if marker in text
    ]
    if remaining:
        raise RuntimeError(f"Dynamic Wormhole markers remain in {pattern}: {remaining}")
    return text

clean(manager, clean_manager)
clean(pattern, clean_pattern)
