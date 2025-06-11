import sys
import socketio
import asyncio
from aiohttp import web
import traceback
from room_manager import Config, RoomManager

server = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
server.attach(app)
manager = RoomManager(server)

@server.event
async def connect(sid, environ):
    print(f"connect: {sid}")

@server.event
async def disconnect(sid):
    print(f"disconnect: {sid}")

async def task():
    try:
        manager.running = True
        manager.logger.info("开始监控直播间")

        websocket = await manager.client.connect()
        tasks = manager.client.get_tasks(websocket)
        return tasks

    except KeyboardInterrupt:
        print("\n[调试] 收到程序中断信号")
    except Exception as e:
        manager.logger.error(f"监控过程中发生错误: {e}")

async def init_app():
    try:
        back_tasks = await task()
    except Exception as e:
        print(f"fail to init bilibili server")
    server.start_background_task(await asyncio.gather(*back_tasks))
    return app

if __name__ == "__main__":
    print("[调试] B站直播间管理系统启动")

    # 检查配置
    if not Config.ACCESS_KEY_ID or not Config.ACCESS_KEY_SECRET:
        print("[错误] 请在Config中设置ACCESS_KEY_ID和ACCESS_KEY_SECRET")
        exit(1)

    if not Config.ROOM_DISPLAY_ID:
        print("[错误] 请在Config中设置ROOM_DISPLAY_ID")
        exit(1)

    if not manager.initialize_client():
        manager.logger.error("客户端初始化失败，无法开始监控")
        sys.exit(1)

    with manager.client:
        try:
            web.run_app(init_app(), host='0.0.0.0', port=8080)
        except KeyboardInterrupt:
            print("quit...")