from engine.constants import VISIBLE, HIDDEN


class Entity:

    #
    # ===============================================================
    # ======================== INITIALIZATION =======================
    # ===============================================================
    #

    def __init__(self, engine, name, x, y, width, height, color, alpha):
        self.engine = engine

        self.name: str = name

        self.x: float = x
        self.y: float = y
        self.width: int = width
        self.height: int = height
        self.rotation: int = 0
        self.color: tuple[int, int, int] = color
        self.alpha: int = alpha
        self.scale: float = 1.0

        # Private variables
        self.__visibility = VISIBLE

        self.engine.add_entity(self)

    #
    # ===============================================================
    # ======================== GETTERS/SETTERS ======================
    # ===============================================================
    #

    def get_name(self):
        return self.name

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def set_visibility(self, hidden):
        if hidden not in [VISIBLE, HIDDEN]:
            raise ValueError("Invalid visibility value")

        self.__visibility = hidden

    def get_visibility(self):
        return self.__visibility

    def is_visible(self):
        return self.__visibility == VISIBLE

    def is_hidden(self):
        return self.__visibility == HIDDEN

    #
    # ===============================================================
    # ======================== CLASS METHODS ========================
    # ===============================================================
    #

    def broadcast(self, message):
        self.engine.broadcast(message)

    def update(self, delta):
        """
        Override this method to update the object.
        For example, position could be updated with:
        self.x += 1
        :param delta: The time since the last frame
        :return:
        """
        pass

    def draw(self, surface):
        """
        Override this method to draw the object.
        For example, a rectangle would be drawn with:
        pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))
        :param surface:
        :return:
        """
        pass

    def initialize(self):
        pass

    def reset(self):
        pass

    def broadcast_recieved(self, message):
        pass