from modules.injection import Injection
from signals import Signals
import asyncio

class Module:
    def __init__(self, signals: Signals, enable: bool):
        self._signals = signals
        self._enable = enable

        self.prompt_injection = Injection("", -1)

    def init_event_loop(self):
        asyncio.run(self.run())
    
    def get_prompt_injection(self):
        return self.prompt_injection
    
    def cleanup(self):
        pass

    async def run(self):
        pass

