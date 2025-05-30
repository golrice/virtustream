import sys
import socketio
import asyncio
from aiohttp import web

server = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
server.attach(app)

@server.event
async def connect(sid, environ):
    print(f"connect: {sid}")

@server.event
async def disconnect(sid):
    print(f"disconnect: {sid}")

async def task():
    while True:
        msg = await asyncio.to_thread(input, "输入消息 (输入 'quit' 退出): ")
        if msg == 'quit':
            print("正在关闭服务器...")
            break
        print(f"msg = {msg}")
        await server.emit('chat_message', msg)
        await asyncio.sleep(0.1)
    sys.exit(0)

async def init_app():
    server.start_background_task(task)
    return app

if __name__ == "__main__":
    web.run_app(init_app(), host='0.0.0.0', port=8080)
