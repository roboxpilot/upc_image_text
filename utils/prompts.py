PRODUCT_CONVERSATION_CLASSIFIER_PROMPT = """
You are an AI assistant tasked with determining whether a given conversation message is related to product creation or if it's a general chatbot conversation. Your goal is to classify the message accurately.

Context:
- Product creation conversations typically involve discussing features, specifications, design, manufacturing, prototypes, materials, dimensions, colors, sizes, functions, purposes, target markets, prices, or costs of a product.
- General chatbot conversations can cover a wide range of topics not specifically related to product creation.

Instructions:
1. Carefully analyze the given message.
2. Determine if the message is primarily about product creation or if it's a general conversation.
3. Provide your classification as either "product_related" or "general_conversation".
4. it is product_related if the text is associated with creation of a plan , product 

Message to classify:
{message}

classification (product_related/general_conversation):
give response in only this format  json
"""


class Prompts:
    # CONFIRMATION_MESSAGE_CHECKER = """
    # Please confirm whether confirmation is made by the user by going through the conversations:
    # see if confirmation message: is present in the conversation message
    # if the user said continue with confirmation message its confirmed
    # conversations:
    # {message}
    # Expected output:
    # reply with  only either True or False nothing else
    # """
    CONFIRMATION_MESSAGE_CHECKER = """
Please confirm whether confirmation is made by the user by going through the conversations:
    - Consider it confirmed if the user explicitly states they want to continue or proceed with the full details provided.
    - If the user says "proceed" after receiving all necessary details, count it as confirmation.
    - Ignore conversations where the user asks for changes or where additional information is requested but not yet provided.
    - If the user says "proceed" but hasn't been given all the necessary details yet, do not count it as confirmation.
conversations:
{message}
Expected output:
reply with {value}
    """

    FINAL_MESSAGE_TEMPLATE = """
   reply with confirmation message from the given schema make a bullet point and ask user for confirmation whether they need to update it or continue .
    The Schema :
    {schema}
    Product Specification 
    expected output:

    Confirmation message:

    text message asking for confirmation of the field , not code. 

    Address by saying  Here are the details of your product with all mandatory default parameters enabled

    showcase the keys and values only give the replay
    remove under score from keys and display it in common language
    dont make up new fields 

    no footer or notes.
    and finally ask Would you like to update any of these details or proceed as is?
    
    expected output :
    Please confirm the following details:

Product Name: Wasel Flexi Plan
Product Description: plan offering flexible data and voice options for users.
Product Family: GSM
Product Group: Prepaid
Product Offer Price: 100 AED
POP Type: Normal
Price Category: Base Price
Price Mode: Non-Recurring
Product Specification Type: ADDON
Data Allowance: 10 GB
Voice Allowance: 500 minutes
Would you like to update any of these details or proceed as is?
    """

    PRODUCT_INFO_EXTRACTION = """Extract the following information from the conversation and format it as JSON. Use the exact field names from the provided schema.
     If any field is missing from the conversation, replace it with null.
     carefully look at user and assistant information 
     Conversation:
     {messages}

      Product Schema: {product_schema} Type means basic / add on  it does not include product specification like 1 GB 
      price, 2 GB price etc the price should be in numeric string nothing should follow after that 
      product_offer_price the field means  the price of the product  / cost of the product . anything related to  price extract it in this field 
      special discount price will be Product_offer_price
      keep the default value as it is unless asked to change it 
      extract the data allowance part like 20 gb , 10 mb etc
      extract the voice allowance part like 100 minutes ,100 sec  etc
      Expected output: 
      just  json don't  include any text every value should be string
       I JUST WANT ONLY JSON , NO QUOTES BEFORE OR AFTER IT"""

    IMAGE_PRODUCT_EXTRACTION = """Extract the content from the image and form JSON from it like key and value. 
      The image will be having the following keys: plan name, validity, units (that can be in GB, minutes etc), duration, price"""

    GENERATE_EXTRACT_PROMPT = """
    Given the following product schema, create a prompt that instructs an AI to extract the relevant information from a conversation and format it as JSON. The prompt should include all fields from the schema.

    Product Schema:
    {product_schema}

    Your task is to create a prompt that will be used to extract information based on this schema. The prompt should be clear and concise, instructing the AI to extract all the fields present in the schema and field name should be exact.
    make sure the prompt provides the schema json and the generated prompt says to construct the json with correct field keys as in json . if any keys are missing replace it with json .
    i want the generated response to be minimal 
    Generated Prompt:
    """

    # MISSING_INFO_PROMPT = """
    #   As a sales executive named AARYA (Automated AI Responder for Your Applications), you are having a conversation with a customer about creating a  plan. The customer has provided some information, but the '{missing_field}' is missing. Your task is to generate a polite and professional response asking for the missing information.
    #
    #   Conversation history:
    #   {conversation_history}
    #
    #   Missing information: {missing_field}
    #   here the messages gives out what information is missing extract the missing info from the message
    #
    #   Please generate a response  asking for the missing information .
    #   make it short and simple
    #   make the tune of the message in common language
    #   only give response
    #   """
    MISSING_INFO_PROMPT = """
    As a sales executive named AARYA (Automated AI Responder for Your Applications), you are having a conversation with a customer about creating a plan. The customer has provided some information, but the '{missing_field}' is missing. Your task is to generate a polite and professional response asking for the missing information.

    Conversation history:
    {conversation_history}

    Missing information: {missing_field}
    Based on the conversation, please generate a short and simple response asking for the missing information, in common language. The response should be polite and direct, without including phrases like "Here is a possible response."

    Only provide the response asking for the missing information.
    """

    AI_RESPONSE_PROMPT = """
        You are an AI assistant  who will create product for a customer 

        Instructions:
        1. Carefully analyze the given message.
        2. give a response as a general conversation.

        the incoming message
        {incoming_message}
        give message as a text 
        """

    AI_GREETING_PROMPT = """
        act as AI assistant  who will create product for a customer . u are directly interacting   with user .
        just reply with the response message dont add note to it 

        Context:

        Instructions:
        1. now provide a short greeting message for the user 
        2. give a response as  a general conversation it should be short 

        expected output:
        Hi I am AARYA (Automated AI Responder at Your Assistance). How may I help you ?
        """