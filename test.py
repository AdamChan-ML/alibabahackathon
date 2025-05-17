from expense_manager import ExpenseManager
from dotenv import load_dotenv
import os
import json
import dashscope

def test_receipt_processing():
    # Load environment variables
    load_dotenv()
    
    # Configure DashScope
    api_key = os.getenv("DASHSCOPE_API_KEY")
    if not api_key:
        raise ValueError("DASHSCOPE_API_KEY not found in environment variables")
    dashscope.api_key = api_key
    dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'
    
    # Check OSS credentials
    required_oss_vars = ['OSS_ACCESS_KEY_ID', 'OSS_ACCESS_KEY_SECRET', 'OSS_ENDPOINT', 'OSS_BUCKET_NAME']
    missing_vars = [var for var in required_oss_vars if not os.getenv(var)]
    if missing_vars:
        raise ValueError(f"Missing OSS credentials: {', '.join(missing_vars)}")
    
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
    
    if result["success"]:
        # Get receipt history
        print("\nReceipt History:")
        print("=" * 50)
        history = manager.get_receipt_history("test@example.com")
        print(json.dumps(history, indent=2))
        
        # Get tax summary
        print("\nTax Summary:")
        print("=" * 50)
        tax_summary = manager.get_tax_summary("test@example.com")
        print(json.dumps(tax_summary, indent=2))

if __name__ == "__main__":
    test_receipt_processing() 