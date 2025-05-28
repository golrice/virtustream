import asyncio
import logging
import os
import signal
import sys
import time
import threading
from logging.handlers import TimedRotatingFileHandler

from signals import Signals
from prompter import Prompter
from stt import STT
from tts import TTS
from LLM import LLMState, textLLMWrapper

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

def get_logger(name: str = "default", level=logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)

    if logger.handlers:
        return logger  

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = TimedRotatingFileHandler(
        filename=os.path.join(LOG_DIR, f"{name}.log"),
        when="midnight",
        interval=1,
        backupCount=7,  
        encoding="utf-8"
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logger.propagate = False  
    return logger

async def main():
    logger = get_logger(__name__)
    logger.info("starting...")

    def signal_handler(sig, frame):
        logger.info("received CTRL + C...")
        signals.terminate = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 信号控制
    signals = Signals()

    # 初始化语音文字功能
    stt = STT(signals)
    tts = TTS(signals)
    
    # 初始化模型功能
    llmState = LLMState.LLMState
    llms = {
        "text": textLLMWrapper.TextLLMWrapper(signals, tts, llmState),
    }
    # 初始化提示词功能 
    prompter = Prompter(signals, llms)

    # 分配计算资源
    prompter_thread = threading.Thread(target=prompter.prompt_loop, daemon=True)
    stt_thread = threading.Thread(target=stt.listen_loop, daemon=True)
    
    prompter_thread.start()
    stt_thread.start()

    # 定时监测生命周期
    while not signals.terminate:
        time.sleep(0.1)
    logger.info("TERMINATING ======================")

    prompter_thread.join()
    logger.info("PROMPTER EXITED ======================")

    logger.info("All threads exited, shutdown complete")
    sys.exit(0)

if __name__ == '__main__':
    asyncio.run(main())