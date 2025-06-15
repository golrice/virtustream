import asyncio
import os
from dotenv import load_dotenv
from socketio import AsyncServer
import websockets
import json
import time
import requests
import hashlib
import hmac
import random
from utils import get_logger
import proto
from hashlib import sha256
from constant import B_APP_HEARTBEAT_INTERVAL, B_BILI_API_HOST, B_HEARTBEAT_INTERVAL, B_MESSAGE_FILE, B_ROOM_DATA_INTERVAL

load_dotenv()

# ========== 配置区域 ==========
class Config:
    # B站API相关密钥
    ACCESS_KEY_ID = os.getenv("B_ACCESS_KEY_ID")
    ACCESS_KEY_SECRET = os.getenv("B_ACCESS_KEY_SECRET")

    # 项目ID
    APP_ID = int(os.getenv("B_APP_ID"))

    # B站用户身份验证信息
    SESSDATA = os.getenv("B_SESSDATA")
    BILI_JCT = os.getenv("B_BILI_JCT")
    BUVID3 = os.getenv("B_BUVID3")
    IDCODE = os.getenv("B_IDCODE")

    # 直播间配置
    ROOM_DISPLAY_ID = int(os.getenv("B_ROOM_DISPLAY_ID"))
    LOCAL_PORT = int(os.getenv("B_LOCAL_PORT"))
    MESSAGE_FILE = B_MESSAGE_FILE

    # 长连信息配置（动态更新）
    WSS_LINKS = []  # WebSocket连接地址列表
    AUTH_BODY: str = ""  # 鉴权体

    # 主播信息配置（动态更新）
    ANCHOR_ROOM_ID = 0  # 主播房间号
    ANCHOR_UNAME = ""   # 主播昵称
    ANCHOR_UFACE = ""   # 主播头像
    ANCHOR_UID = 0      # 主播UID
    ANCHOR_OPEN_ID = "" # 用户唯一标识
    ANCHOR_UNION_ID = "" # 开发者维度下用户唯一标识

    # 时间间隔（秒）
    ROOM_DATA_INTERVAL = B_ROOM_DATA_INTERVAL
    HEARTBEAT_INTERVAL = B_HEARTBEAT_INTERVAL
    APP_HEARTBEAT_INTERVAL = B_APP_HEARTBEAT_INTERVAL

    # API域名
    BILI_API_HOST = B_BILI_API_HOST

# ========== 全局工具函数 ==========

# ========== 命令行交互 ==========

# def command_line_interface(monitor):
#     """处理用户命令输入"""
#     print("[调试] 命令行界面线程启动")

#     while monitor.running:
#         try:
#             cmd = input("\n请输入命令 (help查看帮助): ").strip().lower()
#             print(f"[调试] 收到命令: {cmd}")

#             if cmd == 'exit':
#                 print("[调试] 收到退出命令")
#                 monitor.running = False
#                 print("[系统] 正在停止所有服务...")

#             elif cmd == 'ban':
#                 print("[调试] 执行封禁命令")
#                 users = RoomManager.get_online_users()
#                 if not users:
#                     print("[警告] 没有获取到在线观众")
#                     continue

#                 print("当前在线观众:")
#                 for i, (uid, uname) in enumerate(users, 1):
#                     print(f"{i}. UID:{uid} 昵称:{uname}")

#                 try:
#                     select = int(input("选择要封禁的观众编号: ")) - 1
#                     if select < 0 or select >= len(users):
#                         print("[错误] 选择的编号无效")
#                         continue

#                     hour = int(input("封禁时长(小时): "))
#                     if hour <= 0:
#                         print("[错误] 封禁时长必须大于0")
#                         continue

#                     print(f"[调试] 准备封禁用户: {users[select][1]} (UID:{users[select][0]})")
#                     if RoomManager.ban_user(users[select][0], hour):
#                         print(f"已封禁 {users[select][1]}")
#                     else:
#                         print(f"封禁 {users[select][1]} 失败")

#                 except ValueError:
#                     print("[错误] 输入的不是有效数字")
#                 except IndexError:
#                     print("[错误] 选择的编号超出范围")
#                 except Exception as e:
#                     print(f"[错误] 封禁操作时发生错误: {e}")

#             elif cmd == 'notice':
#                 print("[调试] 执行发送公告命令")
#                 content = input("请输入公告内容: ")
#                 if not content.strip():
#                     print("[错误] 公告内容不能为空")
#                     continue

#                 if RoomManager.send_notice(content):
#                     print("公告发送成功!")
#                 else:
#                     print("公告发送失败!")

#             elif cmd == 'help':
#                 print("""
#                 可用命令:
#                 exit    - 停止程序
#                 ban     - 封禁用户
#                 notice  - 发送公告
#                 help    - 显示帮助
#                 """)

#             else:
#                 print(f"[警告] 未知命令: {cmd}，输入help查看帮助")

#         except KeyboardInterrupt:
#             print("\n[调试] 收到键盘中断信号")
#             monitor.running = False
#             break
#         except EOFError:
#             print("\n[调试] 输入流结束")
#             monitor.running = False
#             break
#         except Exception as e:
#             print(f"[错误] 命令行处理时发生错误: {e}")
#             print(f"[调试] 错误详情: {traceback.format_exc()}")

#     print("[调试] 命令行界面线程结束")

# ========== 实时数据监控 ==========

# def monitor_room_data():
#     """定时获取直播间数据"""
#     print("[调试] 实时数据监控线程启动")

#     while True:
#         try:
#             print("[调试] 正在获取直播间实时数据")

#             优先使用官方API
#             if Config.ACCESS_KEY_ID and Config.ACCESS_KEY_SECRET:
#                 url = "https://live-open.biliapi.com/v2/app/room_play_info"

#                 body_data = {
#                     "room_id": get_real_room_id()
#                 }
#                 body = json.dumps(body_data)

#                 headers = create_bili_api_headers('POST', url, body=body)

#                 if headers:
#                     try:
#                         resp = requests.post(url, headers=headers, data=body, timeout=10)
#                         if resp.status_code == 200:
#                             result = resp.json()
#                             if result.get('code') == 0:
#                                 print(f"[成功] 官方API获取实时数据成功")
#                                 处理实时数据
#                                 time.sleep(Config.ROOM_DATA_INTERVAL)
#                                 continue
#                     except Exception as e:
#                         print(f"[警告] 官方API获取实时数据失败: {e}")

#             回退到传统方式
#             url = f"https://api.live.bilibili.com/xlive/web-room/v1/index/getRoomPlayInfo?room_id={get_real_room_id()}"
#             resp = requests.get(url, cookies={"SESSDATA": Config.SESSDATA}, timeout=10)

#             print(f"[调试] 实时数据API响应状态码: {resp.status_code}")

#             if resp.status_code != 200:
#                 print(f"[错误] 获取实时数据失败，状态码: {resp.status_code}")
#             else:
#                 result = resp.json()
#                 if result.get('code') != 0:
#                     print(f"[错误] 实时数据API返回错误: {result.get('message', '未知错误')}")
#                 else:
#                     data = result['data']
#                     print(f"\n[实时数据] 人气值: {data['online']} | 观看人数: {data['watched_show']['num']} | 关注数: {data['attention']}")

#         except requests.exceptions.Timeout:
#             print("[错误] 获取实时数据超时")
#         except Exception as e:
#             print(f"[错误] 实时数据监控时发生错误: {e}")
#             print(f"[调试] 错误详情: {traceback.format_exc()}")

#         time.sleep(Config.ROOM_DATA_INTERVAL)

# ========== B站客户端实现 ==========
class BiliClient:
    def __init__(self, idCode, appId, key, secret, host, connect_server):
        self.idCode = idCode
        self.appId = appId
        self.key = key
        self.secret = secret
        self.host = host
        self.gameId = ''
        self.connect_server = connect_server

    # 事件循环
    def run(self):
        loop = asyncio.get_event_loop()
        # 建立连接
        websocket = loop.run_until_complete(self.connect())
        tasks = self.get_tasks(websocket)
        loop.run_until_complete(asyncio.gather(*tasks))

    # http的签名
    def sign(self, params):
        key = self.key
        secret = self.secret
        md5 = hashlib.md5()
        md5.update(params.encode())
        ts = time.time()
        nonce = random.randint(1, 100000)+time.time()
        md5data = md5.hexdigest()
        headerMap = {
            "x-bili-timestamp": str(int(ts)),
            "x-bili-signature-method": "HMAC-SHA256",
            "x-bili-signature-nonce": str(nonce),
            "x-bili-accesskeyid": key,
            "x-bili-signature-version": "1.0",
            "x-bili-content-md5": md5data,
        }

        headerList = sorted(headerMap)
        headerStr = ''

        for key in headerList:
            headerStr = headerStr + key+":"+str(headerMap[key])+"\n"
        headerStr = headerStr.rstrip("\n")

        appsecret = secret.encode()
        data = headerStr.encode()
        signature = hmac.new(appsecret, data, digestmod=sha256).hexdigest()
        headerMap["Authorization"] = signature
        headerMap["Content-Type"] = "application/json"
        headerMap["Accept"] = "application/json"
        return headerMap

    # 获取长连信息
    def getWebsocketInfo(self):
        # 开启应用
        postUrl = "%s/v2/app/start" % self.host
        params = '{"code":"%s","app_id":%d}' % (self.idCode, self.appId)
        headerMap = self.sign(params)
        r = requests.post(url=postUrl, headers=headerMap,
                          data=params, verify=False)
        data = json.loads(r.content)
        print(data)

        self.gameId = str(data['data']['game_info']['game_id'])
                # 存储 game_id
        self.gameId = str(data['data']['game_info']['game_id'])

        # 更新Config中的长连信息
        Config.WSS_LINKS = data['data']['websocket_info']['wss_link']
        Config.AUTH_BODY = str(data['data']['websocket_info']['auth_body'])

        # 更新Config中的主播信息
        anchor_info = data['data']['anchor_info']
        Config.ANCHOR_ROOM_ID = anchor_info['room_id']
        Config.ANCHOR_UNAME = anchor_info['uname']
        Config.ANCHOR_UFACE = anchor_info.get('uface', '')
        Config.ANCHOR_UID = anchor_info.get('uid', 0)
        Config.ANCHOR_OPEN_ID = anchor_info.get('open_id', '')
        Config.ANCHOR_UNION_ID = anchor_info.get('union_id', '')

        # 打印更新的配置信息
        print(f"[BiliClient] 已更新Config - 主播房间号: {Config.ANCHOR_ROOM_ID}")
        print(f"[BiliClient] 已更新Config - 主播昵称: {Config.ANCHOR_UNAME}")
        print(f"[BiliClient] 已更新Config - 长连地址数量: {len(Config.WSS_LINKS)}")
        print(f"[BiliClient] Game ID: {self.gameId}")

        # 获取长连地址和鉴权体
        return str(data['data']['websocket_info']['wss_link'][0]), str(data['data']['websocket_info']['auth_body'])

     # 发送游戏心跳

    async def handleMassage(self, respBody):
        """处理弹幕消息"""
        msg = None
        if respBody["cmd"] == "LIVE_OPEN_PLATFORM_DM":# 普通弹幕消息
            uname = respBody["data"]["uname"]
            message = respBody["data"]["msg"]
            msg = f"{uname} 说: {message}"
        if respBody["cmd"] == "LIVE_OPEN_PLATFORM_SEND_GIFT":# 礼物弹幕消息
            uname = respBody["data"]["uname"]
            gift_name = respBody["data"]["gift_name"]
            gift_num = respBody["data"]["num"]
            msg = f"{uname} 送出了 {gift_num} 个 {gift_name}"
        if respBody["cmd"] == "LIVE_OPEN_PLATFORM_SUPER_CHAT":# 付费聊天消息
            uname = respBody["data"]["uname"]
            message = respBody["data"]["message"]
            rmb = respBody["data"]["rmb"]
            msg = f"{uname} 发送了付费聊天: {message} (金额: {rmb}元)"
        if respBody["cmd"] == "LIVE_OPEN_PLATFORM_GUARD":# 上舰消息
            uname = respBody["data"]["user_info"]["uname"]
            guard_level = respBody["data"]["guard_level"]
            msg = f"{uname} 成为了 {guard_level} 舰长"
        
        # if respBody["cmd"] == "LIVE_OPEN_PLATFORM_LIVE_START":# 直播开始信息
        #     room_id = respBody["data"]["room_id"]
        #     msg = f"你在直播间 {room_id} 开始直播"
        # if respBody["cmd"] == "LIVE_OPEN_PLATFORM_LIVE_END":# 直播结束信息
        #     room_id = respBody["data"]["room_id"]
        #     msg = f"你在直播间 {room_id} 结束直播"
        # if respBody["cmd"] == "LIVE_OPEN_PLATFORM_INTERACTION_END":# 长连结束信息
        #     room_id = respBody["data"]["room_id"]
        #     print(f"[错误] 长连在直播间 {room_id} 结束")
        if msg is not None:
            print(f"[BiliClient] 收到消息: {msg}")
            await self.connect_server.emit('chat_message', msg)


    async def appheartBeat(self):
        while True:
            await asyncio.ensure_future(asyncio.sleep(20))
            postUrl = "%s/v2/app/heartbeat" % self.host
            params = '{"game_id":"%s"}' % (self.gameId)
            headerMap = self.sign(params)
            r = requests.post(url=postUrl, headers=headerMap,
                          data=params, verify=False)
            data = json.loads(r.content)
            # print("[BiliClient] send appheartBeat success")


    # 发送鉴权信息
    async def auth(self, websocket, authBody):
        req = proto.Proto()
        req.body = authBody
        req.op = 7
        await websocket.send(req.pack())
        buf = await websocket.recv()
        resp = proto.Proto()
        resp.unpack(buf)
        respBody = json.loads(resp.body)
        if respBody["code"] != 0:
            print("auth 失败")
        else:
            print("auth 成功")

    # 发送心跳
    async def heartBeat(self, websocket):
        while True:
            await asyncio.ensure_future(asyncio.sleep(20))
            req = proto.Proto()
            req.op = 2
            await websocket.send(req.pack())

    # 读取信息
    async def recvLoop(self, websocket):
        print("[BiliClient] run recv...")
        while True:

            recvBuf = await websocket.recv()
            resp = proto.Proto()
            resp.unpack(recvBuf)
            if resp.op == 3:
                # 心跳响应
                # print("[BiliClient] recv heartBeat success")
                pass
            elif resp.op == 5:
                # 弹幕信息
                respBody = json.loads(resp.body)
                # print("[BiliClient] recv danmu:", respBody)
                await asyncio.sleep(0.1)  # 确保异步执行
                await self.handleMassage(respBody)

    # 建立连接
    async def connect(self):
        addr, authBody = self.getWebsocketInfo()
        print(addr, authBody)
        websocket = await websockets.connect(addr)
        # 鉴权
        await self.auth(websocket, authBody)
        return websocket
    
    def get_tasks(self, websocket):
        return [
            # 读取信息
            asyncio.ensure_future(self.recvLoop(websocket)),
            # 发送心跳
            asyncio.ensure_future(self.heartBeat(websocket)),
             # 发送游戏心跳
            asyncio.ensure_future(self.appheartBeat()),
        ]

    def __enter__(self):
        print("[BiliClient] enter")

    def __exit__(self, type, value, trace):
        # 关闭应用
        postUrl = "%s/v2/app/end" % self.host
        params = '{"game_id":"%s","app_id":%d}' % (self.gameId, self.appId)
        headerMap = self.sign(params)
        r = requests.post(url=postUrl, headers=headerMap,
                          data=params, verify=False)
        print("[BiliClient] end app success", params)
# ========== 房间管理器 ==========
class RoomManager:
    def __init__(self, connect_server: AsyncServer):
        self.logger = get_logger("room_manager")
        self.client = None
        self.running = False
        self.connect_server = connect_server

    def initialize_client(self):
        """初始化B站客户端"""
        try:
            self.client = BiliClient(
                idCode=str(Config.IDCODE),  # 使用房间ID作为身份码
                appId=Config.APP_ID,  # 应用ID，需要从B站开放平台获取
                key=Config.ACCESS_KEY_ID,
                secret=Config.ACCESS_KEY_SECRET,
                host=Config.BILI_API_HOST,
                connect_server=self.connect_server
            )
            self.logger.info("B站客户端初始化成功")
            return True
        except Exception as e:
            self.logger.error(f"B站客户端初始化失败: {e}")
            return False

    def start_monitoring(self):
        """开始监控直播间"""
        if not self.initialize_client():
            self.logger.error("客户端初始化失败，无法开始监控")
            return

        try:
            self.running = True
            self.logger.info("开始监控直播间")

            with self.client:
                self.client.run()

        except Exception as e:
            self.logger.error(f"监控过程中发生错误: {e}")
        finally:
            self.running = False
            self.logger.info("监控已停止")

# ========== 主程序 ==========
# if __name__ == "__main__":
#     print("[调试] B站直播间管理系统启动")

#     # 检查配置
#     if not Config.ACCESS_KEY_ID or not Config.ACCESS_KEY_SECRET:
#         print("[错误] 请在Config中设置ACCESS_KEY_ID和ACCESS_KEY_SECRET")
#         exit(1)

#     if not Config.ROOM_DISPLAY_ID:
#         print("[错误] 请在Config中设置ROOM_DISPLAY_ID")
#         exit(1)

#     try:
#         # 创建房间管理器
#         manager = RoomManager()

#         # 开始监控
#         manager.start_monitoring()

#     except KeyboardInterrupt:
#         print("\n[调试] 收到程序中断信号")
#     except Exception as e:
#         print(f"[错误] 程序运行失败: {e}")
#         print(f"[调试] 错误详情: {traceback.format_exc()}")

#     print("[调试] 程序结束")
