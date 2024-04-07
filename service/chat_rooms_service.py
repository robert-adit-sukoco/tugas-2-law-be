from utils.rabbit_mq_client import create_new_client, new_connection
from uuid import uuid4


def create_chat_room():
    new_id = str(uuid4())
    room_id = f"chat_room_{new_id}"
    
    # Connect to RabbitMQ
    connection = new_connection()
    channel = connection.channel()

    # Declare the dynamic queue
    channel.queue_declare(queue=room_id, durable=True)

    return {"room_id": room_id}



def send_message(name : str, message : str, room_id : str):
    try:
        client = create_new_client()
        if not client.check_queue_exists(queue_name=room_id):
            return False
        client.send_message(sender_name=name, message=message, queue_name=room_id)
        return True
    except:
        return False


def list_chat_rooms():
    pass