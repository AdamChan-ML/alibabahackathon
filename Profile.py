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
        current_month = get_current_month_name()

        # --- Static Info ---
        name_static = gr.Markdown(f"Name: {user_data['Name']}")
        ic_static = gr.Markdown(f"IC Number: {user_data['IC Number']}")
        bd_static = gr.Markdown(f"Birthdate: {user_data['Birthdate']}")
        age_static = gr.Markdown(f"Age: {calculate_age(user_data['Birthdate'])}")
        phone_static = gr.Markdown(f"Mobile Number: {user_data['Mobile Number']}")
        email_static = gr.Markdown(f"Email: {user_data['Email']}")
        gender_static = gr.Markdown(f"Gender: {user_data['Gender']}")
        nation_static = gr.Markdown(f"Nationality: {user_data['Nationality']}")

        # --- Editable Fields ---
        name_edit = gr.Textbox(label="Name", value=user_data["Name"], visible=False)
        ic_edit = gr.Textbox(label="IC Number", value=user_data["IC Number"], visible=False)
        bd_edit = gr.Textbox(label="Birthdate (YYYY-MM-DD)", value=user_data["Birthdate"], visible=False)
        phone_edit = gr.Textbox(label="Mobile Number", value=user_data["Mobile Number"], visible=False)
        email_edit = gr.Textbox(label="Email", value=user_data["Email"], visible=False)
        gender_edit = gr.Textbox(label="Gender", value=user_data["Gender"], visible=False)
        nation_edit = gr.Textbox(label="Nationality", value=user_data["Nationality"], visible=False)

        # --- Monthly Income Section ---
        income_section_title = gr.Markdown("## 💰 Monthly Income")
        
        # Show reminder conditionally
        if income_update_reminder():
            gr.HTML("⚠️ <span style='color:red;'>Reminder: Please update your income for this month.</span>")

        months = ['January', 'February', 'March', 'April', 'May', 'June',
                  'July', 'August', 'September', 'October', 'November', 'December']
        
        # Create containers for each month
        month_containers = {}
        income_rows = {}
        row_counters = {}
        month_totals = {}
        add_buttons = {}
        
        for month in months:
            # Only make the current month visible initially
            is_current = month == current_month
            
            with gr.Column(visible=is_current) as month_container:
                gr.Markdown(f"### 📅 {month}")
                
                # Create a container for income rows
                income_rows[month] = []
                
                # First row (always visible)
                with gr.Row():
                    income1 = gr.Number(label="Income (RM)", value=0, interactive=False)
                    source1 = gr.Textbox(label="Income Source", interactive=False)
                
                income_rows[month].append((income1, source1))
                
                # Add 4 more rows that will be initially hidden
                for i in range(4):
                    with gr.Row(visible=False) as row_container:
                        income = gr.Number(label=f"Additional Income {i+2} (RM)", value=0, interactive=False)
                        source = gr.Textbox(label=f"Income Source {i+2}", interactive=False)
                        income_rows[month].append((income, source, row_container))
                
                # Total income for this month
                month_totals[month] = gr.Number(label=f"Total Income for {month} (RM)", value=0, interactive=False)
                
                # Add button for this month - only active for current month
                add_btn = gr.Button(f"➕ Add Income Row for {month}", interactive=is_current)
                add_buttons[month] = add_btn
                
                # Store the container reference
                month_containers[month] = month_container
            
            # Row counter to track visible rows (start with 1 for the default row)
            row_counters[month] = gr.State(value=1)
            
            # Define function to calculate total income for a month
            def make_calculate_total_fn(month_name):
                def calculate_total(*income_values):
                    total = sum(val if val is not None else 0 for val in income_values)
                    return total
                return calculate_total
            
            # Add row function that shows the next hidden row
            def make_add_row_fn(month_name):
                def add_row_fn(counter):
                    if counter < 5:  # Max 5 rows
                        # Show the next row
                        next_row_index = counter
                        if next_row_index < len(income_rows[month_name]) - 1:
                            return counter + 1
                    return counter  # No change if at max
                return add_row_fn
            
            # Connect add button to its month's rows
            if len(income_rows[month]) > 1:
                # For each month, set up the add button to show the next row
                add_btn.click(
                    fn=make_add_row_fn(month),
                    inputs=[row_counters[month]],
                    outputs=[row_counters[month]]
                )
                
                # Now handle the visibility update based on counter
                def update_visibility(counter):
                    updates = []
                    for i in range(1, min(5, len(income_rows[month]))):
                        # Only show rows up to the counter value
                        if i < counter:
                            updates.append(gr.update(visible=True))
                        else:
                            updates.append(gr.update(visible=False))
                    return updates
                
                # Connect counter to row visibility
                visible_rows = [row[2] for row in income_rows[month][1:]]
                row_counters[month].change(
                    fn=update_visibility,
                    inputs=[row_counters[month]],
                    outputs=visible_rows
                )
            
            # Set up calculation of total income
            income_inputs = [row[0] for row in income_rows[month]]
            
            # Create a trigger for calculating the total
            for income_input in income_inputs:
                total_calc_fn = make_calculate_total_fn(month)
                income_input.change(
                    fn=total_calc_fn,
                    inputs=income_inputs,
                    outputs=[month_totals[month]]
                )

        # --- Edit/View Toggle Button ---
        toggle_btn = gr.Button("✏️ Edit Profile")

        # Function to handle toggling between edit and view mode
        def toggle_edit_mode(edit_mode):
            is_editing = not edit_mode
            
            # Prepare updates for month containers visibility
            month_container_updates = []
            for month in months:
                # In view mode, only show current month
                # In edit mode, show all months
                visible = month == current_month or is_editing
                month_container_updates.append(gr.update(visible=visible))
            
            # Prepare updates for add buttons interactivity
            add_button_updates = []
            for month in months:
                # Only current month's add button is interactive in edit mode
                is_interactive = month == current_month and is_editing
                add_button_updates.append(gr.update(interactive=is_interactive))
            
            # Prepare updates for income fields
            income_field_updates = []
            for month in months:
                for row in income_rows[month]:
                    if len(row) == 2:  # Regular row
                        income_field_updates.extend([
                            gr.update(interactive=is_editing),
                            gr.update(interactive=is_editing)
                        ])
                    else:  # Row with container
                        income_field_updates.extend([
                            gr.update(interactive=is_editing),
                            gr.update(interactive=is_editing)
                        ])
            
            if not edit_mode:  # Switching to edit mode
                return (
                    *[gr.update(visible=False) for _ in range(8)],  # Hide static fields
                    *[gr.update(visible=True) for _ in range(7)],   # Show edit fields
                    gr.update(value="✅ Save Changes"),             # Change button text
                    True,                                          # Update edit_mode state
                    *month_container_updates,                      # Update month container visibility
                    *add_button_updates,                           # Update add button interactivity
                    *income_field_updates                          # Update income fields interactivity
                )
            else:  # Switching back to view mode
                age = calculate_age(bd_edit.value)
                
                return (
                    gr.update(value=f"Name: {name_edit.value}", visible=True),
                    gr.update(value=f"IC Number: {ic_edit.value}", visible=True),
                    gr.update(value=f"Birthdate: {bd_edit.value}", visible=True),
                    gr.update(value=f"Age: {age}", visible=True),
                    gr.update(value=f"Mobile Number: {phone_edit.value}", visible=True),
                    gr.update(value=f"Email: {email_edit.value}", visible=True),
                    gr.update(value=f"Gender: {gender_edit.value}", visible=True),
                    gr.update(value=f"Nationality: {nation_edit.value}", visible=True),
                    *[gr.update(visible=False) for _ in range(7)],  # Hide edit fields
                    gr.update(value="✏️ Edit Profile"),             # Change button text
                    False,                                         # Update edit_mode state
                    *month_container_updates,                      # Update month container visibility
                    *add_button_updates,                           # Update add button interactivity 
                    *income_field_updates                          # Update income fields interactivity
                )

        # Collect the core profile fields for toggle outputs
        base_toggle_outputs = [
            name_static, ic_static, bd_static, age_static,
            phone_static, email_static, gender_static, nation_static,
            name_edit, ic_edit, bd_edit, phone_edit,
            email_edit, gender_edit, nation_edit,
            toggle_btn, edit_mode_state
        ]
        
        # Add month containers to toggle outputs
        month_container_outputs = [month_containers[month] for month in months]
        
        # Add buttons to toggle outputs
        add_buttons_outputs = [add_buttons[month] for month in months]
        
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
        all_toggle_outputs = base_toggle_outputs + month_container_outputs + add_buttons_outputs + income_field_outputs

        # Connect the toggle button
        toggle_btn.click(
            fn=toggle_edit_mode,
            inputs=[edit_mode_state],
            outputs=all_toggle_outputs
        )

    return profile