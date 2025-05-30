import logging
import socketio
import signal
from aiohttp import web
from aiohttp.web_runner import GracefulExit
from signals import Signals

from utils import get_logger

class SIOServer:
    def __init__(self, signals: Signals, logger: logging.Logger):
        self._signals = signals
        self._logger = logger

    def start(self):
        sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
        app = web.Application()
        sio.attach(app)

        @sio.event
        async def connect(sid, environ):
            self._logger.info(f"客户端连接：{sid}")

        @sio.event
        async def disconnect(sid):
            self._logger.info(f"客户端断开：{sid}")

        @sio.event
        async def user_message(sid, data):
            self._logger.info(f"收到消息：{data}")
            await sio.emit("broadcast", {"sid": sid, "message": data})

        async def send_messages():
            while True:
                if self._signals._terminate:
                    raise GracefulExit

                while not self._signals.sio_queue.empty():
                    event, data = self._signals.sio_queue.get()
                    print(f"Sending {event} with {data}")
                    await sio.emit(event, data)
                await sio.sleep(0.1)

        async def init_app():
            sio.start_background_task(send_messages)
            return app

        web.run_app(init_app(), host='0.0.0.0', port=5000)

if __name__ == "__main__":
    logger = get_logger("sio")

    def signal_handler(sig, frame):
        logger.info("received CTRL + C...")
        signals.terminate = True

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    signals = Signals()

    server = SIOServer(signals, logger)
    server.start()

