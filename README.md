# Insurance Denial Tracker Application

## Overview
The Insurance Denial Tracker Application is a web-based system designed to help healthcare providers track, manage, and analyze insurance denials and appeals. Built with Python, MongoDB, and Gradio, this tool offers a centralized, user-friendly interface to streamline the denial tracking process.

## Problem Statement
Insurance denial tracking is often performed manually or buried within individual Electronic Health Record (EHR) notes, leading to data silos, difficulty in analysis, and potential data loss. This lack of centralized tracking reduces transparency, complicates appeals, and impacts revenue cycle efficiency.

## Solution
The Insurance Denial Tracker addresses these challenges by offering:

- **Centralized Denials Database**: A unified repository for logging all denial-related information.
- **Detailed Progress Tracking**: Record denials upon receipt and append appeal details or updates over time.
- **Custom Reporting Tools**: Filter denials by patient, date of service, denial reason, and more.
- **Modern Interface**: Built with Gradio for clean, intuitive user interaction.
- **Local Network Accessibility**: Host locally to provide access across multiple workstations.

## Key Features
- **Claim Denial Management**: Log and update denied claims with relevant metadata (e.g., patient name, DOB, service dates, denial amount).
- **Appeal Documentation**: Attach appeal history or progress notes to each denial.
- **Granular Reporting**: Generate reports using filters such as payer, denial status, claim cost, or dates.
- **Role-Based Access**: Supports Guest, User, and Admin roles (with encrypted password support in development).
- **Admin Controls**: Admins can create and manage other user accounts.

## Data Tracked
- Patient Name
- Patient Date of Birth
- Date(s) of Service
- Denial Amount
- Total Billed Amount
- Denial Reason
- Appeal Status

## Technology Stack
- **Frontend**: Gradio
- **Backend**: Python
- **Database**: MongoDB
- **Containerization**: Docker

## Installation Guide

### Prerequisites
- Git: [https://git-scm.com/downloads](https://git-scm.com/downloads)
- Docker: [https://docs.docker.com/get-docker/](https://docs.docker.com/get-docker/)

### Setup Steps
```bash
git clone https://github.com/ksu-hmi/insurance-denial-tracker.git
cd insurance-denial-tracker
docker compose up -d
```

### Access the App
Open a web browser and navigate to:
```
http://localhost:7860/
```
Default credentials:
- **Username**: admin

### Uninstallation
```bash
docker compose down
```
Optionally delete the cloned repository folder.

## Troubleshooting
Need help? Create an issue or contact the developer for support.

## Contributing
We welcome community contributions! Feel free to fork, develop, and open a pull request.

## License
MIT License

## Maintainer
**Christina Ball**  
Developer & Owner of the Insurance Denial Tracker Project

