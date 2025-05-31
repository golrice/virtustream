import time
from signals import Signals

class STT():
    def __init__(self, sg: Signals):
        self._signals = sg

    def speaking(self):
        return False

    def listen_loop(self):
        while not self._signals.terminate:
            # 监听麦克风/检测某个按键开始语音
            if self.speaking():
                self._signals._human_speaking = True
                content = ""
                print("stt...")
                self._signals._human_speaking = False
            time.sleep(0.5)