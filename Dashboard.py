import gradio as gr
import pandas as pd
import plotly.express as px
from datetime import datetime

# If you still need this (e.g., for future use)
def get_income_expenses_data():
    return pd.DataFrame({
        'Month': ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December'],
        'Income': [1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300],
        'Expenses': [800, 900, 850, 950, 1000, 1100, 1200, 1250, 1300, 1400, 1500, 1600],
        'Year': [2024] * 12
    })

# If you still need this
def get_recent_transactions():
    return pd.DataFrame({
        "No.": [1, 2, 3],
        "Date": ["20/04/2025", "05/04/2025", "25/04/2025"],
        "Expense Type": ["Deductable", "Non-Deductable", "Deductable"],
        "Expense Categories": ["Food & Beverage", "Electronics", "Dining"],
        "RM": ["100.00", "250.00", "50.00"]
    })

# Your Quick BI embed URL
quick_bi_embed_url = "https://bi-cn-hongkong.data.aliyun.com/token3rd/dashboard/view/pc.htm?pageId=1b28a72a-e889-479d-bc7e-e5035fee9564&accessTicket=29dc3913-0a71-465c-8a2f-3f6bb11b4e59&dd_orientation=auto"

def create_dashboard():
    with gr.Column() as dashboard:
        gr.Markdown("# Dashboard View")
        gr.Markdown(f"## Today's Date: {datetime.today().strftime('%B %d, %Y')}")
        gr.Markdown("### Estimated Tax Payable: RM5,200 (estimate)")
        gr.Markdown("*⚠️ This is just an estimate. Please confirm with LHDN or your tax consultant.*")

        # ✅ Embedded Quick BI Dashboard replaces pie, bar, and table
        gr.HTML(f"""
            <iframe src="{quick_bi_embed_url}" width="100%" height="1200px" frameborder="0" allowfullscreen></iframe>
            <p style='color: gray; font-size: 12px;'>Dashboard provided by Quick BI</p>
        """)

    return dashboard