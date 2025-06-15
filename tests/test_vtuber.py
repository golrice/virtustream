import asyncio
import os
import signal
import sys
import time
import threading

from typing import Dict
from modules.vtuber import VTuber
from signals import Signals
from utils import get_logger
from constant import LOG_DIR



async def sig(signals): 
   await asyncio.sleep(20) 
   signals._AI_expres="坏笑" 
   await asyncio.sleep(0.1) 
   signals._AI_speaking=True 
   await asyncio.sleep(7) 
   signals._AI_expres="生气" 
   await asyncio.sleep(10) 
   signals._AI_speaking=False 

   await asyncio.sleep(10) 
   signals._AI_expres="高兴" 
   await asyncio.sleep(0.1) 
   signals._AI_speaking=True 
   await asyncio.sleep(15) 
   signals._AI_expres="无语" 
   await asyncio.sleep(10) 
   signals._AI_speaking=False 
   await asyncio.sleep(10) 
   signals._AI_expres="害羞" 
   await asyncio.sleep(0.1) 
   signals._AI_speaking=True 
   await asyncio.sleep(17) 
   signals._AI_speaking=False 
   await asyncio.sleep(10) 

   signals.terminate=True 
 

def chasig(signals): 
 asyncio.run(sig(signals))


def test_my_func():


    logger = get_logger(__name__)
    logger.info("starting...")

    def signal_handler(sig, frame):
        logger.info("received CTRL + C...")
        signals.terminate = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 信号控制
    signals = Signals(logger)


    module_threads: Dict[str, threading.Thread] = {}

    vtuber = VTuber(signals, True, logger)
    module_threads["vtube_studio_client"] = threading.Thread(target=vtuber.init_vtube_studio_client, daemon=True)
    module_threads["vtube_studio_client"].start()
    module_threads["vtube_expression_stream"] = threading.Thread(target=vtuber.init_expression_stream, daemon=True)
    module_threads["vtube_expression_stream"].start()
    t2 = threading.Thread(target=chasig, args=(signals,)) #信号模拟线程
    t2.start() 
    while not signals.terminate:
        time.sleep(0.1)
    t2.join()
    for module_thread in module_threads.values():
        module_thread.join()

    sys.exit(0)