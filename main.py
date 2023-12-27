import os
import gradio as gr
from pymongo import MongoClient
from datetime import datetime

# Set up environment variables
if "MONGODB_PATH" not in os.environ:
    os.environ["MONGODB_PATH"] = "mongodb://127.0.0.1:27017"

# Connect to MongoDB
client = MongoClient(os.environ["MONGODB_PATH"])
db = client["denials_tracker_db"]

# Functions
def add_patient(ln, fn, dob):
    ln = ln.upper()
    fn = fn.upper()
    dob = datetime.strptime(dob, "%m/%d/%Y")
    patient = {
        "last_name": ln,
        "first_name": fn,
        "dob": dob
    }

    # check if patient already exists
    if db.patients.find_one(patient):
        output = "Patient already exists"
    else:
        db.patients.insert_one(patient)
        output = "Patient added"

    return output

# Gradio UI
with gr.Blocks() as ui:
    with gr.Tab("Record"):
        with gr.Row():
            ln = gr.Textbox(label="Last Name")
            fn = gr.Textbox(label="First Name")
            dob = gr.Textbox(label="Date of Birth")
            find_btn = gr.Button("Find")
        notes = gr.TextArea(label="Notes")
        record_submit_btn = gr.Button("Submit")
    with gr.Tab("Report"):
        with gr.Row():
            filter = gr.Dropdown(label="Filter", choices=["Last Name", "First Name", "Date of Birth", "Date of Service", "Bill Amount", "Paid?"])
            condition = gr.Dropdown(label="Condition", choices=["Equals", "Contains"])
            value = gr.Textbox (label="Value")
            filter_btn = gr.Button("Filter")
        out = gr.TextArea(label="Results")
    with gr.Tab("Settings"):
        settings_list = gr.Dropdown(label="Options", choices=["Add New Patient"], value="Add New Patient")
        with gr.Row():            
            ln = gr.Textbox (label="Last Name")
            fn = gr.Textbox (label="First Name")
            dob = gr.Textbox (label="Date of Birth")
            submit_btn = gr.Button("Submit")
        output = gr.Textbox (label="Output")
        
        submit_btn.click(fn = add_patient, inputs = [ln, fn, dob], outputs = output)

ui.launch(server_name='0.0.0.0')