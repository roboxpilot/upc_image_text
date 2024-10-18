from config import Config, ModelType
from exceptions import APICallError
import groq
import openai
import anthropic
import instructor
from logger import setup_logger

logger = setup_logger(__name__)

client = None
image_client = None

def initialize_clients():
    global client, image_client
    logger.info("Initializing AI clients")
    if Config.SELECTED_MODEL == ModelType.GROQ:
        client = groq.Groq(api_key=Config.get_api_key())
        logger.info("Initialized Groq client")
    elif Config.SELECTED_MODEL == ModelType.OPENAI:
        client = openai.OpenAI(api_key=Config.get_api_key())
        logger.info("Initialized OpenAI client")
    elif Config.SELECTED_MODEL == ModelType.CLAUDE:
        client = anthropic.Anthropic(api_key=Config.get_api_key())
        logger.info("Initialized Claude client")
    else:
        logger.error(f"Invalid model selected: {Config.SELECTED_MODEL.value}")
        raise APICallError(Config.SELECTED_MODEL.value, "Invalid model selected")

    # Always use OpenAI for image processing
    image_client = instructor.patch(openai.OpenAI(api_key=Config.get_api_key(ModelType.OPENAI)))
    logger.info("Initialized OpenAI image client")

def make_api_call(prompt: str) -> str:
    try:
        logger.info(f"Making API call to {Config.SELECTED_MODEL.value}")
        if Config.SELECTED_MODEL == ModelType.GROQ:
            response = client.chat.completions.create(
                model=Config.get_model_name(),
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that extracts information and formats it as JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=400
            )
            logger.debug(f"Groq API response: {response.choices[0].message.content}")
            return response.choices[0].message.content
        elif Config.SELECTED_MODEL == ModelType.OPENAI:
            response = client.chat.completions.create(
                model=Config.get_model_name(),
                messages=[
                    {"role": "system",
                     "content": "You are a helpful assistant that extracts information and formats it as JSON."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=200
            )
            logger.debug(f"OpenAI API response: {response.choices[0].message.content}")
            return response.choices[0].message.content
        elif Config.SELECTED_MODEL == ModelType.CLAUDE:
            response = client.completions.create(
                model=Config.get_model_name(),
                prompt=f"Human: {prompt}\n\nAssistant:",
                max_tokens_to_sample=200
            )
            logger.debug(f"Claude API response: {response.completion}")
            return response.completion
    except Exception as e:
        logger.error(f"Error in {Config.SELECTED_MODEL.value} API call: {str(e)}", exc_info=True)
        raise APICallError(Config.SELECTED_MODEL.value, str(e))

def make_image_api_call(prompt: str, image_data: str) -> str:
    try:
        logger.info("Making image API call to OpenAI")
        response = image_client.chat.completions.create(
            model=Config.OPENAI_IMAGE_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{image_data}"}}
                    ]
                }
            ],
            max_tokens=300
        )
        logger.debug(f"OpenAI image API response: {response.choices[0].message.content}")
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error in OpenAI image API call: {str(e)}", exc_info=True)
        raise APICallError(Config.SELECTED_MODEL.value, str(e))

# Initialize clients when this module is imported
initialize_clients()