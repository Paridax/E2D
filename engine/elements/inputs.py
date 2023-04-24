import pygame
from engine.constants import X, Y, LEFT_BUTTON, MIDDLE_BUTTON, RIGHT_BUTTON


class Inputs:

    #
    # ===============================================================
    # ======================== INITIALIZATION =======================
    # ===============================================================
    #

    def __init__(self, engine):
        self.engine = engine
        self.mouse_position = (0, 0)
        self.mouse_pressed = (False, False, False)

    #
    # ===============================================================
    # ======================== GETTERS/SETTERS ======================
    # ===============================================================
    #

    def get_mouse_pos(self):
        return self.engine.screen.window_position_to_screen_position(pygame.mouse.get_pos())

    @staticmethod
    def is_key_pressed(key):
        if type(key) == str:
            if len(key) > 1:
                key = key.upper()
            key = getattr(pygame, "K_" + key)
        return pygame.key.get_pressed()[key]

    def is_mouse_pressed(self, button=LEFT_BUTTON):
        self.mouse_pressed = pygame.mouse.get_pressed(3)
        return self.mouse_pressed[button]

    #
    # ===============================================================
    # ======================== CLASS METHODS ========================
    # ===============================================================
    #
