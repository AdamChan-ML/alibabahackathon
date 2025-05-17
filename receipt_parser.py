# receipt_parser.py

import dashscope
import os
from PIL import Image
from dotenv import load_dotenv
import base64
from io import BytesIO
import json

# Load environment variables and configure DashScope
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("DASHSCOPE_API_KEY not found in environment variables")

# Configure DashScope with international endpoint
dashscope.api_key = api_key
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

def image_to_base64(image: Image.Image) -> str:
    """Convert PIL Image to base64 string"""
    buffered = BytesIO()
    image.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/jpeg;base64,{img_str}"

def extract_json_from_text(text) -> dict:
    """Extract JSON from text that might contain markdown or other formatting"""
    try:
        # If it's already a dict with 'text' key, extract that
        if isinstance(text, dict) and 'text' in text:
            text = text['text']
        # If it's a list, join all text parts
        elif isinstance(text, list):
            text = " ".join(str(item) for item in text)
        
        # Try to find JSON block in markdown
        if "```json" in text:
            json_block = text.split("```json")[1].split("```")[0].strip()
        elif "```" in text:
            json_block = text.split("```")[1].strip()
        else:
            json_block = text.strip()
        
        parsed = json.loads(json_block)
        return parsed
    except json.JSONDecodeError:
        return {"raw_response": text}
    except Exception as e:
        return {"error": f"Failed to parse response: {str(e)}"}

def parse_receipt_qwen(image: Image.Image):
    """
    Parse receipt using Qwen-VL model via DashScope API
    Args:
        image (PIL.Image): Receipt image
    Returns:
        dict: Structured data from receipt
    """

    # Prompt to extract structured data
    prompt = (
        "You are a smart assistant that extracts structured data from receipts. "
        "From the image, extract the following:\n"
        "- Merchant name\n"
        "- Item name (as a list if multiple items)\n"
        "- Date of purchase\n"
        "- Item Price (as a list if multiple items)\n"
        "- Item category (as a list if multiple items, e.g. electronics, food, medical, clothing, etc)\n"
        "- Total amount spent\n"
        "Return the result as a JSON object with consistent key names. "
        "Format your response as a JSON code block."
    )

    try:
        # Convert image to base64
        img_base64 = image_to_base64(image)
        
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

        if response.status_code == 200:
            result_text = response.output.choices[0].message.content
            
            # Try to parse the response
            if isinstance(result_text, dict) and 'text' in result_text:
                text = result_text['text']
                if "```json" in text:
                    json_str = text.split("```json")[1].split("```")[0].strip()
                    try:
                        return json.loads(json_str)
                    except:
                        pass
            
            # If direct parsing failed, try the extract function
            parsed_result = extract_json_from_text(result_text)
            
            if "raw_response" in parsed_result or "error" in parsed_result:
                return parsed_result
            
            # Ensure consistent key names
            key_mappings = {
                "merchant_name": "Merchant name",
                "merchant": "Merchant name",
                "item_name": "Item name",
                "item_names": "Item name",
                "items": "Item name",
                "date": "Date of purchase",
                "date_of_purchase": "Date of purchase",
                "purchase_date": "Date of purchase",
                "item_price": "Item price",
                "item_prices": "Item price",
                "prices": "Item price",
                "item_category": "Item category",
                "item_categories": "Item category",
                "categories": "Item category",
                "total": "Total amount spent",
                "total_amount": "Total amount spent",
                "total_amount_spent": "Total amount spent"
            }
            
            normalized_result = {}
            for key, value in parsed_result.items():
                normalized_key = None
                for old_key, new_key in key_mappings.items():
                    if key.lower().replace("_", " ") == old_key.lower().replace("_", " "):
                        normalized_key = new_key
                        break
                if normalized_key:
                    normalized_result[normalized_key] = value
                else:
                    normalized_result[key] = value
                    
            return normalized_result
        else:
            return {"error": f"API call failed with status {response.status_code}: {response.message}"}

    except Exception as e:
        return {"error": f"Error processing receipt: {str(e)}"}