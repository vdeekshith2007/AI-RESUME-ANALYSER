"""
Utility functions for file handling, PDF extraction, and report generation.
"""

import os
import re
from datetime import datetime
from typing import Optional, Tuple

import PyPDF2

# Project directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
REPORT_DIR = os.path.join(BASE_DIR, "reports")

# Upload constraints
MAX_FILE_SIZE_MB = 5
ALLOWED_EXTENSIONS = {".pdf"}
MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024


def ensure_directories() -> None:
    """Create required project directories."""
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(REPORT_DIR, exist_ok=True)


def validate_pdf_upload(uploaded_file) -> Tuple[bool, str]:
    """
    Validate uploaded PDF file.
    Returns (is_valid, message).
    """
    if uploaded_file is None:
        return False, "No file uploaded."

    filename = uploaded_file.name.lower()
    extension = os.path.splitext(filename)[1]

    if extension not in ALLOWED_EXTENSIONS:
        return False, "Only PDF files are allowed."

    if uploaded_file.size > MAX_FILE_SIZE_BYTES:
        return False, f"File size must be under {MAX_FILE_SIZE_MB} MB."

    if uploaded_file.size == 0:
        return False, "Uploaded file is empty."

    return True, "File is valid."


def save_uploaded_file(uploaded_file, user_id: int) -> str:
    """
    Save uploaded PDF to disk with a unique filename.
    Returns the saved file path.
    """
    ensure_directories()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    safe_name = re.sub(r"[^\w.\-]", "_", uploaded_file.name)
    filename = f"user_{user_id}_{timestamp}_{safe_name}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(uploaded_file.getbuffer())

    return filepath


def extract_text_from_pdf(filepath: str) -> Tuple[bool, str]:
    """
    Extract text content from a PDF file using PyPDF2.
    Returns (success, text_or_error_message).
    """
    if not os.path.exists(filepath):
        return False, "File not found."

    try:
        text_parts = []
        with open(filepath, "rb") as file:
            reader = PyPDF2.PdfReader(file)

            if reader.is_encrypted:
                try:
                    reader.decrypt("")
                except Exception:
                    return False, "PDF is password-protected and cannot be read."

            if len(reader.pages) == 0:
                return False, "PDF contains no pages."

            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        full_text = "\n".join(text_parts).strip()
        if not full_text:
            return False, "Could not extract text from PDF. The file may be image-based."

        return True, full_text

    except PyPDF2.errors.PdfReadError:
        return False, "Invalid or corrupted PDF file."
    except Exception as exc:
        return False, f"Error reading PDF: {str(exc)}"


def clean_text(text: str) -> str:
    """Normalize whitespace and lowercase text for analysis."""
    text = text.lower()
    text = re.sub(r"[^\w\s+#.\-/]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def generate_report(analysis: dict, username: str) -> str:
    """
    Generate a downloadable text report from analysis results.
    Returns the report file path.
    """
    ensure_directories()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"report_{username}_{timestamp}.txt"
    filepath = os.path.join(REPORT_DIR, filename)

    lines = [
        "=" * 60,
        "AI RESUME ANALYZER & ATS SCORE REPORT",
        "=" * 60,
        "",
        f"Generated For : {username}",
        f"Generated On  : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}",
        f"Resume File   : {analysis.get('resume_filename', 'N/A')}",
        "",
        "-" * 60,
        "SCORES",
        "-" * 60,
        f"ATS Score         : {analysis['ats_score']}/100",
        f"Match Percentage  : {analysis['match_percentage']}%",
        "",
        "-" * 60,
        "SKILLS FOUND IN RESUME",
        "-" * 60,
    ]

    resume_skills = analysis.get("resume_skills", [])
    if resume_skills:
        lines.extend(f"  • {skill}" for skill in resume_skills)
    else:
        lines.append("  No technical skills detected.")

    lines.extend(
        [
            "",
            "-" * 60,
            "SKILLS IN JOB DESCRIPTION",
            "-" * 60,
        ]
    )
    jd_skills = analysis.get("jd_skills", [])
    if jd_skills:
        lines.extend(f"  • {skill}" for skill in jd_skills)
    else:
        lines.append("  No technical skills detected in job description.")

    lines.extend(
        [
            "",
            "-" * 60,
            "MATCHED SKILLS",
            "-" * 60,
        ]
    )
    matched = analysis.get("matched_skills", [])
    if matched:
        lines.extend(f"  ✓ {skill}" for skill in matched)
    else:
        lines.append("  No matching skills found.")

    lines.extend(
        [
            "",
            "-" * 60,
            "MISSING SKILLS",
            "-" * 60,
        ]
    )
    missing = analysis.get("missing_skills", [])
    if missing:
        lines.extend(f"  ✗ {skill}" for skill in missing)
    else:
        lines.append("  No missing skills — great match!")

    lines.extend(
        [
            "",
            "-" * 60,
            "RESUME STRENGTHS",
            "-" * 60,
        ]
    )
    for item in analysis.get("strengths", []):
        lines.append(f"  + {item}")

    lines.extend(
        [
            "",
            "-" * 60,
            "AREAS FOR IMPROVEMENT",
            "-" * 60,
        ]
    )
    for item in analysis.get("improvements", []):
        lines.append(f"  - {item}")

    lines.extend(
        [
            "",
            "-" * 60,
            "ATS OPTIMIZATION SUGGESTIONS",
            "-" * 60,
        ]
    )
    for item in analysis.get("suggestions", []):
        lines.append(f"  → {item}")

    lines.extend(["", "=" * 60, "End of Report", "=" * 60])

    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return filepath


def read_report_file(filepath: str) -> Optional[str]:
    """Read report file content for download."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except OSError:
        return None