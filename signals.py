import queue
from typing import Dict, List

class Signals():
    def __init__(self):
        self._tts_ready = False
        self._stt_ready = False

        self._human_speaking = False
        self._AI_speaking = False
        self._AI_thinking = False
        self._last_message_time = 0.0
        self._new_message = False # 人已经读了某些话
        self._recent_messages = []
        self._history : List[Dict[str, str]]= []

        self._terminate = False

        self.sio_queue = queue.SimpleQueue()
    
    @property
    def terminate(self):
        return self._terminate
    
    @terminate.setter
    def terminate(self, value):
        self._terminate = value

    @property
    def recentMessges(self):
        return self._recent_messages
    
    @recentMessges.setter
    def recentMessages(self, value):
        self._recent_messages = value
        self.sio_queue.put(("recent_messages", value))
