import pygame
from engine.constants import X, Y


class Window:

    #
    # ===============================================================
    # ======================== INITIALIZATION =======================
    # ===============================================================
    #

    def __init__(self, engine):
        self.engine = engine
        self.resolution: tuple[int, int] = (800, 600)
        self.locked_resolution = self.resolution
        self.window_resizable = True
        self.title = "PyEngine Window"
        self.aspect_ratio = None
        self.surface = None

    def initialize(self):
        self.engine.core.display.set_caption(self.title)
        self.surface = self.engine.core.display.set_mode(self.resolution, pygame.RESIZABLE if self.window_resizable else 0)
        self.resize(self.resolution)

    #
    # ===============================================================
    # ======================== GETTERS/SETTERS ======================
    # ===============================================================
    #

    def set_resolution(self, resolution):
        if not self.engine.is_running():
            self.locked_resolution = resolution

        if type(resolution) is not tuple:
            raise TypeError("Resolution must be a tuple.")

        if resolution[X] <= 0 or resolution[Y] <= 0:
            raise ValueError("Resolution must be greater than 0.")

        self.resolution = resolution
        self.resize(self.resolution)

    def get_resolution(self):
        if self.engine.core.display.get_window_size() != self.resolution:
            self.resolution = self.engine.core.display.get_window_size()

        return self.resolution

    def set_title(self, title):
        self.title = str(title)
        self.engine.core.display.set_caption(self.title)

    def get_title(self):
        return self.title

    def set_aspect_ratio(self, aspect_ratio):
        if aspect_ratio is not None and type(aspect_ratio) not in [int, float]:
            raise TypeError("Aspect ratio must be a float or int.")

        self.aspect_ratio = aspect_ratio
        self.lock_aspect_ratio(self.aspect_ratio)

    def set_resizable(self, resizable):
        if type(resizable) is not bool:
            raise TypeError("Window resizable must be a boolean.")

        self.window_resizable = resizable
        self.resize(self.resolution)

    #
    # ===============================================================
    # ======================== CLASS METHODS ========================
    # ===============================================================
    #

    def resize(self, resolution):
        self.resolution = resolution

        if not self.window_resizable:
            self.resolution = self.locked_resolution
        else:
            self.lock_aspect_ratio(self.aspect_ratio)

        self.engine.core.display.set_mode(self.resolution, pygame.RESIZABLE if self.window_resizable else 0)

    def lock_aspect_ratio(self, aspect_ratio):
        # Check if the aspect ratio is correct
        if aspect_ratio is not None and self.resolution[X] / self.resolution[Y] != aspect_ratio:
            # Calculate the new resolution
            if self.resolution[X] / self.resolution[Y] > aspect_ratio:
                # Width is too big
                self.resolution = (int(self.resolution[Y] * aspect_ratio), self.resolution[Y])
            else:
                # Height is too big
                self.resolution = (self.resolution[X], int(self.resolution[X] / aspect_ratio))

            self.resize(self.resolution)

    def update(self):
        if self.engine.core.display.get_window_size() != self.resolution:
            self.resolution = self.engine.core.display.get_window_size()

        self.lock_aspect_ratio(self.aspect_ratio)