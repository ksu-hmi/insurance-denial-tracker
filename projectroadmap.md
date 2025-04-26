# 📋 Project Roadmap: Insurance Denial Tracker

## 🏁 Sprint 1: Setup and Planning
- [x] Set up local development environment (Python, MongoDB, Gradio)
- [x] Create initial GitHub repository
- [x] Configure `.gitignore` to protect sensitive files
- [x] Establish MongoDB connection with `.env` for security
- [x] Create a basic test form with Gradio

## 🚀 Sprint 2: Core Development and Analysis
- [x] Build Gradio form for denial entry with patient information (Last Name, First Name, DOB, Admit Date, Discharge Date, etc.)
- [x] Add fields for total claim cost and denied cost
- [x] Save denial records to MongoDB
- [x] Validate form inputs (date formats, logical checks like discharge date after admit date)
- [x] Create initial data analysis script (`analyze_denials.py`)
- [x] Analyze denial data using Pandas (count by payer, reason, appeal status)
- [x] Summarize and print total and average denial costs
- [x] Update README.md with full project description
- [x] Track progress and emerging tasks in projectroadmap.md

## 🏗️ Sprint 3: Refinements and Presentation Prep
- [x] Corrected sensitive info handling for .env
- [x] Improved error handling for database submissions
- [x] Added dropdown for "Appeal Status" options
- [x] Enhanced README.md for professional project documentation
- [x] Prepared final presentation PowerPoint slide
- [x] Scheduled and/or completed project video presentation in Microsoft Teams

## ✨ Future Enhancements (Planned)
- [ ] Create dashboard visualization for denial analytics (using Gradio plots or Dash/Flask)
- [ ] Auto-generate appeal letters based on denial data
- [ ] Predict common denial causes using machine learning (scikit-learn or similar)
- [ ] Add login system with encrypted password storage
- [ ] Deploy application to a public server (AWS, Azure, etc.)

# 📌 Notes
- Code commits and progress updates are available on the [KSU-HMI GitHub organization repository](https://github.com/ksu-hmi/insurance-denial-tracker).
- Final project presentation and code demo scheduled via Microsoft Teams.




