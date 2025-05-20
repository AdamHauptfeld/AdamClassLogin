import streamlit as st
import pandas as pd
import datetime
import os
import json
from streamlit_gsheets import GSheetsConnection

# Set page title
st.title("Classroom Attendance System")

#connect to Google sheet
sheet_url = "https://docs.google.com/spreadsheets/d/1hIm_7dU4PbEWus4eLRTldMU2R2XxdN5VzV1pECTmTpA/edit?usp=sharing"

conn = st.experimental_connection("ghseets", type=GSheetsConnection)
sheet_data = conn.read(spreadsheet=sheet_url, usecols=[0,1])
st.title(sheet_data)

# Config file to store the class code
CONFIG_FILE = "class_config.json"

# Function to load the class code
def load_class_code():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)
            return config.get("class_code", "")
    return ""

# Function to save the class code
def save_class_code(code):
    with open(CONFIG_FILE, 'w') as file:
        json.dump({"class_code": code}, file)

# Today's date for the filename
today = datetime.date.today().strftime("%Y-%m-%d")
csv_filename = f"attendance_{today}.csv"

# Initialize or load the attendance dataframe
if os.path.exists(csv_filename):
    attendance_df = pd.read_csv(csv_filename)
else:
    attendance_df = pd.DataFrame(columns=["Student Name", "Timestamp"])

# Check if we're in the admin section
page = st.sidebar.radio("Select Page", ["Student Attendance", "Teacher Admin"])

if page == "Student Attendance":
    # Student attendance form
    with st.form("attendance_form"):
        student_name = st.text_input("Student Name")
        class_code = st.text_input("Class Code", type="password")
        submit_button = st.form_submit_button("Submit Attendance")

    # Process form submission
    if submit_button and student_name and class_code:
        # Get the current class code
        correct_code = load_class_code()
        
        if class_code == correct_code:
            # Get current timestamp
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Add student to attendance
            new_record = pd.DataFrame({
                "Student Name": [student_name],
                "Timestamp": [timestamp]
            })
            
            # Update the dataframe and save to CSV
            attendance_df = pd.concat([attendance_df, new_record], ignore_index=True)
            attendance_df.to_csv(csv_filename, index=False)
            
            st.success(f"Attendance recorded for {student_name}!")
        else:
            st.error("Incorrect class code. Please try again.")

else:  # Teacher Admin page
    st.subheader("Teacher's Admin Panel")
    
    # Simple password protection for admin section
    admin_password = st.text_input("Admin Password", type="password")
    correct_admin_password = "teacher123"  # Replace with a more secure method
    
    if admin_password == correct_admin_password:
        st.success("Admin access granted")
        
        # Class code setting section
        st.subheader("Set Today's Class Code")
        current_code = load_class_code()
        new_code = st.text_input("New Class Code", value=current_code)
        
        if st.button("Update Class Code"):
            save_class_code(new_code)
            st.success(f"Class code updated to: {new_code}")
            st.info("Write this code on the whiteboard for students to enter.")
        
        # Display current attendance
        st.subheader("Today's Attendance")
        if os.path.exists(csv_filename):
            st.dataframe(attendance_df)
            
            # Download button for the CSV
            with open(csv_filename, 'rb') as file:
                st.download_button(
                    label="Download Attendance CSV",
                    data=file,
                    file_name=csv_filename,
                    mime="text/csv"
                )
        else:
            st.info("No attendance recorded for today yet.")
