import json
from services.ai_client_service import make_classification_call
from utils.prompts import PRODUCT_CONVERSATION_CLASSIFIER_PROMPT
from logger import setup_logger

logger = setup_logger(__name__)


def is_product_related(message: str) -> bool:
    """
    Check if the given message is related to product creation using LLM.
    """
    logger.info("Checking if message is product-related")
    prompt = PRODUCT_CONVERSATION_CLASSIFIER_PROMPT.format(message=message)
    response_data =None
    response =None
    try:
        logger.debug(f"Sending classification prompt to AI: {prompt[:100]}...")  # Log first 100 chars of prompt
        response = make_classification_call(prompt)
        logger.debug(f"Received classification response: {response}")

        response_data = json.loads(response)
        classification = response_data['classification']
        logger.info(f"Message classified as: {classification}")

        return classification == 'product_related'
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {str(e)}")
        logger.debug(f"Raw response that caused the error: {response}")
        # Fallback: assume it's product-related to err on the side of caution
        return True
    except KeyError as e:
        logger.error(f"KeyError in classification response: {str(e)}")
        logger.debug(f"Response data that caused the error: {response_data}")
        # Fallback: assume it's product-related to err on the side of caution
        return True
    except Exception as e:
        logger.error(f"Unexpected error in classification: {str(e)}", exc_info=True)
        # Fallback: assume it's product-related to err on the side of caution
        return True