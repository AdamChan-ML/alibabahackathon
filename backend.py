# app.py
import gradio as gr
from receipt_parser import parse_receipt
from tax_analyzer import analyze_tax
from audit_checker import check_audit_risk
from qwen_chat import chat_with_qwen

def process_receipt(receipt_img, user_input):
    parsed_data = parse_receipt(receipt_img)
    analysis = analyze_tax(parsed_data, user_input)
    risk = check_audit_risk(parsed_data)
    return parsed_data, analysis, risk

def ask_ai(query):
    return chat_with_qwen(query)

iface = gr.Interface(
    fn=process_receipt,
    inputs=[
        gr.Image(type="pil", label="Upload Receipt"),
        gr.Textbox(label="Enter Income / Budget Info (JSON)"),
    ],
    outputs=[
        gr.JSON(label="Parsed Receipt"),
        gr.JSON(label="Tax Analysis"),
        gr.JSON(label="Audit Risk"),
    ],
    title="Smart Tax Refund Assistant"
)

chatbot = gr.Interface(
    fn=ask_ai,
    inputs=gr.Textbox(label="Ask about Tax Deductions"),
    outputs=gr.Textbox(label="Assistant Reply"),
    title="Qwen Tax Assistant"
)

gr.TabbedInterface([iface, chatbot], ["Tax Filing", "Ask AI"]).launch()
