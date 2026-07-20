"""
AI Resume Analyzer & ATS Score Checker
Main Streamlit application entry point.

---------------------------------------------------------------------------
AI Resume Analyzer & ATS Score Checker
Main Streamlit application entry point.
"""

import os

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

import analyzer
import database as db
from utils import (
    ensure_directories,
    extract_text_from_pdf,
    generate_report,
    read_report_file,
    save_uploaded_file,
    validate_pdf_upload,
)

# ---------------------------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Resume Analyzer & ATS Score Checker",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSS_PATH = os.path.join(BASE_DIR, "assets", "style.css")


# ---------------------------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------------------------
def init_session_state() -> None:
    """Initialize Streamlit session state variables."""
    defaults = {
        "authenticated": False,
        "user": None,
        "current_analysis": None,
        "current_page": "Analyze Resume",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def load_css() -> None:
    """Inject custom CSS stylesheet."""
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def logout() -> None:
    """Clear session and log out the user."""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.current_analysis = None
    st.session_state.current_page = "Analyze Resume"


def score_color(score: float) -> str:
    """Return a color hex based on ATS score."""
    if score >= 75:
        return "#16a34a"
    if score >= 50:
        return "#d97706"
    return "#dc2626"


def score_label(score: float) -> str:
    """Return a human-readable label for ATS score."""
    if score >= 75:
        return "Excellent Match"
    if score >= 50:
        return "Moderate Match"
    return "Needs Improvement"


# ---------------------------------------------------------------------------
# Authentication Pages
# ---------------------------------------------------------------------------
def render_login() -> None:
    """Render the login form."""
    st.markdown('<p class="main-header">Welcome Back</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Sign in to analyze your resume</p>',
        unsafe_allow_html=True,
    )

    with st.form("login_form", clear_on_submit=False):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")
        submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

        if submitted:
            user = db.authenticate_user(username, password)
            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.success(f"Welcome, {user['username']}!")
                st.rerun()
            else:
                st.error("Invalid username or password.")

    st.markdown("---")
    if st.button("Create an Account", use_container_width=True):
        st.session_state.show_register = True
        st.rerun()


def render_register() -> None:
    """Render the registration form."""
    st.markdown('<p class="main-header">Create Account</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Register to start analyzing resumes</p>',
        unsafe_allow_html=True,
    )

    with st.form("register_form", clear_on_submit=True):
        username = st.text_input("Username", placeholder="Choose a username (min 3 chars)")
        email = st.text_input("Email", placeholder="your@email.com")
        password = st.text_input("Password", type="password", placeholder="Min 6 characters")
        confirm = st.text_input("Confirm Password", type="password", placeholder="Re-enter password")
        submitted = st.form_submit_button("Register", use_container_width=True, type="primary")

        if submitted:
            if password != confirm:
                st.error("Passwords do not match.")
            else:
                success, message = db.register_user(username, email, password)
                if success:
                    st.success(message)
                    st.session_state.show_register = False
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("---")
    if st.button("Back to Login", use_container_width=True):
        st.session_state.show_register = False
        st.rerun()


def render_auth_page() -> None:
    """Show login or register page."""
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            """
            <div style="text-align:center; padding: 2rem 0 1rem 0;">
                <span style="font-size:3rem;">📄</span>
                <h1 style="color:#1e3a5f; margin:0.5rem 0;">AI Resume Analyzer</h1>
                <p style="color:#64748b;">ATS Score Checker & Skill Matcher</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.session_state.get("show_register"):
            render_register()
        else:
            render_login()


# ---------------------------------------------------------------------------
# Sidebar Navigation
# ---------------------------------------------------------------------------
def render_sidebar() -> str:
    """Render sidebar navigation and return selected page."""
    user = st.session_state.user
    with st.sidebar:
        st.markdown(
            f"""
            <div style="padding: 1rem 0;">
                <h2 style="color:white; margin:0;">📄 Resume Analyzer</h2>
                <p style="color:rgba(255,255,255,0.7); font-size:0.85rem; margin:0.25rem 0 0 0;">
                    ATS Score & Skill Matcher
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")
        st.markdown(f"**👤 {user['username']}**")
        st.markdown(f"_{user['email']}_")
        st.markdown("---")

        pages = [
            "Analyze Resume",
            "Analytics Dashboard",
            "Analysis History",
        ]
        page = st.radio("Navigation", pages, label_visibility="collapsed")
        st.markdown("---")

        if st.button("🚪 Logout", use_container_width=True):
            logout()
            st.rerun()

    return page


# ---------------------------------------------------------------------------
# Analyze Resume Page
# ---------------------------------------------------------------------------
def render_analyze_page() -> None:
    """Render the main resume analysis page."""
    st.markdown('<p class="main-header">Analyze Resume</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Upload your resume and paste the job description to get your ATS score</p>',
        unsafe_allow_html=True,
    )

    col_upload, col_jd = st.columns(2)

    with col_upload:
        st.subheader("📎 Upload Resume (PDF)")
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type=["pdf"],
            help="Upload a text-based PDF resume (max 5 MB)",
        )
        if uploaded_file:
            valid, msg = validate_pdf_upload(uploaded_file)
            if valid:
                st.success(f"✅ {uploaded_file.name} ({uploaded_file.size / 1024:.1f} KB)")
            else:
                st.error(msg)

    with col_jd:
        st.subheader("📋 Job Description")
        job_description = st.text_area(
            "Paste the job description here",
            height=220,
            placeholder="Paste the full job description including required skills, qualifications, and responsibilities...",
        )
        if job_description:
            st.caption(f"{len(job_description.split())} words | {len(job_description)} characters")

    st.markdown("---")

    if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
        if not uploaded_file:
            st.error("Please upload a PDF resume.")
            return
        if not job_description or not job_description.strip():
            st.error("Please paste a job description.")
            return

        valid, msg = validate_pdf_upload(uploaded_file)
        if not valid:
            st.error(msg)
            return

        with st.spinner("Analyzing your resume... This may take a moment."):
            try:
                filepath = save_uploaded_file(uploaded_file, st.session_state.user["id"])
                success, result = extract_text_from_pdf(filepath)

                if not success:
                    st.error(result)
                    return

                analysis = analyzer.analyze_resume(
                    resume_text=result,
                    jd_text=job_description.strip(),
                    resume_filename=uploaded_file.name,
                )

                analysis_id = db.save_analysis(st.session_state.user["id"], analysis)
                analysis["id"] = analysis_id
                st.session_state.current_analysis = analysis
                st.success("Analysis complete!")
                st.rerun()

            except ValueError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"An unexpected error occurred: {exc}")

    if st.session_state.current_analysis:
        render_analysis_results(st.session_state.current_analysis)


def render_analysis_results(analysis: dict) -> None:
    """Display full analysis results with charts and feedback."""
    st.markdown("---")
    st.markdown("## 📊 Analysis Results")

    ats = analysis["ats_score"]
    color = score_color(ats)

    # Score overview row
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(
            f"""
            <div class="score-card">
                <div class="score-value">{ats}</div>
                <div class="score-label">ATS Score / 100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{analysis['match_percentage']}%</div>
                <div class="metric-label">Match Percentage</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{len(analysis['matched_skills'])}</div>
                <div class="metric-label">Matched Skills</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c4:
        st.markdown(
            f"""
            <div class="metric-card">
                <div class="metric-value">{len(analysis['missing_skills'])}</div>
                <div class="metric-label">Missing Skills</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        f"<p style='text-align:center; color:{color}; font-weight:600; font-size:1.1rem;'>"
        f"{score_label(ats)}</p>",
        unsafe_allow_html=True,
    )

    # Charts row
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("ATS Score Breakdown")
        breakdown = {
            "Component": ["Skill Match (40%)", "Keyword Overlap (30%)", "Text Similarity (30%)"],
            "Score": [
                analysis.get("skill_match_pct", 0) * 0.4,
                analysis.get("keyword_overlap_pct", 0) * 0.3,
                analysis.get("tfidf_score_pct", 0) * 0.3,
            ],
        }
        fig_breakdown = px.bar(
            pd.DataFrame(breakdown),
            x="Component",
            y="Score",
            color="Component",
            color_discrete_sequence=["#2563eb", "#7c3aed", "#0891b2"],
            text="Score",
        )
        fig_breakdown.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig_breakdown.update_layout(showlegend=False, yaxis_title="Contribution to Score", height=350)
        st.plotly_chart(fig_breakdown, use_container_width=True)

    with chart_col2:
        st.subheader("Skills Match Overview")
        matched_count = len(analysis["matched_skills"])
        missing_count = len(analysis["missing_skills"])
        fig_pie = go.Figure(
            data=[
                go.Pie(
                    labels=["Matched Skills", "Missing Skills"],
                    values=[matched_count, missing_count] if (matched_count + missing_count) > 0 else [1, 0],
                    marker_colors=["#16a34a", "#dc2626"],
                    hole=0.45,
                    textinfo="label+value",
                )
            ]
        )
        fig_pie.update_layout(height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig_pie, use_container_width=True)

    # Skills section
    st.markdown("---")
    skill_col1, skill_col2, skill_col3 = st.columns(3)

    with skill_col1:
        st.subheader("🔵 Resume Skills")
        if analysis["resume_skills"]:
            tags = "".join(
                f'<span class="skill-tag-resume">{s}</span>' for s in analysis["resume_skills"]
            )
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.info("No technical skills detected in resume.")

    with skill_col2:
        st.subheader("✅ Matched Skills")
        if analysis["matched_skills"]:
            tags = "".join(
                f'<span class="skill-tag-match">{s}</span>' for s in analysis["matched_skills"]
            )
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.warning("No skills matched with the job description.")

    with skill_col3:
        st.subheader("❌ Missing Skills")
        if analysis["missing_skills"]:
            tags = "".join(
                f'<span class="skill-tag-missing">{s}</span>' for s in analysis["missing_skills"]
            )
            st.markdown(tags, unsafe_allow_html=True)
        else:
            st.success("All JD skills found in your resume!")

    # Feedback section
    st.markdown("---")
    fb_col1, fb_col2, fb_col3 = st.columns(3)

    with fb_col1:
        st.subheader("💪 Strengths")
        for item in analysis["strengths"]:
            st.markdown(
                f'<div class="feedback-box feedback-box-strength">{item}</div>',
                unsafe_allow_html=True,
            )

    with fb_col2:
        st.subheader("📈 Areas to Improve")
        for item in analysis["improvements"]:
            st.markdown(
                f'<div class="feedback-box feedback-box-improve">{item}</div>',
                unsafe_allow_html=True,
            )

    with fb_col3:
        st.subheader("💡 ATS Suggestions")
        for item in analysis["suggestions"]:
            st.markdown(
                f'<div class="feedback-box feedback-box-suggest">{item}</div>',
                unsafe_allow_html=True,
            )

    # Download report
    st.markdown("---")
    st.subheader("📥 Download Report")
    if st.button("Generate & Download Report", type="primary"):
        report_path = generate_report(analysis, st.session_state.user["username"])
        report_content = read_report_file(report_path)
        if report_content:
            st.download_button(
                label="⬇️ Download Report (.txt)",
                data=report_content,
                file_name=os.path.basename(report_path),
                mime="text/plain",
                use_container_width=True,
            )
        else:
            st.error("Failed to generate report.")


# ---------------------------------------------------------------------------
# Analytics Dashboard Page
# ---------------------------------------------------------------------------
def render_dashboard_page() -> None:
    """Render analytics dashboard with Plotly charts."""
    st.markdown('<p class="main-header">Analytics Dashboard</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Overview of your resume analysis performance</p>',
        unsafe_allow_html=True,
    )

    user_id = st.session_state.user["id"]
    stats = db.get_user_stats(user_id)
    analyses = db.get_user_analyses(user_id)

    if not analyses:
        st.info("No analyses yet. Go to **Analyze Resume** to run your first analysis.")
        return

    # Summary metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Total Analyses", stats["total_analyses"])
    with m2:
        st.metric("Average ATS Score", f"{stats['avg_ats_score']}/100")
    with m3:
        st.metric("Average Match %", f"{stats['avg_match_percentage']}%")
    with m4:
        st.metric("Best ATS Score", f"{stats['best_ats_score']}/100")

    st.markdown("---")

    df = pd.DataFrame(
        [
            {
                "Date": a["created_at"][:10],
                "ATS Score": a["ats_score"],
                "Match %": a["match_percentage"],
                "Matched Skills": len(a["matched_skills"]),
                "Missing Skills": len(a["missing_skills"]),
                "Resume": a["resume_filename"],
            }
            for a in analyses
        ]
    )

    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("ATS Score Trend")
        fig_line = px.line(
            df.iloc[::-1].reset_index(drop=True),
            x=df.iloc[::-1].reset_index(drop=True).index + 1,
            y="ATS Score",
            markers=True,
            labels={"x": "Analysis #"},
            color_discrete_sequence=["#2563eb"],
        )
        fig_line.add_hline(y=75, line_dash="dash", line_color="#16a34a", annotation_text="Excellent (75)")
        fig_line.add_hline(y=50, line_dash="dash", line_color="#d97706", annotation_text="Moderate (50)")
        fig_line.update_layout(height=380)
        st.plotly_chart(fig_line, use_container_width=True)

    with chart_col2:
        st.subheader("Skills Match vs Missing")
        latest = analyses[0]
        fig_bar = go.Figure(
            data=[
                go.Bar(
                    name="Matched",
                    x=["Skills"],
                    y=[len(latest["matched_skills"])],
                    marker_color="#16a34a",
                ),
                go.Bar(
                    name="Missing",
                    x=["Skills"],
                    y=[len(latest["missing_skills"])],
                    marker_color="#dc2626",
                ),
            ]
        )
        fig_bar.update_layout(barmode="group", height=380, title="Latest Analysis Skills")
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("Analysis Summary Table")
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.subheader("Match Percentage Distribution")
    fig_hist = px.histogram(
        df,
        x="Match %",
        nbins=10,
        color_discrete_sequence=["#7c3aed"],
        labels={"Match %": "Match Percentage"},
    )
    fig_hist.update_layout(height=300)
    st.plotly_chart(fig_hist, use_container_width=True)


# ---------------------------------------------------------------------------
# Analysis History Page
# ---------------------------------------------------------------------------
def render_history_page() -> None:
    """Render analysis history with detail view."""
    st.markdown('<p class="main-header">Analysis History</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Review your previous resume analyses</p>',
        unsafe_allow_html=True,
    )

    analyses = db.get_user_analyses(st.session_state.user["id"])

    if not analyses:
        st.info("No analysis history yet. Run your first analysis from the **Analyze Resume** page.")
        return

    for item in analyses:
        ats = item["ats_score"]
        color = score_color(ats)
        date_str = item["created_at"][:19].replace("T", " ")

        with st.expander(
            f"📄 {item['resume_filename']}  |  ATS: {ats}/100  |  {date_str} UTC"
        ):
            hc1, hc2, hc3 = st.columns(3)
            with hc1:
                st.metric("ATS Score", f"{ats}/100")
            with hc2:
                st.metric("Match %", f"{item['match_percentage']}%")
            with hc3:
                st.metric("Missing Skills", len(item["missing_skills"]))

            st.markdown(
                f"**Status:** <span style='color:{color}; font-weight:600;'>"
                f"{score_label(ats)}</span>",
                unsafe_allow_html=True,
            )

            if item["matched_skills"]:
                st.markdown("**Matched:** " + ", ".join(item["matched_skills"]))
            if item["missing_skills"]:
                st.markdown("**Missing:** " + ", ".join(item["missing_skills"]))

            btn_col1, btn_col2 = st.columns(2)
            with btn_col1:
                if st.button("View Full Results", key=f"view_{item['id']}"):
                    st.session_state.current_analysis = item
                    st.session_state.current_page = "Analyze Resume"
                    st.rerun()
            with btn_col2:
                if st.button("Download Report", key=f"dl_{item['id']}"):
                    report_path = generate_report(item, st.session_state.user["username"])
                    report_content = read_report_file(report_path)
                    if report_content:
                        st.download_button(
                            label="⬇️ Download",
                            data=report_content,
                            file_name=os.path.basename(report_path),
                            mime="text/plain",
                            key=f"dlbtn_{item['id']}",
                        )


# ---------------------------------------------------------------------------
# Main Entry Point
# ---------------------------------------------------------------------------
def main() -> None:
    """Application main entry point."""
    init_session_state()
    load_css()
    ensure_directories()
    db.init_db()

    if not st.session_state.authenticated:
        render_auth_page()
        return

    page = render_sidebar()

    if page == "Analyze Resume":
        render_analyze_page()
    elif page == "Analytics Dashboard":
        render_dashboard_page()
    elif page == "Analysis History":
        render_history_page()


if __name__ == "__main__":
    main()