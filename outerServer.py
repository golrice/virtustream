import sys
import socketio
import asyncio
from aiohttp import web
import room_manager
import traceback

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
    print("[调试] B站直播间管理系统启动")

    # 检查配置
    if not room_manager.Config.ACCESS_KEY_ID or not room_manager.Config.ACCESS_KEY_SECRET:
        print("[错误] 请在Config中设置ACCESS_KEY_ID和ACCESS_KEY_SECRET")
        exit(1)

    if not room_manager.Config.ROOM_DISPLAY_ID:
        print("[错误] 请在Config中设置ROOM_DISPLAY_ID")
        exit(1)

    try:
        # 创建房间管理器
        manager = room_manager.RoomManager()

        # 开始监控
        manager.start_monitoring()

    except KeyboardInterrupt:
        print("\n[调试] 收到程序中断信号")
    except Exception as e:
        print(f"[错误] 程序运行失败: {e}")
        print(f"[调试] 错误详情: {traceback.format_exc()}")

    print("[调试] 程序结束")

    sys.exit(0)

async def init_app():
    server.start_background_task(task)
    return app

if __name__ == "__main__":
    web.run_app(init_app(), host='0.0.0.0', port=8080)