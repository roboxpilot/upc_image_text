from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, Union
from models.product_models import ProductMessage

# schemas.py
from pydantic import BaseModel



class CurrentMessage(BaseModel):
    messageTime: Optional[str] = Field(None, exclude=True)
    messageId: Optional[str] = Field(None, exclude=True)
    source: str = Field(default="AI")
    status: str = Field(default="success")
    messageType: str = Field(default="text")
    payload: Union[Dict[str, Any], str, ProductMessage]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {
            # Add any custom JSON encoders here if needed
        }
        exclude_none = True

class PlanResponse(BaseModel):
    conversationId: Optional[str] = Field(None, example="conv-12345", exclude=True)
    currentMessage: Optional[CurrentMessage] = Field(None, example={
        "messageTime": "2024-08-02T10:53:07.954204Z",
        "messageId": "msg-789",
        "source": "AI",
        "status": "success",
        "messageType": "text",
        "payload": {"text": "Hello! How can I assist you today?"}
    })

    class Config:
        json_encoders = {
            # Add any custom JSON encoders here if needed
        }
        exclude_none = True

class PlanResponseBack(BaseModel):
    conversationId: Optional[str] = Field(None, example="conv-12345")
    currentMessage: Optional[CurrentMessage] = Field(None, example={
        "messageTime": "2024-08-02T10:53:07.954204Z",
        "messageId": "msg-789",
        "source": "AI",
        "status": "success",
        "messageType": "text",
        "payload": {"text": "Hello! How can I assist you today?"}
    })

class ConformationMessage(BaseModel):
    value: str =  Field(..., example="true")