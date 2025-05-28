import queue

class Signals():
    def __init__(self):
        self._tts_ready = False
        self._stt_ready = False

        self._human_speaking = False
        self._AI_speaking = False
        self._AI_thinking = False
        self._last_message_time = 0.0
        self._new_message = False
        self._recentTwitchMessages = []
        self._history = []

        self._terminate = False

        self.sio_queue = queue.SimpleQueue()
    
    @property
    def terminate(self):
        return self._terminate
    
    @terminate.setter
    def terminate(self, value):
        self._terminate = value
