import threading
import os
from time import sleep, localtime
import msvcrt


class Console:

    #
    # ===============================================================
    # ======================== INITIALIZATION =======================
    # ===============================================================
    #

    def __init__(self, engine):
        self.engine = engine

        self.console_thread = None
        self._running = False
        self.parallel_input = None

        self._disabled = False

    def initialize(self):
        if self._disabled:
            return

        os.system(f"title {self.engine.window.get_title()}")

        self.clear()
        self.parallel_input = ParallelInput(self)
        self.console_thread = threading.Thread(target=self.run)
        self.console_thread.daemon = True
        self.console_thread.start()

    #
    # ===============================================================
    # ======================== CONSOLE FUNCTIONS ====================
    # ===============================================================
    #

    def disable(self):
        if self.engine.is_running():
            raise Exception("Cannot disable the console if the engine is running.")
        self._disabled = True

    def handle_console_string(self, command_string):
        self.send(f"> {command_string}", time=False)
        self.engine.commands.execute(command_string)

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        self.clear_line(self.get_raw_data(), end="")

    @staticmethod
    def clear_line(text="", end="", flush=False):
        print("\r" + " " * 100 + "\r" + text, end=end, flush=flush)

    def quit(self):
        self.stop()
        self.parallel_input.quit()

    def is_running(self):
        return self._running

    def stop(self):
        self._running = False
        self.console_thread.join()

    @staticmethod
    def get_time():
        return f"{str(localtime().tm_hour).rjust(2, '0')}:{str(localtime().tm_min).rjust(2, '0')}:{str(localtime().tm_sec).rjust(2, '0')}"

    def get_raw_data(self):
        try:
            raw = self.parallel_input.get_raw()
        except AttributeError:
            raw = ""
        return raw

    def run(self):
        self.send(self.engine.window.get_title())
        self.send("Type 'help' for a list of commands.")

        self._running = True
        while self.is_running():
            self.parallel_input.clear()
            while not self.parallel_input.is_finished():
                if not self.is_running():
                    break
                sleep(0.2)
            sleep(0.2)

    def send(self, *args, time=True):
        raw = self.get_raw_data()
        if time:
            self.clear_line(f"[{self.get_time()}]: {' '.join(args)}\n{raw}", end="")
        else:
            self.clear_line(f"{' '.join(args)}\n{raw}", end="")


class ParallelInput:
    """
    This class is used to handle asynchronous input.
    It will spawn a thread and cancel it when asked.
    """
    def __init__(self, console, message="> "):
        self.console = console
        self._finished = False
        self.output = ""
        self._message = message
        self._kill = False

        self.previous_string = None
        self._thread = None

    def force_update(self):
        self.previous_string = None

    def is_finished(self):
        return self._finished

    def quit(self):
        self._kill = True
        # self._thread._stop()

    def clear(self):
        self.output = ""
        self._finished = False
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def get_output(self):
        return self.output

    def update_line(self):
        # erase only the current line
        if self._message + self.output == self.previous_string:
            return
        self.previous_string = self._message + self.output
        self.console.clear_line(self.previous_string, end="", flush=True)

    def get_raw(self):
        return self._message + self.output

    def _run(self):
        import msvcrt
        while not self._finished:
            if self._kill:
                return

            self.update_line()

            try:
                if msvcrt.kbhit():
                    char = msvcrt.getch().decode()
                    if char == "\r":
                        if self.output.strip() != "":
                            self._finished = True
                    elif char == "\x08":
                        self.output = self.output[:-1]
                    else:
                        self.output = (self.output or "") + char
            except UnicodeDecodeError:
                pass
            sleep(0.01)

        if not self._kill:
            self._finished = True
            output = self.output.strip()
            self.output = ""
            self.console.handle_console_string(output)

    def __str__(self):
        return self.output if self.output is not None else ""