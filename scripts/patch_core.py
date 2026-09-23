#!/usr/bin/env python3
"""Surgically integrate Dynamic Wormhole into an existing SG1 v4 tree."""

import ast
import sys
from pathlib import Path


def fail(message):
    raise SystemExit(f"ERROR: {message}")


def replace_once(text, old, new, label):
    count = text.count(old)
    if count != 1:
        fail(f"Expected one {label} marker, found {count}. No core files were written.")
    return text.replace(old, new, 1)


def patch_manager(text):
    if "DYNAMIC_WORMHOLE_FRAME_SECONDS" not in text:
        marker = "from wormhole_animation_manager import WormholeAnimationManager\n"
        addition = (
            marker
            + "\nKAWOOSH_OPEN_SECONDS = 5\n"
            + "DYNAMIC_WORMHOLE_FRAME_SECONDS = 0.04\n"
        )
        text = replace_once(text, marker, addition, "wormhole manager import")

    # Fix the two legacy timing bugs even on an already installed copy.
    text = text.replace(
        "self.wormhole_max_time = self.wormhole_max_time_blackhole * 60",
        "self.wormhole_max_time = self.wormhole_max_time_blackhole",
    )
    text = text.replace(
        "self.stargate.wormhole_max_time = self.wormhole_max_time_default",
        "self.wormhole_max_time = self.wormhole_max_time_default",
    )
    text = text.replace(
        "self.stargate.audio_clip_wait_time = self.audio_clip_wait_time_default",
        "self.audio_clip_wait_time = self.audio_clip_wait_time_default",
    )

    if "kawoosh_end_time = time() + KAWOOSH_OPEN_SECONDS" not in text:
        marker = "        self.animation_manager.animate_kawoosh()\n"
        addition = (
            "        if not self.stargate.black_hole:\n"
            "            kawoosh_end_time = time() + KAWOOSH_OPEN_SECONDS\n"
            "            self.log.log(f'Kawoosh opening phase started for {KAWOOSH_OPEN_SECONDS} seconds')\n"
            "            while self.stargate.wormhole_active and time() < kawoosh_end_time:\n"
            "                self.animation_manager.animate_kawoosh()\n"
            "            self.log.log('Kawoosh opening phase finished')\n"
        )
        text = replace_once(text, marker, addition, "Kawoosh call")

    close_section_start = text.find("    def close_wormhole(self):")
    close_section_end = text.find("    def get_time_remaining(self):", close_section_start)
    if close_section_start < 0 or close_section_end < 0:
        fail("Could not locate close_wormhole/get_time_remaining methods.")
    close_section = text[close_section_start:close_section_end]

    if "stop_dynamic_wormhole()" not in close_section:
        marker = "        # Reset some state variables\n"
        addition = "        self.animation_manager.pattern_manager.stop_dynamic_wormhole()\n\n" + marker
        if marker not in close_section:
            fail("Could not locate close_wormhole reset marker.")
        close_section = close_section.replace(marker, addition, 1)

    if "self.stargate.manual_dynamic_override = None" not in close_section:
        marker = "        self.stargate.wormhole_active = False"
        addition = "        self.stargate.manual_dynamic_override = None\n" + marker
        if marker not in close_section:
            fail("Could not locate close_wormhole active-state reset.")
        close_section = close_section.replace(marker, addition, 1)

    text = text[:close_section_start] + close_section + text[close_section_end:]

    establish_start = text.find("    def establish_wormhole(self):")
    if establish_start < 0:
        fail("Could not locate establish_wormhole method.")

    if "        self.refresh_runtime_config()\n" not in text[establish_start:]:
        marker = "        # Open The wormhole\n"
        if marker not in text[establish_start:]:
            fail("Could not locate establish_wormhole opening marker.")
        text = text[:establish_start] + text[establish_start:].replace(
            marker,
            "        self.refresh_runtime_config()\n\n" + marker,
            1,
        )

    if "manual_override = getattr(self.stargate" not in text[establish_start:]:
        marker = "        # Open The wormhole\n"
        block = (
            "        manual_override = getattr(self.stargate, \"manual_dynamic_override\", None)\n\n"
            "        incoming_dynamic_enabled = (\n"
            "            self.stargate.wormhole_active == \"incoming\"\n"
            "            and bool(self.cfg.get(\"use_dynamic_wormhole_for_incoming\"))\n"
            "        )\n\n"
            "        if manual_override is True:\n"
            "            self.use_dynamic_wormhole = True\n"
            "        elif manual_override is False:\n"
            "            self.use_dynamic_wormhole = False\n"
            "        else:\n"
            "            self.use_dynamic_wormhole = bool(self.cfg.get(\"use_dynamic_wormhole\")) or incoming_dynamic_enabled\n\n"
        )
        text = text[:establish_start] + text[establish_start:].replace(marker, block + marker, 1)

    if "dynamic_wormhole_step()" not in text[establish_start:]:
        marker = "            self.animation_manager.do_random_transitions(self.stargate.black_hole)\n"
        block = (
            "            if self.use_dynamic_wormhole:\n"
            "                if self.stargate.black_hole:\n"
            "                    dynamic_pattern = self.animation_manager.pattern_manager.dynamic_black_hole_step()\n"
            "                else:\n"
            "                    dynamic_pattern = self.animation_manager.pattern_manager.dynamic_wormhole_step()\n\n"
            "                self.animation_manager.set_wormhole_pattern(dynamic_pattern)\n"
            "                sleep(DYNAMIC_WORMHOLE_FRAME_SECONDS)\n"
            "            else:\n"
            "                self.animation_manager.do_random_transitions(self.stargate.black_hole)\n"
        )
        text = replace_once(text, marker, block, "static wormhole transition")

    final_close = (
        "        self.animation_manager.pattern_manager.stop_dynamic_wormhole()\n"
        "        self.close_wormhole()\n"
    )
    if final_close not in text:
        marker = "        self.close_wormhole()\n"
        text = replace_once(
            text,
            marker,
            "        self.animation_manager.pattern_manager.stop_dynamic_wormhole()\n" + marker,
            "final close_wormhole call",
        )

    manager_hook = (
        "\n# DYNAMIC WORMHOLE ADD-ON HOOK START\n"
        "from dynamic_wormhole_runtime import install_manager_extensions as _install_dynamic_manager_extensions\n"
        "_install_dynamic_manager_extensions(WormholeManager)\n"
        "# DYNAMIC WORMHOLE ADD-ON HOOK END\n"
    )
    if "DYNAMIC WORMHOLE ADD-ON HOOK START" not in text:
        text = text.rstrip() + "\n" + manager_hook

    return text


def patch_pattern_manager(text):
    hook = (
        "\n# DYNAMIC WORMHOLE ADD-ON HOOK START\n"
        "from dynamic_wormhole_runtime import install_pattern_extensions as _install_dynamic_pattern_extensions\n"
        "_install_dynamic_pattern_extensions(WormholePatternManager)\n"
        "# DYNAMIC WORMHOLE ADD-ON HOOK END\n"
    )
    if "DYNAMIC WORMHOLE ADD-ON HOOK START" not in text:
        text = text.rstrip() + "\n" + hook
    return text


def main():
    if len(sys.argv) != 2:
        fail("Usage: patch_core.py /home/pi/sg1_v4")

    target = Path(sys.argv[1])
    manager_path = target / "classes/StargateMilkyWay/wormhole_manager.py"
    pattern_path = target / "classes/StargateMilkyWay/wormhole_pattern_manager.py"

    for path in (manager_path, pattern_path):
        if not path.is_file():
            fail(f"Required file not found: {path}")

    originals = {
        manager_path: manager_path.read_text(encoding="utf-8"),
        pattern_path: pattern_path.read_text(encoding="utf-8"),
    }
    patched = {
        manager_path: patch_manager(originals[manager_path]),
        pattern_path: patch_pattern_manager(originals[pattern_path]),
    }

    # Parse every result before writing either core file.
    for path, content in patched.items():
        try:
            ast.parse(content, filename=str(path))
        except SyntaxError as exc:
            fail(f"Generated invalid Python for {path}: {exc}")

    for path, content in patched.items():
        if content != originals[path]:
            path.write_text(content, encoding="utf-8")
            print(f"Patched core file: {path}")
        else:
            print(f"Core file already patched: {path}")


if __name__ == "__main__":
    main()
