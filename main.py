import os
import gradio as gr
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client["denials_tracker_db"]

with gr.Blocks() as ui:
    with gr.Tab("Record"):
        with gr.Row():
            ln = gr.Dropdown(label="Last Name")
            fn = gr.Dropdown(label="First Name")
            dob = gr.Dropdown(label="Date of Birth")
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
        gr.Markdown(
        """
        # Input New Patient
        """)
        with gr.Row():            
            ln = gr.Textbox (label="Last Name")
            fn = gr.Textbox (label="First Name")
            dob = gr.Textbox (label="Date of Birth")
        settings_submit_btn = gr.Button("Submit")

ui.launch(server_name='0.0.0.0')