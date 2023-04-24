import pygame
from engine.constants import X, Y, FIT, FILL, STRETCH


class Screen:

    #
    # ===============================================================
    # ======================== INITIALIZATION =======================
    # ===============================================================
    #

    def __init__(self, engine, resolution=(800, 600), fill_mode=FIT):
        self.engine = engine
        self.resolution: tuple[int, int] = resolution
        self.fill_mode: int = fill_mode
        self.color: tuple[int, int, int] = (255, 255, 255)

        self.window_position = (0, 0)
        self.scale = (1, 1)

        self.surface = None

    def initialize(self):
        self.surface = self.engine.core.surface.Surface(self.resolution)

    #
    # ===============================================================
    # ======================== GETTERS/SETTERS ======================
    # ===============================================================
    #

    def set_resolution(self, resolution):
        if type(resolution) is not tuple:
            raise TypeError("Resolution must be a tuple of two integers.")

        if resolution[X] <= 0 or resolution[Y] <= 0:
            raise ValueError("Resolution must be greater than 0.")

        self.resolution = resolution

    def set_fill_mode(self, fill_mode):
        if self.engine.is_running():
            raise RuntimeError("Cannot change fill mode while the game is running.")

        if fill_mode not in [FIT, FILL, STRETCH]:
            raise ValueError("Invalid fill mode.")

        self.fill_mode = fill_mode

    def set_color(self, color):
        if type(color) is not tuple:
            raise TypeError("Color must be a tuple of three integers.")

        self.color = color

    def get_width(self) -> int:
        return self.resolution[X]

    def get_height(self) -> int:
        return self.resolution[Y]

    def get_scale(self) -> tuple[int, int]:
        return self.scale

    #
    # ===============================================================
    # ======================== CLASS METHODS ========================
    # ===============================================================
    #

    def draw(self):
        window_resolution = self.engine.window.get_resolution()

        # center the blit x and y coordinates

        if self.fill_mode == FIT:
            scale_x = min(window_resolution[X] / self.resolution[X], window_resolution[Y] / self.resolution[Y])
            scale_y = scale_x
        elif self.fill_mode == FILL:
            scale_x = max(window_resolution[X] / self.resolution[X], window_resolution[Y] / self.resolution[Y])
            scale_y = scale_x
        elif self.fill_mode == STRETCH:
            scale_x = window_resolution[X] / self.resolution[X]
            scale_y = window_resolution[Y] / self.resolution[Y]
        else:
            raise ValueError("Invalid fill mode.")

        # scale the blit x and y coordinates
        center = window_resolution[X] / 2, window_resolution[Y] / 2
        top_corner = (center[X] - (self.resolution[X] * scale_x) / 2, center[Y] - (self.resolution[Y] * scale_y) / 2)
        width, height = self.resolution[X] * scale_x, self.resolution[Y] * scale_y

        self.window_position, self.scale = top_corner, (scale_x, scale_y)

        self.engine.window.surface.blit(
            pygame.transform.scale(self.surface, (int(self.resolution[X] * scale_x), int(self.resolution[Y] * scale_y))),
            (top_corner[X], top_corner[Y])
        )

    def clear(self):
        self.surface.fill(self.color)

    def add(self, entity):
        entity.draw(self.surface)

    def window_position_to_screen_position(self, position):
        x, y = position[X] - self.window_position[X], position[Y] - self.window_position[Y]
        x, y = x / self.scale[X], y / self.scale[Y]
        return round(x, 3), round(y, 3)