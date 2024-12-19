from fastapi import APIRouter, HTTPException, FastAPI
from markdown_it.rules_inline import image
import threading
import  time
from services.notification_service import  notify_image_processing
from models.conversation_models import ConversationRequest
from models.response_models import PlanResponse
from services.conversation_service import handle_conversation, handle_conversation_general
from services.plan_extractor_service import extract_plan, check_confirmation, form_final_message, check_change_confirmation,extract_field
from services.image_processor_service import ImageProcessor
from utils.helpers import is_product_related
import requests
import json
from datetime import datetime
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
    
    conv_start = time.time()
    
    logger.info(f"Received conversation request for conversation ID: {request.conversationId}")
    image_boolean = False
    try:
        conversationId = request.sender.phoneNumber
        print("Conversation ID:", conversationId)

        # Handle image messages
        if request.currentMessage.messageType == "image":
            image_boolean = True
            image_processing_start = time.time()
            logger.info("Starting image processing")

            # Notify the external service about the image processing
            notification_url = "http://10.0.13.74:8099/BPE/api/v1/message/notification"
            notification_params = {
                "notification": "processing image..",
                "conversationId": request.sender.phoneNumber
            }
            try:
                response = requests.post(notification_url, params=notification_params)
                response.raise_for_status()
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
            final = time.time()
            handle_start = time.time()
            logger.info("Starting to handle conversation")
            extracted_plan = await handle_conversation(request)
            handle_end = time.time()
            logger.info(f"extracted_plan Handling conversation completed in {handle_end - handle_start:.2f} seconds")
            logger.debug(f"Extracted plan: {extracted_plan}")

            if image_boolean:
                final_message = form_final_message(extracted_plan)
                logger.info("Sending final confirmation message")
                image_processing_end = time.time()
                logger.info(f"Image processing completed in {image_processing_end - image_processing_start:.2f} seconds")
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
            filtered_messages_c = formatted_messages[-1:]
            print("MESSAFEGVGGHJGVJH---------------------",filtered_messages)
            messages_filtered = json.dumps(filtered_messages, indent=2)
            messages_filtered_c = json.dumps(filtered_messages_c, indent=2)
            print("MESSAFEGVGGHJGVJH---------------------",messages_filtered)

            if not check_confirmation(messages_filtered):
                logger.info("Confirmation not provided, checking for change confirmation.")
                change_time = None
                if not check_change_confirmation(messages_filtered):
                    change_time = time.time()
                    final_message = form_final_message(extracted_plan)
                    final_e = time.time()
                    logger.info(f"extract plan to final message template in {final_e - final:.2f} seconds")
                    logger.info("Sending final message as confirmation and change confirmation are both false.")
                    
                    return PlanResponse(
                        conversationId=request.conversationId,
                        currentMessage={
                            "source": "AI",
                            "status": "success",
                            "messageType": "text",
                            "payload": {"text": final_message}
                        }
                    )
                else:
                    change_time = time.time()
                    logger.info("Change confirmation is true. Reordering extracted plan.")
                    field_to_change = extract_field(messages_filtered)
                    # Define dummy values for different types of fields
                    dummy_values = {
                        'product_name': 'Unnamed Product',
                        'product_description': 'No description provided',
                        'product_family': 'GSM',
                        'product_group': 'Prepaid',
                        'product_offer_price': '0.00',
                        'pop_type': 'Normal',
                        'price_category': 'Base Price',
                        'price_mode': 'Non-Recurring',
                        'product_specification_type': 'ADDON',
                        'data_allowance': '0GB',
                        'voice_allowance': '0 Minutes'
                    }
                    # Create a new plan with dummy values
                    reordered_plan = {}
                    for key in extracted_plan.keys():
                        if key == field_to_change:
                            # Keep the original value as None for the field to change
                            reordered_plan[key] = None
                        else:
                            # Fill with dummy value if exists, otherwise use None
                            reordered_plan[key] = dummy_values.get(key, None)
                    

#                     reordered_plan = {}
#                     if field_to_change and field_to_change in extracted_plan:
#                         reordered_plan[field_to_change] = extracted_plan[field_to_change]
#                         for key, value in extracted_plan.items():
#                             if key != field_to_change:
#                                 reordered_plan[key] = value
#                     else:
#                         reordered_plan = extracted_plan

                    print("---------------------------------------------------------------------------",reordered_plan)
                    change_e = time.time()
                    logger.info(f"CHANGE TIME CHECK {change_e - change_time:.2f} seconds")

                    return PlanResponse(
                        conversationId=request.conversationId,
                        currentMessage={
                            "source": "AI",
                            "status": "success",
                            "messageType": "product",
                            "payload": reordered_plan
                        }
                    )
            else:
                logger.info("Confirmation is true. Sending extracted plan as product response.")
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
           
            gen_start = time.time()
            logger.info("Handling general conversation")
            response = handle_conversation_general(messages)
            gen_end = time.time()
            logger.info(f"general Handling conversation completed in {gen_end - gen_start:.2f} seconds")
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


    #         # Convert the filtered messages to JSON format with indentation
    #         messages_filtered= json.dumps(filtered_messages, indent=2)
            
    #         if not check_confirmation(messages_filtered): #if false means will form a final message else 
    #             final_message = form_final_message(extracted_plan)
    #             logger.info("Sending final confirmation message")
    #             return PlanResponse(
    #                 conversationId=request.conversationId,
    #                 currentMessage={
    #                     "source": "AI",
    #                     "status": "success",
    #                     "messageType": "text",
    #                     "payload": {"text": final_message}
    #                 }
    #             )
    #         logger.info(f"not conformation sendeinf {json.dumps(extracted_plan)}")
    #         return PlanResponse(
    #             conversationId=request.conversationId,
    #             currentMessage={
    #                 "source": "AI",
    #                 "status": "success",
    #                 "messageType": "product",
    #                 "payload": extracted_plan
    #             }
    #         )
    #     else:
    #         logger.info("Handling general conversation")
    #         response = handle_conversation_general(messages)
    #         logger.debug(f"General conversation response: {response}")

    #         return PlanResponse(
    #             conversationId=request.conversationId,
    #             currentMessage={
    #                 "source": "AI",
    #                 "status": "success",
    #                 "messageType": "text",
    #                 "payload": {"text": response}
    #             }
    #         )
    # except Exception as e:
    #     logger.error(f"Error in conversation_endpoint: {str(e)}", exc_info=True)
    #     raise HTTPException(status_code=500, detail=str(e))
