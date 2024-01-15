import os
import sys
import gradio as gr
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
        return "Login successful", session_state
    else:
        session_state['user'] = "Guest"
        return "Invalid username", session_state

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
      
def set_denial(dos, bill_amt, status, paid_amt, note, session_state):
    if dos == "":
        raise gr.Error("Date of Service cannot be blank!")
    
    dos = dos.strip()
    
    user = session_state["user"]

    #find denial
    denial = db.denials.find_one({"patient_id": ObjectId(session_state['patient_id']), "dos": date_format(dos)})

    # if bill_amt is blank, use existing value
    if bill_amt == "":
        if denial:
            bill_amt = denial["bill_amt"]
        else:
            bill_amt = 0.00
    else:
        bill_amt = round(float(bill_amt),2)

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
    updated_denial = db.denials.find_one_and_update({"patient_id": ObjectId(session_state['patient_id']), "dos": date_format(dos)}, 
                                                        {"$set": {"bill_amt": bill_amt, "status": status, "paid_amt": paid_amt},
                                                            "$push": {"notes": insert_note.inserted_id}},
                                                        upsert=True)
    
    return "Note added"

def gather_report_state(filter, filter_condition, value, sort, sort_condition):
    report_state = {
        "filter": filter,
        "filter_condition": filter_condition,
        "filter_value": value,
        "sort": sort,
        "sort_condition": sort_condition
    }
    return report_state

def get_report(report_state):

    # build filter
    if report_state["filter"] == "Date of Service":
        filter = "dos"
    elif report_state["filter"] == "Bill Amount":
        filter = "bill_amt"
    elif report_state["filter"] == "Status":
        filter = "status"
    else:
        filter = ""

    if report_state["filter_condition"] == "Equals":
        filter_condition = "$eq"
    elif report_state["filter_condition"] == "Greater Than":
        filter_condition = "$gt"
    elif report_state["filter_condition"] == "Less Than":
        filter_condition = "$lt"
    else:
        filter_condition = ""

    if filter == "dos":
        filter = {filter: date_format(report_state["filter_value"])}
    elif filter == "bill_amt" or filter == "paid_amt":
        filter = {filter: {filter_condition: float(report_state["filter_value"])}}
    elif filter == "status":
        filter = {filter: report_state["filter_value"]}
    else:
        filter = {}

    # build sort
    if report_state["sort"] == "Date of Service":
        sort = "dos"
    elif report_state["sort"] == "Bill Amount":
        sort = "bill_amt"
    elif report_state["sort"] == "Status":
        sort = "status"
    elif report_state["sort"] == "Last Note":
        sort = "notes"
    else:
        sort = ""

    if report_state["sort_condition"] == "Ascending":
        sort_condition = 1
    elif report_state["sort_condition"] == "Descending":
        sort_condition = -1
    else:
        sort_condition = ""

    if sort != "" and sort_condition != "":
        sort = [(sort, sort_condition)]
    else:
        sort = []

    denials = db.denials.find(filter).sort(sort)      

    # build table
    table = []
    table = "<table><tr><th>Patient</th><th>Date of Service</th><th>Bill Amount</th><th>Status</th><th>Last Note</th></tr>"

    for denial in denials:
        patient = db.patients.find_one({"_id": denial["patient_id"]})        
        table += "<tr><td>" + patient["last_name"] + ", " + patient["first_name"] + " (" + patient["dob"].strftime("%m/%d/%Y") + ")</td>"
        table += "<td>" + denial["dos"].strftime("%m/%d/%Y") + "</td>"
        table += "<td>" + str(denial["bill_amt"]) + "</td>"
        table += "<td>" + denial["status"] + "</td>"
        note = db.notes.find_one({"_id": denial["notes"][-1]})
        table += "<td>" + "(" + note["input_date"].strftime("%m/%d/%y") + ") <b>" + note["input_user"] + "</b>: " + note["note"] + "</td></tr>"
    
    table += "</table>"

    return table

def settings_options(selection):
    if selection == "Login":
        return [gr.Column(visible=True), gr.Column(visible=False)]
    elif selection == "Add New Patient":
        return [gr.Column(visible=False), gr.Column(visible=True)]

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

    username_label = gr.Markdown("Logged in as: Guest")
    with gr.Tab("Record"):
        with gr.Row():
            record_patientSelected_dropdown = gr.Dropdown(label="Patient List", choices=get_patients(), scale=5)
            record_patientRefresh_btn = gr.Button("Refresh")
        with gr.Row(visible=False) as record_addNew_row:
            record_noteAdd_btn = gr.Button("Add New Note")
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
            report_filter = gr.Dropdown(label="Filter", choices=["Date of Service", "Bill Amount", "Status"], value="Status")
            report_filter_condition = gr.Dropdown(label="Condition", choices=["Equals", "Greater Than", "Less Than"], value="Equals")
            report_filter_value = gr.Textbox (label="Value", value="Denied")
        with gr.Row():
            report_sort = gr.Dropdown(label="Sort", choices=["Date of Service", "Bill Amount", "Status", "Last Note"], value="Bill Amount")
            report_sort_condition = gr.Dropdown(label="Condition", choices=["Ascending", "Descending"], value="Descending")
        report_create_btn = gr.Button("Create Report")
        report_list = gr.HTML()
    with gr.Tab("Setting"):
        settings_optionList_dropdown = gr.Dropdown(label="Options", choices=["Login"], value="Login")
        with gr.Column(visible=True) as settings_login_grp:
            with gr.Row():
                settings_login_username = gr.Textbox(label="Username")
                settings_login_password = gr.Textbox(label="Password", interactive=False)
                settings_login_login_btn = gr.Button("Login")
            with gr.Row():
                settings_login_label = gr.Markdown()
        with gr.Column(visible=False) as settings_manageUser_grp:
            with gr.Row():
                settings_manageUser_username = gr.Textbox(label="Username")
                settings_manageUser_password = gr.Textbox(label="Password", interactive=False)
                settings_manageUser_role = gr.Dropdown(label="Role", choices=["administrator", "user"], value="user")
                settings_manageUser_createUser_btn = gr.Button("Create User")
            with gr.Row():
                settings_manageUser_label = gr.Markdown()
    
    # Event Handlers
    # Record Tab
    record_patientSelected_dropdown.select(
        fn = select_patient, inputs = [record_patientSelected_dropdown, session_state], outputs = session_state).then(
        fn = list_denials, inputs = session_state, outputs = noteList)    
    record_patientRefresh_btn.click(
        fn = lambda: gr.Dropdown(choices=get_patients()), outputs = record_patientSelected_dropdown)
    
    record_noteAdd_btn.click(
        fn = lambda: [gr.Textbox(value=""), gr.Textbox(value=""), gr.Dropdown(value=None), gr.Textbox(value=""), gr.TextArea(value="")], outputs = [record_addNewNote_dos, record_addNewNote_billAmt, record_addNewNote_status, record_addNewNote_paidAmt, record_addNewNote_note]).then(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewPt_col).then(
        fn = lambda: gr.Column(visible=True), outputs = record_addNewNote_col)
    record_addNewNote_status.change(
        fn = lambda x: gr.Textbox(visible=True) if x == "Paid" else gr.Textbox(value=0, visible=False), inputs = record_addNewNote_status, outputs = record_addNewNote_paidAmt)
    record_addNewNote_addNote_btn.click(
        fn = set_denial, inputs = [record_addNewNote_dos, record_addNewNote_billAmt, record_addNewNote_status, record_addNewNote_paidAmt, record_addNewNote_note, session_state]).success(
        fn = lambda: gr.Textbox(value=""), outputs = record_addNewNote_billAmt).then(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewNote_col).then(
        fn = list_denials, inputs = session_state, outputs = noteList)
    record_addNewNote_cancel_btn.click(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewNote_col)
    
    record_patientAdd_btn.click(
        fn = lambda: [gr.Textbox(value=""), gr.Textbox(value=""), gr.Textbox(value="")], outputs = [record_addNewPt_lastName, record_addNewPt_firstName, record_addNewPt_dob]).then(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewNote_col).then(
        fn = lambda: gr.Column(visible=True), outputs = record_addNewPt_col)
    record_addNewPt_addPatient_btn.click(
        fn = set_patient, inputs = [record_addNewPt_lastName, record_addNewPt_firstName, record_addNewPt_dob]).success(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewPt_col).then(
        fn = lambda: gr.Dropdown(choices=get_patients()), outputs = record_patientSelected_dropdown)
    record_addNewPt_cancel_btn.click(
        fn = lambda: gr.Column(visible=False), outputs = record_addNewPt_col)
    
    # Report Tab
    report_create_btn.click(
        fn = gather_report_state, inputs = [report_filter, report_filter_condition, report_filter_value, report_sort, report_sort_condition], outputs = report_state).then(
        fn = get_report, inputs = report_state, outputs = report_list)
    
    # Settings Tab
    settings_optionList_dropdown.select(fn = settings_options, inputs = settings_optionList_dropdown, outputs = [settings_login_grp])
    settings_login_login_btn.click(
        fn = authenticate, inputs = [settings_login_username, session_state], outputs = [settings_login_label, session_state]).then(
        fn = lambda x: gr.Row(visible=True) if x['user'] != "Guest" else gr.Row(visible=False), inputs = session_state, outputs = record_addNew_row).then(
        fn = lambda: gr.Dropdown(choices=["Login"]), outputs = settings_optionList_dropdown).then(
        fn = update_username, inputs = session_state, outputs = username_label)
    settings_manageUser_createUser_btn.click(fn = set_user, inputs = [settings_manageUser_username, settings_manageUser_password], outputs = settings_manageUser_label)

# Run Gradio server
ui.launch(server_name='0.0.0.0', show_api=False)