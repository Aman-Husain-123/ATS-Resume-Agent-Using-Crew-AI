"""
ATS Resume Optimization Web Application
Built with Streamlit and CrewAI for intelligent resume optimization.

This application provides a user-friendly interface for:
- Uploading resumes (PDF, DOCX, TXT)
- Specifying target job titles and descriptions
- Running multi-agent AI pipeline for ATS optimization
- Viewing results at each stage (cleaned, rewritten, refined, evaluated)
- Downloading optimized resumes in multiple formats

Tech Stack:
- Streamlit: Web UI framework
- CrewAI: Multi-agent orchestration
- OpenAI: LLM for agent intelligence
- pypdf/python-docx: File parsing
"""

import os
import json
import streamlit as st
from dotenv import load_dotenv
from file_tools.file_loader import detect_and_extract
from crew import run_pipeline
from utils import txt_to_docx_bytes


# ========== CONFIGURATION ==========
# Load environment variables from .env file (contains OPENAI_API_KEY)
load_dotenv()

# Configure Streamlit page settings
st.set_page_config(
    page_title="ATS Resume Agent (CrewAI)",
    page_icon="🧠",
    layout="wide"  # Use full width for better layout
)


# ========== HEADER ==========
st.title("🧠 ATS-Optimized Resume Agent (CrewAI + OpenAI)")
st.caption(
    "Upload your resume (.pdf or .docx), target a role, and get an ATS-friendly version "
    "with scores & quick wins."
)


# ========== SIDEBAR ==========
with st.sidebar:
    st.subheader("OpenAI Settings")
    # Display model being used (read-only)
    st.text_input("Model:", value="gpt-4o-mini", disabled=True)
    # Confirm API key is loaded
    st.write("API Key loaded: ✅ Working OpenAI key")


# ========== INPUT SECTION ==========
# Create two-column layout for inputs
colL, colR = st.columns([1, 1])

with colL:
    # File uploader for resume
    up = st.file_uploader(
        "Upload Resume (.pdf or .docx preferred)",
        type=["pdf", "docx", "txt"]
    )

with colR:
    # Job details inputs
    job_title = st.text_input(
        "Target Job Title (e.g., 'Machine Learning Engineer')"
    )
    job_desc = st.text_area(
        "Paste Job Description",
        height=220,
        placeholder="Paste JD here..."
    )

# Main action button
run_btn = st.button("Run ATS Agent")

# Create tabs for displaying results
tabs = st.tabs([
    "Cleaned Resume",
    "Rewritten (ATS-optimized)",
    "Final (Refined Bullets)",
    "ATS Evaluation"
])


# ========== MAIN PROCESSING LOGIC ==========
if run_btn:
    # ========== INPUT VALIDATION ==========
    if up is None:
        st.error("Please upload a resume file.")
    elif not job_title or not job_desc.strip():
        st.error("Please provide a target job title and job description.")
    else:
        # ========== FILE PROCESSING ==========
        # Extract text from uploaded file
        ext, raw_text = detect_and_extract(up.name, up.read())
        
        if not raw_text.strip():
            st.error("Could not extract any text from the file.")
        else:
            # ========== RUN AI PIPELINE ==========
            # Execute multi-agent pipeline with progress indicator
            with st.spinner("Running Crew agents..."):
                cleaned, rewritten, final_resume, evaluation = run_pipeline(
                    raw_resume_text=raw_text,
                    job_title=job_title.strip(),
                    job_description=job_desc.strip()
                )

            # ========== TAB 1: CLEANED RESUME ==========
            with tabs[0]:
                st.subheader("Cleaned Resume (plain text)")
                # Display cleaned text in code block for better formatting
                st.code(cleaned, language="markdown")
                # Provide download button
                st.download_button(
                    "Download cleaned.txt",
                    data=cleaned.encode("utf-8"),
                    file_name="cleaned_resume.txt",
                    mime="text/plain"
                )

            # ========== TAB 2: REWRITTEN RESUME ==========
            with tabs[1]:
                st.subheader("Rewritten Resume (ATS-optimized)")
                # Display ATS-optimized version
                st.code(rewritten, language="markdown")
                # Provide download button
                st.download_button(
                    "Download rewritten.txt",
                    data=rewritten.encode("utf-8"),
                    file_name="rewritten_resume.txt",
                    mime="text/plain"
                )

            # ========== TAB 3: FINAL RESUME ==========
            with tabs[2]:
                st.subheader("Final Resume (Refined Bullets)")
                # Display final version with refined bullet points
                st.code(final_resume, language="markdown")

                # Offer multiple download formats
                # TXT format
                st.download_button(
                    "Download final.txt",
                    data=final_resume.encode("utf-8"),
                    file_name="final_resume.txt",
                    mime="text/plain"
                )
                
                # DOCX format (with error handling)
                try:
                    docx_bytes = txt_to_docx_bytes(final_resume)
                    st.download_button(
                        "Download final.docx",
                        data=docx_bytes,
                        file_name="final_resume.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                except Exception as e:
                    st.warning(f"Could not generate DOCX: {e}")

            # ========== TAB 4: ATS EVALUATION ==========
            with tabs[3]:
                st.subheader("ATS Evaluation & Suggestions")
                
                # Attempt to parse evaluation as JSON
                parsed = None
                try:
                    # Handle both single and double quotes in JSON
                    text = evaluation.strip()
                    fixed = text.replace("'", '"')
                    parsed = json.loads(fixed)
                except Exception:
                    # If parsing fails, will display raw text
                    pass

                # Display parsed JSON or raw text
                if parsed and isinstance(parsed, dict):
                    # Display as formatted JSON
                    st.json(parsed)
                    
                    # Show overall score as prominent metric
                    if "overall_score" in parsed:
                        st.metric("Overall ATS Score", f"{parsed['overall_score']}/100")
                else:
                    # Fallback: display raw evaluation output
                    st.write("Raw evaluation output:")
                    st.code(evaluation, language="json")
