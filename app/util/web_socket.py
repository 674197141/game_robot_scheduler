from starlette.endpoints import WebSocketEndpoint
from typing import Optional,List,Dict
from starlette.websockets import WebSocket,WebSocketDisconnect
from loguru import logger
import asyncio

class ConnectionManager:

    # 存放激活的ws连接对象
    active_connections: Dict[int,WebSocket] = {}

    async_callback = {}

    def __init__(self):
        pass

    async def connect(self, ws: WebSocket,user_id:int):
        # 等待连接
        await ws.accept()
        # 存储ws连接对象
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_json({"msg":"被其他用户t下线"})
            await self.active_connections[user_id].close()
        self.active_connections[user_id] = ws

    def disconnect(self, user_id):
        # 关闭时 移除ws对象
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    @staticmethod
    async def send_personal_message(message: dict, ws: WebSocket):
        # 发送个人消息
        await ws.send_json(message)

    @classmethod
    async def send_user_msg(cls,user_id,message):
        if not user_id in cls.active_connections:
            return {"msg":"错误，客户端未连接"}
        if user_id in cls.active_connections:
            await cls.active_connections[user_id].send_json(message)
            data = await cls.active_connections[user_id].receive_text()
            return data
        return "okokokok"

    async def broadcast(self, message: str):
        # 广播消息
        for connection in self.active_connections.values():
            await connection.send_text(message)

    @classmethod
    async def call_back(cls,user_id,call_back_func_name,data):
        func_name_dc = cls.async_callback.get(user_id,{})
        if func_name_dc == {}:
            logger.error("未找到注册方法")
            return
        func = func_name_dc.get(call_back_func_name,None)
        if func == None:
            logger.error("注册方法为空，逻辑异常")
            return
        await func(data)