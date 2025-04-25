import gradio as gr
from pymongo import MongoClient
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# MongoDB connection
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("MONGO_DB")]
collection = db["denials"]

def validate_date(date_str):
    try:
        return datetime.strptime(date_str, "%m-%d-%Y")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Use MM-DD-YYYY.")

def submit_denial(patient_last_name, patient_first_name, patient_dob, admit_date, discharge_date,
                  total_claim_cost, denied_cost, denial_reason, payer, appeal_status):
    # Required field check
    if not patient_last_name or not patient_first_name or not payer or not denial_reason:
        return "Error: Required fields are missing."

    try:
        dob = validate_date(patient_dob)
        admit = validate_date(admit_date)
        discharge = validate_date(discharge_date)
    except ValueError as ve:
        return str(ve)

    if discharge < admit:
        return "Error: Discharge date cannot be before admit date."
    if denied_cost > total_claim_cost:
        return "Error: Denied cost cannot exceed total claim cost."

    record = {
        "patient_last_name": patient_last_name,
        "patient_first_name": patient_first_name,
        "patient_dob": patient_dob,
        "admit_date": admit_date,
        "discharge_date": discharge_date,
        "total_claim_cost": total_claim_cost,
        "denied_cost": denied_cost,
        "denial_reason": denial_reason,
        "payer": payer,
        "appeal_status": appeal_status
    }

    try:
        collection.insert_one(record)
        return "Denial record submitted successfully."
    except Exception as e:
        return f"Database error: {str(e)}"

# Gradio Interface
denial_form = gr.Interface(
    fn=submit_denial,
    inputs=[
        gr.Textbox(label="Patient Last Name"),
        gr.Textbox(label="Patient First Name"),
        gr.Textbox(label="Date of Birth (MM-DD-YYYY)"),
        gr.Textbox(label="Admit Date (MM-DD-YYYY)"),
        gr.Textbox(label="Discharge Date (MM-DD-YYYY)"),
        gr.Number(label="Total Claim Cost"),
        gr.Number(label="Denied Cost"),
        gr.Textbox(label="Denial Reason"),
        gr.Textbox(label="Payer"),
        gr.Dropdown(label="Appeal Status", choices=[
            "Under Review",
            "Appeal Sent and Waiting Response",
            "Appeal Approved",
            "Appeal Denied"
        ])
    ],
    outputs="text",
    title="Submit Insurance Denial Record"
)

denial_form.launch()




