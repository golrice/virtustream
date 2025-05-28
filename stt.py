import time
from signals import Signals

class STT():
    def __init__(self, sg: Signals):
        self._signals = sg

    def listen_loop(self):
        while not self._signals.terminate:
            print("stt")
            time.sleep(0.5)