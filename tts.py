import time
from signals import Signals
import os
import torch
import ChatTTS
import sounddevice as sd
import soundfile
import numpy as np
from typing import Optional

from utils import get_logger

class TTS():
    def __init__(self, sg: Signals):
        self._signals = sg
        self._stream = None

        # 初始化ChatTTS
        self.chat = ChatTTS.Chat()
        self.chat.load(compile=False)

        # 默认参数
        self.default_params_infer_code = {
            'spk_emb': None,
            'temperature': 0.01,
            'top_P': 0.7,
            'top_K': 20
        }

        self.default_params_refine_text = {
            'prompt': '[oral_2][laugh_0][break_6]'
        }

        # 确保speakers目录存在
        os.makedirs("speaker", exist_ok=True)

        self.speaker_path = self.generate_speaker("speaker1")

        self._signals._tts_ready = True
    
    def generate_speaker(self, speaker_name: str = None) -> str:
        """
        生成随机音色
        :param speaker_name: 音色保存名称
        :return: 音色文件路径
        """
        speaker = self.chat.sample_random_speaker()
        # print(speaker)

        if not speaker_name:
            import time
            speaker_name = f"speaker_{int(time.time())}"

        save_path = os.path.join("speaker", f"{speaker_name}.pt")
        torch.save(speaker, save_path)

        return save_path

    def load_speaker(self, speaker_name: str) -> str:
        """
        加载音色
        :param speaker_path: 音色文件路径
        :return: 音色embedding
        """
        speaker_path = os.path.join("speaker", f"{speaker_name}.pt")
        if not os.path.exists(speaker_path):
            return None

        return speaker_path

    def text_to_speech(self, text: str,
                       speaker_path: Optional[str] = None,
                       refine_text: bool = False,
                       play_audio: bool = True) -> np.ndarray:
        """
        文本转语音
        :param text: 输入文本
        :param speaker_path: 音色文件路径
        :param refine_text: 是否优化文本
        :param play_audio: 是否实时播放音频
        :return: 音频数据
        """
        # 加载音色
        speaker = None
        if speaker_path:
            speaker = torch.load(speaker_path)
        else:
            print("--未找到音色--")
            return np.array([])
        # 设置infer_code参数
        infer_code_params = self.default_params_infer_code.copy()
        if speaker is not None:
            infer_code_params['spk_emb'] = speaker
        params_infer_code = ChatTTS.Chat.InferCodeParams(
            spk_emb=infer_code_params['spk_emb'],  # add sampled speaker
            temperature=infer_code_params['temperature'],  # using custom temperature
            top_P=infer_code_params['top_P'],  # top P decode
            top_K=infer_code_params['top_K'],  # top K decode
        )
        # oral：连接词，AI可能会自己加字，取值范围 0-9，比如：卡壳、嘴瓢、嗯、啊、就是之类的词
        # laugh：笑，取值范围 0-9
        # break：停顿，取值范围 0-9
        refine_text_params = self.default_params_refine_text.copy()
        params_refine_text = ChatTTS.Chat.RefineTextParams(
            prompt=refine_text_params['prompt'],
        )
        # 文本优化
        if refine_text:
            text = self.chat.infer(text,
                                    refine_text_only=True,
                                    params_refine_text=params_refine_text,
                                    params_infer_code=params_infer_code)
            # text = texts[0] if texts else text  #这行代码的作用是?
            print(text)

        # 生成语音
        wavs = self.chat.infer(text,
                               params_infer_code=params_infer_code)

        if not wavs:
            raise ValueError("语音生成失败")
        soundfile.write("output1.wav", wavs[0], 24000)
        # if play_audio:
        #     playsound(r"E:\pycharm_project\ChatTTS\output1.wav")
        audio_data = wavs[0]

        # 实时播放
        # if play_audio:
        #     sd.play(audio_data, samplerate=24000)
        #     sd.wait()

        return audio_data
    
    def play(self, message):
        if not message.strip():
            return

        self._signals._AI_speaking = True
        # self._signals.sio_queue.put(("current_message", message))
        # 语音播放 steam ... play or something else
        print(f"simulating tts... I am talking...")
        self.text_to_speech(message, self.speaker_path)
        self._signals._AI_speaking = False

    def stop(self):
        self._stream.stop()
        self._signals._AI_speaking = False

    def audio_started(self):
        self._signals._AI_speaking = True

    def audio_ended(self):
        self._signals._last_message_time = time.time()
        self._signals._AI_speaking = False

if __name__ == "__main__":
    logger = get_logger()
    signals = Signals(logger)

    tts = TTS(signals)
    start = time.time()
    tts.text_to_speech("你好,我是mico酱,是一名主播", tts.generate_speaker("speaker1"))
    end = time.time()
    print(f"costed: {end - start}s")
