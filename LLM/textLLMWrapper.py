from copy import deepcopy
import time
from typing import Dict, List
from constant import IHISTORY, ISYSTEM, MODEL_NAME, SYSTEM_PROMPT
from modules.injection import Injection
from modules.module import Module
from signals import Signals
from tts import TTS
from openai import OpenAI
from dotenv import load_dotenv
import os
import re
from utils import get_logger

class TextLLMWrapper():
    def __init__(self, signals: Signals, tts: TTS, modules: Dict[str, Module]):
        self._signals = signals
        self._tts = tts

        if modules is None:
            self.modules = {}
        else:
            self.modules = modules
        
        self.model_name = MODEL_NAME

        # 加载一些本地的信息...
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        load_dotenv()
        self.client = OpenAI(api_key=os.getenv("LLM_API_KEY"), base_url="https://api.deepseek.com")

    # 聚合所有的prompt注入 包括所有外部模块
    def assemble_injections(self, injections: List[Injection]=None):
        if injections is None:
            injections = []
        
        for module in self.modules.values():
            injections.append(module.get_prompt_injection())
    
        for module in self.modules.values():
            module.cleanup()

        injections.sort(key=lambda x : x.priority)

        return [{"role": x.name, "content": x.text} for x in injections if x.priority != -1]
    
    def extract_emotion_and_text(self, message: str) -> tuple[str, str]:
        """提取文本中的表情和清理后的文本
        Args:
            message: 包含表情的原始文本，如：（高兴）"你好啊"
        Returns:
            tuple: (清理后的文本, 表情)，如：("你好啊", "高兴")
        """
        emotion = ""
        # 修改正则表达式以匹配中文括号
        pattern = r'[(（](.*?)[）)]'
        matches = re.findall(pattern, message)
        if matches:
            emotion = matches[0]  # 取第一个匹配的表情
        
        # 删除所有中文括号及其内容
        clean_text = re.sub(pattern, '', message).strip()
        
        # 如果清理后的文本以引号开头和结尾，去除引号
        clean_text = clean_text.strip('"')
        
        return clean_text, emotion

    def generate_prompt(self):
        # 拷贝历史消息 防止更新过程出现冲突
        historys = deepcopy(self._signals._history)

        # 将历史消息转换成为字符串
        msg = "\n".join(f"{block['role']}: {block['content']}" for block in historys)

        # 拼接所有的prompt
        injections = [Injection(self.SYSTEM_PROMPT, ISYSTEM, "system"), Injection(msg, IHISTORY)]
        prompt = self.assemble_injections(injections)

        return prompt
    
    # 后续发起llm请求的负载
    # def prepare_payload(self):
    #     return {
    #         "mode": "instruct",
    #         "stream": True,
    #         "max_tokens": 200,
    #         "skip_special_tokens": False,  # Necessary for Llama 3
    #         "stop": STOP_STRINGS,
    #         "messages": [{
    #             "role": "user",
    #             "content": self.generate_prompt()
    #         }]
    #     }
    
    def generate_response(self):
        self._signals._AI_thinking = True
        self._signals._new_message = False

        # 发起请求...
        AI_message = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.generate_prompt(),
            stream=False
        ).choices[0].message.content

        print(f"AI_message = {AI_message}")
        self._signals._last_message_time = time.time()
        self._signals._AI_thinking = False

        # 提取表情和清理文本
        clean_text, emotion = self.extract_emotion_and_text(AI_message)
        print(f"clean_text = {clean_text}, emotion = {emotion}")
        # 设置表情信号
        if emotion:
            self._signals.AI_expres = emotion

        # 更新历史记录使用原始消息（包含表情），但TTS使用清理后的文本
        self._signals._history.append({"role": "assistant", "content": AI_message})
        self._tts.play(clean_text)

if __name__ == "__main__":
    logger = get_logger()
    signals = Signals(logger)

    start = time.time()
    end = time.time()
