from signals import Signals
from tts import TTS
from LLM.LLMState import LLMState

class TextLLMWrapper():
    def __init__(self, signals: Signals, tts: TTS, llmState: LLMState):
        self._signals = signals
        self._tts = tts
        self._llmState = llmState
