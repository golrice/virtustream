import asyncio
import logging
import socketio
from constant import IUSER, MAX_MESSAGES_LEN_FROM_GAME
from modules.injection import Injection
from signals import Signals
from modules.module import Module
import re

from utils import get_logger

class Game(Module):
    def __init__(self, signals: Signals, enable: bool):
        super().__init__(signals, enable)
        self._logger = get_logger("Game")
        self._io = socketio.AsyncClient()
        self._start_game = False
        # 创建两个TCP服务器
        self._tcp_server_rec = None  # 接收日志的服务器（12345端口）
        self._tcp_server_send = None  # 发送步骤的服务器（12346端口）
        self.prompt_injection = Injection("", IUSER)
        self.step_from_user = []
        
        @self._io.event
        async def chat_message(data):
            # 处理来自outerServer的消息
            self._logger.info(f"Received from outerServer: {data}")
            if data == "开始中国象棋游戏":
                pass
            pattern = r"请这样下棋.(([a-z][0-9]){2})"
            err_pattern1 = r"请这样下棋"
            err_pattern2 = r"(([a-z][0-9]){2})"
            match = re.search(pattern, data)
            # step = match.group(1)
            if match and match.group(1) not in self.step_from_user:
                # 这里可以想办法把东西传过去
                # self.step_from_user.append(match.group(1))
                match_step = match.group(1)
                if match_step[0] > 'h' or match_step[2] > 'h' or match_step[1] == '0' or match_step[1] == '9' or match_step[3] == '0' or match_step[3] == '9':
                    txt = "用户使用了超出棋盘范围的坐标，可以调侃观众：棋子飞出棋盘啦，飞出棋盘的棋子记得放到盖子里哦~"
                    self._signals.recentMessages.append(txt)
                    # 保持最近消息列表长度不超过最大值
                    self._signals.recentMessages = self._signals.recentMessages[:MAX_MESSAGES_LEN_FROM_GAME]
                else:
                    self.step_from_user.append(match.group(1))
                print(self.step_from_user)
            elif re.search(err_pattern1, data) or re.search(err_pattern2, data):
                txt = "用户使用了错误的指令，可以告诉他们正确的使用样例是：请这样下棋：a1a2\n"
                self._signals.recentMessages.append(txt)
                # 保持最近消息列表长度不超过最大值
                self._signals.recentMessages = self._signals.recentMessages[:MAX_MESSAGES_LEN_FROM_GAME]
        
        @self._io.event
        async def connect():
            self._logger.info("Game connected to server!")
        
        @self._io.event
        async def disconnect():
            self._logger.warning("Game disconnected from server!")
    
    async def _handle_tcp_rec_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理接收日志的TCP长连接（12345端口）"""
        addr = writer.get_extra_info('peername')
        self._logger.info(f"New TCP connection from {addr}")
        
        try:
            while not self._signals.terminate:  # 持续监听直到终止信号
                try:
                    # 设置读取超时为0.5秒
                    data = await asyncio.wait_for(reader.read(1024), timeout=0.5)
                    
                    if not data:  # 连接被客户端关闭
                        self._logger.info(f"Client {addr} disconnected")
                        break
                        
                    message = data.decode().strip()
                    if message:
                        self._logger.info(f"Received log via TCP: {message}")
                        
                        # 将消息添加到最近消息列表中
                        self._signals.recentMessages.append(f"Log: {message}")
                        
                        # 保持最近消息列表长度不超过最大值
                        if len(self._signals.recentMessages) > MAX_MESSAGES_LEN_FROM_GAME:
                            self._signals.recentMessages.pop(0)
                        
                        # 可以选择发送响应确认
                        # writer.write(b"ACK\n")
                        # await writer.drain()
                    
                except asyncio.TimeoutError:
                    # 超时后继续循环，检查终止信号
                    continue
                except Exception as e:
                    self._logger.error(f"Error reading from TCP connection: {e}")
                    break
                
        except Exception as e:
            self._logger.error(f"Error in TCP connection loop: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
            self._logger.info(f"Closed TCP connection from {addr}")
    
    async def _handle_tcp_send_connection(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """处理发送步骤的TCP连接（12340端口）"""
        try:
            if self.step_from_user:
                send_msg = ""
                for i,step in enumerate(self.step_from_user):
                    send_msg += step
                    if i == len(self.step_from_user) - 1:
                        continue
                    send_msg += ","
                writer.write(send_msg.encode())
                self.step_from_user.clear()
                await writer.drain()
                self._logger.info(f"Sent step via TCP: {send_msg}")
            else:
                print("nothing to send")
        except Exception as e:
            self._logger.error(f"Error handling TCP connection: {e}")
        finally:
            writer.close()
            await writer.wait_closed()
    
    # 为llm提供prompt注入的信息
    def get_prompt_injection(self):
        if len(self._signals.recentMessages) > 0:
            output = "\nThese are recent messages from chess game:\n"
            for idx, message in enumerate(self._signals.recentMessages):
                output += f"{idx + 1}: {message}\n"

            output += "Pick the highest quality message with the most potential for an interesting answer and respond to them.\n"
            self.prompt_injection.text = output
        else:
            self.prompt_injection.text = ""
        return self.prompt_injection

    async def run(self):
        # 创建TCP服务器监听12345端口（接收日志）
        self._tcp_server_rec = await asyncio.start_server(
            self._handle_tcp_rec_connection, 
            '127.0.0.1',  # 只监听本地回环地址
            12345
        )
        self._logger.info("TCP log receiver started on port 12345")
        
        # # 创建TCP服务器监听12346端口（发送步骤）
        self._tcp_server_send = await asyncio.start_server(
            self._handle_tcp_send_connection,
            '127.0.0.1',
            12340
        )
        self._logger.info("TCP step sender started on port 12340")
        
        # 连接到Socket.IO服务器
        await self._io.connect("http://localhost:8080")

        # 主循环
        while not self._signals.terminate:
            await asyncio.sleep(0.5)
        await self._io.disconnect()
        
        # 清理TCP服务器
        if self._tcp_server_rec:
            self._tcp_server_rec.close()
            await self._tcp_server_rec.wait_closed()
            self._logger.info("TCP log receiver closed")
        
        if self._tcp_server_send:
            self._tcp_server_send.close()
            await self._tcp_server_send.wait_closed()
            self._logger.info("TCP step sender closed")

    def cleanup(self):
        self._signals.recentMessages = []
    
    @property
    def io(self):
        return self._io