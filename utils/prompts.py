PRODUCT_CONVERSATION_CLASSIFIER_PROMPT = """
You are an AI assistant tasked with determining whether a given conversation message is related to specific product creation details or if it's a general/exploratory conversation. Your goal is to classify the message accurately.

### Context:
- Product-related conversations MUST include SPECIFIC details about:
  - Concrete product specifications (exact dimensions, materials, colors)
  - Detailed feature descriptions
  - product name , validity
  - Precise design elements
  - Target market specifications
  - Exact pricing or cost details
  - If the user says they need change , modify or update product details like examples (Product Name,product Description,Product Family, Product Group, Product Offer Price,POP Type,Price Category,Price Mode,Product Specification Type,Data Allowance,Voice Allowance)

- General conversations include:
  - Vague statements about wanting to create products
  - Questions about the product creation process
  - Exploratory discussions without specific details
  - Mentions of tools or methods without product specifics
  - Initial inquiries about product creation

### Examples:
Product-related:
- "I want to create a product with some data for some valitiy"
- "create a product with 10gb data or some data with price or dollar "
- "Creating a mobile app with user authentication and payment processing features"

General conversation:
- "I want to create a product"
- "How do I start making products?"
- "Can I create a product by uploading an image?"
- "What's the best way to design a product?"
- "I'm thinking about creating something"

### Instructions:
1. Carefully analyze the given message.
2. Classify as product_related ONLY if specific product details are provided.
3. Classify as general_conversation if the message is exploratory or lacks specific details.
4. Respond with the classification in JSON format only.

### Message to classify:
{message}

### Classification (product_related/general_conversation):
Respond in JSON format only.

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
    - If the user says doesnt say "yes" or "proceed" do not count it as confirmation (Recurring or non Recurring is not confirmation)
    - If the user says "proceed" but hasn't been given all the necessary details yet, do not count it as confirmation.
conversations:
{message}
Expected output:
reply with {value}

    """
    
    
    
    CHANGE_CONFIRMATION_CHECKER = """
    
    **ONLY CONSIDER THE USER MESSAGE HERE WHAT USER IS TELLING 
    The focus should be on the user's message, not the assistant message
    **If user is mentioning any product details with values then it's not a change**
    Please confirm whether the user wants to make changes to an EXISTING product specification by analyzing the provided conversation:
    - Consider it a change request ONLY if the user explicitly mentions MODIFYING or CHANGING a SPECIFIC existing product's DETAILS with clear intent to alter the specification.
    - EXCLUDE scenarios that are merely:
      * Providing a name for the first time
      * Adding basic initial details to a draft product
      * Simple first-time specification of product attributes
    - Look for more definitive change language like:
      * "I want to change..."
      * "Modify the existing..."
      * "Revise the product..." 
    - The message must show a clear INTENT TO ALTER an existing, fully defined product.
    - Generic statements about adding or naming a product are NOT change requests.
Please confirm whether the user wants to make changes to an EXISTING product specification by analyzing the provided conversation:
    - Consider it a change request ONLY if the user explicitly mentions modifying,changing a SPECIFIC existing product's details.
    - This is NOT a change request if the user is creating a new product from scratch.
    - Look for clear language like "I want to change", "modify" or "revise" an existing product.
    - Ignore general product creation requests or first-time product specification discussions.
    - The message must indicate an intent to ALTER something that already exists.
    
    - Examples:
  IS a change request:
  * "update the product name"
  * "change the price mode"
  * "modify the data allowance"

  NOT a change request:
  * "update product name to daily5gb"
  * "change price mode to normal"
  * "set data allowance to 5GB"

User message:
{message}

Expected output:
reply with {value}
"""

        
    FINAL_MESSAGE_TEMPLATE = """Reply with confirmation message from the given schema make a bullet point and ask user for confirmation whether they need to update it or continue.
The Schema:
{schema}
Product Specification 

Expected output:
Confirmation message:
text message asking for confirmation of the field, not code.
Address by saying "Here are the details of your product with all mandatory default parameters enabled"
showcase the keys and values only give the replay
remove under score from keys and display it in common language
dont make up new fields
no footer or notes
and finally ask "Would you like to update any of these details or proceed as is?"

Format each field with:
- An asterisk (*) followed by a space at the start of each line
- Each field on a new line with proper spacing
- Exact formatting as shown below:

Here are the details of your product with all mandatory default parameters enabled
* Product Name: [value]
* Product Description: [value]
* Product Family: [value]
* Product Group: [value]
* Product Offer Price: [value]
* POP Type: [value]
* Price Category: [value]
* Price Mode: [value]
* Product Specification Type: [value]
* Data Allowance: [value]
* Voice Allowance: [value]

Would you like to update any of these details or proceed as is?


Note: please format the expected output with correct new lines"""
    
    PRODUCT_INFO_EXTRACTION = """
         Extract the following information from the conversation and format it as JSON. Use the exact field names from the provided schema.

        **Conversation:**
        {messages}

        **Product Schema:**
        {product_schema}

        **CORE RULES:**
        1. ALWAYS keep default schema values unless explicitly asked to change them
        2. NEVER set a default value to null during product creation
        3. ONLY set fields to null when explicitly asked to change without a new value

        **Field Processing Rules:**

        1. NEW PRODUCT CREATION:
        - Keep ALL schema default values (e.g., GSM, Prepaid, Normal, etc.)
        - Only modify fields explicitly mentioned in request
        - Example: "create product with name test"
          - Changes: ONLY product_name/description
          - Everything else: KEEPS SCHEMA DEFAULTS

        2. FIELD MODIFICATIONS:
        - ONLY modify the exact field mentioned
        - ALL other fields keep their current values
        - Set to null ONLY when field change requested without new value
        - When the user mentions 'update [specification] to [value]', update that specification with the new value and maintain the rest of the product details as they are
        - Examples:
          - "change price_mode" → price_mode: null, rest unchanged
          - "set group to Postpaid" → product_group: "Postpaid", rest unchanged
          
         
         

        3. FIELD SPECIFIC HANDLING:
         **Product Name / Pack Name / Plan Name**:
         - Only extract if explicitly mentioned (e.g., "Data Pack Plus", "Freedom Plan"). If no specific name is provided, keep it empty dont assume anything.
         PRODUCT_NAME_EXTRACTION_RULES
        1. ONLY extract the EXACT product name mentioned by the user
        2. DO NOT modify, interpret, or create a name if not explicitly stated
        3. If NO specific name is provided, leave the product_name EMPTY
         - Set the `product_name` field to be the same as the `product_description`.
        **Product_offer_price**:
        - This field represents the price or cost of the product. Only Extract any price-related information here. The value must be a **numeric string** with no additional text, symbols, or units (e.g., 10 dollars, 5 dollar, 3$ or any currency).
        **Data and Voice Allowance**:
        - Extract the **data_allowance** and **voice_allowance** if explicitly mentioned
        - Extract the **data allowance** (e.g., "20 GB", "10 MB") in the `data_allowance` field .
        - Extract the **voice allowance** (e.g., "100 minutes", "100 MINS", "flexi minutes", "100 seconds") in the `voice_allowance` field.  
        - If not mentioned, keep existing values
      -Keep in mind that days months if user is telling then it is validity not data or voice allowance
        
      

        4. JSON OUTPUT REQUIREMENTS:
        - Include ALL schema fields
        - Keep ALL default values from schema
        - Only change specifically mentioned fields
        - No quotes around JSON object

        VALIDATION STEPS:
        1. Check all schema default values are preserved
        2. Verify only mentioned fields are modified
        3. Confirm null only used for explicit change requests

        DO NOT set fields to null unless explicitly requested to change them. Keep schema defaults for all unmentioned fields.
    
    """
     
   
    PRODUCT_INFO_EXTRACTION_new = """
            Extract the following information from the conversation and format it as JSON. Use the exact field names from the provided schema. 
        **IF THE USER REQUESTS A FIELD TO BE CHANGED WITHOUT SPECIFYING A NEW VALUE, SET THAT FIELD TO NULL. DO NOT SKIP THIS RULE UNDER ANY CIRCUMSTANCES..**

        **Conversation:**
        {messages}

        **Product Schema:**
        {product_schema}

        **Guidelines:**
        
        PLEASE KEEP THE PRODUCT SCHEMA DEFAULT VALUES AS THEY ARE UNLESS YOU ARE SPECIFICALLY ASKED TO CHANGE THEM. 
        
        DEFAULT VALUE RULES FROM PRODUCT SCHEMA:
        - When creating a new product, ALL default values from the schema MUST be preserved
        - Only override fields that are explicitly mentioned in the user request
        - Fields with default values should NEVER become null during product creation
        - Null values should only be set when explicitly changing a field without providing a new value

        1. CRITICAL FIELD CHANGE RULES:
        - When processing a "change" request, ONLY modify the SPECIFICALLY mentioned field
        - If user says "change price_mode", ONLY price_mode should become null
        - If user says "update product_group to Postpaid", ONLY product_group should change
        - NEVER modify fields that aren't explicitly mentioned in the request
        - ALL other fields must retain their exact previous values

        2. Field Change Detection Examples:
        - Message: "change price_mode" → ONLY price_mode becomes null
        - Message: "update product_group to Postpaid" → ONLY product_group changes
        - Message: "modify product_family" → ONLY product_family becomes null
        - Message: "create product with name test" → ONLY product_name changes

        3. Value Assignment Rules:
        - For explicit change without value: Set ONLY that field to null
            Example: "change price_mode" → price_mode: null
        - For change with new value: Set ONLY that field to new value
            Example: "set group to Postpaid" → product_group: "Postpaid"
        - For all other fields: Keep their existing values exactly as is

        4. **Product Name / Pack Name / Plan Name**:
        - Only extract if explicitly mentioned by the user
        - If no specific name is provided, keep the field empty
        - please keep the product description same as product name 

        5. **Product_offer_price**:
        - This field represents the price or cost of the product. Extract any price-related information here. The value must be a **numeric string** with no additional text, symbols, or units. 
        

        6. **Data and Voice Allowance**:
        - Extract the **data_allowance** and **voice_allowance** if explicitly mentioned
        - If not mentioned, keep existing values

        7. Field Update Validation:
        - Before updating any field, verify it was explicitly mentioned
        - Do not modify fields by inference or assumption
        - When in doubt, preserve the existing field value

        8. **JSON Format**:
        - Provide the output strictly as JSON
        - Do not include any quotes before or after the JSON object

        Please extract the product information based on these guidelines and ensure ONLY mentioned fields are modified.
    
    """
    
    PRODUCT_INFO_EXTRACTION_OLD = """
            Extract the following information from the conversation and format it as JSON. Use the exact field names from the provided schema.  
        If any field is missing from the conversation, replace it with null.  
        Carefully look at user and assistant information.  

        **Conversation:**  
        {messages}  

        **Product Schema:**  
        {product_schema}  

        **Guidelines:**  
        -  **Product Name / Pack Name / Plan Name**: Only extract if explicitly mentioned (e.g., "Data Pack Plus", "Freedom Plan"). If no specific name is provided, keep it empty dont assume anything.
        - **Type**: Identify whether the product is "basic" or "add-on." Do not include product specifications like "1 GB price" or "2 GB price."  
        - **Product_offer_price**: This field represents the price or cost of the product. Extract any price-related information here. The value must be a **numeric string** with no additional text, symbols, or units.  
        - If a special discount price is mentioned, use it as `Product_offer_price`.  
        - Keep the default values in the schema unless explicitly asked to change them.  
        - Extract the **data allowance** (e.g., "20 GB", "10 MB") in the `data_allowance` field.
        - Extract the **voice allowance** (e.g., "100 minutes", "100 MINS", "flexi minutes", "100 seconds") in the `voice_allowance` field. 
        - Set the `product_name` field to be the same as the `product_description`.  

        **Expected Output:**  
        - Only JSON—no additional text or comments.  
        - Every value should be a **string**.  
        - Do not include any quotes before or after the JSON object.
    
    """

    IMAGE_PRODUCT_EXTRACTION = """IMAGE DATA EXTRACTION PROMPT:

Please analyze the image with extreme precision and create a JSON output following these steps:

1. NUMERICAL ACCURACY:
- Look at each number individually
- Distinguish between "1" and "10" carefully
- Count the exact digits present
- Pay special attention to price figures

2. Required fields to extract:
- Plan Name (exactly as written)
- Price (verify each digit separately)
- Validity (exact number of days)
- Data Allowance (exact number with unit)
- Data allowance can be GB,Mb.
- Voice Allowance (exact number with unit)
- Voice Allowance can be minutes, minute, MINS, flexi minutes, seconds, second carefully examine.

3. Format as JSON with strict number validation:
{
    "product name/plan name": "[exact text as shown]",
    "price": {
        "amount": [single digit or double digit - verify carefully],
        "currency": "[currency code]"
    },
    "validity": {
        "duration": [exact number],
        "unit": "day"
    },
    "data_allowance": {
        "amount": [exact number],
        "unit": "[exact unit]"
    },
    "voice_allowance": {
        "amount": [exact number],
        "unit": "[exact unit]"
    }
    
}

CRITICAL CHECKS:
- Price: Count exact number of digits (1 OMR ≠ 10 OMR)
- Double-verify all numerical values
- Ensure no assumptions are made about numbers

Please analyze the image again and confirm the exact number written for the price."""
     
    FIELD_EXTRACTION = """Based on the user's conversation, identify the field they want to change from the product details.
Focus on explicit mentions like "change the price mode" or "update the description."
Do not infer any additional fields not mentioned.
Conversation:
{message}
Expected response format: {"field_name": "price_mode"}"""


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
        You are an AI assistant focused on providing concise, natural responses for product creation and general inquiries.

        Response Guidelines:
        1. For product creation requests without image:
           - Kindly provide the details of the product you wish to create.
           - Let's get started! Can you tell me details of product you'd like to create?
           
        2. For product creation requests with image:
           - If user mentions images: "Please click the image upload button on the left to share your  image. and say nothing more"

        3. For greetings:
           - Respond warmly but briefly: "Hello! How may I assist you today? "
           - If user is telling hey ,how are you , hello etc please respond in such way with proper greeting fallowed by asking would you like to create product? nothing more.
           - Avoid lengthy explanations about being an AI

        4. For unclear requests:
           - Ask for clarification concisely: "Could you please provide more details about what you're looking for?"

        5. General rules:
           - Keep responses under 2 sentences when possible
           - Be direct and friendly
           - Guide users to next steps without overwhelming them
           - Avoid technical jargon unless specifically requested

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