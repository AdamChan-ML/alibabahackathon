import gradio as gr
import time
import mimetypes
import os
from expense_manager import ExpenseManager
import tempfile
from PIL import Image
import dashscope
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure DashScope
api_key = os.getenv("DASHSCOPE_API_KEY")
if api_key:
    dashscope.api_key = api_key
    dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

# Initialize the expense manager
manager = ExpenseManager()

# Hardcoded user ID
DEFAULT_USER_ID = "default@example.com"

# --- Simulated upload + preview handler ---
def simulate_upload_and_categorise(files):
    if not api_key:
        return [], "Error: DASHSCOPE_API_KEY not found in environment variables", gr.update(visible=False)

    image_previews = []
    status_messages = []
    processed_results = []

    for file in files:
        time.sleep(0.3)
        mime_type, _ = mimetypes.guess_type(file.name)
        file_name = os.path.basename(file.name)

        if mime_type and mime_type.startswith("image"):
            try:
                # Open and process the image
                img = Image.open(file.name)
                image_previews.append(file.name)  # Add to preview immediately
                
                # Process with ExpenseManager
                result = manager.process_receipt_image(
                    user_id=DEFAULT_USER_ID, 
                    image_path=file.name
                )

                if result.get("success", False):
                    status_messages.append(f"✅ Processed receipt: {file_name}")
                    processed_results.append(result)
                else:
                    error_msg = result.get("error", "Unknown error")
                    if "OCR failed" in error_msg:
                        status_messages.append(f"⚠️ OCR processing for {file_name}: {error_msg}")
                    else:
                        status_messages.append(f"❌ Failed to process: {file_name} - {error_msg}")
            except Exception as e:
                status_messages.append(f"❌ Error processing {file_name}: {str(e)}")
        elif file_name.endswith(".pdf"):
            status_messages.append(f"✅ PDF received: {file_name} (Processing not available)")
        else:
            status_messages.append(f"❌ Unsupported file type: {file_name}")

    return image_previews, "\n".join(status_messages), gr.update(visible=True) if image_previews else gr.update(visible=False)

# --- Enhanced categorisation with real processing results ---
def show_categorised(receipts):
    if not receipts:
        return gr.update(visible=False)

    components = []
    
    # Get tax summary for the user
    tax_summary = manager.get_tax_summary(DEFAULT_USER_ID)
    
    if tax_summary:
        # Tax Deductible Items
        with gr.Accordion(label="📁 Tax Deductible Expenses", open=True) as section:
            for category, data in tax_summary.items():
                if data["total_claimed"] > 0:
                    components.append(gr.Markdown(f"### 📂 {category}"))
                    components.append(gr.Markdown(f"Total Claimed: RM {data['total_claimed']:.2f}"))
                    
                    # Show expenses in this category
                    for expense in data["expenses"]:
                        components.append(gr.Markdown(f"""
                        **Date:** {expense['date']}
                        **Amount:** RM {expense['amount']:.2f}
                        **Description:** {expense['description']}
                        **Claim Type:** {expense['matched_rule']}
                        """))
    
    # Non-tax deductible items are shown in a separate section
    with gr.Accordion(label="📁 Non Tax Deductible Expenses", open=True) as section:
        components.append(gr.Markdown("### 📂 Other Expenses"))
        # Add any non-deductible items here

    return gr.update(visible=True), *components

def create_upload_receipt():
    # --- Frontend ---
    with gr.Blocks() as demo:
        gr.Markdown("## 📤 Upload Your Receipts")
        gr.Markdown("Supported formats: PNG, JPG, JPEG, PDF")

        file_input = gr.Files(
            label="Choose receipt files",
            file_types=[".png", ".jpg", ".jpeg", ".pdf"],
            file_count="multiple",
            interactive=True
        )

        upload_btn = gr.Button("📨 Upload & Process Receipts")

        image_gallery = gr.Gallery(
            label="🖼️ Receipt Previews", 
            columns=3, 
            height=150,
            object_fit="contain",
            interactive=False
        )

        status_output = gr.Textbox(
            label="📎 Processing Status",
            lines=10,
            interactive=False
        )

        next_btn = gr.Button("View Tax Analysis ➡️", visible=False)

        # --- Output area for categorised receipts ---
        categorised_area = gr.Column(visible=False)

        # --- Handle receipt upload and make "Next" button visible ---
        upload_btn.click(
            fn=simulate_upload_and_categorise,
            inputs=[file_input],
            outputs=[image_gallery, status_output, next_btn]
        )

        # --- When "Next" is clicked, show categorised folders ---
        next_btn.click(
            fn=show_categorised,
            inputs=[image_gallery],
            outputs=[categorised_area]
        )

    return demo

