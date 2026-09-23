#!/usr/bin/env python3
"""Non-hardware verification for a Dynamic-Wormhole installation."""

import ast
import importlib.util
import sys
from pathlib import Path


def fail(message):
    raise SystemExit(f"ERROR: {message}")


def main():
    if len(sys.argv) != 2:
        fail("Usage: verify_install.py /home/pi/sg1_v4")

    target = Path(sys.argv[1])
    base = target / "classes/StargateMilkyWay"
    manager_path = base / "wormhole_manager.py"
    pattern_path = base / "wormhole_pattern_manager.py"
    runtime_path = base / "dynamic_wormhole_runtime.py"

    for path in (manager_path, pattern_path, runtime_path):
        if not path.is_file():
            fail(f"Required file not found: {path}")
        try:
            ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            fail(f"Invalid Python in {path}: {exc}")

    manager_text = manager_path.read_text(encoding="utf-8")
    required_manager_markers = (
        "self.refresh_runtime_config()",
        "dynamic_wormhole_step()",
        "dynamic_black_hole_step()",
        "DYNAMIC WORMHOLE ADD-ON HOOK START",
    )
    for marker in required_manager_markers:
        if marker not in manager_text:
            fail(f"Missing manager integration marker: {marker}")

    forbidden_manager_markers = (
        "self.wormhole_max_time = self.wormhole_max_time_blackhole * 60",
        "self.stargate.wormhole_max_time = self.wormhole_max_time_default",
        "self.stargate.audio_clip_wait_time = self.audio_clip_wait_time_default",
    )
    for marker in forbidden_manager_markers:
        if marker in manager_text:
            fail(f"Legacy timing bug is still present: {marker}")

    spec = importlib.util.spec_from_file_location("dynamic_wormhole_runtime_verify", runtime_path)
    runtime = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(runtime)

    class Config:
        values = {
            "wormhole_max_time_minutes": 7.25,
            "wormhole_max_time_blackhole": 23.5,
            "audio_wormhole_active_quotes_interval": 11,
            "audio_clip_wait_time_blackhole": 22,
            "audio_wormhole_close_headstart": 3,
        }

        def get(self, key):
            return self.values[key]

    class Manager:
        cfg = Config()

    manager = Manager()
    runtime.refresh_runtime_config(manager)
    if manager.wormhole_max_time_default != 435.0:
        fail("Normal wormhole time is not derived correctly from config.")
    if manager.wormhole_max_time_blackhole != 1410.0:
        fail("Black Hole time is not derived correctly from config.")
    if manager.wormhole_max_time != manager.wormhole_max_time_default:
        fail("Runtime timer did not reset to the configured normal value.")

    sys.path.insert(0, str(base))
    pattern_spec = importlib.util.spec_from_file_location(
        "wormhole_pattern_manager_verify", pattern_path
    )
    pattern_module = importlib.util.module_from_spec(pattern_spec)
    pattern_spec.loader.exec_module(pattern_module)
    pattern_manager = pattern_module.WormholePatternManager(24)
    normal_pattern = pattern_manager.dynamic_wormhole_step()
    black_hole_pattern = pattern_manager.dynamic_black_hole_step()
    if len(normal_pattern) != 24 or len(black_hole_pattern) != 24:
        fail("Dynamic pattern helpers returned an invalid LED count.")
    if not all(len(pixel) == 3 for pixel in normal_pattern + black_hole_pattern):
        fail("Dynamic pattern helpers returned an invalid RGB value.")

    print("Dynamic Wormhole verification passed.")


if __name__ == "__main__":
    main()
