import gradio as gr
from Dashboard import create_dashboard
from Profile import create_profile
from UploadReceipt import upload_receipt_feature
from TaxDeduction import tax_summary
from TaxReadiness import tax_readiness_feat

with gr.Blocks() as app:
    with gr.Tab("Profile"):
        create_profile()

    with gr.Tab("Receipts"):
        upload_receipt_feature() 

    with gr.Tab("Dashboard"):
        create_dashboard()  # ✅ No `.render()`  # ✅ No `.render()`

    with gr.Tab("Tax Deduction Suggestions"):
        tax_summary()

    with gr.Tab("Tax Readiness"):
        tax_readiness_feat()

app.launch(share=True)
