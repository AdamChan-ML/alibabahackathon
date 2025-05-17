from receipt_parser import parse_receipt_qwen
from rag_analyzer import analyze_receipt_with_rag
from database import ExpenseDB
import json
from PIL import Image

class ExpenseManager:
    def __init__(self, db_path="expenses.db"):
        self.db = ExpenseDB(db_path)

    def process_receipt_image(self, user_id: str, image_path: str):
        """
        Process a receipt image through OCR, tax analysis, and store in database
        
        Args:
            user_id (str): Unique identifier for the user
            image_path (str): Path to the receipt image
        """
        try:
            # Load and process the image
            with Image.open(image_path) as img:
                # Convert to RGB if needed (in case of RGBA or other formats)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                
                # Process with OCR
                ocr_result = parse_receipt_qwen(img)

            if "error" in ocr_result:
                return {"success": False, "error": ocr_result["error"]}

            # Handle raw response if OCR didn't return proper JSON
            if "raw_response" in ocr_result:
                try:
                    # Try to parse the raw response as it might be a string representation of a dict
                    if isinstance(ocr_result["raw_response"], dict) and "text" in ocr_result["raw_response"]:
                        import json
                        text = ocr_result["raw_response"]["text"]
                        if "```json" in text:
                            json_str = text.split("```json")[1].split("```")[0].strip()
                            ocr_result = json.loads(json_str)
                        else:
                            return {"success": False, "error": f"OCR returned unstructured data"}
                    else:
                        return {"success": False, "error": f"OCR returned unstructured data"}
                except Exception as e:
                    return {"success": False, "error": f"Failed to parse OCR response: {str(e)}"}

            # Extract common receipt data
            receipt_info = {
                "date": ocr_result.get("date_of_purchase", "") or ocr_result.get("Date of purchase", ""),
                "merchant": ocr_result.get("merchant_name", "") or ocr_result.get("Merchant name", ""),
                "total_amount": self._clean_amount(ocr_result.get("total_amount_spent", "0"))
            }

            # Handle multiple items
            items = []
            item_names = ocr_result.get("item_names", []) or ocr_result.get("Item name", [])
            item_prices = ocr_result.get("item_prices", []) or ocr_result.get("Item price", [])
            item_categories = ocr_result.get("item_categories", []) or ocr_result.get("Item category", [])

            # Ensure all are lists
            if not isinstance(item_names, list):
                item_names = [item_names]
            if not isinstance(item_prices, list):
                item_prices = [item_prices]
            if not isinstance(item_categories, list):
                item_categories = [item_categories]

            # Ensure all arrays are the same length
            max_length = max(len(item_names), len(item_prices), len(item_categories))
            item_names = (item_names + [""] * max_length)[:max_length]
            item_prices = (item_prices + ["0"] * max_length)[:max_length]
            item_categories = (item_categories + [""] * max_length)[:max_length]

            stored_items = []
            for name, price, category in zip(item_names, item_prices, item_categories):
                if not name and not price:
                    continue

                # Clean the price
                cleaned_price = self._clean_amount(price)

                # Prepare item data for tax analysis
                receipt_data = {
                    "merchant": receipt_info["merchant"],
                    "category": category,
                    "amount": cleaned_price,
                    "date": receipt_info["date"]
                }

                # Analyze for tax deductions
                tax_analysis = analyze_receipt_with_rag(receipt_data)

                # Extract tax-related information
                is_tax_deductible = False
                suggested_claim = ""
                matched_rule = ""

                # Parse the tax analysis response
                if isinstance(tax_analysis, str) and "deductible" in tax_analysis.lower():
                    is_tax_deductible = True
                    if "category:" in tax_analysis.lower():
                        matched_rule = tax_analysis.split("category:")[1].split("\n")[0].strip()
                    if "claimable:" in tax_analysis.lower():
                        suggested_claim = tax_analysis.split("claimable:")[1].split("\n")[0].strip()

                # Store in database
                self.db.add_expense(
                    user_id=user_id,
                    source="receipt_qwen",
                    date=receipt_info["date"],
                    amount=cleaned_price,
                    category=category,
                    description=name,
                    is_tax_deductible=is_tax_deductible,
                    suggested_claim=suggested_claim,
                    matched_rule=matched_rule
                )

                stored_items.append({
                    "name": name,
                    "price": cleaned_price,
                    "category": category,
                    "is_tax_deductible": is_tax_deductible,
                    "suggested_claim": suggested_claim,
                    "matched_rule": matched_rule
                })

            return {
                "success": True,
                "receipt_info": receipt_info,
                "items": stored_items,
                "ocr_data": ocr_result
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _clean_amount(self, amount_str):
        """Clean amount string by removing currency symbols and converting to float"""
        if not amount_str:
            return 0.0
        try:
            # Remove currency symbols and convert to float
            cleaned = str(amount_str).replace('$', '').replace('RM', '').replace(',', '').strip()
            return float(cleaned)
        except (ValueError, TypeError):
            return 0.0

    def get_tax_summary(self, user_id: str):
        """
        Get a summary of tax-deductible expenses for a user
        
        Args:
            user_id (str): Unique identifier for the user
        """
        expenses = self.db.get_expenses_by_user(user_id)
        
        # Group by tax categories
        tax_summary = {}
        for expense in expenses:
            if expense[7]:  # is_tax_deductible
                category = expense[5]  # category
                amount = expense[4]  # amount
                if category not in tax_summary:
                    tax_summary[category] = {
                        "total_claimed": 0,
                        "expenses": []
                    }
                tax_summary[category]["total_claimed"] += amount
                tax_summary[category]["expenses"].append({
                    "date": expense[3],
                    "amount": amount,
                    "description": expense[6],
                    "suggested_claim": expense[8],
                    "matched_rule": expense[9]
                })

        return tax_summary

    def get_spending_patterns(self, user_id: str):
        """
        Get spending patterns and category-wise breakdown
        
        Args:
            user_id (str): Unique identifier for the user
        """
        return self.db.get_summary_by_category(user_id)

# Example usage:
if __name__ == "__main__":
    manager = ExpenseManager()
    
    # Example: Process a receipt
    result = manager.process_receipt_image(
        user_id="john@example.com",
        image_path="veggie-grocery-receipt_orig.jpeg"
    )
    print("\nProcessing Result:")
    print(json.dumps(result, indent=2))
    
    # Get tax summary
    tax_summary = manager.get_tax_summary("john@example.com")
    print("\nTax Summary:")
    print(json.dumps(tax_summary, indent=2))
    
    # Get spending patterns
    patterns = manager.get_spending_patterns("john@example.com")
    print("\nSpending Patterns:")
    print(patterns) 