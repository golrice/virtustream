import time
from signals import Signals

class Prompter():
    def __init__(self, sg: Signals, llms: dict):
        self._signals = sg
        self._llms = llms

    def prompt_loop(self):
        while not self._signals.terminate:
            print("prompter")
            time.sleep(0.5)