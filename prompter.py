import logging
import time
from typing import Dict

from LLM.textLLMWrapper import TextLLMWrapper
from constant import WAIT_TIME
from modules.module import Module
from signals import Signals

class Prompter():
    def __init__(self, sg: Signals, llm: TextLLMWrapper, logger: logging.Logger, modules: Dict[str, Module] = None):
        self._signals = sg
        self._llm = llm
        self._logger = logger
        if modules is None:
            self._modules = {}
        else:
            self._modules = modules

        self.system_ready = False
        self.timeSinceLast = 0

    def should_prompt(self):
        # 如果tts/stt没有准备好就不能启动
        if not self._signals._tts_ready or not self._signals._stt_ready:
            return False
        
        # 如果正在回答不能启动
        if self._signals._AI_thinking or self._signals._AI_speaking:
            return False

        # 上述条件都满足了

        # 如果有消息就可以启动
        if len(self._signals.recentMessages) > 0:
            return True

        if self.timeSinceLast > WAIT_TIME:
            return True
        
        return False
    
    def prompt_loop(self):
        self._logger.info("Prompt loop start")

        # 启动状态的初始化
        if self._signals._last_message_time == 0.0 or (not self._signals._tts_ready or not self._signals._stt_ready):
            self._signals._last_message_time = time.time()
            self.timeSinceLast = 0
        while not self._signals.terminate:
            self.timeSinceLast = time.time() - self._signals._last_message_time

            if self.should_prompt():
                self._llm.generate_response()
                self._signals._last_message_time = time.time()

            time.sleep(1)
