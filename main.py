import os
import sys
import gradio as gr
from pymongo import MongoClient
from datetime import datetime

# Set up environment variables
if "MONGODB_PATH" not in os.environ:
    os.environ["MONGODB_PATH"] = "mongodb://127.0.0.1:27017"

# Declare variables
patient_selected = None
user_name = ""

# Connect to MongoDB
print("Connecting to the database...")
client = MongoClient(os.environ["MONGODB_PATH"])
try:
    client.admin.command('ismaster')
    print("Database connection successful")
except Exception as e:
    print("Database connection unsuccessful")
    sys.exit(1)
db = client["denials_tracker_db"]

# Functions
def date_format(dateString):
    for format in ('%m/%d/%y', '%m/%d/%Y'):
        try:
            return datetime.strptime(dateString, format)
        except ValueError:
            pass
    raise ValueError('no valid date format found')

def list_denials():
    denials = db.denials.find({"patient_id": patient_selected['_id']}).sort("dos", -1)
    table = "<table style='width: 100%'><tr><th style='width:10%'>Date of Service</th><th style='width:10%'>Bill Amount</th><th style='width:10%'>Status</th><th style='width:70%'>Notes</th></tr>"

    for denial in denials:
        table += "<tr valign='top'><td>" + denial["dos"].strftime("%m/%d/%Y") + "</td><td>" + str(denial["bill_amt"]) + "</td><td>" + 'denial["status"]' + "</td>"
        # list all notes in decending order
        table += "<td><ul>"
        for note in db.notes.find({"_id": {"$in": denial["notes"]}}).sort("input_date", -1):
            table += "<li>" + "(" + note["input_date"].strftime("%m/%d/%Y") + ") " + note["input_user"] + ": " + note["note"] + "</li>"
        table += "</ul></td></tr>"
    table += "</table>"

    return table

def find_patient(lastname, firstname, dob):

    if lastname != "" and firstname == "" and dob == "":
        dat = {"last_name": lastname.upper()}
    elif lastname == "" and firstname != "" and dob == "":
        dat = {"first_name": firstname.upper()}
    elif lastname == "" and firstname == "" and dob != "":
        dat = {"dob": date_format(dob)}
    elif lastname != "" and firstname != "" and dob == "":
        dat = {"last_name": lastname.upper(), "first_name": firstname.upper()}
    elif lastname != "" and firstname == "" and dob != "":
        dat = {"last_name": lastname.upper(), "dob": date_format(dob)}
    elif lastname == "" and firstname != "" and dob != "":
        dat = {"first_name": firstname.upper(), "dob": date_format(dob)}
    elif lastname != "" and firstname != "" and dob != "":
        dat = {"last_name": lastname.upper(), "first_name": firstname.upper(), "dob": date_format(dob)}
    else:
        dat = {}
    
    patient = db.patients.find_one(dat)

    # Return patient _id ObjectId
    if patient:
        global patient_selected
        patient_selected = patient
        return "Patient: " + patient_selected["last_name"] + ", " + patient_selected["first_name"] + " (" + patient_selected["dob"].strftime("%m/%d/%Y") + ")"
    else:
        return "Patient not found"
      
def upsert_denial(dos, bill_amt, note, user = ""):
    bill_amt = round(float(bill_amt),2)

    dat = {"input_date": datetime.now(), "input_user": user, "note": note}
    insert_note = db.notes.insert_one(dat)

    inserted_denial = db.denials.find_one_and_update({"patient_id": patient_selected['_id'], "dos": datetime.strptime(dos, "%m/%d/%Y"), "bill_amt": bill_amt},
                                                        {"$push": {"notes": insert_note.inserted_id}},
                                                        upsert=True),
    return inserted_denial

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
with gr.Blocks(title="Denials Tracker", analytics_enabled=False) as ui:
    with gr.Tab("Record"):
        with gr.Row():
            record_lastName = gr.Textbox(label="Last Name")
            record_fistName = gr.Textbox(label="First Name")
            record_dob = gr.Textbox(label="Date of Birth")
            record_find_btn = gr.Button("Find")
        with gr.Row():
            record_patientList = gr.Markdown()
        with gr.Accordion(label= "Input new note", visible=False, open=False) as record_input_accordion:
            with gr.Row():
                record_dos = gr.Textbox(label="Date of Service")
                record_billAmt = gr.Textbox(label="Bill Amount")
            note = gr.TextArea(label="Note")
            record_submit_btn = gr.Button("Submit")
        with gr.Column():
            noteList = gr.HTML()
    with gr.Tab("Search"):
        with gr.Row():
            filter = gr.Dropdown(label="Filter", choices=["Last Name", "First Name", "Date of Birth", "Date of Service", "Bill Amount", "Paid?"])
            condition = gr.Dropdown(label="Condition", choices=["Equals", "Contains"])
            value = gr.Textbox (label="Value")
            filter_btn = gr.Button("Filter")
        out = gr.TextArea(label="Results")
    with gr.Tab("Settings"):
        settings_list = gr.Dropdown(label="Options", choices=["Add New Patient"], value="Add New Patient")
        with gr.Row():            
            ln = gr.Textbox(label="Last Name")
            fn = gr.Textbox(label="First Name")
            dob = gr.Textbox(label="Date of Birth")
            setting_addNewPt_submit_btn = gr.Button("Submit")
        output = gr.Markdown(label="Output")
    
    # Event Handlers
    record_find_btn.click(fn = find_patient, inputs = [record_lastName, record_fistName, record_dob], outputs = record_patientList).then(
        fn = lambda _: gr.Accordion(visible=True), outputs = record_input_accordion).then(
        fn = list_denials, outputs = noteList)
    record_submit_btn.click(fn = upsert_denial, inputs = [record_dos, record_billAmt, note], outputs = noteList).then(
        fn = list_denials, outputs = noteList)
    
    setting_addNewPt_submit_btn.click(fn = add_patient, inputs = [ln, fn, dob], outputs = output)

ui.launch(server_name='0.0.0.0', show_api=False)