import gradio as gr
from Dashboard import create_dashboard
from Profile import create_profile

with gr.Blocks() as app:
    with gr.Tab("Dashboard"):
        create_dashboard()  # ✅ No `.render()`

    with gr.Tab("Profile"):
        create_profile()   # ✅ No `.render()`

app.launch()
