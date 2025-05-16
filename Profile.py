import gradio as gr
from datetime import datetime

# Sample profile data
user_data = {
    "Name": "Jiaying",
    "IC Number": "020124080662",
    "Birthdate": "2002-01-24",
    "Mobile Number": "01136252270",
    "Email": "gjyktt@gmail.com",
    "Gender": "Female",
    "Nationality": "Malaysian"
}

def calculate_age(birthdate_str):
    try:
        bd = datetime.strptime(birthdate_str, "%Y-%m-%d")
        today = datetime.today()
        return today.year - bd.year - ((today.month, today.day) < (bd.month, bd.day))
    except:
        return "Invalid"

def income_update_reminder():
    return datetime.today().day <= 5

def get_current_month_name():
    return datetime.today().strftime("%B")

def create_profile():
    with gr.Column() as profile:
        gr.Markdown("## 👤 Profile Page")
        edit_mode_state = gr.State(value=False)

        # --- Static Info ---
        name_static = gr.Markdown(f"**Name**: {user_data['Name']}")
        ic_static = gr.Markdown(f"**IC Number**: {user_data['IC Number']}")
        bd_static = gr.Markdown(f"**Birthdate**: {user_data['Birthdate']}")
        age_static = gr.Markdown(f"**Age**: {calculate_age(user_data['Birthdate'])}")
        phone_static = gr.Markdown(f"**Mobile Number**: {user_data['Mobile Number']}")
        email_static = gr.Markdown(f"**Email**: {user_data['Email']}")
        gender_static = gr.Markdown(f"**Gender**: {user_data['Gender']}")
        nation_static = gr.Markdown(f"**Nationality**: {user_data['Nationality']}")

        # --- Editable Fields ---
        name_edit = gr.Textbox(label="Name", value=user_data["Name"], visible=False)
        ic_edit = gr.Textbox(label="IC Number", value=user_data["IC Number"], visible=False)
        bd_edit = gr.Textbox(label="Birthdate (YYYY-MM-DD)", value=user_data["Birthdate"], visible=False)
        phone_edit = gr.Textbox(label="Mobile Number", value=user_data["Mobile Number"], visible=False)
        email_edit = gr.Textbox(label="Email", value=user_data["Email"], visible=False)
        gender_edit = gr.Textbox(label="Gender", value=user_data["Gender"], visible=False)
        nation_edit = gr.Textbox(label="Nationality", value=user_data["Nationality"], visible=False)

        # --- Monthly Income Section ---
        gr.Markdown("## 💰 Monthly Income")
        if income_update_reminder():
            gr.Markdown("⚠️ <span style='color:red;'>Reminder: Please update your income for this month.</span>", unsafe_allow_html=True)

        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        current_month = get_current_month_name()
        monthly_income_components = []

        with gr.Group():
            for month in months:
                visible = (month == current_month)
                input_box = gr.Number(label=month, value=0, interactive=False, visible=visible)
                monthly_income_components.append(input_box)

        # --- Edit/View Toggle Button ---
        toggle_btn = gr.Button("✏️ Edit Profile")

        # --- Toggle Logic ---
        def toggle_edit_mode(edit_mode, name, ic, bd, phone, email, gender, nation):
            current_month = get_current_month_name()
            if not edit_mode:
                return (
                    *[gr.update(visible=False) for _ in range(8)],
                    *[gr.update(visible=True) for _ in range(7)],
                    gr.update(value="✅ Save Changes"),
                    True,
                    *[gr.update(visible=True, interactive=True) for _ in monthly_income_components]
                )
            else:
                age = calculate_age(bd)
                income_visibility = [
                    gr.update(visible=(months[i] == current_month), interactive=False)
                    for i in range(len(monthly_income_components))
                ]
                return (
                    gr.update(value=f"**Name**: {name}", visible=True),
                    gr.update(value=f"**IC Number**: {ic}", visible=True),
                    gr.update(value=f"**Birthdate**: {bd}", visible=True),
                    gr.update(value=f"**Age**: {age}", visible=True),
                    gr.update(value=f"**Mobile Number**: {phone}", visible=True),
                    gr.update(value=f"**Email**: {email}", visible=True),
                    gr.update(value=f"**Gender**: {gender}", visible=True),
                    gr.update(value=f"**Nationality**: {nation}", visible=True),
                    *[gr.update(visible=False) for _ in range(7)],
                    gr.update(value="✏️ Edit Profile"),
                    False,
                    *income_visibility
                )

        toggle_btn.click(
            fn=toggle_edit_mode,
            inputs=[
                edit_mode_state,
                name_edit, ic_edit, bd_edit, phone_edit,
                email_edit, gender_edit, nation_edit
            ],
            outputs=[
                name_static, ic_static, bd_static, age_static,
                phone_static, email_static, gender_static, nation_static,
                name_edit, ic_edit, bd_edit, phone_edit,
                email_edit, gender_edit, nation_edit,
                toggle_btn,
                edit_mode_state,
                *monthly_income_components
            ]
        )

    return profile
