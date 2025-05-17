import gradio as gr
import time
import mimetypes
import os
from PIL import Image
from receipt_parser import parse_receipt_qwen
import logging
import oss2
from dotenv import load_dotenv
import json
from datetime import datetime
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure OSS
access_key_id = os.getenv('OSS_ACCESS_KEY_ID')
access_key_secret = os.getenv('OSS_ACCESS_KEY_SECRET')
endpoint = os.getenv('OSS_ENDPOINT')
bucket_name = os.getenv('OSS_BUCKET_NAME')

def upload_to_oss(file_path, receipt_data):
    """Upload receipt image and data to OSS"""
    try:
        # Initialize OSS client
        auth = oss2.Auth(access_key_id, access_key_secret)
        bucket = oss2.Bucket(auth, endpoint, bucket_name)
        
        # Generate unique ID for this receipt
        receipt_id = str(uuid.uuid4())
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Upload image
        image_key = f"receipts/images/{timestamp}_{receipt_id}.jpg"
        with open(file_path, 'rb') as f:
            bucket.put_object(image_key, f)
            
        # Upload receipt data
        data_key = f"receipts/data/{timestamp}_{receipt_id}.json"
        receipt_data['image_key'] = image_key
        receipt_data['upload_timestamp'] = timestamp
        receipt_data['receipt_id'] = receipt_id
        
        bucket.put_object(data_key, json.dumps(receipt_data))
        
        logger.info(f"Successfully uploaded receipt {receipt_id} to OSS")
        return True, receipt_id
        
    except Exception as e:
        logger.error(f"Failed to upload to OSS: {str(e)}")
        return False, str(e)

def process_receipt(file):
    """Process a single receipt file and return parsed data"""
    try:
        logger.info(f"Processing receipt file: {file.name}")
        
        # Open image with PIL
        image = Image.open(file.name)
        logger.info(f"Successfully opened image: {image.size}, {image.mode}")
        
        # Parse receipt
        logger.info("Calling parse_receipt_qwen...")
        parsed_data = parse_receipt_qwen(image)
        logger.info(f"Parsed data received: {parsed_data}")
        
        if not parsed_data:
            logger.error("Parsed data is empty")
            return file, {"error": "No data extracted from receipt"}
            
        return file, parsed_data
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}", exc_info=True)
        return file, {"error": f"Failed to parse receipt: {str(e)}"}

def format_receipt_info(parsed_data):
    """Format parsed receipt data into a readable string"""
    logger.info(f"Formatting receipt info from data: {parsed_data}")
    
    if "error" in parsed_data:
        logger.error(f"Error in parsed data: {parsed_data['error']}")
        return parsed_data["error"]
    
    info = []
    info.append(f"🏪 Merchant: {parsed_data.get('Merchant name', 'N/A')}")
    info.append(f"📅 Date: {parsed_data.get('Date of purchase', 'N/A')}")
    
    # Format items and prices
    items = parsed_data.get('Item name', [])
    prices = parsed_data.get('Item price', [])
    categories = parsed_data.get('Item category', [])
    
    logger.info(f"Raw items: {items}")
    logger.info(f"Raw prices: {prices}")
    logger.info(f"Raw categories: {categories}")
    
    info.append("\n📝 Items:")
    if len(items) > 0:
        for i in range(len(items)):
            item = items[i]
            price = prices[i] if i < len(prices) else 'N/A'
            category = categories[i] if i < len(categories) else 'N/A'
            info.append(f"  • {item} - {price} ({category})")
    else:
        info.append("  No items found")
    
    info.append(f"\n💰 Total Amount: {parsed_data.get('Total amount spent', 'N/A')}")
    
    formatted_info = "\n".join(info)
    logger.info(f"Formatted receipt info: {formatted_info}")
    return formatted_info

def update_receipt_info(parsed_data, merchant, date, items, prices, categories, total):
    """Update receipt information based on user input"""
    updated_data = {
        "Merchant name": merchant,
        "Date of purchase": date,
        "Item name": items.split("\n") if items else [],
        "Item price": prices.split("\n") if prices else [],
        "Item category": categories.split("\n") if categories else [],
        "Total amount spent": total
    }
    logger.info(f"Updated receipt data: {updated_data}")
    return updated_data

def upload_receipt_feature():
    with gr.Blocks() as uploadreceipt_feat:
        gr.Markdown("## 📤 Receipt Scanner and Information Extractor")
        gr.Markdown("Upload your receipt image to extract information. Supported formats: PNG, JPG, JPEG")
        
        # Add status message for debugging
        status_message = gr.Markdown("")
        
        with gr.Row():
            # Left column for upload and preview
            with gr.Column(scale=1):
                file_input = gr.Files(
                    label="Upload Receipt",
                    file_types=["image"],
                    file_count="single"
                )
                
                image_preview = gr.Image(
                    label="Receipt Preview",
                    type="filepath",
                    interactive=False
                )
                
                scan_btn = gr.Button("🔍 Scan Receipt", variant="primary")
            
            # Right column for extracted information
            with gr.Column(scale=1):
                # Original extracted info
                extracted_info = gr.Textbox(
                    label="Extracted Information",
                    lines=10,
                    interactive=False
                )
                
                # Editable fields for confirmation
                with gr.Group(visible=False) as edit_group:
                    gr.Markdown("### ✏️ Confirm or Edit Information")
                    merchant_input = gr.Textbox(label="Merchant Name")
                    date_input = gr.Textbox(label="Date of Purchase")
                    items_input = gr.Textbox(label="Items (one per line)", lines=3)
                    prices_input = gr.Textbox(label="Prices (one per line)", lines=3)
                    categories_input = gr.Textbox(label="Categories (one per line)", lines=3)
                    total_input = gr.Textbox(label="Total Amount")
                    
                    confirm_btn = gr.Button("✅ Confirm Information", variant="secondary")
        
        # Store parsed data state and file path
        parsed_data_state = gr.State({})
        file_path_state = gr.State("")
        
        def handle_upload(file):
            """Handle receipt upload and initial parsing"""
            try:
                if not file:
                    return None, "Please upload a receipt image.", None, gr.Group(visible=False), {}, "", "", "", "", "", "", ""
                
                logger.info(f"Processing uploaded file: {file}")
                image_file, parsed_data = process_receipt(file)
                
                if "error" in parsed_data:
                    return None, parsed_data["error"], None, gr.Group(visible=False), {}, "", "", "", "", "", "", ""
                
                formatted_info = format_receipt_info(parsed_data)
                
                # Handle items, prices, and categories
                items = parsed_data.get("Item name", [])
                prices = parsed_data.get("Item price", [])
                categories = parsed_data.get("Item category", [])
                
                # Convert to strings for display
                items_str = "\n".join(str(item) for item in items)
                prices_str = "\n".join(str(price) for price in prices)
                categories_str = "\n".join(str(cat) for cat in categories)
                total = str(parsed_data.get("Total amount spent", ""))
                
                return (
                    image_file.name,  # Preview
                    "✅ Receipt processed successfully!",  # Status
                    formatted_info,   # Extracted info
                    gr.Group(visible=True),  # Show edit group
                    parsed_data,     # Store parsed data
                    image_file.name,  # Store file path
                    parsed_data.get("Merchant name", ""),
                    parsed_data.get("Date of purchase", ""),
                    items_str,
                    prices_str,
                    categories_str,
                    total
                )
            except Exception as e:
                logger.error(f"Error in handle_upload: {str(e)}", exc_info=True)
                return None, f"Error processing receipt: {str(e)}", None, gr.Group(visible=False), {}, "", "", "", "", "", "", ""
        
        def handle_confirmation(parsed_data, file_path, merchant, date, items, prices, categories, total):
            """Handle confirmation of receipt information and upload to OSS"""
            try:
                # Update receipt data with confirmed information
                updated_data = update_receipt_info(parsed_data, merchant, date, items, prices, categories, total)
                
                # Upload to OSS
                success, result = upload_to_oss(file_path, updated_data)
                
                if success:
                    # Show success popup
                    gr.Info("Receipt information uploaded successfully!")
                    return (
                        "✅ Receipt uploaded successfully!",  # status message
                        "",  # clear extracted info
                        {},  # clear parsed data state
                        gr.Group(visible=False),  # hide edit group
                        None,  # clear image preview
                        "",  # clear merchant
                        "",  # clear date
                        "",  # clear items
                        "",  # clear prices
                        "",  # clear categories
                        ""   # clear total
                    )
                else:
                    # Show error popup
                    gr.Warning(f"Failed to upload receipt: {result}")
                    return (
                        f"❌ Failed to upload receipt: {result}",  # status message
                        format_receipt_info(updated_data),  # keep current info
                        updated_data,  # keep current data
                        gr.Group(visible=True),  # keep edit group visible
                        gr.update(value=None),  # keep current image
                        merchant,  # keep current values
                        date,
                        items,
                        prices,
                        categories,
                        total
                    )
                    
            except Exception as e:
                logger.error(f"Error in handle_confirmation: {str(e)}", exc_info=True)
                # Show error popup
                gr.Error(f"Error updating information: {str(e)}")
                return (
                    f"Error updating information: {str(e)}",  # status message
                    format_receipt_info(parsed_data),  # keep current info
                    parsed_data,  # keep current data
                    gr.Group(visible=True),  # keep edit group visible
                    gr.update(value=None),  # keep current image
                    merchant,  # keep current values
                    date,
                    items,
                    prices,
                    categories,
                    total
                )
        
        # Add a hidden component for navigation
        nav_state = gr.State(value=0)
        
        # Connect upload button
        scan_btn.click(
            fn=handle_upload,
            inputs=[file_input],
            outputs=[
                image_preview,
                status_message,
                extracted_info,
                edit_group,
                parsed_data_state,
                file_path_state,
                merchant_input,
                date_input,
                items_input,
                prices_input,
                categories_input,
                total_input
            ]
        )
        
        # Connect confirm button
        confirm_btn.click(
            fn=handle_confirmation,
            inputs=[
                parsed_data_state,
                file_path_state,
                merchant_input,
                date_input,
                items_input,
                prices_input,
                categories_input,
                total_input
            ],
            outputs=[
                status_message,
                extracted_info,
                parsed_data_state,
                edit_group,
                image_preview,
                merchant_input,
                date_input,
                items_input,
                prices_input,
                categories_input,
                total_input
            ]
        )
        
        return uploadreceipt_feat