import gradio as gr

# --- Checklist items ---
checklist_items = [
    "All freelance and gig income declared",
    "Invoices or payment proof are uploaded",
    "Business-related expenses logged",
    "Receipts uploaded",
    "Expenses are categorized",
]

# --- Function to render score bar ---
def render_score_bar(score):
    return f"""
    <div style="position: relative; height: 28px; background: #ddd; border-radius: 14px;">
        <div style="width: {score}%; background: #f39c12; height: 100%; border-radius: 14px;"></div>
        <div style="position: absolute; left: {score}%; top: 50%; transform: translate(-50%, -50%); font-weight: bold; color:black;">
            {score}%
        </div>
    </div>
    """

# --- Logic to update progress & progress message ---
def update_progress(selected_items):
    total = len(checklist_items)
    completed = len(selected_items)
    percentage = round((completed / total) * 100)

    if percentage == 100:
        msg = "✅ You're ready to file your taxes on the LHDN portal."
    elif percentage >= 70:
        msg = "🟡 Almost ready. Just a few things to complete."
    else:
        msg = "🔴 Incomplete. Several key areas need attention."

    return render_score_bar(percentage), msg

    return percentage, msg

# --- Logic behind the PDF report download button ---
def provide_summary_pdf():
    return "tax_summary_report.pdf" 
def provide_formb_pack():
    return "form_b_readypack.pdf"

# --- Initial state ---
initial_checked = [
    "All freelance and gig income declared",
    "Business-related expenses logged",
    "Receipts uploaded",
    "Expenses are categorized"
]
initial_score, initial_msg = update_progress(initial_checked)

# --- Dummy data for rendering ---
def get_dummy_expense_categories():
    return {
        "Education": ["img/Sunway_Re.png", "img/Sunway2.png"],
        "Food & Beverage": ["img/FnB.jpeg"],
        "Medical": []
    }

# --- Expenses & receipts categorisations and organisation rendering ---
def render_expense_breakdown():
    data = get_dummy_expense_categories()
    components = []

    for category, receipts in data.items():
        with gr.Accordion(label=f"📁 {category}", open=False):
            if receipts:
                components.append(gr.Markdown(f"### {category} Receipts"))
                components.append(
                    gr.Gallery(
                        value=receipts,
                        columns=3,
                        object_fit="contain",
                        height=150
                    )
                )
            else:
                components.append(gr.Markdown("_No receipts uploaded for this category._"))

    return components

def tax_readiness_feat():
    # --- UI ---
    with gr.Blocks() as tax_readiness_feat:
        gr.Markdown("## 📋 Tax Readiness")

        # Tax Readiness Score
        with gr.Row():
            with gr.Column(scale=1):
                    with gr.Group():
                        gr.Markdown("### 🧮 Tax Readiness Score")
                        #progress = gr.Slider(minimum=0, maximum=100, value=initial_score, interactive=False, label="", show_label=False)
                        progress = gr.HTML(value=render_score_bar(initial_score))
                        progress_msg = gr.Textbox(label="Status", value=initial_msg, interactive=False)

        # Readiness Checklist
        with gr.Group():
            gr.Markdown("### ✅ Readiness Checklist")

            checklist_items = [
                "All freelance and gig income declared",
                "Invoices or payment proof are uploaded",
                "Business-related expenses logged",
                "Receipts uploaded",
                "Expenses are categorized",
            ]

            readiness_checklist = gr.CheckboxGroup(
                label="Select completed items",
                choices=checklist_items,
                interactive=True,
                type="value",
                value=initial_checked
            )

            readiness_checklist.change(
                fn=update_progress,
                inputs=readiness_checklist,
                outputs=[progress, progress_msg]
            )

        # View expenses categorisation
        gr.Markdown("### 🧾 Categorised Expenses & Receipts")

        categories = get_dummy_expense_categories()

    for cat, receipts in categories.items():
        with gr.Accordion(label=f"📁 {cat}", open=False):
            if receipts:
                gr.Markdown(f"**{len(receipts)} receipt(s) found**")
                gr.Gallery(value=receipts, columns=3, object_fit="contain", height=150)
            else:
                gr.Markdown("_No receipts uploaded for this category._")


    return tax_readiness_feat