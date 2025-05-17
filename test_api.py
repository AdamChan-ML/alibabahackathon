# import os
# from dotenv import load_dotenv
# from dashscope import TextEmbedding

# # Load environment variables
# load_dotenv()
# api_key = os.getenv("DASHSCOPE_API_KEY")
# print(f"API Key loaded: {'Yes' if api_key else 'No'}")
# print(f"API Key length: {len(api_key) if api_key else 0}")
# print(f"API Key starts with 'sk-': {api_key.startswith('sk-') if api_key else False}")

# # Test with a simple embedding
# try:
#     response = TextEmbedding.call(
#         model="text-embedding-v3",
#         input=["Hello, this is a test"]
#     )
#     print("\nAPI Response:")
#     print(response)
# except Exception as e:
#     print("\nError occurred:")
#     print(str(e)) 

# from database import ExpenseDB

# db = ExpenseDB()

# db.add_expense(
#     user_id="john@example.com",
#     source="receipt_qwen",
#     date="2025-05-15",
#     amount=850.00,
#     category="Electronics",
#     description="Laptop for work purposes",
#     is_tax_deductible=True,
#     suggested_claim="Lifestyle",
#     matched_rule="Lifestyle claim up to RM2,500"
# )

from receipt_parser import parse_receipt_qwen
import json

result = parse_receipt_qwen("/Users/adam/Documents/devkaki-alibaba/veggie-grocery-receipt_orig.jpeg")
print(json.loads(result))