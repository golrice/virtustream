import time
from signals import Signals

class TTS():
    def __init__(self, sg: Signals):
        self._signals = sg
        self._stream = None

        self._signals._tts_ready = True
    
    def play(self, message):
        if not message.strip():
            return

        self._signals._AI_speaking = True
        self._signals.sio_queue.put(("current_message", message))
        # 语音播放 steam ... play or something else
        print(f"simulating tts... I am talking...")
        self._signals._AI_speaking = False

    def stop(self):
        self._stream.stop()
        self._signals._AI_speaking = False

    def audio_started(self):
        self._signals._AI_speaking = True

    def audio_ended(self):
        self._signals._last_message_time = time.time()
        self._signals._AI_speaking = False