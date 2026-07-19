# 🤖 AI Resume Analyzer

An intelligent AI-powered Resume Analyzer that helps job seekers evaluate, improve, and optimize their resumes using Machine Learning and Generative AI. The system analyzes resumes, extracts important information, matches skills with job requirements, and provides actionable improvement suggestions.

![AI Resume Analyzer Banner](screenshots/banner.png)

---

## 🚀 Features

✨ **Resume Upload & Parsing**

* Upload resumes in PDF format
* Automatically extract text and important details
* Supports multiple resume formats

🧠 **AI Resume Analysis**

* Analyzes resume content using Generative AI
* Identifies strengths and weaknesses
* Provides personalized improvement suggestions

📊 **ATS Score Prediction**

* Calculates resume compatibility score
* Checks keyword optimization
* Helps improve Applicant Tracking System ranking

💼 **Job Description Matching**

* Compares resume skills with job requirements
* Finds missing skills and keywords
* Provides match percentage

🎯 **Skill Analysis**

* Extracts technical and soft skills
* Highlights important skills for targeted roles

📄 **Resume Improvement Suggestions**

* Provides AI-generated recommendations
* Improves formatting, skills, and project descriptions

---

# 📸 Screenshots

## 🏠 Home Page

![Home Page](screenshots/home.png)

---

## 📤 Resume Upload Section

![Resume Upload](screenshots/upload.png)

---

## 📊 Resume Analysis Dashboard

![Analysis Dashboard](screenshots/dashboard.png)

---

## 🎯 ATS Score Result

![ATS Score](screenshots/ats-score.png)

---

## 🧠 AI Suggestions

![AI Suggestions](screenshots/suggestions.png)

---

# 🏗️ System Architecture

```
              User
               |
               ↓
        Resume Upload (PDF)
               |
               ↓
        Text Extraction
        (PyPDF / NLP)
               |
               ↓
        AI Processing Layer
        (LLM + LangChain)
               |
               ↓
     Resume Analysis Engine
               |
               ↓
 ATS Score | Skill Analysis | Suggestions
               |
               ↓
          User Dashboard
```

---

# 🛠️ Tech Stack

## Frontend

* HTML
* CSS
* JavaScript
* React.js *(if used)*

## Backend

* Python
* Flask / FastAPI

## AI & NLP

* Generative AI
* LangChain
* Large Language Models (LLMs)
* NLP Techniques

## Database

* MongoDB / PostgreSQL

## Libraries

* PyPDF
* NLTK
* Pandas
* NumPy
* Scikit-learn

## Tools

* Git & GitHub
* VS Code
* Docker *(optional)*

---

# ⚙️ Installation & Setup

### Clone Repository

```bash
git clone https://github.com/yourusername/AI-Resume-Analyzer.git
```

### Navigate to Project Folder

```bash
cd AI-Resume-Analyzer
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

Linux/Mac:

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

---

# 📂 Project Structure

```
AI-Resume-Analyzer/
│
├── app.py
├── requirements.txt
├── README.md
│
├── models/
│   └── resume_model.py
│
├── utils/
│   ├── pdf_parser.py
│   └── skill_extractor.py
│
├── templates/
│
├── static/
│
└── screenshots/
    ├── banner.png
    ├── home.png
    ├── upload.png
    ├── dashboard.png
    ├── ats-score.png
    └── suggestions.png
```

---

# 🔍 How It Works

1. User uploads a resume PDF.
2. System extracts resume text.
3. NLP techniques process the extracted information.
4. AI model analyzes:

   * Skills
   * Experience
   * Education
   * Projects
   * Keywords
5. The system generates:

   * ATS score
   * Missing skills
   * Resume improvement suggestions

---

# 📈 Future Enhancements

* 🔹 AI-powered resume builder
* 🔹 LinkedIn profile analyzer
* 🔹 Multiple job role recommendations
* 🔹 Interview question generation
* 🔹 Voice-based career assistant
* 🔹 Cloud deployment

---

# 👨‍💻 Author

**Deekshith Vataparthi**

Computer Science Engineering Student

🔗 GitHub: your-github-link
🔗 LinkedIn: your-linkedin-link

---

# ⭐ Support

If you like this project, consider giving it a ⭐ on GitHub.
