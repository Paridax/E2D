from engine.elements.entity import Entity


class Player(Entity):
    def __init__(self, engine):
        super().__init__(engine, "Player", 0, 0, 50, 50, 0, 0)

        self.x_speed = 0
        self.y_speed = 0

        self.VELOCITY = 0.01
        self.FRICTION = 0.99
        self.JUMP_VELOCITY = 1.5
        self.GRAVITY = 5.0

        self.on_ground = False

    def initialize(self):
        self.engine.commands.register("player", self.cmd_player, "Allow you to control the player, such as position, speed, etc.")

        self.reset()

    def cmd_player(self, send, args):
        if len(args) == 0:
            send("Invalid number of arguments")
            return

        if args[0] == "reset" and len(args) == 1:
            self.reset()
        if args[0] == "pos" and len(args) == 1:
            send("Player position: ({}, {})".format(self.x, self.y))

        try:
            if args[0] == "set" and len(args) == 3:
                if args[1] == "x":
                    self.x = float(args[2])
                elif args[1] == "y":
                    self.y = float(args[2])
                elif args[1] == "y_vel":
                    self.y_speed = float(args[2])
                elif args[1] == "x_vel":
                    self.x_speed = float(args[2])
                else:
                    send("Invalid argument")
        except Exception:
            send("Couldn't set player position.\nMake sure your command looks like this: player set {x/y/x_vel/y_vel} {number}")

    def reset(self):
        self.x = self.engine.screen.get_width() / 2 - self.width / 2
        self.y = self.engine.screen.get_height() / 2 - self.height / 2
        self.x_speed = 0
        self.y_speed = 0

    def update(self, delta):
        if self.engine.inputs.is_key_pressed("a"):
            self.x_speed -= self.VELOCITY * delta
        if self.engine.inputs.is_key_pressed("d"):
            self.x_speed += self.VELOCITY * delta
        if self.engine.inputs.is_key_pressed("w") and self.on_ground:
            self.y_speed = -self.JUMP_VELOCITY
            self.engine.console.send("Player jumped!")

        self.x += self.x_speed * delta
        self.y += self.y_speed * delta

        self.x_speed *= self.FRICTION**delta

        self.limit(delta)

    def draw(self, surface):
        surface.fill((255, 0, 0), (self.x, self.y, self.width, self.height))

    def limit(self, delta):
        if self.y + self.height >= self.engine.screen.get_height():
            self.y = self.engine.screen.get_height() - self.height
            self.y_speed = 0
            self.on_ground = True
        else:
            self.y_speed += (self.GRAVITY / 1000) * delta
            self.on_ground = False

        if self.x + self.width >= self.engine.screen.get_width():
            self.x = self.engine.screen.get_width() - self.width
            self.x_speed = 0
        elif self.x <= 0:
            self.x = 0
            self.x_speed = 0