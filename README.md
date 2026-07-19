# AI-RESUME-ANALYSER
AI Resume Analyzer & ATS Score Checker
A professional web application built with Streamlit that analyzes resumes against job descriptions and provides ATS scores, skill matching, missing skills detection, and actionable improvement suggestions.

Features
User Authentication — Register, login, and secure session management
PDF Resume Upload — Extract text from PDF resumes using PyPDF2
Job Description Analysis — Paste and analyze any job description
ATS Score Checker — Composite score out of 100 with match percentage
Skill Extraction — Detect 150+ technical skills from resume and JD
Missing Skills Detection — Identify gaps between resume and job requirements
Resume Feedback — Strengths, improvements, and ATS optimization tips
Analytics Dashboard — Interactive Plotly charts and performance trends
Analysis History — Save and review all past analyses
Download Report — Export a full text report of any analysis
Project Structure
AI_Resume_Analyzer/
│
├── app.py              # Main Streamlit application
├── database.py         # SQLite database & user management
├── analyzer.py         # ATS scoring & skill extraction engine
├── utils.py            # PDF extraction & report generation
├── requirements.txt    # Python dependencies
├── README.md           # This file
│
├── uploads/            # Uploaded PDF resumes (auto-created)
├── reports/            # Generated text reports (auto-created)
├── database/           # SQLite database file (auto-created)
└── assets/
    └── style.css       # Custom UI styles
Prerequisites
Python 3.9 or higher
pip (Python package manager)
Installation
1. Clone or navigate to the project folder
cd C:\Users\gracy\OneDrive\Desktop\AI_Resume_Analyzer
2. Create a virtual environment (recommended)
python -m venv venv
Windows:

venv\Scripts\activate
macOS/Linux:

source venv/bin/activate
3. Install dependencies
pip install -r requirements.txt
NLTK data (stopwords, punkt tokenizer) is downloaded automatically on first run.

Running Locally
Quick Start (Windows)
For the easiest startup experience on Windows:

Double-click launch.vbs
This will automatically check for Python and dependencies
Install missing dependencies if needed
Start the Streamlit server
Open your browser to http://localhost:8501
Or if you prefer to see the startup process:

Double-click run.bat
Shows detailed startup messages
Checks for Python and Streamlit
Installs dependencies if missing
Starts the application
Manual Start
Start the Streamlit development server manually:

streamlit run app.py
The app opens automatically in your browser at:

http://localhost:8501
First-time usage
Click Create an Account on the login screen
Register with a username, email, and password
Sign in with your credentials
Upload a PDF resume and paste a job description
Click Analyze Resume to get your ATS score and feedback
Troubleshooting
Python not found:

Download Python 3.9+ from https://www.python.org/downloads/
During installation, check "Add Python to PATH"
Dependencies missing:

Run pip install -r requirements.txt manually
Or use run.bat which will install them automatically
Browser doesn't open:

Manually navigate to http://localhost:8501
Check if port 8501 is already in use
How ATS Score Is Calculated
The ATS score is a weighted composite of three components:

Component	Weight	Method
Skill Match	40%	Overlap of detected technical skills between resume and JD
Keyword Overlap	30%	NLTK tokenization + stopword removal, keyword intersection ratio
Text Similarity	30%	Scikit-learn TF-IDF vectorization + cosine similarity
Formula:

ATS Score = (Skill Match × 0.40) + (Keyword Overlap × 0.30) + (TF-IDF Similarity × 0.30)
Score Interpretation:

Score	Rating
75–100	Excellent Match
50–74	Moderate Match
0–49	Needs Improvement
Database Schema
users table
Column	Type	Description
id	INTEGER	Primary key
username	TEXT	Unique username
email	TEXT	Unique email address
password_hash	TEXT	SHA-256 hashed password
salt	TEXT	Random salt for hashing
created_at	TEXT	Registration timestamp (UTC)
analyses table
Column	Type	Description
id	INTEGER	Primary key
user_id	INTEGER	Foreign key → users.id
resume_filename	TEXT	Original PDF filename
job_description	TEXT	Full job description text
ats_score	REAL	ATS score (0–100)
match_percentage	REAL	Overall match percentage
resume_skills	TEXT	JSON array of detected resume skills
jd_skills	TEXT	JSON array of JD skills
missing_skills	TEXT	JSON array of missing skills
matched_skills	TEXT	JSON array of matched skills
strengths	TEXT	JSON array of strength feedback
improvements	TEXT	JSON array of improvement feedback
suggestions	TEXT	JSON array of ATS suggestions
created_at	TEXT	Analysis timestamp (UTC)
Deploy on Streamlit Cloud
Step 1 — Push to GitHub
git init
git add .
git commit -m "Initial commit: AI Resume Analyzer"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/ai-resume-analyzer.git
git push -u origin main
Ensure .gitignore excludes uploads/, reports/, database/, and venv/.

Step 2 — Deploy on Streamlit Cloud
Go to share.streamlit.io
Sign in with your GitHub account
Click New app
Select your repository and branch (main)
Set Main file path to app.py
Click Deploy
Streamlit Cloud installs dependencies from requirements.txt automatically.

Step 3 — Configure (optional)
In your Streamlit Cloud app settings, you can set:

Python version: 3.11
Secrets: Not required for this app (no API keys needed)
Note: On Streamlit Cloud, the SQLite database resets when the app redeploys. For persistent storage in production, migrate to a cloud database (e.g., PostgreSQL via Supabase or PlanetScale).

Tech Stack
Technology	Purpose
Python	Core language
Streamlit	Web UI framework
SQLite	User & analysis storage
Pandas	Data manipulation for charts
Plotly	Interactive visualizations
PyPDF2	PDF text extraction
NLTK	NLP tokenization & stopwords
Scikit-learn	TF-IDF & cosine similarity
License
MIT License — free to use and modify.