import json
from typing import List, Dict, Any
from models.conversation_models import Message
from models.product_models import ProductMessage
from models.response_models import ConformationMessage
from services.ai_client_service import make_api_call, client
import groq
from utils.prompts import Prompts
from exceptions import JSONParseError
from config import Config, ModelType
import instructor
from logger import setup_logger

logger = setup_logger(__name__)

inst_client = instructor.from_groq(client, mode=instructor.Mode.TOOLS)
client_small =  groq.Groq(api_key=Config.get_api_key())
inst_client_small = instructor.from_groq(client_small, mode=instructor.Mode.TOOLS)

from pydantic import BaseModel, Field

class FieldNameResponse(BaseModel):
    field_name: str = Field(default="")

def extract_field(messages: str) -> str:
    """
    Extracts the field name that the user wants to change from conversation messages.
    
    Args:
        messages (str): Conversation messages
        
    Returns:
        str: The name of the field to be changed
    """
    try:
        # Convert messages to string if it's a list
        if isinstance(messages, list):
            messages = json.dumps(messages)
        
        # Explicit prompt for field extraction
        prompt = f"""
        Based on the following conversation, identify the specific field the user wants to change:
        {messages}
        Respond ONLY with the field name. 
        If no clear field is mentioned, return an empty string.
        """
        
        resp = inst_client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[
                {"role": "system", "content": "You are a precise assistant that extracts field names."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000,
            response_model=FieldNameResponse  # Use the Pydantic model here
        )
        
        # Safely extract field name
        field_name = resp.field_name.lower().replace(' ', '_') if resp.field_name else ""
        
        logger.info(f"Extracted field name: {field_name}")
        return field_name
    except Exception as e:
        logger.error(f"Error in field extraction: {str(e)}")
        return ""

def check_change_confirmation(messages: str) -> bool:
    prompt = Prompts.CHANGE_CONFIRMATION_CHECKER.format(message=messages, value="{'value':'true/false'}")
    logger.info("The prompt for change confirmation")
    logger.info(prompt)
    resp = inst_client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        response_model=ConformationMessage,
    )
    resp.model_dump()
    val = resp.model_dump().get("value")
    logger.info(f"The value got for change confirmation is {val}")
    return val.lower() == 'true'

def check_confirmation(messages: str) -> bool:
    prompt = Prompts.CONFIRMATION_MESSAGE_CHECKER.format(message=messages,value = "{'value':'true/false'}")
    logger.info(" the prompt for conformation")
    logger.info(prompt)
    resp = inst_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system",
             "content": "You are a helpful assistant "},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
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
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system",
                         "content": "You are a helpful assistant that extracts information and formats it as JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=1000,
                    response_model=ProductMessage,
                )
                extracted_data = resp.model_dump()
            else:
                json_response = make_api_call(prompt)
                extracted_data = json.loads(json_response)
                
            # Fill in missing or empty values from product_schema
            filled_data = {}
            for key, default_value in product_schema.items():
                extracted_value = extracted_data.get(key)

                if extracted_value == "":  # Only check for empty string
                    # Use default only if the extracted value is an empty string
                    filled_data[key] = default_value if default_value else ""
                    logger.debug(f"Using default value for {key}: {default_value}")
                else:
                    # Retain None or any valid non-empty extracted value
                    filled_data[key] = extracted_value
                    logger.debug(f"Using extracted value for {key}: {extracted_value}")

#             # Fill in missing or empty values from product_schema
#             filled_data = {}
#             for key, default_value in product_schema.items():
#                 # Check if key exists in extracted_data and has a non-empty value
#                 extracted_value = extracted_data.get(key)
#                 is_empty = extracted_value is None or extracted_value == "" or extracted_value == "None"

#                 if is_empty and default_value:  # If extracted value is empty and default exists
#                     filled_data[key] = default_value
#                     logger.debug(f"Using default value for {key}: {default_value}")
#                 else:
#                     filled_data[key] = extracted_value if not is_empty else ""
#                     if not is_empty:
#                         logger.debug(f"Using extracted value for {key}: {extracted_value}")

            return filled_data

        except json.JSONDecodeError:
            logger.error("Failed to parse JSON response, retrying...")
            continue
        except Exception as e:
            logger.error(f"Error in extract_plan: {str(e)}", exc_info=True)
            continue

    raise JSONParseError()

def extract_plan1(messages: List[Message], product_schema: Dict[str, Any]) -> Dict[str, Any]:
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
                    max_tokens=1000,
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