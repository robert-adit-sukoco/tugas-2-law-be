from fastapi import APIRouter, status, HTTPException, WebSocket, WebSocketDisconnect
from utils.rabbit_mq_client import new_connection, create_new_client
from service import chat_rooms_service
from model.Chat import ChatSchema
import asyncio
from global_variables import chat_room_connections 

router = APIRouter(prefix="/chat_room")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_room():
    result = chat_rooms_service.create_chat_room()
    return result
    

@router.get("/{room_id}")
async def check_room_exists(room_id : str):
    client = create_new_client()
    check_exists = client.check_queue_exists(room_id)
    return {"result" : check_exists}



@router.websocket("/ws/connect/{room_id}")
async def connect_to_chat_room(websocket: WebSocket, room_id: str):
    """Endpoint to connect to a chat room"""
    client = create_new_client()
    if not client.check_queue_exists(room_id):
        raise HTTPException(status=status.HTTP_404_NOT_FOUND, detail='room not found')
    
    await websocket.accept()

    # Connect to RabbitMQ
    connection = new_connection()
    channel = connection.channel()

    async def consume_messages(channel):
        print("consuming message")
        # Continuously consume messages from RabbitMQ and send them over WebSocket
        while True:
            method_frame, properties, body = channel.basic_get(queue=room_id, auto_ack=True)
            if method_frame:
                message = body.decode()
                print("Message: " + message)
                try:
                    await websocket.send_text(message)
                except WebSocketDisconnect:
                    print("WebSocket connection closed. Stopping message consumption.")
                    break

            else:
                # Wait for a short interval to avoid busy looping
                await asyncio.sleep(0.1)
    
    await websocket.send_json({"name" : "[SYSTEM]", "message" : "connected to chat"})

    # Declare the dynamic queue
    channel.queue_declare(queue=room_id, durable=True)

    # Store WebSocket connection for this chat room
    if room_id not in chat_room_connections:
        chat_room_connections[room_id] = []
    chat_room_connections[room_id].append(websocket)
    
    try:
        new_channel = new_connection().channel()

        # Start consuming messages from RabbitMQ
        asyncio.create_task(consume_messages(new_channel))
        while True:
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        chat_room_connections[room_id].delete(websocket)



@router.delete("/{room_id}")
async def delete_room(room_id : str):
    pass


@router.post('/{room_id}/send_message', status_code=status.HTTP_201_CREATED)
async def send_message(payload: ChatSchema, room_id : str):
    chat_rooms_service.send_message(
        name=payload.name, 
        message=payload.message, 
        room_id=room_id
    )
    return {"status": "ok"}


