from typing import List, Dict, Any
from models.conversation_models import MessageItem, Message, ConversationRequest
from services.ai_client_service import make_api_call
from utils.prompts import Prompts
from services.plan_extractor_service import extract_plan
from logger import setup_logger

logger = setup_logger(__name__)

def format_messages(messages: List[MessageItem]) -> List[Message]:
    logger.debug(f"Formatting {len(messages)} messages")
    return [
        Message(
            role="user" if msg.source == "ui" else "assistant",
            content=msg.payload.text
        )
        for msg in messages
    ]

def handle_greeting(username: str) -> str:
    logger.info(f"Handling greeting for user: {username}")
    prompt = Prompts.AI_GREETING_PROMPT.format(user_name=username)
    response = make_api_call(prompt)
    logger.debug(f"Greeting response: {response.strip()}")
    return response.strip()

async def handle_conversation(request: ConversationRequest) -> Dict[str, Any]:
    logger.info(f"Handling conversation for conversation ID: {request.conversationId}")
    all_messages = request.previousMessages + [request.currentMessage]
    if len(all_messages) > 6:
        all_messages = all_messages[-4:]
    formatted_messages = format_messages(all_messages)
    product_schema = {
        "product_name": "",
        "product_description": "",
        "product_family": "GSM",
        "product_group": "Prepaid",
        "product_offer_price": "",
        "pop_type": "Normal",
        "price_category": "Base Price",
        "price_mode": "Non-Recurring",
        "product_specification_type": "ADDON",
        "data_allowance":"",
        "voice_allowance":""
    }
    logger.debug(f"Extracting plan with schema: {product_schema}")
    extracted_plan = extract_plan(formatted_messages, product_schema)
    logger.debug(f"Extracted plan: {extracted_plan}")
    return extracted_plan

def handle_conversation_general(message: str) -> str:
    logger.info("Handling general conversation")
    prompt = Prompts.AI_RESPONSE_PROMPT.format(incoming_message=message)
    response = make_api_call(prompt)
    logger.debug(f"General conversation response: {response.strip()}")
    return response.strip()