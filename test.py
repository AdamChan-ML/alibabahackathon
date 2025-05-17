from expense_manager import ExpenseManager
from dotenv import load_dotenv
import os
import json
import dashscope

def test_receipt_processing():
    # Load environment variables
    load_dotenv()
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not found in environment variables")

    # Configure DashScope with international endpoint
    dashscope.api_key = api_key
    dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'
    
    # Initialize expense manager
    manager = ExpenseManager()
    
    # Test image path
    image_path = "veggie-grocery-receipt_orig.jpeg"
    
    # Process receipt
    result = manager.process_receipt_image(
        user_id="test@example.com",
        image_path=image_path
    )
    
    # Print results
    print("\nReceipt Processing Results:")
    print("=" * 50)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    test_receipt_processing() 