from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from typing import Optional

class MessageContent(BaseModel):
    text: Optional[str] = Field(None, example="Please activate Data_1_GB")
    image: Optional[str] = Field(None, example="base64_encoded_image_data")

class MessageItem(BaseModel):
    messageTime: str = Field(..., example="2024-07-30T10:15:30Z")
    messageId: str = Field(..., example="msg-789")
    source: str = Field(..., example="ui")
    status: str = Field(..., example="success")
    messageType: str = Field(..., example="text")
    payload: MessageContent

# ... (rest of the file remains the same)
class User(BaseModel):
    name: str = Field(..., example="USER123")
    phoneNumber: str = Field(..., example="1234567899")

class ConversationRequest(BaseModel):
    conversationId: str = Field(..., example="conv-12345")
    currentMessage: MessageItem
    sender: User
    previousMessages: List[MessageItem] = Field(default=[])

class Message(BaseModel):
    role: str = Field(..., example="user")
    content: str = Field(..., example="Please activate Data_1_GB")

class GreetingRequest(BaseModel):
    sender: User

