import random
import sys
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
from faker import Faker

# Connect to MongoDB
print("Connecting to the database...")
client = MongoClient("db:27017")
try:
    client.admin.command('ismaster')
    print("Database connection successful")
except Exception as e:
    print("Database connection unsuccessful")
    sys.exit(1)
db = client["denials_tracker_db"]

# Create faker object
fake = Faker()

# how many patients to generate
inp = input("How many patients to generate? ")
for i in range(int(inp)):
    # generate random last name, first name, and dob
    last_name = fake.last_name().upper()
    first_name = fake.first_name().upper()
    dob = fake.date_of_birth(minimum_age=18, maximum_age=90)
    dob = str(dob)
    dob = datetime.strptime(dob, "%Y-%m-%d")
    patient = {
        "last_name": last_name,
        "first_name": first_name,
        "dob": dob
    }

    inserted = db.patients.insert_one(patient)
    print(patient)

    # insert random denials
    patient_id = inserted.inserted_id

    for j in range(random.randint(1, 5)):

        # get random date of service
        dos = fake.date_of_birth(minimum_age=0, maximum_age=2)
        dos = str(dos)
        dos = datetime.strptime(dos, "%Y-%m-%d")

        user = "test_user"

        bill_amt = fake.random_element(elements=(250, 500, 750, 1500))
        bill_amt = round(float(bill_amt),2)

        status = fake.random_element(elements=("Denied", "Appealed", "Paid", "Write Off", "Other"))

        if status == "Paid":
            paid_amt = fake.pyfloat(left_digits=4, right_digits=2, positive=True, min_value=1, max_value=bill_amt)
        else:
            paid_amt = 0.00

        # random for loop between 1 and 5
        for k in range(random.randint(1, 5)):
            note = fake.text(max_nb_chars=200, ext_word_list=None)

            # Insert note
            dat = {"input_date": datetime.now(), "input_user": user, "note": note}
            insert_note = db.notes.insert_one(dat)

            # Update denial
            updated_denial = db.denials.find_one_and_update({"patient_id": ObjectId(patient_id), "dos": dos}, 
                                                                {"$set": {"bill_amt": bill_amt, "status": status, "paid_amt": paid_amt},
                                                                    "$push": {"notes": insert_note.inserted_id}},
                                                                upsert=True)