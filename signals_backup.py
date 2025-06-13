import logging
import queue
from typing import Dict, List

class Signals():
    def __init__(self, logger: logging.Logger):
        self._logger = logger

        self._tts_ready = False
        self._stt_ready = False

        self._human_speaking = False
        self._AI_speaking = False
        self._AI_thinking = False
        self._last_message_time = 0.0
        self._new_message = False # 人已经读了某些话
        self._recent_messages = []
        self._history : List[Dict[str, str]]= []
        self._AI_expres = "初始" #模型表情

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

    @property
    def human_speaking(self):
        return self._human_speaking

    @human_speaking.setter
    def human_speaking(self, value):
        self._human_speaking = value
        self.sio_queue.put(('human_speaking', value))
        if value:
            self._logger.info("SIGNALS: Human Talking Start")
        else:
            self._logger.info("SIGNALS: Human Talking Stop")
    
    @property
    def AI_expres(self):
        return self._AI_expres
    
    @AI_expres.setter
    def AI_expres(self, value):
        self._AI_expres = value


    @property
    def AI_speaking(self):
        return self._AI_speaking

    @AI_speaking.setter
    def AI_speaking(self, value):
        self._AI_speaking = value
        self.sio_queue.put(('AI_speaking', value))
        if value:
            self._logger.info("SIGNALS: AI Talking Start")
        else:
            self._logger.info("SIGNALS: AI Talking Stop")
    
    @property
    def AI_thinking(self):
        return self._AI_thinking

    @AI_thinking.setter
    def AI_thinking(self, value):
        self._AI_thinking = value
        self.sio_queue.put(('AI_thinking', value))
        if value:
            self._logger.info("SIGNALS: AI Thinking Start")
        else:
            self._logger.info("SIGNALS: AI Thinking Stop")
    
    @property
    def last_message_time(self):
        return self._last_message_time

    @last_message_time.setter
    def last_message_time(self, value):
        self._last_message_time = value

    @property
    def new_message(self):
        return self._new_message

    @new_message.setter
    def new_message(self, value):
        self._new_message = value
        if value:
            self._logger.info("SIGNALS: New Message")

    @property
    def tts_ready(self):
        return self._tts_ready

    @tts_ready.setter
    def tts_ready(self, value):
        self._tts_ready = value

    @property
    def stt_ready(self):
        return self._stt_ready

    @stt_ready.setter
    def stt_ready(self, value):
        self._stt_ready = value