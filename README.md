# Insurance Denial Tracker Application

## Overview

This repository contains the source code for a web application designed to track, manage, and report insurance denials and appeals. The application is built with Python for back-end operations, MongoDB for data management, and a responsive Gradio web UI for user interaction.

## Problem Statement

Currently, the tracking of denial progress is manual and documented within patient charts. This approach is prone to loss, misplacement, and difficulty in comprehensive analysis. Additionally, while denial progress can be entered into the Electronic Health Records (EHR), notes are restricted to individual patient records, limiting the ability to query across patients for broader denial reports.

## Solution

The Insurance Denial Tracker Application aims to address these challenges by providing:

* **Centralized Denials Database:** A dedicated database to log all denials after a claim denial are received, eliminating reliance on paper or scattered EHR notes.
* **Progress Tracking:** The ability to capture denial details upon receipt, add appeals as notes or other progress, and track the progress of each case over time.
* **Filter & Report:** Filtering options to easily identify outstanding denials based on various criteria, such as date of service, patient, or bill amount.
* **User-Friendly Interface:** A modern and intuitive web interface accessible through any web browser.
* **Local Deployment:** The application can be deployed directly on a local server for centralized and shared access to every computer in the local network.

## Key Functionalities:

* **Centralized Claims Management:** Seamlessly input and record received insurance claim denials, eliminating reliance on scattered document management and facilitating efficient data retrieval.
* **Comprehensive Reporting:** Generate insightful reports with granular filtering and sorting options based on pre-defined criteria (date of service, bill amount, paid amount, denials status).
* **User Roles:** While password encryption and cookie-based sessions are currently under development, the system already supports user roles (Guest, User, Admin ) for access management.
* **Administrative Privileges:** Admin users hold the authority to create and manage additional user accounts.

## Technology Stack

* **Front-End:** Gradio
* **Back-End:** Python
* **Database:** MongoDB
* **Deployment:** Docker

## Installation Guide

**Prerequisites:**

* **Git:** [https://git-scm.com/downloads](https://git-scm.com/downloads)
* **Docker:** [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

**Installation:**

1. **Clone this repository:**

   ```
   git clone https://github.com/kensantanu/denials-tracker
   ```

2. **Navigate to the project directory:**

   ```
   cd denials-tracker
   ```

3. **Build and run the server using Docker Compose:**

   ```
   docker compose up -d
   ```

**Accessing the Web App:**

* Once the app is running, Open a web browser and navigate to http://localhost:7860/
* The default username is `admin`.

**Uninstallation:**

1. **Navigate to the project directory and stop the running containers:**

   ```
   docker compose down
   ```

2. **(Optional) Delete the repository:**

   Safely delete the local repository directory after stopping the containers.

**Having trouble?**

If you encounter any issues during installation, feel free to reach out for assistance!

## Contributing

This project is open-source and welcomes contributions. Feel free to fork the repository, add features, improve the code, and submit pull requests.