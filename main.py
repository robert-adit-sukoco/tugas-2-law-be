from fastapi import FastAPI, APIRouter, WebSocket
from typing import List
from utils.rabbit_mq_client import new_connection
from routers import chat_rooms
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware


RABBIT_MQ_HOSTNAME = 'localhost'


class ChatRoomApp(FastAPI):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_room_connections = {}

    @classmethod
    def log_incoming_message(cls, message: dict):
        """Method to do something meaningful with the incoming message"""
        print('Here we got incoming message %s', message)



app = ChatRoomApp()

default_router = APIRouter(prefix="/api/v1")
default_router.include_router(chat_rooms.router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)




# @app.on_event('startup')
# async def startup():
#     loop = asyncio.get_running_loop()
#     task = loop.create_task(app.rabbit_mq_client.consume(loop))
#     await task

app.include_router(default_router)