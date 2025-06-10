import logging
import os
import queue
import time
import sounddevice as sd
import soundfile as sf
import numpy as np
from constant import VOICE_CHANNELS, VOICE_DTYPE, VOICE_SAMPLERATE, VOICE_SENSEVOICE_DIR, VOICE_SILENCE_DURATION, VOICE_SILENCE_THRESHOLD_DB, VOICE_UPDATE_INTERVAL
from signals import Signals
from funasr import AutoModel
from typing import Callable
from threading import Thread, Event
from funasr.utils.postprocess_utils import rich_transcription_postprocess

class STT():
    def __init__(self, sg: Signals, logger: logging.Logger):
        self._signals = sg
        self._signals.stt_ready = True
        self._logger = logger

        # self.model = AutoModel(model=VOICE_SENSEVOICE_DIR)
        # 音频控制
        self.fs = VOICE_SAMPLERATE
        self.channels = VOICE_CHANNELS
        self.dtype = VOICE_DTYPE
        self.blocksize = int(self.fs * VOICE_UPDATE_INTERVAL)

        # 录音控制
        self.is_recording = False
        self.audio_queue = queue.Queue()
        self.stop_event = Event()

        # 静音检测参数
        self.silence_threshold_db = VOICE_SILENCE_THRESHOLD_DB
        self.silence_duration = VOICE_SILENCE_DURATION
        self.silent_blocks_threshold = int(VOICE_SILENCE_DURATION / VOICE_UPDATE_INTERVAL)
        self.silent_blocks_count = 0

        # 音量显示相关
        self.current_volume_db = -100.0  # 初始设为极低值
        self.volume_history = []
        self.max_history_length = 100
        self.volume_callback = None

        # 可视化相关
        self.fig = None
        self.ax = None
        self.line = None
        self.ani = None

        self._logger.info("stt init")
    
    def _calculate_volume_db(self, audio_data: np.ndarray) -> float:
        """计算音频数据的音量(dB)"""
        if audio_data.size == 0:
            return -100.0  # 静音

        # 计算RMS并转换为dB
        rms = np.sqrt(np.mean(np.square(audio_data.astype(np.float32))))
        return 20 * np.log10(rms + 1e-10)  # 避免log(0)

    def _record_callback(self, indata, frames, time, status):
        """录音回调函数"""
        if self.is_recording:
            self.audio_queue.put(indata.copy())

            # 计算当前音量
            volume_db = self._calculate_volume_db(indata)
            self.current_volume_db = volume_db

            # 更新音量历史
            self.volume_history.append(volume_db)
            if len(self.volume_history) > self.max_history_length:
                self.volume_history.pop(0)

            # 检测静音
            if volume_db < self.silence_threshold_db:
                self.silent_blocks_count += 1
                if self.silent_blocks_count >= self.silent_blocks_threshold:
                    self.is_recording = False
                    self.stop_event.set()
            else:
                self.silent_blocks_count = 0

            # 调用音量回调函数
            if self.volume_callback:
                self.volume_callback(volume_db)

    def set_volume_callback(self, callback: Callable[[float], None]):
        """设置音量回调函数"""
        self.volume_callback = callback

    def wav_to_text(self, wav_path: str) -> str:
        """wav文件转文字"""
        if not os.path.exists(wav_path):
            raise FileNotFoundError(f"WAV file not found: {wav_path}")

        res = self.model.generate(
            input=wav_path,
            use_itn=True,
        )
        if res and len(res) > 0 and 'text' in res[0]:
            return rich_transcription_postprocess(res[0]['text'])
        return ""

    def speaking(self):
        return False

    def listen_loop(self):
        while not self._signals.terminate:
            self.is_recording = True
            self.stop_event.clear()
            self.silent_blocks_count = 0
            audio_frames = []
            start_time = time.time()
            timeout = 30.0
    
            try:
                # 在独立线程中录音
                def recording_thread():
                    with sd.InputStream(samplerate=self.fs, channels=self.channels,
                                        dtype=self.dtype, blocksize=self.blocksize,
                                        callback=self._record_callback):
                        while self.is_recording and not self.stop_event.is_set():
                            if time.time() - start_time > timeout:
                                self.is_recording = False
                                self.stop_event.set()
                            time.sleep(0.1)
    
                thread = Thread(target=recording_thread)
                thread.start()
    
                # 主线程处理音频数据
                while self.is_recording or not self.audio_queue.empty():
                    if not self.audio_queue.empty():
                        data = self.audio_queue.get()
                        audio_frames.append(data)
                    time.sleep(0.05)
    
                thread.join()
    
                # 合并音频数据
                if not audio_frames:
                    return ""
    
                audio_data = np.concatenate(audio_frames, axis=0)
    
                # 保存临时wav文件
                temp_wav = "temp_recording.wav"
                sf.write(temp_wav, audio_data, self.fs)
    
                # 调用ASR识别
                text = self.wav_to_text(temp_wav)
    
                # 删除临时文件
                try:
                    os.remove(temp_wav)
                except:
                    pass
    
                return text
    
            except Exception as e:
                print(f"录音出错: {e}")
                return ""
            finally:
                self.is_recording = False
                self.stop_event.set()
