# Project Roadmap – Insurance Denial Tracking System

## 🏁 Sprint 1: Setup and Exploration

### 🔍 Codebase 1 Reviewed
**Title**: Denials Tracker  
**Link**: [https://github.com/kennysantanu/denials-tracker](https://github.com/kennysantanu/denials-tracker)  
**Language**: Python (Streamlit, Pandas, SQLite)  
**Last Updated**: 2023  
**License**: MIT

### 🧠 What I Learned
- How to use Streamlit for quick front-end UI creation
- How SQLite can be used for small-scale denial tracking
- The structure of basic denial fields like `claim_id`, `payer`, `denial_reason`, `appeal_status`
- Useful inspiration for UI layout and data table views

---

### 🔍 Codebase 2 Reviewed
**Title**: Denial Reason Prediction Model  
**Link**: [https://github.com/MacHu-GWU/Denial-Reason-Prediction-Model](https://github.com/MacHu-GWU/Denial-Reason-Prediction-Model)  
**Language**: Python (Pandas, Scikit-learn)  
**Last Updated**: ~10 years ago  
**License**: MIT

### 🧠 What I Learned
- How to preprocess healthcare claim data for modeling
- Methods for encoding categorical features
- Application of logistic regression to predict denial likelihood
- Model evaluation using accuracy and confusion matrices
- This code inspired me to include predictive analytics in future sprints


## 🏗️ Sprint 2: Development and Progress

### 🎯 Goals
- [x] Build a form interface to enter denial details (using Gradio)
- [x] Store denial data in MongoDB (connection successful via `.env`)
- [x] Use Pandas to group and count denials by reason, payer, and status
- [ ] Create a basic dashboard to display analytics
- [ ] Begin drafting auto-generated appeal letter templates
- [ ] Plan future integration of predictive modeling

### ✅ Completed Tasks
- MongoDB Atlas connection established and tested
- `.env` file configured and functional
- `test_mongo_connection.py` script confirmed successful connection
- Project cloned and running locally with required dependencies
- Streamlit environment partially tested (pending dashboard integration)
- Several commits completed with meaningful messages in GitHub organization repo

---

## 🧠 Notes
These two codebases provided both structural guidance and stretch ideas. One taught me how to track and display denials simply with Streamlit and SQLite, and the other inspired future AI integration with machine learning. I plan to build on these to create a tool that is both practical and intelligent for denial management in healthcare.


