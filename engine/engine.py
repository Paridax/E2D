import pygame
import math
from engine.elements.screen import Screen
from engine.elements.window import Window
from engine.elements.inputs import Inputs
from engine.elements.console import Console
from engine.elements.commands import Commands
from engine.constants import *
from time import time
import os
import signal


def hex_to_rgb(hex_val):
    hex_val = hex_val.lstrip('#')
    hlen = len(hex_val)
    return tuple(int(hex[i:i + hlen // 3], 16) for i in range(0, hlen, hlen // 3))


class PyEngine:

    #
    # ===============================================================
    # ======================== INITIALIZATION =======================
    # ===============================================================
    #

    def __init__(self):
        self.core = pygame

        os.system("cls" if os.name == "nt" else "clear")

        # Private variables, set and accessed through methods
        self.running = False
        self.paused = False
        self.framerate = 60
        self.ms_per_frame = []
        self.resolution: tuple[int, int] = (800, 600)
        self.timer_reset_time = 0
        self.time_pause_started = 0
        self.timer_paused_time = 0

        self.start_time = 0
        self.frame_count = 0

        self.target_delta_time = max(math.floor(1000 / self.framerate), 0)
        self.delta = 0
        self.last_delta = 0

        self.pre_processing_time = 0
        self.processing_time = 0

        # Elements of the engine, in their own classes
        self.screen = Screen(self)
        self.window = Window(self)
        self.inputs = Inputs(self)
        self.console = Console(self)
        self.commands = Commands(self)

        self.broadcasts = [self]
        self.entities = {}

        self.__debug = False

    #
    # ===============================================================
    # ======================== GETTERS/SETTERS ======================
    # ===============================================================
    #

    def get_frame_count(self) -> int:
        return self.frame_count

    def get_target_time(self):
        # find the time that it is currently supposed to be by getting number of frames that have passed
        # and multiplying that by the target delta time
        return self.target_delta_time * self.get_frame_count()

    def get_framerate(self):
        if len(self.ms_per_frame) == 0:
            return 0

        avg_ms_per_frame = sum(self.ms_per_frame) / len(self.ms_per_frame)

        if avg_ms_per_frame == 0:
            return float("inf")

        return round(1000 / avg_ms_per_frame)

    def add_to_average_ms_per_frame(self, ms):
        if len(self.ms_per_frame) >= 10:
            self.ms_per_frame.pop(0)
        self.ms_per_frame.append(ms)

    def set_framerate(self, framerate):
        if self.is_running():
            raise RuntimeError("Cannot set framerate while the engine is running.")
        if self.framerate <= 0:
            raise ValueError("Framerate must be greater than 0.")

        self.framerate = framerate
        self.target_delta_time = max(math.floor(1000 / self.framerate), 0)

    def is_paused(self) -> bool:
        return self.paused

    def is_running(self) -> bool:
        return self.running

    def is_exited(self) -> bool:
        # Check if any of the event types are quit events
        if self.core.QUIT in [event.type for event in self.core.event.get()]:
            return True
        return False

    def get_timer_time(self):  # Milliseconds
        currently_paused_time = 0
        if self.time_pause_started is not None:
            currently_paused_time = self.get_system_time() - self.time_pause_started
        return self.get_system_time() - self.timer_reset_time - self.timer_paused_time - currently_paused_time

    def get_time(self):  # Milliseconds
        return self.get_system_time() - self.start_time

    @staticmethod
    def get_system_time():
        return time() * 1000

    def get_delta_time(self):
        return self.delta

    def set_processing_time(self):
        self.processing_time = self.get_system_time() - self.pre_processing_time

    def get_processing_time(self):
        return self.processing_time

    def enable_debug_mode(self):
        self.__debug = True

    def disable_debug_mode(self):
        self.__debug = False

    def is_debug_mode_enabled(self):
        return self.__debug

    #
    # ===============================================================
    # ======================== CLASS METHODS ========================
    # ===============================================================
    #

    def pause(self):
        if not self.is_running():
            raise Exception("Cannot pause the engine if it is not running.")
        elif self.is_paused():
            raise Exception("Cannot pause the engine if it is already paused.")

        self.paused = True
        self.time_pause_started = self.get_system_time()

    def unpause(self):
        if not self.is_running():
            raise Exception("Cannot unpause the engine if it is not running.")
        elif not self.is_paused():
            raise Exception("Cannot unpause the engine if it is not paused.")

        self.paused = False
        self.timer_paused_time += self.get_system_time() - self.time_pause_started
        self.time_pause_started = None

    def add_listener(self, listener):
        self.broadcasts.append(listener)

    def broadcast(self, message):
        for broadcast in self.broadcasts:
            broadcast.broadcast_recieved(message)

    def reset_delta(self):
        self.delta = self.get_system_time() - self.last_delta
        self.last_delta = self.get_system_time()

    def wait_for_next_frame(self):
        self.set_processing_time()

        while self.get_time() < self.get_target_time():
            # Check if the game has been exited
            if self.is_exited():
                self.quit()
            self.window.update()

            self.interframe()

        self.frame_count += 1
        # Calculate the framerate
        self.add_to_average_ms_per_frame(self.get_delta_time())
        self.reset_delta()

    def reset_timer(self):
        self.timer_reset_time = self.get_system_time()

    def start(self):
        print(f"Starting {self.window.get_title()}...")

        self.core.init()
        self.console.clear()
        self.running = True
        self.reset_timer()
        self.reset_delta()
        self.reset()

        self.initialize_entities()

        self.window.initialize()
        self.screen.initialize()
        self.console.initialize()
        self.commands.initialize()

        self.start_time = self.get_system_time()

        self.run()

    def quit(self):
        # Handle any closing events here
        self.console.quit()
        self.core.display.quit()
        exit()

    def pre_update(self):
        self.pre_processing_time = self.get_system_time()
        if self.is_exited():
            self.quit()

    def draw_frame(self):
        self.core.display.flip()

    def add_entity(self, entity):
        self.entities[entity.name] = entity

    def get_entity(self, name):
        return self.entities.get(name)

    def remove_entity(self, name):
        self.entities.pop(name)

    def initialize_entities(self):
        for entity in self.entities.items():
            entity[1].initialize()

    def reset_entities(self):
        for entity in self.entities.items():
            entity[1].reset()

    def draw_entities(self):
        for entity in self.entities.items():
            if entity[1].is_visible():
                entity[1].draw(self.screen.surface)

    def update_entities(self):
        for entity in self.entities.items():
            if entity[1].is_visible():
                entity[1].update(self.delta)

    def stop_running(self):
        self.running = False

    def run(self):
        try:
            while self.is_running():
                self.pre_update()

                self.window.update()
                if not self.is_paused():
                    self.update()

                self.draw()

                if self.is_debug_mode_enabled():
                    self.debug()

                self.screen.draw()

                self.draw_frame()
                self.wait_for_next_frame()
        except Exception as e:
            self.console.send("An error occurred while running the game.")
            self.console.send(e)
        except KeyboardInterrupt:
            self.console.send("Keyboard interrupt detected. Quitting...")

        self.quit()

    #
    # =====================================================================
    # ======================== OVERRIDABLE METHODS ========================
    # =====================================================================
    #

    def interframe(self):
        # This method will run constantly between frames
        pass

    def reset(self):
        # Override this method to reset the game
        pass

    def update(self):
        # Override this method to update the game
        pass

    def draw(self):
        # Override this method to draw the game
        pass

    def broadcast_recieved(self, message):
        # Override this method to handle broadcast messages
        pass

    def debug(self):
        # Override this method to handle debug mode actions
        pass