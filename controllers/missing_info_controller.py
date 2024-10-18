from fastapi import APIRouter, HTTPException
from models.conversation_models import ConversationRequest
from models.response_models import PlanResponse
from services.missing_info_service import MissingInfoAdapter
from datetime import datetime
from logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()

@router.post("/handle_missing_info", response_model=PlanResponse)
async def handle_missing_info(request: ConversationRequest):
    logger.info(f"Received missing info request for conversation ID: {request.conversationId}")
    adapter = MissingInfoAdapter()
    try:
        response = adapter.process_request(request)
        logger.debug(f"Missing info response: {response}")
        return PlanResponse(
            conversationId=request.conversationId,
            currentMessage={
                "messageTime": datetime.utcnow().isoformat() + "Z",
                "messageId": request.currentMessage.messageId,
                "source": "AI",
                "status": "success",
                "messageType": "text",
                "payload": {"text": response}
            }
        )
    except HTTPException as e:
        logger.error(f"Error in handle_missing_info: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")