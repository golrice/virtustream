import unittest
import os
import numpy as np
from dotenv import load_dotenv
from unittest.mock import MagicMock, patch
from tts import TTS
from signals import Signals
from utils import get_logger
import logging
import json
import base64

class TestTTS(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """测试类初始化"""
        load_dotenv()
        cls.required_env_vars = ['TTS_APPID', 'TTS_APIKey', 'TTS_APISecret']
        for var in cls.required_env_vars:
            if not os.getenv(var):
                raise EnvironmentError(f"缺少环境变量: {var}")

    def setUp(self):
        """每个测试用例前的设置"""
        self.logger = get_logger("test_tts")
        self.signals = Signals(self.logger)
        self.tts = TTS(self.signals)

    def tearDown(self):
        """每个测试用例后的清理"""
        if self.tts._ws:
            self.tts._ws.close()
        # 清空队列
        while not self.tts.audio_queue.empty():
            self.tts.audio_queue.get()

    def test_init(self):
        """测试TTS类初始化"""
        self.assertIsNotNone(self.tts._signals)
        self.assertIsNotNone(self.tts._logger)
        self.assertTrue(self.tts._signals._tts_ready)
        self.assertIsNotNone(self.tts.voice_params)

    def test_create_url(self):
        """测试WebSocket URL生成"""
        url = self.tts._create_url()
        self.assertIsInstance(url, str)
        self.assertTrue(url.startswith('wss://'))
        self.assertIn('authorization=', url)
        self.assertIn('date=', url)

    @patch('websocket.WebSocketApp')
    def test_ensure_ws_connection(self, mock_ws):
        """测试WebSocket连接确保机制"""
        # 模拟WebSocket实例
        mock_ws_instance = MagicMock()
        mock_ws_instance.sock = True
        mock_ws.return_value = mock_ws_instance

        # 模拟连接成功的行为
        def mock_run_forever():
            self.tts._ws_ready.set()
            return True
        mock_ws_instance.run_forever = mock_run_forever

        # 模拟连接事件
        def mock_on_open(ws):
            self.tts._ws_ready.set()
        mock_ws_instance.on_open = mock_on_open

        # 执行测试
        result = self.tts._ensure_ws_connection()
        
        # 验证结果
        self.assertTrue(result)
        self.assertEqual(self.tts._ws_retry_count, 0)
        self.assertTrue(mock_ws.called)
        self.assertTrue(self.tts._ws_ready.is_set())

    def test_process_queue(self):
        """测试消息队列处理"""
        test_message = "测试消息"
        self.signals.tts_queue.put(test_message)
        self.assertFalse(self.signals.tts_queue.empty())

    @patch('sounddevice.play')
    def test_text_to_speech(self, mock_play):
        """测试文本转语音功能"""
        test_text = "你好，这是测试文本"
        
        # 不播放音频的测试
        result = self.tts.text_to_speech(test_text, play_audio=False)
        self.assertIsInstance(result, np.ndarray)
        mock_play.assert_not_called()

        # 空文本测试
        empty_result = self.tts.text_to_speech("", play_audio=False)
        self.assertEqual(len(empty_result), 0)

    def test_on_message_handling(self):
        """测试WebSocket消息处理"""
        test_message = {
            "code": 0,
            "data": {
                "audio": base64.b64encode(b'test_audio').decode(),
                "status": 2
            }
        }
        
        # 将消息转换为JSON字符串
        message_str = json.dumps(test_message)
        
        # 清空队列
        while not self.tts.audio_queue.empty():
            self.tts.audio_queue.get()
        
        # 调用消息处理函数
        self.tts._on_message(None, message_str)
        
        # 验证音频数据被添加到队列
        self.assertFalse(self.tts.audio_queue.empty())
        
        # 验证结束标记也被添加到队列
        audio_data = self.tts.audio_queue.get()
        self.assertIsNotNone(audio_data)
        end_marker = self.tts.audio_queue.get()
        self.assertIsNone(end_marker)

    def test_error_handling(self):
        """测试错误处理"""
        logger = self.tts._logger
        
        # 设置测试logger
        test_handler = logging.StreamHandler()
        test_handler.setLevel(logging.ERROR)
        logger.addHandler(test_handler)
        
        try:
            # 测试连接错误
            test_error = Exception("测试错误")
            self.tts._on_error(None, test_error)
            self.assertIsNone(self.tts._ws)
            
            # 测试无效的API密钥
            original_secret = self.tts.APISecret
            self.tts.APISecret = None
            with self.assertRaises(AttributeError):
                self.tts._create_url()
            self.tts.APISecret = original_secret
            
        finally:
            logger.removeHandler(test_handler)

if __name__ == '__main__':
    unittest.main(verbosity=2)