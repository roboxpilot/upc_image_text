from services.ai_client_service import make_image_api_call
from utils.prompts import Prompts
from logger import setup_logger

logger = setup_logger(__name__)

class ImageProcessor:
    @staticmethod
    def extract_image_content(image_data: str) -> str:
        logger.info("Extracting content from image")
        content = make_image_api_call(Prompts.IMAGE_PRODUCT_EXTRACTION, image_data)
        logger.debug(f"Extracted image content: {content}")
        return content