import gradio as gr
import pandas as pd
import plotly.express as px
from datetime import datetime

def get_income_expenses_data():
    return pd.DataFrame({
        'Month': ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December'],
        'Income': [1200, 1300, 1400, 1500, 1600, 1700, 1800, 1900, 2000, 2100, 2200, 2300],
        'Expenses': [800, 900, 850, 950, 1000, 1100, 1200, 1250, 1300, 1400, 1500, 1600],
        'Year': [2024] * 12
    })

def get_recent_transactions():
    return pd.DataFrame({
        "No.": [1, 2, 3],
        "Date": ["20/04/2025", "05/04/2025", "25/04/2025"],
        "Expense Type": ["Deductable", "Non-Deductable", "Deductable"],
        "Expense Categories": ["Food & Beverage", "Electronics", "Dining"],
        "RM": ["100.00", "250.00", "50.00"]
    })

def plot_pie_chart_plotly(labels, sizes, colors, title):
    fig = px.pie(
        names=labels,
        values=sizes,
        title=title,
        color_discrete_sequence=colors
    )
    fig.update_traces(textinfo='percent+label')
    return fig

def plot_bar_chart(year):
    df = get_income_expenses_data()
    return px.bar(
        df[df['Year'] == year], x='Month', y=['Income', 'Expenses'],
        title=f"Income and Expenses for {year}",
        labels={'value': 'Amount (RM)', 'variable': 'Type'},
        barmode='group'
    )

def create_dashboard():
    with gr.Column() as dashboard:  # ✅ No gr.Blocks inside here
        gr.Markdown("# Dashboard View")
        gr.Markdown(f"## Today's Date: {datetime.today().strftime('%B %d, %Y')}")
        gr.Markdown("### Estimated Tax Payable: RM5,200 (estimate)")
        gr.Markdown("*⚠️ This is just an estimate. Please confirm with LHDN or your tax consultant.*")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Deductible Expenses")
                gr.Plot(plot_pie_chart_plotly(
                    ['Lifestyle & Education', 'Medical & Insurance', 'Childcare & Family', 'Home Equipment'],
                    [25, 20, 15, 10],
                    ['#3498db', '#e74c3c', '#f39c12', '#2ecc71'],
                    "Deductible Expenses"
                ))
            with gr.Column():
                gr.Markdown("### Non-Deductible Expenses")
                gr.Plot(plot_pie_chart_plotly(
                    ['Food & Beverage', 'Utilities & Rent', 'Entertainment', 'Others'],
                    [30, 20, 10, 20],
                    ['#e74c3c', '#9b59b6', '#f1c40f', '#34495e'],
                    "Non-Deductible Expenses"
                ))

        gr.Markdown("### Monthly Income & Expenses")
        gr.Plot(plot_bar_chart(2024))

        gr.Markdown("### Recent Transactions")
        gr.Dataframe(get_recent_transactions())

    return dashboard
