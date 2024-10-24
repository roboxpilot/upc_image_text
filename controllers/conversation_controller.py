from fastapi import APIRouter, HTTPException, FastAPI
from markdown_it.rules_inline import image
import threading
import  time
from services.notification_service import  notify_image_processing
from models.conversation_models import ConversationRequest
from models.response_models import PlanResponse
from services.conversation_service import handle_conversation, handle_conversation_general
from services.plan_extractor_service import extract_plan, check_confirmation, form_final_message
from services.image_processor_service import ImageProcessor
from utils.helpers import is_product_related
import requests
import json
from logger import setup_logger

logger = setup_logger(__name__)

router = APIRouter()
def periodic_notifications(conversationId, stop_event):
    messages = [
        "Processing your image...",
        "This might take a few more seconds...",
        "Almost there! Thanks for your patience.",
        "Just a bit longer...",
        "Finalizing the image processing..."
    ]
    message_index = 0
    while not stop_event.is_set():
        notify_image_processing(conversationId, messages[message_index])
        message_index = (message_index + 1) % len(messages)
        time.sleep(2)  # Wait for 2 seconds before sending the next notification

@router.post("/conversation", response_model=PlanResponse)
async def conversation_endpoint(request: ConversationRequest):
    logger.info(f"Received conversation request for conversation ID: {request.conversationId}")
    image_boolean = False
    try:
        # print("Received request", request.dict())
        conversationId = request.sender.phoneNumber
        print("IDDDDDDDDDDD", conversationId)
        # Handle image messages
        if request.currentMessage.messageType == "image":
            image_boolean = True
            # Notify the external service about the image processing
            notification_url = "http://10.0.13.74:8099/BPE/api/v1/message/notification"
            notification_params = {
                "notification": "processing image..",
                "conversationId": request.sender.phoneNumber
            }
            try:
                response = requests.post(notification_url, params=notification_params)
                response.raise_for_status()  # Raise an error for bad status codes
                print("Notification sent successfully.")
            except requests.exceptions.RequestException as e:
                print(f"Failed to send notification: {e}")

            logger.info("Processing image message")
            stop_event = threading.Event()
            notification_thread = threading.Thread(target=periodic_notifications, args=(conversationId, stop_event))
            notification_thread.start()
            image_processor = ImageProcessor()
            image_data = request.currentMessage.payload.text

            extracted_content = image_processor.extract_image_content(image_data)
            logger.debug(f"Extracted content from image: {extracted_content}")
            stop_event.set()
            notification_thread.join()
            # Replace the image payload with the extracted content
            request.currentMessage.payload.text = extracted_content
            request.currentMessage.messageType = "text"
            request.currentMessage.payload.text = extracted_content

        all_messages = request.previousMessages + [request.currentMessage]
        formatted_messages = [
            {
                "role": "user" if msg.source == "ui" else "assistant",
                "content": msg.payload.text
            } for msg in all_messages
        ]
        messages = json.dumps(formatted_messages, indent=2)
        logger.debug(f"Formatted messages: {messages}")

        if is_product_related(messages):
            logger.info("Conversation is product-related")
            extracted_plan = await handle_conversation(request)
            logger.debug(f"Extracted plan: {extracted_plan}")
#             if all(value is not None and value != "" for key, value in extracted_plan.items() if
# key != "product_description"):
            if image_boolean:
                # if check_confirmation(messages):
                #     logger.info("Product creation confirmed")
                #     final_message = "the product has been created successfully "
                #     return PlanResponse(
                #         conversationId=request.conversationId,
                #         currentMessage={
                #             "source": "AI",
                #             "status": "success",
                #             "messageType": "product",
                #             "payload": extracted_plan
                #         }
                #     )

                final_message = form_final_message(extracted_plan)
                logger.info("Sending final confirmation message")
                return PlanResponse(
                    conversationId=request.conversationId,
                    currentMessage={
                        "source": "AI",
                        "status": "success",
                        "messageType": "text",
                        "payload": {"text": final_message}
                    }
                )

            for key, value in extracted_plan.items():
                if value == "0":
                    extracted_plan[key] = "None"
            logger.debug(f"Final extracted plan: {json.dumps(extracted_plan, indent=2)}")
            filtered_messages = formatted_messages[-2:]

            # Convert the filtered messages to JSON format with indentation
            messages_filtered= json.dumps(filtered_messages, indent=2)
            if not check_confirmation(messages_filtered):
                final_message = form_final_message(extracted_plan)
                logger.info("Sending final confirmation message")
                return PlanResponse(
                    conversationId=request.conversationId,
                    currentMessage={
                        "source": "AI",
                        "status": "success",
                        "messageType": "text",
                        "payload": {"text": final_message}
                    }
                )
            logger.info(f"not conformation sendeinf {json.dumps(extracted_plan)}")
            return PlanResponse(
                conversationId=request.conversationId,
                currentMessage={
                    "source": "AI",
                    "status": "success",
                    "messageType": "product",
                    "payload": extracted_plan
                }
            )
        else:
            logger.info("Handling general conversation")
            response = handle_conversation_general(messages)
            logger.debug(f"General conversation response: {response}")

            return PlanResponse(
                conversationId=request.conversationId,
                currentMessage={
                    "source": "AI",
                    "status": "success",
                    "messageType": "text",
                    "payload": {"text": response}
                }
            )
    except Exception as e:
        logger.error(f"Error in conversation_endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))