import random
import time


class WormholePatternManager:

    def __init__(self, tot_leds):
        self.tot_leds = tot_leds

        self.standard_patterns = []
        self.black_hole_patterns = []

        # Dynamic wormhole / black hole state
        # [active, brightness, fade_direction, hue/color_index]
        self.wormhole_array = None
        self.wormhole_start_time = None
        self.last_random_ms = 0

        self.init_patterns()

    def pattern_off(self):
        off_pattern = []
        for index in range(self.tot_leds):  # pylint: disable=unused-variable
            off_pattern.append((0, 0, 0))
        return off_pattern

    def pattern1(self, color1, color2):
        pattern = []
        for led in range(self.tot_leds):
            pattern.append(color1)
        for led in range(0, self.tot_leds, 5):
            pattern[led] = color2
            pattern[led - 1] = color2
        return pattern

    def pattern2(self, base_color, size):
        pattern = []
        second_color = ((base_color[0] + 5) % 255, (base_color[1] + 5) % 255, (base_color[2] - 190) % 255)
        third_color = ((base_color[0] + 5) % 255, (base_color[1] + 200) % 255, (base_color[2] // 2) % 255)
        for led in range(self.tot_leds):
            pattern.append(base_color)
        for led in range(0, self.tot_leds, self.tot_leds // size):
            pattern[led] = second_color
            pattern[(led + 1) % self.tot_leds] = second_color
            pattern[(led - 1) % self.tot_leds] = second_color
            pattern[(led + 2) % self.tot_leds] = third_color
            pattern[(led - 2) % self.tot_leds] = third_color
        return pattern

    def pattern3(self, base_color, size):
        pattern = []
        for led in range(self.tot_leds):
            pattern.append(base_color)
        for led in range(0, self.tot_leds, size):
            pattern[(led - 1) % self.tot_leds] = (base_color[0] // 2, base_color[1] // 2, base_color[2] // 2)
            pattern[(led - 2) % self.tot_leds] = (base_color[0] // 3, base_color[1] // 3, base_color[2] // 3)
            pattern[(led - 3) % self.tot_leds] = (base_color[0] // 4, base_color[1] // 4, base_color[2] // 4)
            pattern[(led - 4) % self.tot_leds] = (base_color[0] // 5, base_color[1] // 5, base_color[2] // 5)
            pattern[(led - 5) % self.tot_leds] = (base_color[0] // 6, base_color[1] // 6, base_color[2] // 6)
            pattern[(led - 6) % self.tot_leds] = (base_color[0] // 7, base_color[1] // 7, base_color[2] // 7)
            pattern[(led - 7) % self.tot_leds] = (base_color[0] // 8, base_color[1] // 8, base_color[2] // 8)
            pattern[led] = base_color
            pattern[(led + 1) % self.tot_leds] = (base_color[0] // 2, base_color[1] // 2, base_color[2] // 2)
            pattern[(led + 2) % self.tot_leds] = (base_color[0] // 3, base_color[1] // 3, base_color[2] // 3)
            pattern[(led + 3) % self.tot_leds] = (base_color[0] // 4, base_color[1] // 4, base_color[2] // 4)
            pattern[(led + 4) % self.tot_leds] = (base_color[0] // 5, base_color[1] // 5, base_color[2] // 5)
            pattern[(led + 5) % self.tot_leds] = (base_color[0] // 6, base_color[1] // 6, base_color[2] // 6)
            pattern[(led + 6) % self.tot_leds] = (base_color[0] // 7, base_color[1] // 7, base_color[2] // 7)
            pattern[(led + 7) % self.tot_leds] = (base_color[0] // 8, base_color[1] // 8, base_color[2] // 8)
        return pattern

    def get_patterns(self, black_hole=False):
        if not black_hole:
            return self.standard_patterns
        return self.black_hole_patterns

    def init_patterns(self):
        self.standard_patterns = [
            self.pattern1((26, 56, 105), (5, 37, 247)),
            self.pattern1((2, 172, 207), (5, 46, 250)),
            self.pattern1((56, 25, 252), (97, 184, 255)),
            self.pattern2((0, 0, 200), 12),
            self.pattern2((0, 10, 255), 8),
            self.pattern2((10, 20, 200), 15),
            self.pattern3((10, 10, 255), 10),
            self.pattern3((64, 229, 247), 11),
            self.pattern3((22, 83, 102), 15),
            self.pattern3((0, 49, 133), 16),
            self.pattern3((47, 0, 255), 9),
            self.pattern3((0, 26, 74), 12),
            self.pattern3((20, 26, 74), 15)
        ]

        self.black_hole_patterns = [
            self.pattern3((127, 5, 29), 10),
            self.pattern3((123, 32, 47), 11),
            self.pattern3((15, 3, 5), 15),
            self.pattern3((19, 0, 3), 16),
            self.pattern3((127, 0, 42), 9),
            self.pattern3((11, 0, 2), 12)
        ]

    @staticmethod
    def hsv_to_rgb(h, s, v):
        if s == 0:
            return (v, v, v)

        h = h % 256
        region = h // 43
        remainder = (h - (region * 43)) * 6

        p = (v * (255 - s)) >> 8
        q = (v * (255 - ((s * remainder) >> 8))) >> 8
        t = (v * (255 - ((s * (255 - remainder)) >> 8))) >> 8

        if region == 0:
            return (v, t, p)
        if region == 1:
            return (q, v, p)
        if region == 2:
            return (p, v, t)
        if region == 3:
            return (p, q, v)
        if region == 4:
            return (t, p, v)
        return (v, p, q)

    # ============================================================
    # DYNAMIC WORMHOLE
    # ============================================================

    def start_dynamic_wormhole(self):
        self.wormhole_start_time = int(time.time() * 1000)
        self.last_random_ms = self.wormhole_start_time

        self.wormhole_array = []
        for _ in range(self.tot_leds):
            self.wormhole_array.append([0, 255, 1, 0])

    def stop_dynamic_wormhole(self):
        self.wormhole_array = None
        self.wormhole_start_time = None
        self.last_random_ms = 0

    def dynamic_wormhole_step(self):
        if self.wormhole_array is None or self.wormhole_start_time is None:
            self.start_dynamic_wormhole()

        now_ms = int(time.time() * 1000)
        wormhole_duration = now_ms - self.wormhole_start_time

        if wormhole_duration < 1700:
            wormhole_brightness = int((wormhole_duration / 1700.0) * 210)
            if wormhole_brightness > 210:
                wormhole_brightness = 210

            pattern = []
            for _ in range(self.tot_leds):
                pattern.append((wormhole_brightness, wormhole_brightness, wormhole_brightness))
            return pattern

        if now_ms - self.last_random_ms >= 30:
            self.last_random_ms = now_ms

            random_led = random.randint(0, self.tot_leds - 1)

            random_pick = random.randint(0, 99)
            if random_pick < 50:
                random_color = 100
            elif random_pick < 85:
                random_color = 130
            else:
                random_color = 160

            if self.wormhole_array[random_led][0] == 0:
                self.wormhole_array[random_led][0] = 1
                self.wormhole_array[random_led][1] = 0
                self.wormhole_array[random_led][2] = 1
                self.wormhole_array[random_led][3] = random_color

        pattern = []

        for i in range(self.tot_leds):
            if self.wormhole_array[i][0] == 1:
                self.wormhole_array[i][1] = self.wormhole_array[i][1] + (8 * self.wormhole_array[i][2])

                if self.wormhole_array[i][1] >= 255:
                    self.wormhole_array[i][1] = 255
                    self.wormhole_array[i][2] = -1

                if self.wormhole_array[i][1] <= 0:
                    self.wormhole_array[i][0] = 0
                    self.wormhole_array[i][1] = 0
                    self.wormhole_array[i][2] = 1
                    pattern.append((0, 0, 0))
                    continue

                brightness = self.wormhole_array[i][1]

                if self.wormhole_array[i][3] == 100:
                    pattern.append((brightness, brightness, brightness))
                else:
                    pattern.append(self.hsv_to_rgb(self.wormhole_array[i][3], 255, brightness))
            else:
                pattern.append((0, 0, 0))

        return pattern

    # ============================================================
    # DYNAMIC BLACK HOLE
    # ============================================================

    def start_dynamic_black_hole(self):
        self.wormhole_start_time = int(time.time() * 1000)
        self.last_random_ms = self.wormhole_start_time

        self.wormhole_array = []
        for _ in range(self.tot_leds):
            self.wormhole_array.append([0, 0, 1, 0])

    def stop_dynamic_black_hole(self):
        self.wormhole_array = None
        self.wormhole_start_time = None
        self.last_random_ms = 0

    def dynamic_black_hole_step(self):
        if self.wormhole_array is None or self.wormhole_start_time is None:
            self.start_dynamic_black_hole()

        now_ms = int(time.time() * 1000)
        wormhole_duration = now_ms - self.wormhole_start_time

        black_hole_colors = [
            (127, 5, 29),
            (123, 32, 47),
            (80, 0, 25),
            (50, 0, 12),
            (160, 0, 42),
            (35, 0, 5)
        ]

        if wormhole_duration < 1700:
            ramp = int((wormhole_duration / 1700.0) * 100)
            if ramp > 100:
                ramp = 100

            pattern = []
            for _ in range(self.tot_leds):
                pattern.append((ramp, int(ramp * 0.03), int(ramp * 0.16)))
            return pattern

        if now_ms - self.last_random_ms >= 28:
            self.last_random_ms = now_ms

            random_led = random.randint(0, self.tot_leds - 1)
            random_color = random.randint(0, len(black_hole_colors) - 1)

            if self.wormhole_array[random_led][0] == 0:
                self.wormhole_array[random_led][0] = 1
                self.wormhole_array[random_led][1] = 0
                self.wormhole_array[random_led][2] = 1
                self.wormhole_array[random_led][3] = random_color

        pattern = []

        for i in range(self.tot_leds):
            if self.wormhole_array[i][0] == 1:
                self.wormhole_array[i][1] += 6 * self.wormhole_array[i][2]

                if self.wormhole_array[i][1] >= 190:
                    self.wormhole_array[i][1] = 190
                    self.wormhole_array[i][2] = -1

                if self.wormhole_array[i][1] <= 0:
                    self.wormhole_array[i][0] = 0
                    self.wormhole_array[i][1] = 0
                    self.wormhole_array[i][2] = 1
                    pattern.append((0, 0, 0))
                    continue

                brightness = self.wormhole_array[i][1]
                base_color = black_hole_colors[self.wormhole_array[i][3]]

                red = int((base_color[0] * brightness) / 255)
                green = int((base_color[1] * brightness) / 255)
                blue = int((base_color[2] * brightness) / 255)

                pattern.append((red, green, blue))
            else:
                pattern.append((0, 0, 0))

        return pattern