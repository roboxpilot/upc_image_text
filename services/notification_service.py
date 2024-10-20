import requests
from typing import Optional


def notify_image_processing(conversation_id: str, notification_message: str = "processing image..") -> Optional[
    requests.Response]:
    """
    Notify an external service about image processing.

    Args:
    conversation_id (str): The ID of the conversation (typically a phone number).
    notification_message (str): The notification message to send. Defaults to "processing image..".

    Returns:
    Optional[requests.Response]: The response from the external service if successful, None otherwise.
    """
    notification_url = "http://10.0.13.74:8099/BPE/api/v1/message/notification"
    notification_params = {
        "notification": notification_message,
        "conversationId": conversation_id
    }

    try:
        response = requests.post(notification_url, params=notification_params)
        response.raise_for_status()  # Raise an error for bad status codes
        print("Notification sent successfully.")
        return response
    except requests.exceptions.RequestException as e:
        print(f"Failed to send notification: {e}")
        return None