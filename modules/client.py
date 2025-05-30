import asyncio
import logging

import socketio
from constant import IUSER, MAX_MESSAGES_LEN
from modules.injection import Injection
from signals import Signals
from modules.module import Module

class Client(Module):
    def __init__(self, signals: Signals, enable: bool, logger: logging.Logger):
        super().__init__(signals, enable)

        self._logger = logger

        self._io = socketio.AsyncClient()

        self.prompt_injection = Injection("", IUSER)

        @self._io.event
        async def chat_message(data):
            # 保持数据只有最多十条
            if len(self._signals.recentMessages) >= MAX_MESSAGES_LEN:
                self._signals.recentMessages.pop()

            self._signals.recentMessages.append(data)
            # 触发setter
            self._signals.recentMessages = self._signals.recentMessages
        @self._io.event
        async def connect():
            self._logger.info("SocketIO connected to server!")
        @self._io.event
        async def disconnect():
            self._logger.warning("SocketIO disconnected from server!")
    
    # 为llm提供prompt注入的信息
    def get_prompt_injection(self):
        if len(self._signals.recentMessages) > 0:
            output = "\nThese are recent messages:\n"
            for idx, message in enumerate(self._signals.recentMessages):
                output += f"{idx + 1}: {message}\n"

            output += "Pick the highest quality message with the most potential for an interesting answer and respond to them.\n"
            self.prompt_injection.text = output
        else:
            self.prompt_injection.text = ""
        return self.prompt_injection

    async def run(self):
        # 获取用户的输入并且通过signals传输到系统中
        await self._io.connect("http://localhost:8080")

        while not self._signals.terminate:
            await asyncio.sleep(0.5)

    def cleanup(self):
        self._signals.recentMessages = []
    
    @property
    def io(self):
        return self._io



