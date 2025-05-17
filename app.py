import gradio as gr
from Dashboard import create_dashboard
from Profile import create_profile
from UploadReceipt import create_upload_receipt
with gr.Blocks() as app:
    with gr.Tab("Dashboard"):
        create_dashboard()  # ✅ No `.render()`

    with gr.Tab("Profile"):
        create_profile()   # ✅ No `.render()`

    with gr.Tab("Receipts"):
        create_upload_receipt()

app.launch()
