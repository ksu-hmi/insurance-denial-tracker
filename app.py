import gradio as gr
import pandas as pd
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGO_URI"))
db = client["insurance_tracker"]
collection = db["denials"]

def submit_denial(claim_id, payer, denial_reason, appeal_status):
    record = {
        "claim_id": claim_id,
        "payer": payer,
        "denial_reason": denial_reason,
        "appeal_status": appeal_status
    }
    collection.insert_one(record)
    return f"✅ Denial recorded for claim ID: {claim_id}"

with gr.Blocks() as demo:
    gr.Markdown("### Insurance Denial Tracker")
    claim_id = gr.Textbox(label="Claim ID")
    payer = gr.Textbox(label="Payer")
    denial_reason = gr.Textbox(label="Denial Reason")
    appeal_status = gr.Textbox(label="Appeal Status")
    submit_btn = gr.Button("Submit")
    output = gr.Textbox(label="Status")

    submit_btn.click(fn=submit_denial, inputs=[claim_id, payer, denial_reason, appeal_status], outputs=output)

demo.launch()
