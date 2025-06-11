import asyncio
import logging
import websockets
import json
import random
import uuid

from modules.module import Module
from signals import Signals

class VTuber(Module):
    def __init__(self, signals: Signals, enable: bool, logger: logging.Logger):
        super().__init__(signals, enable)

        self._logger = logger

        # 你的动作列表，对应 motion3.json 的文件名（不带路径和后缀）
        self.motions = [
            "28727ee300564a9ea4aff2e31f2281a9",
            "bb4d960a884942ce8872e295c8345bc0",
            "9411e6e8bcf847f18fcc02c2ccdf1612",
            "1027fad1430547df9d0392666d71388c",
            "cd1c3cc338c345a1990c2e253982437e",
            "6016c8141de542b3a071933dbf7fc600",
            "38e7ea08123d4423888c2189091b3432",
            "f8fb9a7712e74ef283bfbf6e50b55ee0",
            "02c935e6fe0343f6a4aaa88bc19a7796"
        ]
        
        self.mottim = {
            "28727ee300564a9ea4aff2e31f2281a9":5.1,
            "bb4d960a884942ce8872e295c8345bc0":5.6,
            "9411e6e8bcf847f18fcc02c2ccdf1612":6.2,
            "1027fad1430547df9d0392666d71388c":6.6,
            "cd1c3cc338c345a1990c2e253982437e":8.8,
            "6016c8141de542b3a071933dbf7fc600":6.8,
            "38e7ea08123d4423888c2189091b3432":7.3,
            "f8fb9a7712e74ef283bfbf6e50b55ee0":8.5,
            "02c935e6fe0343f6a4aaa88bc19a7796":6.4
        }
        
        self.expr = {
            "高兴": "65846363556842d9ac5ad76b2bafaa57",
            "生气": "c765df8e356e41d58741951d0d35d0fd",
            "伤心": "d679e6c2c22b4cf394e753d2432c7425",
            "中性": "e0ee3bd63868410985e654315be8d9aa",
            "激动": "0d0ba3c043a14ab080e3a20d19524ac0",
            "无语": "a11c3a0786fb432aa2b399f8d8202052",
            "坏笑": "4f736d47be1d4126baa30dd28c826705"
        }
    
    # a24f6e40fe174d4ea50499853b02ac4c 
    # 请求模板
    def create_request(self, message_type, data={}):
        return {
            "apiName": "VTubeStudioPublicAPI",
            "apiVersion": "1.0",
            "requestID": str(uuid.uuid4()),
            "messageType": message_type,
            "data": data
        }
    
    # 播放指定动作
    async def play_motion(self, ws, motion_name):
        request = self.create_request("HotkeyTriggerRequest", {
            "hotkeyID": motion_name
        })
        await ws.send(json.dumps(request))
        print(f" 触发动作：{motion_name}")
        response2 = await ws.recv()
    
    async def run_vtube_studio_client(self):
        uri = "ws://localhost:8001"  # 默认本地端口 
        async with websockets.connect(uri) as ws:
            
            request1={
    	        "apiName": "VTubeStudioPublicAPI",
    	        "apiVersion": "1.0",
    	        "requestID": "SomeID",
    	        "messageType": "AuthenticationTokenRequest",
    	        "data": {
    	            "pluginName": "wytl",
    	            "pluginDeveloper": "wytl"
    	        }
            }
            
            await ws.send(json.dumps(request1))
            response = await ws.recv()
            response_dict = json.loads(response)
            print("收到响应：", response)
            request2={
    	        "apiName": "VTubeStudioPublicAPI",
    	        "apiVersion": "1.0",
    	        "requestID": "SomeID",
    	        "messageType": "AuthenticationRequest",
    	        "data": {
    		        "pluginName": "wytl",
    		        "pluginDeveloper": "wytl",
    	            "authenticationToken": response_dict["data"]["authenticationToken"]
                }
            }
            
            await ws.send(json.dumps(request2))
            response1 = await ws.recv()
            print("收到响应：", response1)
    
            while not self._signals.terminate:
                # 随机选择动作
                motion = random.choice(self.motions)
                await self.play_motion(ws, motion)
                await asyncio.sleep(self.mottim[motion])  
    
    async def control_vtube_expression_stream(self):
        uri = "ws://localhost:8001"  # 默认本地端口 
        async with websockets.connect(uri) as ws:
            
            request1={
    	        "apiName": "VTubeStudioPublicAPI",
    	        "apiVersion": "1.0",
    	        "requestID": "SomeID1",
    	        "messageType": "AuthenticationTokenRequest",
    	        "data": {
    	            "pluginName": "ltyw",
    	            "pluginDeveloper": "ltyw"
    	        }
            }
            await asyncio.sleep(8)
            await ws.send(json.dumps(request1))
            response = await ws.recv()
            response_dict = json.loads(response)
            print("收到响应：", response)
            request2={
    	        "apiName": "VTubeStudioPublicAPI",
    	        "apiVersion": "1.0",
    	        "requestID": "SomeID1",
    	        "messageType": "AuthenticationRequest",
    	        "data": {
    		        "pluginName": "ltyw",
    		        "pluginDeveloper": "ltyw",
    	            "authenticationToken": response_dict["data"]["authenticationToken"]
                }
            }
            
            await ws.send(json.dumps(request2))
            response1 = await ws.recv()
            print("收到响应：", response1)
    
            temex="初始"
            temsp=False
    
            while not self._signals.terminate:
                if temex!=self._signals._AI_expres:
                    if temsp==True :
                        await self.play_motion(ws, self.expr[temex])
                    else:
                        while self._signals._AI_speaking==False:
                            temsp=False
                        temsp=True
                    temex=self._signals._AI_expres
                    await self.play_motion(ws, self.expr[temex])
                if self._signals._AI_speaking==False and temsp==True:
                    temsp=False
                    await self.play_motion(ws, self.expr[temex])
    
    def init_vtube_studio_client(self):
        asyncio.run(self.run_vtube_studio_client())
    
    def init_expression_stream(self):
        asyncio.run(self.control_vtube_expression_stream())
    
    # async def connect_and_start(self, signals):
    #     t1 = threading.Thread(target=self.run_async_task, args=(signals,))
    #     t2 = threading.Thread(target=self.run_async_task1, args=(signals,))
    #     t1.start()
    #     t2.start()
    #     t1.join()
    #     t2.join()
    #     print("主程序结束")
    