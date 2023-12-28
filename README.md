# Insurance Denial Tracker Application

## Overview

This repository contains the source code for a web application designed to track, manage, and report insurance denials and appeals. The application is built with Python for back-end operations, MongoDB for data management, and a responsive Gradio web UI for user interaction.

## Problem Statement

Currently, the tracking of denial progress is manual and documented within patient charts. This approach is prone to loss, misplacement, and difficulty in comprehensive analysis. Additionally, while denial progress can be entered into the Electronic Health Records (EHR), notes are restricted to individual patient records, limiting the ability to query across patients for broader denial reports.

## Solution

The Insurance Denial Tracker Application aims to address these challenges by providing:

* **Centralized Denials Database:** A dedicated database to log all denials after claim denial are received, eliminating reliance on paper or scattered EHR notes.
* **Progress Tracking:** The ability to capture denial details upon receipt, add appeals as notes or other progress, and track the progress of each case over time.
* **Filter & Report:** Filtering options to easily identify outstanding denials based on various criteria, such as date of service, patient, or bill amount.
* **User-Friendly Interface:** A modern and intuitive web interface accessible through any web browser.
* **Local Deployment:** The application can be deployed directly on a local server for centralized and shared access to every computer in the local network.

## Technology Stack

* **Front-End:** Gradio
* **Back-End:** Python
* **Database:** MongoDB

## Getting Started

1. **Clone the project repository:** Use the command `git clone https://github.com/kensantanu/Denials-Tracker`.
2. **Install Dependencies:** Refer to the `requirements.txt` file for Python dependencies and install them using the command `pip install -r requirements.txt`.
3. **Configure Database:** Modify the MONGODB_PATH environment variable in run.bat or run.sh as per your setup.
4. **Start the Web Server:** Launch the application using run.bat or run.sh, depending on your server operating system.
5. **Access the UI:** Open a web browser and navigate to http://server-ip-address:port (e.g., http://127.0.0.1:7860).

## Contributing

This project is open-source and welcomes contributions. Feel free to fork the repository, add features, improve the code, and submit pull requests.