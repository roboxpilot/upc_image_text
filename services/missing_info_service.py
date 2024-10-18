import json
from typing import Dict, Any
from fastapi import HTTPException
from config import Config, ModelType
from exceptions import APICallError, JSONParseError
from utils.prompts import Prompts
from models.conversation_models import ConversationRequest
from services.ai_client_service import make_api_call
from logger import setup_logger

logger = setup_logger(__name__)

class MissingInfoAdapter:
    def __init__(self):
        logger.info("Initializing MissingInfoAdapter")

    def generate_missing_info_prompt(self, conversation: ConversationRequest, missing_field: str) -> str:
        logger.debug(f"Generating missing info prompt for field: {missing_field}")
        conversation_history = json.dumps([
            {"role": "user" if msg.source == "ui" else "assistant", "content": msg.payload.text}
            for msg in conversation.previousMessages
        ], indent=2)
        prompt = Prompts.MISSING_INFO_PROMPT.format(
            missing_field=missing_field,
            conversation_history=conversation_history
        )
        logger.debug(f"Generated prompt: {prompt}")
        return prompt

    def process_request(self, request: ConversationRequest) -> str:
        try:
            logger.info(f"missing info request : {request}")
            missing_field = request.currentMessage.payload.text
            logger.info(f"Processing missing info request for field: {missing_field}")
            prompt = self.generate_missing_info_prompt(request, missing_field)
            response = make_api_call(prompt)
            logger.debug(f"Missing info response: {response.strip()}")
            return response.strip()
        except KeyError as e:
            logger.error(f"Missing key in request data: {str(e)}")
            raise HTTPException(status_code=400, detail=f"Missing key in request data: {str(e)}")
        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response")
            raise JSONParseError()