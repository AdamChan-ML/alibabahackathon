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
        name_static = gr.Markdown(f"*Name*: {user_data['Name']}")
        ic_static = gr.Markdown(f"*IC Number*: {user_data['IC Number']}")
        bd_static = gr.Markdown(f"*Birthdate*: {user_data['Birthdate']}")
        age_static = gr.Markdown(f"*Age*: {calculate_age(user_data['Birthdate'])}")
        phone_static = gr.Markdown(f"*Mobile Number*: {user_data['Mobile Number']}")
        email_static = gr.Markdown(f"*Email*: {user_data['Email']}")
        gender_static = gr.Markdown(f"*Gender*: {user_data['Gender']}")
        nation_static = gr.Markdown(f"*Nationality*: {user_data['Nationality']}")

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
        
        # Create fixed number of income rows per month (we'll use visibility to hide/show extras)
        income_rows = {}
        row_counters = {}
        
        for month in months:
            gr.Markdown(f"### 📅 {month}")
            income_rows[month] = []
            
            # Container for this month's rows
            with gr.Column() as month_container:
                # First row (always visible)
                income1 = gr.Number(label="Income (RM)", value=0, interactive=False)
                source1 = gr.Textbox(label="Income Source", interactive=False)
                income_rows[month].append((income1, source1))
                
                # Add 4 more rows that will be initially hidden
                # This gives us 5 total rows per month which should be enough for most users
                for i in range(4):
                    with gr.Column(visible=False) as row_container:
                        income = gr.Number(label=f"Additional Income {i+2} (RM)", value=0, interactive=False)
                        source = gr.Textbox(label=f"Income Source {i+2}", interactive=False)
                        income_rows[month].append((income, source, row_container))
            
            # Row counter to track visible rows (start with 1 for the default row)
            row_counters[month] = gr.State(value=1)
            
            # Add button for this month
            add_btn = gr.Button(f"➕ Add Income Row for {month}")
            
            # Add row function that shows the next hidden row
            def make_add_row_fn(month_name):
                def add_row_fn(counter):
                    if counter < 5:  # Max 5 rows
                        # Show the next row
                        next_row_index = counter
                        if next_row_index < len(income_rows[month_name]):
                            return gr.update(visible=True), counter + 1
                    return gr.update(), counter  # No change if at max
                return add_row_fn
            
            # Connect each add button to its specific row container
            if len(income_rows[month]) > 1:  # If we have additional rows beyond the first
                add_btn.click(
                    fn=make_add_row_fn(month),
                    inputs=[row_counters[month]],
                    outputs=[income_rows[month][1][2], row_counters[month]]  # Update visibility of the 2nd row container
                )

        # --- Edit/View Toggle Button ---
        toggle_btn = gr.Button("✏️ Edit Profile")

        # Function to toggle interactivity of all income fields
        def update_all_income_fields(is_editing):
            updates = []
            for month in months:
                for row in income_rows[month]:
                    if len(row) == 2:  # Regular row
                        income, source = row
                        updates.extend([
                            gr.update(interactive=is_editing),
                            gr.update(interactive=is_editing)
                        ])
                    else:  # Row with container
                        income, source, _ = row
                        updates.extend([
                            gr.update(interactive=is_editing),
                            gr.update(interactive=is_editing)
                        ])
            return updates

        # Function to handle toggling between edit and view mode
        def toggle_edit_mode(edit_mode):
            is_editing = not edit_mode
            
            if not edit_mode:  # Switching to edit mode
                # Update income fields to be editable
                income_updates = update_all_income_fields(True)
                
                return (
                    *[gr.update(visible=False) for _ in range(8)],  # Hide static fields
                    *[gr.update(visible=True) for _ in range(7)],   # Show edit fields
                    gr.update(value="✅ Save Changes"),             # Change button text
                    True,                                          # Update edit_mode state
                    *income_updates                                # Update income fields
                )
            else:  # Switching back to view mode
                age = calculate_age(bd_edit.value)
                
                # Update income fields to be non-editable
                income_updates = update_all_income_fields(False)
                
                return (
                    gr.update(value=f"*Name*: {name_edit.value}", visible=True),
                    gr.update(value=f"*IC Number*: {ic_edit.value}", visible=True),
                    gr.update(value=f"*Birthdate*: {bd_edit.value}", visible=True),
                    gr.update(value=f"*Age*: {age}", visible=True),
                    gr.update(value=f"*Mobile Number*: {phone_edit.value}", visible=True),
                    gr.update(value=f"*Email*: {email_edit.value}", visible=True),
                    gr.update(value=f"*Gender*: {gender_edit.value}", visible=True),
                    gr.update(value=f"*Nationality*: {nation_edit.value}", visible=True),
                    *[gr.update(visible=False) for _ in range(7)],  # Hide edit fields
                    gr.update(value="✏️ Edit Profile"),             # Change button text
                    False,                                         # Update edit_mode state
                    *income_updates                                # Update income fields
                )

        # Collect the core profile fields for toggle outputs
        base_toggle_outputs = [
            name_static, ic_static, bd_static, age_static,
            phone_static, email_static, gender_static, nation_static,
            name_edit, ic_edit, bd_edit, phone_edit,
            email_edit, gender_edit, nation_edit,
            toggle_btn, edit_mode_state
        ]
        
        # Collect all income field components for toggle outputs
        income_field_outputs = []
        for month in months:
            for row in income_rows[month]:
                if len(row) == 2:  # Regular row
                    income, source = row
                    income_field_outputs.extend([income, source])
                else:  # Row with container
                    income, source, _ = row
                    income_field_outputs.extend([income, source])
        
        # Combine all outputs for the toggle function
        all_toggle_outputs = base_toggle_outputs + income_field_outputs

        # Connect the toggle button
        toggle_btn.click(
            fn=toggle_edit_mode,
            inputs=[edit_mode_state],
            outputs=all_toggle_outputs
        )

    return profile