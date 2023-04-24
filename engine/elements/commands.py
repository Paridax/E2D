FUNCTION = 0
DESCRIPTION = 1
TYPE = 2

class Commands:

    #
    # ===============================================================
    # ========================= INITIALIZATION ======================
    # ===============================================================
    #

    def __init__(self, engine):
        self.engine = engine
        self.console = self.engine.console

        self.commands = {}

    def initialize(self):
        self.register("help", self.help, "Prints this help screen.")
        self.register("framerate", self.print_framerate, "Prints the current framerate.")
        self.register("echo", self.echo, "Prints the arguments.")
        self.register("timer", self.print_timer_time, "Prints the current timer time.")
        self.register(["quit", "stop"], self.quit, "Quits the engine.")
        self.register("pause", self.pause, "Pauses the engine.")
        self.register(["resume", "unpause"], self.resume, "Resumes the engine.")
        self.register("debug", self.debug, "Toggles debug mode.")
        self.register("clear", self.clear, "Clears the console.")
        self.register("reset", self.reset, "Resets the engine.")

    #
    # ===============================================================
    # ========================= CLASS METHODS =======================
    # ===============================================================
    #

    def register(self, command, function, description=""):
        command_type = None

        # if there are aliases, register them all
        if type(command) in [list, tuple]:
            for c in command:
                self.register(c, function, description)
            return
        if not type(command) == str:
            raise Exception(f"Error processing {str(command)}: Command must be a string or list of strings")
        if not callable(function):
            raise Exception(f"Error processing {str(command)}: Function must be callable")
        if not type(description) == str:
            raise Exception(f"Error processing {str(command)}: Description must be a string")
        # check if the function's first argument is a self reference
        if function.__code__.co_varnames[0] == "self":
            if not (1 <= function.__code__.co_argcount <= 4):
                raise Exception(f"Error processing {str(command)}: Command functions must have 0 to 3 arguments (send, args, engine)")
            command_type = function.__code__.co_argcount - 1
        else:
            if not (0 <= function.__code__.co_argcount <= 3):
                raise Exception(f"Error processing {str(command)}: Command functions must have 0 to 3 arguments (send, args, engine)")
            command_type = function.__code__.co_argcount

        if command.lower() in self.commands:
            raise Exception(f"Error processing {str(command)}: Command already registered")

        self.commands[command.lower()] = (function, description, command_type)

    def execute(self, string):
        command = string.split(" ")[0].lower()
        args = string.split(" ")[1:]

        if command in self.commands:
            try:
                if self.commands[command][TYPE] == 3:
                    self.commands[command][FUNCTION](self.console.send, args, self.engine)
                elif self.commands[command][TYPE] == 2:
                    self.commands[command][FUNCTION](self.console.send, args)
                elif self.commands[command][TYPE] == 1:
                    self.commands[command][FUNCTION](self.console.send)
                else:
                    self.commands[command][FUNCTION]()
            except Exception as e:
                self.console.send(f"Error while executing command: {e}")
        else:
            self.console.send(f"Unknown command: {command}")

    #
    # ===============================================================
    # ======================== COMMAND FUNCTIONS ====================
    # ===============================================================
    #

    def help(self, send, args, engine):
        if len(args) > 0:
            if args[0] in self.commands:
                send(f"Help page for {args[0]}")
                send(f"{args[0].ljust(10, ' ')}  {self.commands[args[0]][DESCRIPTION]}")
            else:
                send(f"Unknown command: {args[0]}")
            return

        send(f"Help page for {engine.window.get_title()}")
        for command in self.commands:
            send(f"{command.ljust(10, ' ')}  {self.commands[command][DESCRIPTION]}")

    @staticmethod
    def print_framerate(send, args, engine):
        send(f"Current framerate: {engine.get_framerate()}")

    @staticmethod
    def echo(send, args):
        send(" ".join(args))

    @staticmethod
    def print_timer_time(send, args, engine):
        send(f"Game elapsed time (seconds): {engine.get_timer_time() / 1000:.2f}")

    @staticmethod
    def quit(send, args, engine):
        send("Exiting...")
        engine.stop_running()

    @staticmethod
    def pause(send, args, engine):
        send("Pausing...")
        engine.pause()

    @staticmethod
    def resume(send, args, engine):
        send("Resuming...")
        engine.unpause()

    @staticmethod
    def debug(send, args, engine):
        if engine.is_debug_mode_enabled():
            send("Debug mode disabled")
            engine.disable_debug_mode()
        else:
            send("Debug mode enabled")
            engine.enable_debug_mode()

    @staticmethod
    def clear(send, args, engine):
        engine.console.clear()

    @staticmethod
    def reset(send, args, engine):
        engine.reset()