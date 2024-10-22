import json
from typing import List, Dict, Any
from models.conversation_models import Message
from models.product_models import ProductMessage
from models.response_models import ConformationMessage
from services.ai_client_service import make_api_call, client
from utils.prompts import Prompts
from exceptions import JSONParseError
from config import Config, ModelType
import instructor
from logger import setup_logger
logger = setup_logger(__name__)
inst_client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)
def check_confirmation(messages: str) -> bool:
    prompt = Prompts.CONFIRMATION_MESSAGE_CHECKER.format(message=messages)
    logger.info(" the prompt for conformation")
    logger.info(prompt)
    resp = inst_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant "},
            {"role": "user", "content": prompt}
        ],
        max_tokens=800,
        response_model=ConformationMessage,
    )
    resp.model_dump()
    # response = make_api_call(prompt)
    val = resp.model_dump()
    val =val.get("value")
    logger.info(f" the value got for conformation message is {val}")
    return val.lower() == 'true'


def form_final_message(extracted_plan: Dict[str, Any]) -> str:
    prompt = Prompts.FINAL_MESSAGE_TEMPLATE.format(schema=json.dumps(extracted_plan, indent=2))
    response = make_api_call(prompt)
    return response.strip()


def extract_plan(messages: List[Message], product_schema: Dict[str, Any]) -> Dict[str, Any]:
    formatted_messages = [{"role": msg.role, "content": msg.content} for msg in messages]
    prompt = Prompts.PRODUCT_INFO_EXTRACTION.format(
        messages=json.dumps(formatted_messages, indent=2),
        product_schema=json.dumps(product_schema, indent=2)
    )

    max_retries = 3
    for _ in range(max_retries):
        try:
            if Config.SELECTED_MODEL == ModelType.GROQ:
                inst_client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)
                resp = inst_client.chat.completions.create(
                    model="llama3-70b-8192",
                    messages=[
                        {"role": "system",
                         "content": "You are a helpful assistant that extracts information and formats it as JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=400,
                    response_model=ProductMessage,
                )
                return resp.model_dump()
            else:
                json_response = make_api_call(prompt)
                plan_data = json.loads(json_response)
                return plan_data
        except json.JSONDecodeError:
            continue

    raise JSONParseError()