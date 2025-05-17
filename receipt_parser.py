# receipt_parser.py

import dashscope
import os
from PIL import Image
import base64
from io import BytesIO
import json
import logging
from dotenv import load_dotenv

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

# Configure DashScope with API key from environment
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("DASHSCOPE_API_KEY not found in environment variables")

logger.info("Configuring DashScope with API key")
dashscope.api_key = api_key
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

def parse_receipt_qwen(image: Image.Image):
    """
    Parse receipt using Qwen-VL model via DashScope API
    Args:
        image (PIL.Image): Receipt image
    Returns:
        dict: Structured data from receipt
    """
    logger.info("Starting receipt parsing with Qwen-VL")

    prompt = (
        "Extract the following information from this receipt image and format it as a JSON format:\n"
        "- merchant_name (store name)\n"
        "- date_of_purchase\n"
        "- items (array of objects with name, price, and category)\n"
        "- total_amount_spent\n"
    )

    try:
        # Convert image to base64
        img_base64 = image_to_base64(image)
        logger.info("Image converted to base64")
        
        # Call API
        logger.info("Calling DashScope API")
        response = dashscope.MultiModalConversation.call(
            model='qwen-vl-plus',
            messages=[
                {
                    "role": "user", 
                    "content": [
                        {"image": img_base64},
                        {"text": prompt}
                    ]
                }
            ]
        )

        logger.info(f"Response: {response}")

        if response.status_code == 200:
            logger.info("Received successful response from API")
            
            # Get the response text from the first item
            result = response.output.choices[0].message.content[0]['text']
            logger.info(f"Raw API response: {result}")
            
            # Extract JSON string from the markdown code block
            json_str = result.split("```json\n")[1].split("\n```")[0]
            logger.info(f"Extracted JSON string: {json_str}")
            
            # Parse the JSON string
            parsed_data = json.loads(json_str)
            logger.info(f"Parsed JSON data: {parsed_data}")
            
            # Transform the data into the UI's expected format
            formatted_data = {
                "Merchant name": parsed_data["merchant_name"],
                "Date of purchase": parsed_data["date_of_purchase"],
                "Item name": [],
                "Item price": [],
                "Item category": [],
                "Total amount spent": str(parsed_data["total_amount_spent"])
            }
            
            # Extract items information
            for item in parsed_data["items"]:
                formatted_data["Item name"].append(item["name"])
                formatted_data["Item price"].append(str(item["price"]))
                formatted_data["Item category"].append(item["category"])
            
            logger.info(f"Formatted data for UI: {formatted_data}")
            return formatted_data
            
        else:
            error_msg = f"API call failed with status {response.status_code}: {response.message}"
            logger.error(error_msg)
            return {
                "Merchant name": "API Error",
                "Date of purchase": "",
                "Item name": [],
                "Item price": [],
                "Item category": [],
                "Total amount spent": "",
                "error": error_msg
            }

    except Exception as e:
        error_msg = f"Error processing receipt: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return {
            "Merchant name": "Processing Error",
            "Date of purchase": "",
            "Item name": [],
            "Item price": [],
            "Item category": [],
            "Total amount spent": "",
            "error": error_msg
        }
            