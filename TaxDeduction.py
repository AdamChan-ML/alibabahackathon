import gradio as gr
import time
from tax_relief_advisor import get_tax_summary, chat_with_context  # Import your backend functions

# Global state for chatbot session
session_state = {"session_id": None}

# --- Tax Payable Scorecard ---
def delayed_tax_scorecard():
    time.sleep(2)  # Simulated delay
    return "<div style='text-align:center; font-size:40px; font-weight:bold; color:#4caf50;'>RM 1,500.00</div>"

# --- Relief Bar Renderer ---
def render_relief_bar(label, claimed, max_value):
    percent = int((claimed / max_value) * 100) if max_value else 0
    return f"""
    <div style='margin-bottom:4px;'>
        <div style='background:#eee; border-radius:5px; width:100%; height:20px;'>
            <div style='background:#4caf50; width:{percent}%; height:100%; border-radius:5px;'></div>
        </div>
        <p style="font-size:12px; margin-top:2px;">{label}: Claimed RM{claimed} / RM{max_value}</p>
    </div>
    """

# --- Chat Handler ---
def ui_chat(user_message, history):
    response, session_id, error = chat_with_context(user_message, session_state["session_id"])
    if error:
        return history + [[user_message, f"⚠️ {error}"]]
    session_state["session_id"] = session_id
    return history + [[user_message, response]]

# --- Main App ---
def tax_summary():
    with gr.Blocks(title="Malaysian Tax Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🇲🇾 Malaysian Tax Deduction Assistant
        Welcome to your personalized Malaysian tax relief guide powered by AI.
        """)

        # --- Tax Payable Scorecard ---
        gr.Markdown("## 💰 Current Tax Payable")
        with gr.Row():
            with gr.Column(scale=1):
                pass
            with gr.Column(scale=2):
                tax_output = gr.HTML("<div style='text-align:center; font-size:32px; font-weight:bold; color:#999;'>Loading...</div>")
            with gr.Column(scale=1):
                pass

        demo.load(fn=delayed_tax_scorecard, inputs=[], outputs=tax_output)

        # --- AI Summary Section ---
        gr.Markdown("## 🧠 AI Tax Relief Summary")
        gr.Markdown("Click the button below to receive a personalized summary of your tax deductions.")

        with gr.Row():
            with gr.Column(scale=1):
                pass
            with gr.Column(scale=6):
                summary_output = gr.HTML("<div style='text-align:center; font-size:16px; color:#555;'>Your summary will appear here.</div>", elem_id="summary-box")
            with gr.Column(scale=1):
                pass

        with gr.Row():
            with gr.Column(scale=4):
                pass
            with gr.Column(scale=2):
                summary_btn = gr.Button("📊 Generate Summary", scale=1)
            with gr.Column(scale=4):
                pass

        def ui_get_summary():
            time.sleep(2)  # Simulate delay
            summary, error = get_tax_summary()
            if error:
                return f"<div style='color:red; font-weight:bold;'>⚠️ Error: {error}</div>"
            
            return f"""
        <div style='background:#f9f9f9; border:1px solid #ddd; padding:20px; border-radius:10px; box-shadow:0 4px 12px rgba(0,0,0,0.05); font-size:16px; color:#000;'>
            <strong style="color:#000;">✅ Your Tax Deduction Summary:</strong><br><br>{summary.replace('\n', '<br>')}
        </div>
        """

        summary_btn.click(fn=ui_get_summary, inputs=[], outputs=summary_output)

        # --- Tax Relief Breakdown ---
        gr.Markdown("## 📊 Tax Relief Breakdown")
        accordion_data = {
            "👪 Self, Parents & Spouse": [
                ("Automatic Individual Relief", 9000, 9000),
                ("Medical Expenses For Parents", 4000, 8000),
                ("Spouse/Alimony", 1000, 4000)
            ],
            "🎓 Education": [
                ("Education Fees in Malaysia", 5000, 7000),
                ("Upskilling/Self-Enhancement Courses", 1000, 2000)
            ],
            "🏥 Medical": [
                ("Serious Disease/Vaccination", 6000, 8000),
                ("Fertility Treatment", 0, 5000),
                ("Medical & Mental Health Exam", 800, 1000),
                ("Rehabilitation for Learning Disabilities", 0, 3000)
            ],
            "🎮 Lifestyle": [
                ("Lifestyle Purchases", 2500, 2500),
                ("Sports Activity Expenses", 300, 500),
                ("EV Charging Equipment", 0, 2500)
            ],
            "👶 Parenthood": [
                ("Breastfeeding Equipment", 1000, 1000),
                ("Childcare Fees", 3000, 3000),
                ("SSPN Deposit", 4000, 8000),
                ("Child Relief", 2000, 2000),
                ("Child 18+ in Full-Time Education", 0, 2000),
                ("Child 18+ in Tertiary Education", 0, 8000)
            ],
            "💼 Insurance & Investment": [
                ("Life Insurance (Non-Public Servants)", 3000, 3000),
                ("EPF (Statutory & Voluntary)", 4000, 4000),
                ("PRS & Deferred Annuity", 2500, 3000),
                ("Education and Medical Insurance", 3000, 3000),
                ("SOCSO", 250, 350)
            ],
            "♿ Disabled Persons": [
                ("Equipment for Disabled", 0, 6000),
                ("Disabled Individual", 0, 6000),
                ("Disabled Spouse", 0, 5000),
                ("Disabled Child", 0, 6000),
                ("Disabled Child 18+ in Education/Training", 0, 8000)
            ]
        }

        for section, bars in accordion_data.items():
            with gr.Accordion(section, open=False):
                for label, claimed, max_val in bars:
                    gr.HTML(render_relief_bar(label, claimed, max_val))

        # --- Chatbot Section ---
        gr.Markdown("## 🤖 Ask About Your Tax Deductions")
        chatbot = gr.Chatbot(label="AI Tax Chat")
        msg_input = gr.Textbox(placeholder="e.g. What documents do I need for education relief?", label="Your Question")
        send_btn = gr.Button("Send")

        send_btn.click(fn=ui_chat, inputs=[msg_input, chatbot], outputs=chatbot)
        msg_input.submit(fn=ui_chat, inputs=[msg_input, chatbot], outputs=chatbot)

        return demo
