import os
import sys
import gradio as gr
import pandas as pd
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime

# Set up environment variables
if "MONGODB_PATH" not in os.environ:
    os.environ["MONGODB_PATH"] = "mongodb://127.0.0.1:27017"

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

# check if any users exist
if db.users.count_documents({}) == 0:
    print("No users found. Create new admin account:")
    username = input("Username: ")
    db.users.insert_one({"username": username, "password": "", "role": "administrator"})

# Functions
def date_format(dateString):
    for format in ('%m/%d/%y', '%m/%d/%Y', '%m%d%Y'):
        try:
            return datetime.strptime(dateString, format)
        except ValueError:
            pass
    raise gr.Error('No valid date format found')

def authenticate(username, session_state):
    username = username.strip().lower()
    user = db.users.find_one({"username": username})
    if user:
        session_state['user'] = username
        return session_state
    else:
        session_state['user'] = "Guest"
        return session_state

def get_patients():
    patients = db.patients.find()

    patient_list = []

    for patient in patients:
        patient_list.append((patient["last_name"] + ", " + patient["first_name"] + " (" + patient["dob"].strftime("%m/%d/%Y") + ")", str(patient["_id"])))
    
    # sort by last name
    patient_list.sort(key=lambda x: x[0])

    return patient_list

def set_patient(ln, fn, dob):
    ln = ln.strip().upper()
    fn = fn.strip().upper()
    dob = dob.strip()

    # check if required fields are blank
    if ln == "" or fn == "" or dob == "":
        raise gr.Error("Last Name, First Name, and Date of Birth are required!")

    dob = date_format(dob)
    patient = {
        "last_name": ln,
        "first_name": fn,
        "dob": dob
    }

    # check if patient already exists
    if db.patients.find_one(patient):
        raise gr.Error("Patient already exists!")
    else:
        db.patients.insert_one(patient)
        gr.Info(ln + ", " + fn + " (" + dob.strftime("%m/%d/%Y") + ") added")
    
def select_patient(patient_id, session_state):
    session_state['patient_id'] = patient_id
    return session_state
    
def list_denials(session_state):
    denials = db.denials.find({"patient_id": ObjectId(session_state['patient_id'])}).sort("dos", -1)
    table = "<table style='width: 100%'><tr><th style='width:10%'>Date of Service</th><th style='width:10%'>Bill Amount</th><th style='width:10%'>Status</th><th style='width:70%'>Notes</th></tr>"

    for denial in denials:
        table += "<tr valign='top'><td>" + denial["dos"].strftime("%m/%d/%Y") + "</td><td>" + str(denial["bill_amt"]) + "</td><td>" + denial["status"] + "</td>"
        # list all notes in decending order
        table += "<td><ul>"
        for note in db.notes.find({"_id": {"$in": denial["notes"]}}).sort("input_date", -1):
            table += "<li>" + "(" + note["input_date"].strftime("%m/%d/%y") + ") <b>" + note["input_user"] + "</b>: " + note["note"] + "</li>"
        table += "</ul></td></tr>"
    table += "</table>"

    return table

def get_dos_dropdown(session_state):
    if session_state['patient_id'] == None:
        raise gr.Error("No patient selected!")

    dosList = []
    denials = db.denials.find({"patient_id": ObjectId(session_state['patient_id'])}).sort("dos", -1)

    for denial in denials:
        dosList.append(denial["dos"].strftime("%m/%d/%Y"))

    return gr.Dropdown(choices=dosList)

def get_denial(dos, session_state):
    if session_state['patient_id'] == None:
        raise gr.Error("No patient selected!")
    
    dos = date_format(dos)

    denial = db.denials.find_one({"patient_id": ObjectId(session_state['patient_id']), "dos": dos})
    session_state['denial_id'] = denial["_id"]
    bill_amt = denial["bill_amt"]
    paid_amt = denial["paid_amt"]
    status = denial["status"]

    noteList = []
    for note in db.notes.find({"_id": {"$in": denial["notes"]}}).sort("input_date", -1):
        noteList.append(("(" + note["input_date"].strftime("%m/%d/%y") + ") " + note["input_user"] + ": " + note["note"], str(note["_id"])))

    return bill_amt, gr.Dropdown(choices=get_status_dropdown(), value=status), paid_amt, gr.Dropdown(choices=noteList), session_state

def set_denial(denialId, patientId, dos, bill_amt, status, paid_amt, notesId):
    # insert_one
    if denialId == None:
        denial = {
            "patient_id": ObjectId(patientId),
            "dos": date_format(dos),
            "bill_amt": round(float(bill_amt),2),
            "status": status,
            "paid_amt": round(float(paid_amt),2),
            "notes": [ObjectId(notesId)]
        }
        db.denials.insert_one(denial)

    # update_one
    else:
        denial = {
            "bill_amt": round(float(bill_amt),2),
            "status": status,
            "paid_amt": round(float(paid_amt),2)
        }
        db.denials.update_one({"_id": ObjectId(denialId)}, {"$set": denial})
    
      
def add_denial(dos, bill_amt, status, paid_amt, note, session_state):
    if dos == "":
        raise gr.Error("Date of Service cannot be blank!")
    
    dos = dos.strip()

    dos = date_format(dos)
    
    user = session_state["user"]

    #find denial
    denial = db.denials.find_one({"patient_id": ObjectId(session_state['patient_id']), "dos": dos})

    # if bill_amt is blank, use existing value
    if bill_amt == "":
        if denial:
            bill_amt = denial["bill_amt"]
        else:
            bill_amt = 0.00
    else:
        # check if value is a number
        try:
            bill_amt = round(float(bill_amt),2)
        except ValueError:
            raise gr.Error("Bill Amount must be a number!")

    # if status is blank, use existing value
    if status == None:
        if denial:
            status = denial["status"]
        else:
            status = "Denied"

    # if paid_amt is blank, use existing value
    if paid_amt == "":
        if denial:
            paid_amt = denial["paid_amt"]
        else:
            paid_amt = 0.00
    else:
        paid_amt = round(float(paid_amt),2)

    # Insert note
    dat = {"input_date": datetime.now(), "input_user": user, "note": note}
    insert_note = db.notes.insert_one(dat)

    # Update denial
    updated_denial = db.denials.find_one_and_update({"patient_id": ObjectId(session_state['patient_id']), "dos": dos}, 
                                                        {"$set": {"bill_amt": bill_amt, "status": status, "paid_amt": paid_amt},
                                                            "$push": {"notes": insert_note.inserted_id}},
                                                        upsert=True)
    
    return "Note added"

def update_denial(bill_amt, status, paid_amt, session_state):
    if session_state['patient_id'] == None:
        raise gr.Error("No patient selected!")
    
    if session_state['denial_id'] == None:
        raise gr.Error("No denial selected!")
    
    if bill_amt == "":
        raise gr.Error("Bill Amount cannot be blank!")
    
    if status == None:
        raise gr.Error("Status cannot be blank!")
    
    if paid_amt == "":
        raise gr.Error("Paid Amount cannot be blank!")
    
    denial = {
        "bill_amt": round(float(bill_amt),2),
        "status": status,
        "paid_amt": round(float(paid_amt),2)
    }
    db.denials.update_one({"_id": ObjectId(session_state['denial_id'])}, {"$set": denial})

def get_note(note_id):
    note = db.notes.find_one({"_id": ObjectId(note_id)})
    return note["note"]

def set_note(notes_id, input_date, input_user, note):
    if notes_id == None:
        note = {
            "input_date": input_date,
            "input_user": input_user,
            "note": note
        }
        db.notes.insert_one(note)
    else:
        note = {
            "input_date": input_date,
            "input_user": input_user,
            "note": note
        }
        db.notes.update_one({"_id": ObjectId(notes_id)}, {"$set": note})

def update_note(note_id, note, session_state):

    input_date = db.notes.find_one({"_id": ObjectId(note_id)})["input_date"]

    set_note(note_id, input_date, session_state["user"], note)

def get_status_dropdown():
    status = db.denials.distinct("status")
    return status

def gather_report_state(filter, filter_condition, value_text, value_dropdown):
    if filter == "Date of Service":
        if value_text == "":
            raise gr.Error("Date of Service cannot be blank!")
        else:
            value_text = date_format(value_text)

    if filter == "Bill Amount":
        if value_text == "":
            raise gr.Error("Bill Amount cannot be blank!")
        else:
            # check if value is a number
            try:
                value_text = round(float(value_text),2)
            except ValueError:
                raise gr.Error("Bill Amount must be a number!")            

    if filter == "Status":
        if value_dropdown == None:
            raise gr.Error("Status cannot be blank!")
        else:
            value_dropdown = value_dropdown

    report_state = {
        "filter": filter,
        "filter_condition": filter_condition,
        "filter_value_text": value_text,
        "filter_value_dropdown": value_dropdown
    }
    return report_state

def get_report(report_state):
    
    if report_state["filter"] == "Date of Service":
        filter = "dos"
    elif report_state["filter"] == "Bill Amount":
        filter = "bill_amt"
    elif report_state["filter"] == "Status":
        filter = "status"
    else:
        filter = ""

    if report_state["filter_condition"] == "Equals":
        condition = "$eq"
    elif report_state["filter_condition"] == "Not Equals":
        condition = "$ne"
    elif report_state["filter_condition"] == "Greater Than":
        condition = "$gt"
    elif report_state["filter_condition"] == "Less Than":
        condition = "$lt"
    else:
        condition = ""

    if report_state["filter_value_text"] != "":
        value = report_state["filter_value_text"]
    elif report_state["filter_value_dropdown"] != None:
        value = report_state["filter_value_dropdown"]
    else:
        value = ""
    
    query = {filter: {condition: value}}

    # get denials
    denials = db.denials.find(query)

    dat = []

    for denial in denials:
        patient = db.patients.find_one({"_id": denial["patient_id"]})
        note = db.notes.find_one({"_id": denial["notes"][-1]})

        status = denial["status"] if denial["status"] != "Paid" else "Paid $" + "{:.2f}".format(denial["paid_amt"])
        dat.append({"Patient": patient["last_name"] + ", " + patient["first_name"] + "\n (" + patient["dob"].strftime("%m/%d/%Y") + ")",
                        "Date of Service": denial["dos"],
                        "Bill Amount": denial["bill_amt"],                    
                        "Status": status,
                        "Last Action": note["input_date"],
                        "Note": note["input_user"] + ": " + note["note"]})
        
    df = pd.DataFrame(dat)

    # return empty dataframe if no results
    if len(df) == 0:
        gr.Info("No results found")
        return gr.DataFrame(visible=False)
    
    # sort by note input date
    df = df.sort_values(by=["Last Action"])

    def format_date(val):
        return val.strftime("%m/%d/%y")
    
    # format dataframe
    formattedDF = df.style.format({"Date of Service": format_date}, subset=["Date of Service"]) \
        .format({"Bill Amount": "${:,.2f}"}, subset=["Bill Amount"]) \
        .format({"Last Action": format_date}, subset=["Last Action"]) \
        .set_properties(**{'font-family': 'var(--font)', 'background-color': 'var(--body-background-fill)', 'border-top': '1px solid var(--border-color-primary)', 'border-left': 'none', 'border-right': 'none', 'border-bottom': 'none'})    
    
    return gr.DataFrame(formattedDF, visible=True)

def settings_options(selection):
    pass

def set_user(username, password = "", role = "user"):
    user = {
        "username": username,
        "password": password,
        "role": role
    }

    # check if user already exists
    if db.users.find_one(user):
        output = "User already exists"
    else:
        db.users.insert_one(user)
        output = "User added"

    return output

def update_username(session_state):
    name = session_state['user']
    return gr.Markdown("Logged in as: " + name)

# Gradio UI
with gr.Blocks(title="Denials Tracker", analytics_enabled=False) as ui:   
    session_state = gr.State({'user': "Guest", 'patient_id': None, 'patient_list': []})
    
    with gr.Column() as header_grp:
        with gr.Row() as header_login_grp:
            settings_login_username = gr.Textbox(label="Username")
            settings_login_password = gr.Textbox(label="Password", interactive=False)
            settings_login_login_btn = gr.Button("Login")
        username_label = gr.Markdown("Logged in as: Guest")
    with gr.Tab("Record"):
        with gr.Row():
            record_patientSelected_dropdown = gr.Dropdown(label="Patient List", choices=get_patients(), scale=5)
            record_patientRefresh_btn = gr.Button("Refresh")
        with gr.Row(visible=False) as record_addNew_row:
            record_noteAdd_btn = gr.Button("Add New Note")
            record_editRecord_btn = gr.Button("Edit Record")
            record_patientAdd_btn = gr.Button("Add New Patient")
        with gr.Column(visible=False) as record_addNewNote_col:
            with gr.Tab("New Note"):
                with gr.Row():
                    record_addNewNote_dos = gr.Textbox(label="Date of Service")
                    record_addNewNote_billAmt = gr.Textbox(label="Bill Amount")
                    record_addNewNote_status = gr.Dropdown(label="Status", choices=["Denied", "Appealed", "Paid", "Write Off", "Other"], value="Denied")
                    record_addNewNote_paidAmt = gr.Textbox(label="Paid Amount", visible=False)
                record_addNewNote_note = gr.TextArea(label="Note")
                with gr.Row():
                    record_addNewNote_addNote_btn = gr.Button("Add Note")
                    record_addNewNote_cancel_btn = gr.Button("Cancel")
        with gr.Column(visible=False) as record_editRecord_col:
            with gr.Tab("Edit Record"):
                with gr.Row():
                    record_editRecord_dos_dropdown = gr.Dropdown(label="Date of Service")
                    record_editRecord_billAmt_text = gr.Textbox(label="Bill Amount")
                    record_editRecord_status_dropdown = gr.Dropdown(label="Status")
                    record_editRecord_paidAmt_text = gr.Textbox(label="Paid Amount", visible=False)
                with gr.Column():
                    record_editRecord_noteSelect_dropdown = gr.Dropdown(label="Select Note")
                    record_editRecord_note = gr.TextArea(label="Note")
                with gr.Row():
                    record_editRecord_save_btn = gr.Button("Save")
                    record_editRecord_cancel_btn = gr.Button("Cancel")
        with gr.Column(visible=False) as record_addNewPt_col:
            with gr.Tab("New Patient"):
                with gr.Row():     
                    record_addNewPt_lastName = gr.Textbox(label="Last Name")
                    record_addNewPt_firstName = gr.Textbox(label="First Name")
                    record_addNewPt_dob = gr.Textbox(label="Date of Birth")
                with gr.Row():
                    record_addNewPt_addPatient_btn = gr.Button("Add Patient")
                    record_addNewPt_cancel_btn = gr.Button("Cancel")
        with gr.Column() as record_patient_grp:
            noteList = gr.HTML()
    with gr.Tab("Report"):
        report_state = gr.State()
        with gr.Row():
            report_filter_dropdown = gr.Dropdown(label="Filter", choices=["Date of Service", "Bill Amount", "Status"], value="Status")
            report_filter_condition_dropdown = gr.Dropdown(label="Condition", choices=["Equals", "Not Equals", "Greater Than", "Less Than"], value="Not Equals")
            report_filter_value_text = gr.Textbox(label="Value", visible=False)
            report_filter_value_dropdown = gr.Dropdown(label="Value", choices=["Denied", "Appealed", "Paid", "Write Off", "Other"], value="Paid")
        report_create_btn = gr.Button("Create Report")
        report_list_dataframe = gr.DataFrame(height=700, wrap=True, visible=False)
    with gr.Tab("Setting"):
        settings_optionList_dropdown = gr.Dropdown(label="Options", choices=["Manage Users"], visible=False)
        with gr.Column(visible=False) as settings_manageUser_grp:
            with gr.Row():
                settings_manageUser_username = gr.Textbox(label="Username")
                settings_manageUser_password = gr.Textbox(label="Password", interactive=False)
                settings_manageUser_role = gr.Dropdown(label="Role", choices=["administrator", "user"], value="user")
                settings_manageUser_createUser_btn = gr.Button("Create User")
            with gr.Row():
                settings_manageUser_label = gr.Markdown()
    
    # Event Handlers
    # Header
    settings_login_login_btn.click(
        fn = authenticate, inputs = [settings_login_username, session_state], outputs = session_state).then(
        fn = lambda x: gr.Row(visible=True) if x['user'] != "Guest" else gr.Row(visible=False), inputs = session_state, outputs = record_addNew_row).then(
        fn = lambda: gr.Column(visible=False), outputs = header_login_grp).then(
        fn = update_username, inputs = session_state, outputs = username_label)
    settings_manageUser_createUser_btn.click(fn = set_user, inputs = [settings_manageUser_username, settings_manageUser_password], outputs = settings_manageUser_label)          

    # Record Tab
    record_patientSelected_dropdown.select(
        fn = select_patient, inputs = [record_patientSelected_dropdown, session_state], outputs = session_state).then(
        fn = list_denials, inputs = session_state, outputs = noteList)    
    record_patientRefresh_btn.click(
        fn = lambda: gr.Dropdown(choices=get_patients()), outputs = record_patientSelected_dropdown)
    
    record_noteAdd_btn.click(
        fn = lambda: [gr.Textbox(value=""), gr.Textbox(value=""), gr.Dropdown(value=None), gr.Textbox(value=""), gr.TextArea(value="")], outputs = [record_addNewNote_dos, record_addNewNote_billAmt, record_addNewNote_status, record_addNewNote_paidAmt, record_addNewNote_note]).then(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewPt_col).then(
        fn = lambda: gr.Column(visible=False), outputs = record_editRecord_col).then(
        fn = lambda: gr.Column(visible=True), outputs = record_addNewNote_col)
    record_addNewNote_status.change(
        fn = lambda x: gr.Textbox(visible=True) if x == "Paid" else gr.Textbox(value=0, visible=False), inputs = record_addNewNote_status, outputs = record_addNewNote_paidAmt)
    record_addNewNote_addNote_btn.click(
        fn = add_denial, inputs = [record_addNewNote_dos, record_addNewNote_billAmt, record_addNewNote_status, record_addNewNote_paidAmt, record_addNewNote_note, session_state]).success(
        fn = lambda: gr.Textbox(value=""), outputs = record_addNewNote_billAmt).then(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewNote_col).then(
        fn = list_denials, inputs = session_state, outputs = noteList)
    record_addNewNote_cancel_btn.click(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewNote_col)
    
    record_editRecord_btn.click(
        fn = lambda: gr.Textbox(value="", interactive=False), outputs = record_editRecord_billAmt_text).then(
        fn = lambda: gr.Dropdown(choices=None, value=None, interactive=False), outputs = record_editRecord_status_dropdown).then(
        fn = lambda: gr.Textbox(value="", interactive=False), outputs = record_editRecord_paidAmt_text).then(
        fn = lambda: gr.Dropdown(choices=None, value=None, interactive=False), outputs = record_editRecord_noteSelect_dropdown).then(
        fn = lambda: gr.TextArea(value="", interactive=False), outputs = record_editRecord_note).then(
        fn = lambda: gr.Button(interactive=False), outputs = record_editRecord_save_btn).then(
        fn = get_dos_dropdown, inputs = session_state, outputs = record_editRecord_dos_dropdown).success(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewNote_col).then(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewPt_col).then(
        fn = lambda: gr.Column(visible=True), outputs = record_editRecord_col)
    record_editRecord_dos_dropdown.select(
        fn = get_denial, inputs = [record_editRecord_dos_dropdown, session_state], outputs = [record_editRecord_billAmt_text, record_editRecord_status_dropdown, record_editRecord_paidAmt_text, record_editRecord_noteSelect_dropdown, session_state]).success(
        fn = lambda: gr.Textbox(interactive=True), outputs = record_editRecord_billAmt_text).then(
        fn = lambda: gr.Dropdown(interactive=True), outputs = record_editRecord_status_dropdown).then(
        fn = lambda: gr.Textbox(interactive=True), outputs = record_editRecord_paidAmt_text).then(
        fn = lambda: gr.Dropdown(interactive=True), outputs = record_editRecord_noteSelect_dropdown).then(
        fn = lambda: gr.TextArea(interactive=True), outputs = record_editRecord_note)
    record_editRecord_status_dropdown.change(
        fn = lambda x: gr.Textbox(visible=True) if x == "Paid" else gr.Textbox(value=0, visible=False), inputs = record_editRecord_status_dropdown, outputs = record_editRecord_paidAmt_text)
    record_editRecord_noteSelect_dropdown.select(
        fn = get_note, inputs = record_editRecord_noteSelect_dropdown, outputs = record_editRecord_note).then(
        fn = lambda: gr.Button(interactive=True), outputs = record_editRecord_save_btn)
    record_editRecord_save_btn.click(
        fn = update_denial, inputs = [record_editRecord_billAmt_text, record_editRecord_status_dropdown, record_editRecord_paidAmt_text, session_state]).success(
        fn = update_note, inputs = [record_editRecord_noteSelect_dropdown, record_editRecord_note, session_state]).success(
        fn = lambda: gr.Column(visible=False), outputs = record_editRecord_col).then(
        fn = list_denials, inputs = session_state, outputs = noteList)
    record_editRecord_cancel_btn.click(
        fn = lambda: gr.Column(visible=False), outputs = record_editRecord_col)

    record_patientAdd_btn.click(
        fn = lambda: [gr.Textbox(value=""), gr.Textbox(value=""), gr.Textbox(value="")], outputs = [record_addNewPt_lastName, record_addNewPt_firstName, record_addNewPt_dob]).then(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewNote_col).then(
        fn = lambda: gr.Column(visible=False), outputs = record_editRecord_col).then(
        fn = lambda: gr.Column(visible=True), outputs = record_addNewPt_col)
    record_addNewPt_addPatient_btn.click(
        fn = set_patient, inputs = [record_addNewPt_lastName, record_addNewPt_firstName, record_addNewPt_dob]).success(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewPt_col).then(
        fn = lambda: gr.Dropdown(choices=get_patients()), outputs = record_patientSelected_dropdown)
    record_addNewPt_cancel_btn.click(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewPt_col)
    
    # Report Tab
    report_filter_dropdown.select(
        fn = lambda x: gr.Textbox(visible=True) if x == "Date of Service" or x ==  "Bill Amount" else gr.Textbox(value="", visible=False), inputs = report_filter_dropdown, outputs = report_filter_value_text).then(
        fn = lambda x: gr.Dropdown(visible=True) if x == "Status" else gr.Dropdown(value=None, visible=False), inputs = report_filter_dropdown, outputs = report_filter_value_dropdown)
    report_create_btn.click(
        fn = gather_report_state, inputs = [report_filter_dropdown, report_filter_condition_dropdown, report_filter_value_text, report_filter_value_dropdown], outputs = report_state).success(
        fn = get_report, inputs = report_state, outputs = report_list_dataframe, scroll_to_output=True)
    
    # Settings Tab
    settings_optionList_dropdown.select(fn = settings_options, inputs = settings_optionList_dropdown)

# Run Gradio server
if __name__ == "__main__":
    ui.launch(server_name='0.0.0.0', show_api=False)