"""Runtime helpers installed by the Dynamic-Wormhole add-on.

This is an add-on owned file.  Existing SG1 v4 source files only receive small,
marked integration hooks; they are never replaced wholesale.
"""

import random
import time


def refresh_runtime_config(manager):
    """Reload user-editable timing values before every connection."""
    manager.wormhole_max_time_default = manager.cfg.get("wormhole_max_time_minutes") * 60
    manager.wormhole_max_time_blackhole = manager.cfg.get("wormhole_max_time_blackhole") * 60
    manager.audio_clip_wait_time_default = manager.cfg.get("audio_wormhole_active_quotes_interval")
    manager.audio_clip_wait_time_blackhole = manager.cfg.get("audio_clip_wait_time_blackhole")
    manager.audio_wormhole_close_headstart = manager.cfg.get("audio_wormhole_close_headstart")
    manager.wormhole_max_time = manager.wormhole_max_time_default
    manager.audio_clip_wait_time = manager.audio_clip_wait_time_default


def install_manager_extensions(manager_class):
    manager_class.refresh_runtime_config = refresh_runtime_config


def hsv_to_rgb(_manager, h_value, saturation, value):
    if saturation == 0:
        return (value, value, value)

    h_value %= 256
    region = h_value // 43
    remainder = (h_value - (region * 43)) * 6
    p_value = (value * (255 - saturation)) >> 8
    q_value = (value * (255 - ((saturation * remainder) >> 8))) >> 8
    t_value = (value * (255 - ((saturation * (255 - remainder)) >> 8))) >> 8

    if region == 0:
        return (value, t_value, p_value)
    if region == 1:
        return (q_value, value, p_value)
    if region == 2:
        return (p_value, value, t_value)
    if region == 3:
        return (p_value, q_value, value)
    if region == 4:
        return (t_value, p_value, value)
    return (value, p_value, q_value)


def start_dynamic_wormhole(manager):
    manager.wormhole_start_time = int(time.time() * 1000)
    manager.last_random_ms = manager.wormhole_start_time
    manager.wormhole_array = [[0, 255, 1, 0] for _ in range(manager.tot_leds)]


def stop_dynamic_wormhole(manager):
    manager.wormhole_array = None
    manager.wormhole_start_time = None
    manager.last_random_ms = 0


def dynamic_wormhole_step(manager):
    if getattr(manager, "wormhole_array", None) is None or getattr(manager, "wormhole_start_time", None) is None:
        manager.start_dynamic_wormhole()

    now_ms = int(time.time() * 1000)
    wormhole_duration = now_ms - manager.wormhole_start_time

    if wormhole_duration < 1700:
        brightness = min(int((wormhole_duration / 1700.0) * 210), 210)
        return [(brightness, brightness, brightness) for _ in range(manager.tot_leds)]

    if now_ms - manager.last_random_ms >= 30:
        manager.last_random_ms = now_ms
        random_led = random.randint(0, manager.tot_leds - 1)
        random_pick = random.randint(0, 99)
        random_color = 100 if random_pick < 50 else (130 if random_pick < 85 else 160)
        if manager.wormhole_array[random_led][0] == 0:
            manager.wormhole_array[random_led] = [1, 0, 1, random_color]

    pattern = []
    for index in range(manager.tot_leds):
        led_state = manager.wormhole_array[index]
        if led_state[0] != 1:
            pattern.append((0, 0, 0))
            continue

        led_state[1] += 8 * led_state[2]
        if led_state[1] >= 255:
            led_state[1] = 255
            led_state[2] = -1
        if led_state[1] <= 0:
            manager.wormhole_array[index] = [0, 0, 1, led_state[3]]
            pattern.append((0, 0, 0))
            continue

        brightness = led_state[1]
        if led_state[3] == 100:
            pattern.append((brightness, brightness, brightness))
        else:
            pattern.append(manager.hsv_to_rgb(led_state[3], 255, brightness))
    return pattern


def start_dynamic_black_hole(manager):
    manager.wormhole_start_time = int(time.time() * 1000)
    manager.last_random_ms = manager.wormhole_start_time
    manager.wormhole_array = [[0, 0, 1, 0] for _ in range(manager.tot_leds)]


def stop_dynamic_black_hole(manager):
    stop_dynamic_wormhole(manager)


def dynamic_black_hole_step(manager):
    if getattr(manager, "wormhole_array", None) is None or getattr(manager, "wormhole_start_time", None) is None:
        manager.start_dynamic_black_hole()

    now_ms = int(time.time() * 1000)
    wormhole_duration = now_ms - manager.wormhole_start_time
    colors = [(127, 5, 29), (123, 32, 47), (80, 0, 25), (50, 0, 12), (160, 0, 42), (35, 0, 5)]

    if wormhole_duration < 1700:
        ramp = min(int((wormhole_duration / 1700.0) * 100), 100)
        return [(ramp, int(ramp * 0.03), int(ramp * 0.16)) for _ in range(manager.tot_leds)]

    if now_ms - manager.last_random_ms >= 28:
        manager.last_random_ms = now_ms
        random_led = random.randint(0, manager.tot_leds - 1)
        if manager.wormhole_array[random_led][0] == 0:
            manager.wormhole_array[random_led] = [1, 0, 1, random.randint(0, len(colors) - 1)]

    pattern = []
    for index in range(manager.tot_leds):
        led_state = manager.wormhole_array[index]
        if led_state[0] != 1:
            pattern.append((0, 0, 0))
            continue

        led_state[1] += 6 * led_state[2]
        if led_state[1] >= 190:
            led_state[1] = 190
            led_state[2] = -1
        if led_state[1] <= 0:
            manager.wormhole_array[index] = [0, 0, 1, led_state[3]]
            pattern.append((0, 0, 0))
            continue

        brightness = led_state[1]
        base_color = colors[led_state[3]]
        pattern.append(tuple(int(component * brightness / 255) for component in base_color))
    return pattern


def install_pattern_extensions(pattern_class):
    pattern_class.hsv_to_rgb = hsv_to_rgb
    pattern_class.start_dynamic_wormhole = start_dynamic_wormhole
    pattern_class.stop_dynamic_wormhole = stop_dynamic_wormhole
    pattern_class.dynamic_wormhole_step = dynamic_wormhole_step
    pattern_class.start_dynamic_black_hole = start_dynamic_black_hole
    pattern_class.stop_dynamic_black_hole = stop_dynamic_black_hole
    pattern_class.dynamic_black_hole_step = dynamic_black_hole_step
