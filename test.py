import asyncio
import os
import signal
import sys
import time
import threading

from typing import Dict
from modules.client import Client
from modules.module import Module
from signals import Signals
from prompter import Prompter
from stt import STT
from tts import TTS
from LLM import LLMState, textLLMWrapper
from utils import get_logger
from constant import LOG_DIR
from modules.game import Game
os.makedirs(LOG_DIR, exist_ok=True)

async def main():
    logger = get_logger(__name__)
    logger.info("starting...")

    def signal_handler(sig, frame):
        logger.info("received CTRL + C...")
        signals.terminate = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 信号控制
    signals = Signals(logger)
    game_signals = Signals(logger)
    # 初始化语音文字功能
    stt = STT(signals)
    tts = TTS(signals)

    # 初始化模块
    modules: Dict[str, Module] = {}
    module_threads: Dict[str, threading.Thread] = {}

    # 初始化外部客户端
    modules["client"] = Client(signals, True, logger)
    modules["game"] = Game(game_signals, True, logger)
    # 初始化模型
    text_llm = textLLMWrapper.TextLLMWrapper(signals, tts, modules)
    # # 初始化提示词功能 
    prompter = Prompter(signals, text_llm, logger, modules)

    # # 分配计算资源
    prompter_thread = threading.Thread(target=prompter.prompt_loop, daemon=True)
    # stt_thread = threading.Thread(target=stt.listen_loop, daemon=True)
    
    prompter_thread.start()
    # stt_thread.start()

    for name, module in modules.items():
        module_threads[name] = threading.Thread(target=module.init_event_loop, daemon=True)
        module_threads[name].start()

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