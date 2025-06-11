import asyncio
import sys
import socketio
from aiohttp import web
from room_manager import Config, RoomManager
from aioconsole import ainput

server = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
server.attach(app)
manager = RoomManager(server)
websocket = None

@server.event
async def connect(sid, environ):
    print(f"connect: {sid}")

@server.event
async def disconnect(sid):
    print(f"disconnect: {sid}")

async def get_websocket():
    try:
        manager.running = True
        manager.logger.info("开始监控直播间")

        websocket = await manager.client.connect()
        return websocket

    except KeyboardInterrupt:
        print("\n[调试] 收到程序中断信号")
    except Exception as e:
        manager.logger.error(f"监控过程中发生错误: {e}")

async def listen_keyboard():
    while True:
        msg = await ainput()
        await server.emit("chat_message", msg)
        await asyncio.sleep(0.2)

async def init_app():
    try:
        websocket = await get_websocket()
        server.start_background_task(manager.client.recvLoop, websocket)
        server.start_background_task(manager.client.heartBeat, websocket)
        server.start_background_task(manager.client.appheartBeat)
        # server.start_background_task(listen_keyboard)
    except Exception as e:
        manager.logger.error(f"初始化失败: {e}")
        raise
    
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

    try:
        # 正确调用方式
        web.run_app(init_app(), host='0.0.0.0', port=8080)
    except KeyboardInterrupt:
        manager.logger.info("服务正常终止")
    except Exception as e:
        manager.logger.error(f"服务异常终止: {e}")
    finally:
        # 确保资源清理
        if hasattr(manager, 'client'):
            manager.client.__exit__()
        manager.logger.info("资源清理完成")
