"""
Resume analysis engine.
Handles skill extraction, ATS scoring, and feedback generation.
-------------------------------------------------------------------------------------------
Resume analysis engine.
Handles skill extraction, ATS scoring, and feedback generation.


"""

import re
from typing import Dict, List, Set, Tuple

import nltk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from utils import clean_text

# Ensure NLTK data is available on module load
def _ensure_nltk_data() -> None:
    """Download required NLTK resources if missing."""
    packages = ["stopwords", "punkt", "punkt_tab"]
    for package in packages:
        try:
            if package == "stopwords":
                nltk.data.find("corpora/stopwords")
            else:
                nltk.data.find(f"tokenizers/{package}")
        except (LookupError, OSError):
            nltk.download(package, quiet=True)


_ensure_nltk_data()

# Comprehensive technical skills dictionary
TECH_SKILLS: Set[str] = {
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl", "dart",
    "objective-c", "shell", "bash", "powershell", "lua", "haskell", "elixir",
    # Web Technologies
    "html", "css", "react", "reactjs", "angular", "vue", "vuejs", "nextjs", "next.js",
    "nodejs", "node.js", "express", "expressjs", "django", "flask", "fastapi",
    "spring", "spring boot", "asp.net", ".net", "laravel", "rails", "ruby on rails",
    "bootstrap", "tailwind", "tailwindcss", "jquery", "redux", "graphql", "rest",
    "restful", "api", "websocket", "sass", "less", "webpack", "vite",
    # Databases
    "sql", "mysql", "postgresql", "postgres", "mongodb", "redis", "sqlite", "oracle",
    "sql server", "mssql", "dynamodb", "cassandra", "elasticsearch", "firebase",
    "supabase", "mariadb", "neo4j", "influxdb",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "k8s", "jenkins",
    "ci/cd", "terraform", "ansible", "helm", "nginx", "apache", "linux", "unix",
    "devops", "git", "github", "gitlab", "bitbucket", "circleci", "travis ci",
    "argocd", "prometheus", "grafana", "cloudformation", "serverless", "lambda",
    "ec2", "s3", "ecs", "eks", "heroku", "vercel", "netlify",
    # Data Science & ML
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn", "sklearn",
    "pandas", "numpy", "scipy", "matplotlib", "seaborn", "plotly", "jupyter",
    "data analysis", "data science", "statistics", "big data", "hadoop", "spark",
    "pyspark", "airflow", "dbt", "etl", "data engineering", "data visualization",
    "opencv", "xgboost", "lightgbm", "huggingface", "llm", "generative ai",
    # Mobile
    "android", "ios", "react native", "flutter", "xamarin", "mobile development",
    # Testing & QA
    "selenium", "pytest", "junit", "jest", "cypress", "unit testing", "integration testing",
    "test automation", "qa", "tdd", "bdd",
    # Tools & Methodologies
    "agile", "scrum", "kanban", "jira", "confluence", "figma", "postman",
    "swagger", "microservices", "oop", "solid", "design patterns", "mvc", "mvvm",
    "rest api", "soap", "oauth", "jwt", "ssl", "tls", "cybersecurity", "encryption",
    # Business & Soft Skills (technical context)
    "project management", "leadership", "communication", "problem solving",
    "analytical", "teamwork", "collaboration",
    # Additional
    "blockchain", "solidity", "web3", "sap", "salesforce", "power bi", "tableau",
    "looker", "snowflake", "databricks", "kafka", "rabbitmq", "celery", "grpc",
    "streamlit", "dash", "power automate", "sharepoint", "excel", "vba",
    "autocad", "solidworks", "arduino", "raspberry pi", "iot",
}

# Sort by length descending so multi-word skills match first
_SORTED_SKILLS = sorted(TECH_SKILLS, key=len, reverse=True)


def extract_skills(text: str) -> List[str]:
    """
    Extract technical skills from text using dictionary matching.
    Returns a sorted list of unique skills found.
    """
    cleaned = clean_text(text)
    found: Set[str] = set()

    for skill in _SORTED_SKILLS:
        pattern = r"\b" + re.escape(skill) + r"\b"
        if re.search(pattern, cleaned):
            found.add(skill.title() if skill.islower() else skill)

    return sorted(found, key=str.lower)


def _tokenize_keywords(text: str) -> List[str]:
    """Extract meaningful keywords using NLTK stopword removal."""
    from nltk.corpus import stopwords
    from nltk.tokenize import word_tokenize

    cleaned = clean_text(text)
    tokens = word_tokenize(cleaned)
    stops = set(stopwords.words("english"))
    keywords = [
        token for token in tokens
        if token not in stops and len(token) > 2 and token.isalpha()
    ]
    return keywords


def calculate_keyword_overlap(resume_text: str, jd_text: str) -> Tuple[float, List[str], List[str]]:
    """
    Calculate keyword overlap between resume and job description.
    Returns (overlap_ratio, matched_keywords, missing_keywords).
    """
    resume_keywords = set(_tokenize_keywords(resume_text))
    jd_keywords = set(_tokenize_keywords(jd_text))

    if not jd_keywords:
        return 0.0, [], []

    matched = resume_keywords & jd_keywords
    missing = jd_keywords - resume_keywords
    overlap_ratio = len(matched) / len(jd_keywords)

    return overlap_ratio, sorted(matched), sorted(missing)


def calculate_tfidf_similarity(resume_text: str, jd_text: str) -> float:
    """
    Calculate cosine similarity between resume and JD using TF-IDF.
    Returns a score between 0 and 1.
    """
    if not resume_text.strip() or not jd_text.strip():
        return 0.0

    try:
        vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=5000,
        )
        tfidf_matrix = vectorizer.fit_transform([resume_text, jd_text])
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return float(similarity)
    except ValueError:
        return 0.0


def calculate_skill_match(resume_skills: List[str], jd_skills: List[str]) -> Tuple[float, List[str], List[str]]:
    """
    Compare skills between resume and job description.
    Returns (match_ratio, matched_skills, missing_skills).
    """
    resume_set = {s.lower() for s in resume_skills}
    jd_set = {s.lower() for s in jd_skills}

    if not jd_set:
        return 0.0, [], []

    matched_lower = resume_set & jd_set
    missing_lower = jd_set - resume_set

    # Preserve original casing from JD skills list
    matched = [s for s in jd_skills if s.lower() in matched_lower]
    missing = [s for s in jd_skills if s.lower() in missing_lower]

    match_ratio = len(matched_lower) / len(jd_set)
    return match_ratio, matched, missing


def calculate_ats_score(
    resume_text: str,
    jd_text: str,
    skill_match_ratio: float,
    keyword_overlap: float,
    tfidf_score: float,
) -> Tuple[float, float]:
    """
    Calculate composite ATS score out of 100.

    Weighting:
    - Skill match:       40%
    - Keyword overlap:   30%
    - TF-IDF similarity: 30%

    Returns (ats_score, match_percentage).
    """
    skill_component = skill_match_ratio * 40
    keyword_component = keyword_overlap * 30
    tfidf_component = tfidf_score * 30

    ats_score = round(skill_component + keyword_component + tfidf_component, 1)
    ats_score = min(max(ats_score, 0.0), 100.0)

    match_percentage = round(
        (skill_match_ratio * 0.4 + keyword_overlap * 0.3 + tfidf_score * 0.3) * 100, 1
    )

    return ats_score, match_percentage


def generate_strengths(
    resume_skills: List[str],
    matched_skills: List[str],
    ats_score: float,
    resume_text: str,
) -> List[str]:
    """Generate resume strength bullet points."""
    strengths = []

    if matched_skills:
        top_skills = ", ".join(matched_skills[:5])
        strengths.append(f"Strong alignment with required skills: {top_skills}.")

    if len(resume_skills) >= 8:
        strengths.append(f"Rich technical skill set with {len(resume_skills)} skills identified.")

    if ats_score >= 70:
        strengths.append("High overall compatibility with the job description.")
    elif ats_score >= 50:
        strengths.append("Moderate compatibility — solid foundation to build upon.")

    resume_lower = resume_text.lower()
    if any(word in resume_lower for word in ["led", "managed", "developed", "implemented", "designed"]):
        strengths.append("Uses strong action verbs that highlight accomplishments.")

    if any(word in resume_lower for word in ["certified", "certification", "degree", "bachelor", "master"]):
        strengths.append("Includes educational credentials or certifications.")

    if not strengths:
        strengths.append("Resume provides a baseline profile for further optimization.")

    return strengths


def generate_improvements(
    missing_skills: List[str],
    ats_score: float,
    resume_text: str,
    jd_text: str,
) -> List[str]:
    """Generate areas for improvement."""
    improvements = []

    if missing_skills:
        top_missing = ", ".join(missing_skills[:5])
        improvements.append(f"Add or highlight these missing skills: {top_missing}.")

    if ats_score < 50:
        improvements.append("Overall match is low — tailor resume keywords to mirror the job description.")
    elif ats_score < 70:
        improvements.append("Good start, but further keyword alignment would improve ATS ranking.")

    resume_lower = resume_text.lower()
    if not any(word in resume_lower for word in ["project", "experience", "worked", "built"]):
        improvements.append("Include concrete project or work experience sections with measurable outcomes.")

    if len(resume_text.split()) < 200:
        improvements.append("Resume appears short — expand with relevant experience and achievements.")

    jd_lower = jd_text.lower()
    if "years" in jd_lower and "year" not in resume_lower and "years" not in resume_lower:
        improvements.append("Job description mentions experience requirements — ensure yours is clearly stated.")

    if not improvements:
        improvements.append("Fine-tune formatting and quantify achievements for even stronger impact.")

    return improvements


def generate_suggestions(
    missing_skills: List[str],
    matched_skills: List[str],
    ats_score: float,
) -> List[str]:
    """Generate ATS optimization suggestions."""
    suggestions = [
        "Use standard section headings: Experience, Education, Skills, Projects.",
        "Avoid tables, images, and complex formatting that ATS systems cannot parse.",
        "Mirror exact keywords from the job description where truthfully applicable.",
        "Place the most relevant skills near the top of your resume.",
        "Use bullet points with quantifiable results (e.g., 'Increased efficiency by 30%').",
    ]

    if missing_skills:
        suggestions.append(
            f"Incorporate these JD keywords naturally: {', '.join(missing_skills[:8])}."
        )

    if matched_skills:
        suggestions.append(
            f"Emphasize your matched skills prominently: {', '.join(matched_skills[:5])}."
        )

    if ats_score < 60:
        suggestions.append(
            "Create a dedicated 'Technical Skills' section listing tools and technologies explicitly."
        )
        suggestions.append(
            "Customize your resume summary to reflect the role's core requirements."
        )

    suggestions.append("Save and submit your resume as a text-searchable PDF (not scanned images).")

    return suggestions


def analyze_resume(resume_text: str, jd_text: str, resume_filename: str = "resume.pdf") -> Dict:
    """
    Run full resume analysis against a job description.
    Returns a complete analysis dictionary.
    """
    if not resume_text or not resume_text.strip():
        raise ValueError("Resume text is empty.")
    if not jd_text or not jd_text.strip():
        raise ValueError("Job description is empty.")

    resume_skills = extract_skills(resume_text)
    jd_skills = extract_skills(jd_text)

    skill_match_ratio, matched_skills, missing_skills = calculate_skill_match(
        resume_skills, jd_skills
    )

    keyword_overlap, matched_keywords, _ = calculate_keyword_overlap(resume_text, jd_text)
    tfidf_score = calculate_tfidf_similarity(resume_text, jd_text)

    ats_score, match_percentage = calculate_ats_score(
        resume_text, jd_text, skill_match_ratio, keyword_overlap, tfidf_score
    )

    strengths = generate_strengths(resume_skills, matched_skills, ats_score, resume_text)
    improvements = generate_improvements(missing_skills, ats_score, resume_text, jd_text)
    suggestions = generate_suggestions(missing_skills, matched_skills, ats_score)

    return {
        "resume_filename": resume_filename,
        "job_description": jd_text,
        "ats_score": ats_score,
        "match_percentage": match_percentage,
        "resume_skills": resume_skills,
        "jd_skills": jd_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "matched_keywords_count": len(matched_keywords),
        "keyword_overlap_pct": round(keyword_overlap * 100, 1),
        "tfidf_score_pct": round(tfidf_score * 100, 1),
        "skill_match_pct": round(skill_match_ratio * 100, 1),
        "strengths": strengths,
        "improvements": improvements,
        "suggestions": suggestions,
    }