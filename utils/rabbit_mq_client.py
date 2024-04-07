import pika
import json
from aio_pika import connect_robust
from fastapi.logger import logger


HOSTNAME = 'localhost'


def new_connection() -> pika.BlockingConnection:
    connection_params = pika.ConnectionParameters(host=HOSTNAME)
    connection = pika.BlockingConnection(connection_params)
    return connection

class RabbitMQClient:

    # https://itracer.medium.com/rabbitmq-publisher-and-consumer-with-fastapi-175fe87aefe1


    def __init__(self, connection : pika.BlockingConnection):
        self.connection = connection
        self.channel = connection.channel()
        print('Successfully initialized connection with Rabbit MQ Server')



    # async def consume(self, loop):
    #     """Setup message listener with the current running loop"""
        
    #     connection = await connect_robust(host=self.hostname, port=5672, loop=loop)
    #     channel = await connection.channel()
    #     queue = await channel.declare_queue('foo_consume_queue')
    #     await queue.consume(self.process_incoming_message, no_ack=False)
    #     return connection
    
    # async def process_incoming_message(self, message):
    #     """Processing incoming message from RabbitMQ"""
    #     message.ack()
    #     body = message.body
    #     print('Received message')
    #     if body:
    #         self.process_callable(json.loads(body))

    def send_message(self, sender_name : str, message : str, queue_name : str):
        """Method to publish message to RabbitMQ"""

        message_obj = {
            "name" : sender_name,
            "message" : message
        }

        if self.check_queue_exists(queue_name):
            print("queue exists")

            try:
                self.channel.queue_declare(queue=queue_name, durable=True)
                print("connection with queue declared")

                self.channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(message_obj)
                )
                print("message sent")
            except Exception as e:
                print("Got an exception: " + str(e))
            return True
        else:
            print("queue not exist")
            return False


    
    def flush_connection(self) -> None:
        """Close the RabbitMQ connection."""
        self.channel.close()


    def connect_to_queue(self, queue_name : str, force_new : bool = False):
        """Declare and connect to a queue."""
        try:
            if force_new or not self.check_queue_exists(queue_name):
                self.channel.queue_declare(queue=queue_name, durable=True)
        except pika.exceptions.ChannelClosedByBroker as e:
            raise RuntimeError(f"Error connecting to queue '{queue_name}': {e}") from e

    
    def check_queue_exists(self, queue_name : str):
        """Check if a queue exists."""
        try:
            self.channel.queue_declare(queue=queue_name, passive=True)
            return True
        except pika.exceptions.ChannelClosedByBroker:
            return False

def create_new_client() -> RabbitMQClient:
    connection = new_connection()
    new_client = RabbitMQClient(connection)
    return new_client