from time import sleep, time
from datetime import timedelta
from pathlib import Path
import math

from wormhole_animation_manager import WormholeAnimationManager


class WormholeManager:
    """
    This class handles all things wormhole. It takes the stargate object as input.
    """
    def __init__(self, stargate):

        self.stargate = stargate
        self.log = stargate.log
        self.cfg = stargate.cfg
        self.audio = stargate.app.audio
        self.electronics = stargate.electronics

        self.pixels = self.electronics.get_wormhole_pixels()
        self.tot_leds = self.electronics.get_wormhole_pixel_count()
        self.animation_manager = WormholeAnimationManager(stargate)

        self.root_path = Path(__file__).parent.absolute()

        self.wormhole_max_time_default = self.cfg.get("wormhole_max_time_minutes") * 60
        self.wormhole_max_time_blackhole = self.cfg.get("wormhole_max_time_blackhole") * 60
        self.audio_play_random_clips = self.cfg.get("audio_play_random_clips")
        self.audio_clip_wait_time_default = self.cfg.get("audio_wormhole_active_quotes_interval")
        self.audio_clip_wait_time_blackhole = self.cfg.get("audio_clip_wait_time_blackhole")
        self.audio_wormhole_close_headstart = self.cfg.get("audio_wormhole_close_headstart")
        self.use_dynamic_wormhole = self.cfg.get("use_dynamic_wormhole")
        self.use_dynamic_wormhole_for_incoming = self.cfg.get("use_dynamic_wormhole_for_incoming")

        self.audio_clip_wait_time = self.audio_clip_wait_time_default
        self.wormhole_max_time = self.wormhole_max_time_default

        self.open_time = None

    def initialize_animation_manager(self):
        self.animation_manager.after_init(self)

    def open_wormhole(self):
        """
        Normal wormhole uses original kawoosh.
        Black hole skips white kawoosh.
        """
        self.audio.sound_start('wormhole_open')

        if not self.stargate.black_hole:
            self.animation_manager.animate_kawoosh()

    def close_wormhole(self):
        """
        Disengage wormhole.
        """

        def pattern_blue(number_of_leds):
            blue_pattern = []
            for index in range(number_of_leds):  # pylint: disable=unused-variable
                blue_pattern.append((81, 110, 158))
            return blue_pattern

        no_pattern = self.animation_manager.pattern_manager.pattern_off()

        self.stargate.wormhole_active = True
        self.animation_manager.fade_transition(pattern_blue(self.tot_leds))
        self.audio.sound_start('wormhole_close')
        sleep(self.audio_wormhole_close_headstart)
        self.animation_manager.fade_transition(no_pattern)

        self.animation_manager.pattern_manager.stop_dynamic_wormhole()

        self.stargate.wormhole_max_time = self.wormhole_max_time_default
        self.stargate.audio_clip_wait_time = self.audio_clip_wait_time_default
        self.stargate.manual_dynamic_override = None
        self.stargate.wormhole_active = False

    def get_time_remaining(self):
        if self.open_time:
            time_elapsed = time() - self.open_time
            return math.floor(self.wormhole_max_time - time_elapsed)
        return 0

    def establish_wormhole(self):
        """
        Main method that opens and maintains a wormhole.
        """

        # Runtime test override:
        # True  = force dynamic for this one test
        # False = force static for this one test
        # None  = use checkbox/config value
        manual_override = getattr(self.stargate, "manual_dynamic_override", None)

        incoming_dynamic_enabled = (
            self.stargate.wormhole_active == "incoming"
            and bool(self.cfg.get("use_dynamic_wormhole_for_incoming"))
        )

        if manual_override is True:
            self.use_dynamic_wormhole = True
        elif manual_override is False:
            self.use_dynamic_wormhole = False
        else:
            self.use_dynamic_wormhole = bool(self.cfg.get("use_dynamic_wormhole")) or incoming_dynamic_enabled

        self.log.log(
            f'Opening Wormhole! black_hole={self.stargate.black_hole}, dynamic={self.use_dynamic_wormhole}'
        )

        self.open_wormhole()
        self.audio.sound_start('wormhole_established')

        self.open_time = time()
        random_audio_start_time = self.open_time

        audio_group = "audio_clips"

        if self.stargate.black_hole:
            self.wormhole_max_time = self.wormhole_max_time_blackhole * 60
            self.audio_clip_wait_time = self.audio_clip_wait_time_blackhole
            audio_group = "audio_clips/black_hole"
        else:
            self.wormhole_max_time = self.wormhole_max_time_default
            self.audio_clip_wait_time = self.audio_clip_wait_time_default

        if self.use_dynamic_wormhole:
            if self.stargate.black_hole:
                self.animation_manager.pattern_manager.start_dynamic_black_hole()
            else:
                self.animation_manager.pattern_manager.start_dynamic_wormhole()

        while self.stargate.wormhole_active and self.get_time_remaining() > 0:

            if self.use_dynamic_wormhole:
                if self.stargate.black_hole:
                    dynamic_pattern = self.animation_manager.pattern_manager.dynamic_black_hole_step()
                else:
                    dynamic_pattern = self.animation_manager.pattern_manager.dynamic_wormhole_step()

                self.animation_manager.set_wormhole_pattern(dynamic_pattern)
                sleep(0.01)

            else:
                self.animation_manager.do_random_transitions(self.stargate.black_hole)

            if (
                self.audio_play_random_clips
                and self.stargate.wormhole_active
                and (time() - random_audio_start_time) > self.audio_clip_wait_time
            ):
                self.audio.play_random_clip(audio_group)
                random_audio_start_time = time()

        if self.get_time_remaining() < 1:
            if self.audio.random_clip_is_playing():
                self.audio.random_clip_wait_done()

            self.audio.play_random_clip("38min")
            self.audio.random_clip_wait_done()

        self.close_wormhole()

        if self.audio.is_playing('wormhole_established'):
            self.audio.sound_stop('wormhole_established')

        self.stargate.wormhole_active = False
        self.log.log(f'Disengaged Wormhole after {timedelta(seconds=int(time() - self.open_time))}')
        self.open_time = None
