import time
from signals import Signals
import os
import websocket
import threading
import queue
import base64
import hmac
import json
import datetime
import hashlib
import urllib
import sounddevice as sd
import numpy as np
from typing import Optional
from dotenv import load_dotenv
from utils import get_logger
from constant import TTS_PARAMS
class TTS():
    def __init__(self, sg: Signals):
        self._signals = sg
        self._stream = None
        self._logger = get_logger("tts")
        load_dotenv()
        # 科大讯飞参数配置
        self.APPID = os.getenv("APPID")
        self.APIKey = os.getenv("APIKey")
        self.APISecret = os.getenv("APISecret")
        
        # 语音合成参数
        self.voice_params = TTS_PARAMS.copy()  # 使用深拷贝避免修改原始参数
        
        self.audio_queue = queue.Queue()
        self._signals._tts_ready = True
        self._ws = None  # 添加 WebSocket 连接实例变量
        self._ws_lock = threading.Lock()  # 添加线程锁
        self._ws_thread = None  # 添加 WebSocket 线程变量
        self.TIMEOUT = 60  # 添加超时时间配置，单位为秒

    def _create_url(self):
        """生成鉴权url"""
        url = 'wss://tts-api.xfyun.cn/v2/tts'
        # 生成RFC1123格式的时间戳
        now = datetime.datetime.now(datetime.timezone.utc)  # 使用 UTC 时间
        date = now.strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        # 拼接字符串
        signature_origin = f"host: tts-api.xfyun.cn\ndate: {date}\nGET /v2/tts HTTP/1.1"
        
        # 进行hmac-sha256加密
        signature_sha = hmac.new(self.APISecret.encode('utf-8'),
                            signature_origin.encode('utf-8'),
                            digestmod=hashlib.sha256).digest()
        signature_sha_base64 = base64.b64encode(signature_sha).decode()
        
        authorization_origin = f'api_key="{self.APIKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha_base64}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode()
        
        # 将请求的鉴权参数组合为字典
        v = {
            "authorization": authorization,
            "date": date,
            "host": "tts-api.xfyun.cn"
        }
        # 拼接鉴权参数，生成url
        url = url + '?' + urllib.parse.urlencode(v)
        return url

    def _on_message(self, ws, message):
        try:
            message = json.loads(message)
            if message["code"] != 0:
                self._logger.error(f'合成失败: {message["code"]}, {message["message"]}')
                return
            
            data = base64.b64decode(message["data"]["audio"])
            audio_array = np.frombuffer(data, dtype=np.int16)
            self.audio_queue.put(audio_array)
            
            if message["data"]["status"] == 2:
                self.audio_queue.put(None)  # 结束标记
                
        except Exception as e:
            self._logger.error(f"处理消息时出错: {str(e)}")

    def _on_error(self, ws, error):
        self._logger.error(f"WebSocket错误: {error}")
        self._ws = None  # 清空连接以便重新建立
        
    def _on_close(self, ws, *args):
        self._logger.info("WebSocket连接关闭")
        self._ws = None
        
    def _on_open(self, ws):
        self._logger.info("WebSocket连接已建立")
        
    def _ensure_ws_connection(self):
        """确保 WebSocket 连接存在且有效"""
        with self._ws_lock:
            if self._ws is None or not self._ws.sock:
                websocket.setdefaulttimeout(self.TIMEOUT)  # 设置 WebSocket 连接超时
                self._ws = websocket.WebSocketApp(
                    self._create_url(),
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
                self._ws.on_open = self._on_open
                
                if self._ws_thread is not None and self._ws_thread.is_alive():
                    self._ws_thread.join(timeout=1)
                    
                self._ws_thread = threading.Thread(target=self._ws.run_forever)
                self._ws_thread.daemon = True  # 设置为守护线程
                self._ws_thread.start()
                time.sleep(0.5)  # 等待连接建立

    def text_to_speech(self, text: str,
                      speaker_path: Optional[str] = None,
                      refine_text: bool = False,
                      play_audio: bool = True) -> np.ndarray:
        """
        文本转语音
        :param text: 输入文本
        :param speaker_path: 兼容参数，不使用
        :param refine_text: 兼容参数，不使用
        :param play_audio: 是否实时播放音频
        :return: 音频数据
        """
        audio_data = []
        self._ensure_ws_connection()  # 确保连接存在
        
        try:
            data = {
                "common": {"app_id": self.APPID},
                "business": self.voice_params,
                "data": {
                    "status": 2,
                    "text": base64.b64encode(text.encode('utf-8')).decode(),
                }
            }
            self._ws.send(json.dumps(data))
            
            # 收集音频数据
            while True:
                data = self.audio_queue.get(timeout=self.TIMEOUT)  # 使用配置的超时时间
                if data is None:
                    break
                audio_data.extend(data)
                
        except queue.Empty:
            self._logger.error("等待音频数据超时")
            return np.array([], dtype=np.float32)
        except Exception as e:
            self._logger.error(f"语音合成错误: {str(e)}")
            return np.array([], dtype=np.float32)
            
        audio_data = np.array(audio_data, dtype=np.float32) / 32768.0

        # 实时播放
        if play_audio and len(audio_data) > 0:
            sd.play(audio_data, samplerate=16000)
            sd.wait()

        return audio_data
        
    def play(self, message):
        if not message.strip():
            return

        self._signals._AI_speaking = True
        try:
            self.text_to_speech(message)
        except Exception as e:
            self._logger.error(f"播放失败: {str(e)}")
        finally:
            self._signals._AI_speaking = False

    def stop(self):
        """停止并清理资源"""
        if self._stream:
            self._stream.stop()
        if self._ws:
            self._ws.close()
        self._ws = None
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
    print("API配置信息：")
    print(f"APPID: {tts.APPID}")
    print(f"APIKey: {tts.APIKey}")
    print(f"APISecret: {tts.APISecret[:5]}...{tts.APISecret[-5:]}")
    start = time.time()
    tts.text_to_speech("你好,我是mico酱,是一名主播")
    end = time.time()
    print(f"costed: {end - start}s")



