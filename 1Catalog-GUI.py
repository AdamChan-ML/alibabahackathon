import dashscope  
import os
import gradio as gr
import base64
import re
from dotenv import load_dotenv
from dashscope import MultiModalConversation  

load_dotenv()

dashscope.api_key = os.getenv("DASHSCOPE_API_KEY")
if not dashscope.api_key:
    raise ValueError("API_KEY is missing. Please check your .env file.")
dashscope.base_http_api_url = 'https://dashscope-intl.aliyuncs.com/api/v1'

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

def get_book_info(image_path):
    if not image_path:
        return "Error", "No image uploaded", "Error"

    base64_image = encode_image(image_path)

    messages = [
        {
            "role": "user",
            "content": [
                {"image": f"data:image/png;base64,{base64_image}"},
                {"text": "Extract receipt information from the image, what products are bought, and their prices. \
                    Assuming this is a purchase of personal computer and the price is in Malaysian Riggit and with 6% SST included, is there any tax relief for income tax can be done in Malaysia? \
                    If yes, how much can be deducted, please provide more info. \
                    Below are the tax reliefs available in Malaysia: \
                        Lifestyle – Expenses for the use / benefit of self, spouse or child in respect of: \
                        Purchase or subscription of books / journals / magazines / newspapers / other similar publications (Not banned reading materials) \
                        Purchase of personal computer, smartphone or tablet (Not for business use) \
                        Payment of monthly bill for internet subscription (Under own name) \
                        Skill improvement / personal development course fee \
                        2,500 (Restricted) \
                    What is the total amount of tax relief available for the above?"}
                #{"text": "Extract book details in CSV format: Book Name, Author(s), Publisher. No extra text, just the CSV output."}
            ]
        }
    ]

    try:
        response = MultiModalConversation.call(model='qwen-vl-plus', messages=messages, stream=False)

        print(response)  # Debugging line to check the response structure

        if response and 'output' in response and 'choices' in response['output']:
            book_info = response['output']['choices'][0]['message']['content'][0]['text']
            return parse_book_info(book_info)
        return "Unknown", "Unknown", "Unknown"
    except Exception as e:
        return "Error", str(e), "Error"

def parse_book_info(book_info):
    """Parse book details from API response."""
    match = re.match(r'^"([^"]+)",\s*(.+),\s*([^,]+)$', book_info)
    if match:
        return (
            match.group(1).strip(),  # Book title
            match.group(2).strip(),  # Authors
            match.group(3).strip()   # Publisher
        )
    return "Parsing Failed", "Unknown", "Unknown"

def process_image(image_path):
    return get_book_info(image_path)

gr.Interface(
    fn=process_image,
    inputs=gr.Image(type="filepath"),
    outputs=[
        gr.Textbox(label="Book Name"),
        gr.Textbox(label="Author(s)"),
        gr.Textbox(label="Publisher")
    ],
    title="Book Info Extractor",
    description="Upload a book cover image to extract details."
).launch()