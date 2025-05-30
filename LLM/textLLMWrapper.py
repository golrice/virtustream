from copy import deepcopy
import time
from typing import Dict, List
from constant import AI_NAME, IHISTORY, ISYSTEM, IUSER, STOP_STRINGS, SYSTEM_PROMPT
from modules.injection import Injection
from modules.module import Module
from signals import Signals
from tts import TTS
from LLM.LLMState import LLMState

class TextLLMWrapper():
    def __init__(self, signals: Signals, tts: TTS, modules: Dict[str, Module]):
        self._signals = signals
        self._tts = tts

        if modules is None:
            self.modules = {}
        else:
            self.modules = modules
        
        # 加载一些本地的信息...
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
            
    # 聚合所有的prompt注入 包括所有外部模块
    def assemble_injectinos(self, injections: List[Injection]=None):
        if injections is None:
            injections = []
        
        for module in self.modules.values():
            injections.append(module.get_prompt_injection())
    
        for module in self.modules.values():
            module.cleanup()

        injections.sort(key=lambda x : x.priority)

        return "\n".join(x.text for x in injections if x.priority != -1)
    
    def generate_prompt(self):
        # 拷贝历史消息 防止更新过程出现冲突
        historys = deepcopy(self._signals._history)

        # 将历史消息转换成为字符串
        msg = "\n".join(f"{block['role']}: {block['content']}" for block in historys)

        # 生成prompt
        generation_prompt = AI_NAME + ": "

        # 拼接所有的prompt
        injections = [Injection(self.SYSTEM_PROMPT, ISYSTEM), Injection(msg, IHISTORY)]
        prompt = self.assemble_injectinos(injections) + generation_prompt

        return prompt
    
    # 后续发起llm请求的负载
    def prepare_payload(self):
        return {
            "mode": "instruct",
            "stream": True,
            "max_tokens": 200,
            "skip_special_tokens": False,  # Necessary for Llama 3
            "stop": STOP_STRINGS,
            "messages": [{
                "role": "user",
                "content": self.generate_prompt()
            }]
        }
    
    def generate_response(self):
        self._signals._AI_thinking = True
        self._signals._new_message = False

        payload = self.prepare_payload()

        # 发起请求...
        print(f"prompt: [{payload['messages'][0]['content']}]")
        AI_message = "我是Nico\n"

        print(f"AI_message = {AI_message}")
        self._signals._last_message_time = time.time()
        self._signals._AI_thinking = False

        self._signals._history.append({"role": AI_NAME, "content": AI_message})
        self._tts.play(AI_message)

