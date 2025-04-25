🏥 Insurance Denial Tracker Application
📘 Overview
The Insurance Denial Tracker is a web-based system that helps healthcare providers track, manage, and analyze insurance denials and appeals. Built using Python, MongoDB, and a clean Gradio UI, this application streamlines denial management through centralized logging, custom reporting, and intuitive user interaction.

❗ Problem Statement
Insurance denial tracking is often scattered across manual notes or isolated EHR entries, leading to:

Data loss or duplication

Limited visibility across patients

Complicated appeals

Revenue cycle inefficiencies

✅ Solution
The Insurance Denial Tracker addresses these challenges with:

🗃 Centralized Denials Database

📈 Detailed Progress Tracking and History

🔍 Filterable and Searchable Reports

💻 Modern Web Interface with Gradio

🧑‍💼 Role-Based Access (Admin/User/Guest)

🌐 Accessible on Local Network via Docker

🔑 Key Features
Claim Denial Entry
Log patient info, service dates, costs, reasons, and appeal status

Appeal Documentation
Capture and track progress of appeals

Granular Reporting
Filter by payer, reason, date, cost, and more

Admin Controls
Manage users, roles, and system configuration (in development)

🗃 Data Tracked
Patient Last Name

Patient First Name

Date of Birth (MM-DD-YYYY)

Admit Date and Discharge Date

Total Claim Cost

Denied Cost

Denial Reason

Payer

Appeal Status

⚙ Technology Stack

Component	Technology
Frontend	Gradio
Backend	Python
Database	MongoDB
Container	Docker
🚀 Installation Guide
Prerequisites
Git

Docker

Setup Instructions
bash
Copy
Edit
git clone https://github.com/ksu-hmi/insurance-denial-tracker.git
cd insurance-denial-tracker
docker compose up -d
Access the App
Open your browser and visit:
http://localhost:7860
Default login:

Username: admin

🧹 Uninstallation
bash
Copy
Edit
docker compose down
Delete the repository folder if needed.

🛠 Troubleshooting
Having issues? Open a GitHub Issue or contact the maintainer.

🤝 Contributing
We welcome community contributions!
Fork this repo, add your features, and submit a pull request.

🪪 License
MIT License

👩‍💻 Maintainer
Christina Ball
Developer & Owner
Insurance Denial Tracker Project

