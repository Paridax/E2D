from engine.engine import PyEngine, FIT
from src.player import Player


def cmd_hi(send, args):
    send("Hi!", " ".join(args))


def cmd_multiply(send, args):
    if len(args) != 2:
        send("Invalid number of arguments")
        return
    try:
        send(float(args[0]) * float(args[1]))
    except ValueError:
        send("Invalid arguments")


class Game(PyEngine):
    def __init__(self, no_console=False):
        super().__init__()
        self.set_framerate(60)
        self.window.set_resolution((1280, 720))
        self.screen.set_resolution((960, 720))
        self.window.set_title("Trevor's Epic Game")
        self.screen.set_fill_mode(FIT)

        self.enable_debug_mode()

        if no_console:
            self.console.disable()

        Player(self)

        self.commands.register("hi", cmd_hi, "Prints hi")
        self.commands.register("multiply", cmd_multiply, "Multiplies two numbers")

        self.start()

    def reset(self):
        self.reset_entities()

    def update(self):
        self.update_entities()

        if self.inputs.is_key_pressed("r"):
            self.reset()

    def draw(self):
        self.screen.clear()
        self.draw_entities()

    def debug(self):
        # draw the framerate in the top left using pygame as self.core
        mouse_pos = self.inputs.get_mouse_pos()
        mouse_pos_text = self.core.font.SysFont("Arial", 20).render(str(mouse_pos), True, (0, 0, 0))
        fps = self.core.font.SysFont("Arial", 20).render(str(self.get_framerate()), True, (0, 0, 0))

        # draw red circle at mouse position
        self.core.draw.circle(self.screen.surface, (255, 0, 0), mouse_pos, 5)

        self.screen.surface.blit(mouse_pos_text, (0, 0))
        self.screen.surface.blit(fps, (0, 20))