from fastapi import APIRouter
from models.conversation_models import GreetingRequest
from models.response_models import PlanResponse
from services.conversation_service import handle_greeting
from logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.post("/greeting", response_model=PlanResponse)
async def greeting(request: GreetingRequest):
    logger.info(f"Received greeting request for user: {request.sender.name}")
    user_name = request.sender.name
    resp = handle_greeting(user_name)
    logger.debug(f"Greeting response: {resp}")
    return PlanResponse(
        currentMessage={
            "source": "AI",
            "status": "success",
            "messageType": "text",
            "payload": {"text": resp}
        }
    )