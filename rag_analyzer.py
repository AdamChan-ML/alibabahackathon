# rag_analyzer.py
from dashscope import Generation
from retriever import retrieve_relevant_rules
import os
from dotenv import load_dotenv
import dashscope
import json

# Load environment variables and configure DashScope
load_dotenv()
api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    raise ValueError("DASHSCOPE_API_KEY not found in environment variables")

# Configure DashScope with international endpoint
dashscope.api_key = api_key
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

def analyze_receipt_with_rag(receipt):
    merchant = receipt.get("merchant", "")
    category = receipt.get("category", "")
    amount = receipt.get("amount", "")
    date = receipt.get("date", "")

    query = f"The receipt is from {merchant}, category {category}, with RM {amount} spent on {date}. What deductions can I make based on Malaysian LHDN tax rules?"
    context_data = retrieve_relevant_rules(query)
    context = "\n\n".join([c["description"] for c in context_data])

    prompt = f"""You are a Malaysian tax assistant. Based on the LHDN rules below:

{context}

Analyze the following receipt:
Merchant: {merchant}
Category: {category}
Amount: {amount}
Date: {date}

Answer with the deductible category (if any), amount claimable, remaining budget, and recommendation."""

    try:
        response = Generation.call(
            model='qwen-plus',
            prompt=prompt
        )
        
        if not response:
            return "Error: No response from API"
        if isinstance(response, dict) and "code" in response and response["code"] == "InvalidApiKey":
            return f"Error: Invalid API key - {response.get('message', 'No error message')}"
        if "output" not in response:
            return f"Error: Unexpected API response format: {response}"
        return response["output"]["text"]
    except Exception as e:
        return f"Error analyzing receipt: {str(e)}\nFull error type: {type(e)}"


# Example usage:
if __name__ == "__main__":
    sample_receipt = {
        "merchant": "Machines",
        "category": "electronics",
        "amount": "1500",
        "date": "2024-11-04"
    }
    result = analyze_receipt_with_rag(sample_receipt)
    print("\n--- Tax Analysis Result ---\n")
    print(result)
