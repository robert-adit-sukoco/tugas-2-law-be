from pydantic import BaseModel


class ChatSchema(BaseModel):
    name : str
    message : str