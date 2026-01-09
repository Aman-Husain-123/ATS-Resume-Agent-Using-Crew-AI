"""
ATS Resume Optimization Web Application
Built with Streamlit and CrewAI for intelligent resume optimization.
"""

import os
import json
import time
import streamlit as st
from dotenv import load_dotenv
from file_tools.file_loader import detect_and_extract
from crew import run_pipeline
from utils import txt_to_docx_bytes


# ========== CONFIGURATION ==========
load_dotenv()

st.set_page_config(
    page_title="ATS Resume Agent",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ========== CLEAN CSS ==========
st.markdown("""
<style>
    /* Clean professional styling */
    .main {
        background-color: #f8f9fa;
    }
    
    .stButton>button {
        background-color: #4CAF50;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        border: none;
        width: 100%;
    }
    
    .stButton>button:hover {
        background-color: #45a049;
    }
    
    .stDownloadButton>button {
        background-color: #2196F3;
        color: white;
        border-radius: 6px;
        border: none;
    }
    
    .stDownloadButton>button:hover {
        background-color: #0b7dda;
    }
    
    h1 {
        color: #1f2937;
        font-weight: 700;
    }
    
    h3 {
        color: #374151;
        font-weight: 600;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 0.5rem 1rem;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)


# ========== HEADER ==========
st.title("🚀 ATS Resume Agent")
st.markdown("**Transform your resume with AI-powered optimization | Powered by EURI AI**")
st.markdown("---")


# ========== SIDEBAR ==========
with st.sidebar:
    st.header("⚙️ Settings")
    
    st.subheader("AI Configuration")
    st.info("**Model:** gpt-4.1-nano")
    st.success("**Provider:** EURI (euron.one)")
    st.success("**Status:** ✅ Connected")
    
    st.markdown("---")
    
    st.subheader("📋 How It Works")
    st.markdown("""
    1. Upload your resume
    2. Enter job details
    3. Click 'Run ATS Agent'
    4. Review optimized results
    5. Download your resume
    """)
    
    st.markdown("---")
    
    st.subheader("✨ Features")
    st.markdown("""
    - 📄 PDF, DOCX, TXT support
    - 🎯 Job-specific optimization
    - 📊 ATS scoring
    - 💡 Smart recommendations
    - 📥 Multiple formats
    """)


# ========== MAIN CONTENT ==========
st.subheader("📤 Upload & Configure")

# Input section
col1, col2 = st.columns([1, 1])

with col1:
    up = st.file_uploader(
        "📄 Upload Resume",
        type=["pdf", "docx", "txt"],
        help="Supported: PDF, DOCX, TXT"
    )

with col2:
    job_title = st.text_input(
        "🎯 Job Title",
        placeholder="e.g., Machine Learning Engineer"
    )

job_desc = st.text_area(
    "📋 Job Description",
    height=120,
    placeholder="Paste the job description here..."
)

st.markdown("")
run_btn = st.button("🚀 Run ATS Agent", type="primary")

st.markdown("---")

# Results tabs
tabs = st.tabs([
    "🔍 Cleaned",
    "✍️ Optimized",
    "✨ Final",
    "📊 Score"
])


# ========== PROCESSING ==========
if run_btn:
    if up is None:
        st.error("⚠️ Please upload a resume file")
    elif not job_title or not job_desc.strip():
        st.error("⚠️ Please provide job title and description")
    else:
        with st.spinner("📄 Reading resume..."):
            ext, raw_text = detect_and_extract(up.name, up.read())
        
        if not raw_text.strip():
            st.error("❌ Could not extract text from file")
        else:
            progress = st.progress(0)
            status = st.empty()
            
            status.text("🤖 Starting AI agents...")
            progress.progress(20)
            
            try:
                cleaned, rewritten, final_resume, evaluation = run_pipeline(
                    raw_resume_text=raw_text,
                    job_title=job_title.strip(),
                    job_description=job_desc.strip()
                )
                
                progress.progress(100)
                status.text("✅ Complete!")
                time.sleep(0.5)
                progress.empty()
                status.empty()
                
                st.success("🎉 Resume optimized successfully!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
                st.stop()

            # TAB 1: Cleaned
            with tabs[0]:
                st.markdown("### 🔍 Cleaned Resume")
                st.code(cleaned, language="markdown")
                st.download_button(
                    "📥 Download",
                    data=cleaned.encode("utf-8"),
                    file_name="cleaned_resume.txt",
                    mime="text/plain"
                )

            # TAB 2: Optimized
            with tabs[1]:
                st.markdown("### ✍️ ATS-Optimized")
                st.code(rewritten, language="markdown")
                st.download_button(
                    "📥 Download",
                    data=rewritten.encode("utf-8"),
                    file_name="ats_optimized.txt",
                    mime="text/plain"
                )

            # TAB 3: Final
            with tabs[2]:
                st.markdown("### ✨ Final Version")
                st.code(final_resume, language="markdown")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "📥 Download TXT",
                        data=final_resume.encode("utf-8"),
                        file_name="final_resume.txt",
                        mime="text/plain"
                    )
                with col2:
                    try:
                        docx_bytes = txt_to_docx_bytes(final_resume)
                        st.download_button(
                            "📥 Download DOCX",
                            data=docx_bytes,
                            file_name="final_resume.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                        )
                    except Exception as e:
                        st.warning(f"⚠️ DOCX error: {e}")

            # TAB 4: Score
            with tabs[3]:
                st.markdown("### 📊 ATS Evaluation")
                
                parsed = None
                try:
                    text = evaluation.strip()
                    fixed = text.replace("'", '"')
                    parsed = json.loads(fixed)
                except:
                    pass

                if parsed and isinstance(parsed, dict):
                    if "overall_score" in parsed:
                        score = parsed['overall_score']
                        
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            st.metric("Overall ATS Score", f"{score}/100")
                        
                        if score >= 80:
                            st.success("🌟 Excellent! Highly ATS-compatible")
                        elif score >= 60:
                            st.info("👍 Good! Some improvements possible")
                        else:
                            st.warning("⚠️ Needs improvement")
                    
                    st.markdown("---")
                    st.markdown("#### Detailed Report")
                    st.json(parsed)
                    
                    if "quick_wins" in parsed:
                        st.markdown("#### 💡 Quick Wins")
                        for i, win in enumerate(parsed["quick_wins"], 1):
                            st.markdown(f"{i}. {win}")
                    
                    if "missing_keywords" in parsed:
                        st.markdown("#### 🔑 Missing Keywords")
                        keywords = parsed["missing_keywords"]
                        if isinstance(keywords, list):
                            st.info(", ".join(keywords))
                        else:
                            st.info(keywords)
                else:
                    st.code(evaluation, language="json")
    # ========== INPUT VALIDATION ==========
    if up is None:
        st.error("⚠️ Please upload a resume file to get started!")
    elif not job_title or not job_desc.strip():
        st.error("⚠️ Please provide both job title and job description!")
    else:
        # ========== FILE PROCESSING ==========
        # Extract text from uploaded file
        with st.spinner("📄 Reading your resume..."):
            time.sleep(0.5)  # Brief pause for UX
            ext, raw_text = detect_and_extract(up.name, up.read())
        
        if not raw_text.strip():
            st.error("❌ Could not extract text from the file. Please try a different format.")
        else:
            # ========== RUN AI PIPELINE ==========
            # Show progress with custom messages
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🤖 Initializing AI agents...")
            progress_bar.progress(10)
            time.sleep(0.3)
            
            status_text.text("🔍 Parsing and cleaning resume...")
            progress_bar.progress(25)
            
            # Execute multi-agent pipeline
            try:
                cleaned, rewritten, final_resume, evaluation = run_pipeline(
                    raw_resume_text=raw_text,
                    job_title=job_title.strip(),
                    job_description=job_desc.strip()
                )
                
                progress_bar.progress(100)
                status_text.text("✅ Processing complete!")
                time.sleep(0.5)
                progress_bar.empty()
                status_text.empty()
                
                # Success message with animation
                st.success("🎉 Your resume has been optimized successfully!")
                
            except Exception as e:
                st.error(f"❌ An error occurred: {str(e)}")
                st.stop()

            # ========== TAB 1: CLEANED RESUME ==========
            with tabs[0]:
                st.markdown("### 🔍 Cleaned Resume")
                st.markdown("*Parsed and structured version of your original resume*")
                
                # Display cleaned text in an attractive container
                with st.container():
                    st.code(cleaned, language="markdown", line_numbers=False)
                
                # Download button
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.download_button(
                        "📥 Download TXT",
                        data=cleaned.encode("utf-8"),
                        file_name="cleaned_resume.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

            # ========== TAB 2: REWRITTEN RESUME ==========
            with tabs[1]:
                st.markdown("### ✍️ ATS-Optimized Resume")
                st.markdown("*Rewritten with job-specific keywords and ATS-friendly formatting*")
                
                # Display ATS-optimized version
                with st.container():
                    st.code(rewritten, language="markdown", line_numbers=False)
                
                # Download button
                col1, col2, col3 = st.columns([1, 1, 2])
                with col1:
                    st.download_button(
                        "📥 Download TXT",
                        data=rewritten.encode("utf-8"),
                        file_name="ats_optimized_resume.txt",
                        mime="text/plain",
                        use_container_width=True
                    )

            # ========== TAB 3: FINAL RESUME ==========
            with tabs[2]:
                st.markdown("### ✨ Final Polished Resume")
                st.markdown("*Enhanced with refined bullet points and quantified achievements*")
                
                # Display final version with refined bullet points
                with st.container():
                    st.code(final_resume, language="markdown", line_numbers=False)

                # Offer multiple download formats
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    # TXT format
                    st.download_button(
                        "📥 Download TXT",
                        data=final_resume.encode("utf-8"),
                        file_name="final_resume.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                with col2:
                    # DOCX format (with error handling)
                    try:
                        docx_bytes = txt_to_docx_bytes(final_resume)
                        st.download_button(
                            "📥 Download DOCX",
                            data=docx_bytes,
                            file_name="final_resume.docx",
                            mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                            use_container_width=True
                        )
                    except Exception as e:
                        st.warning(f"⚠️ Could not generate DOCX: {e}")

            # ========== TAB 4: ATS EVALUATION ==========
            with tabs[3]:
                st.markdown("### 📊 ATS Evaluation & Recommendations")
                st.markdown("*Detailed scoring and actionable improvement suggestions*")
                
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
                    # Show overall score as prominent metric
                    if "overall_score" in parsed:
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col2:
                            score = parsed['overall_score']
                            st.metric(
                                label="🎯 Overall ATS Score",
                                value=f"{score}/100",
                                delta=f"{score - 70} vs average" if score > 70 else None
                            )
                        
                        # Score interpretation
                        if score >= 80:
                            st.success("🌟 Excellent! Your resume is highly ATS-compatible!")
                        elif score >= 60:
                            st.info("👍 Good! A few improvements will make it even better.")
                        else:
                            st.warning("⚠️ Needs improvement. Follow the recommendations below.")
                    
                    st.markdown("---")
                    
                    # Display detailed breakdown
                    st.markdown("#### 📋 Detailed Breakdown")
                    st.json(parsed)
                    
                    # Quick wins section
                    if "quick_wins" in parsed:
                        st.markdown("#### 💡 Quick Wins")
                        for i, win in enumerate(parsed["quick_wins"], 1):
                            st.markdown(f"{i}. {win}")
                    
                    # Missing keywords
                    if "missing_keywords" in parsed:
                        st.markdown("#### 🔑 Missing Keywords")
                        keywords = parsed["missing_keywords"]
                        if isinstance(keywords, list):
                            st.info(", ".join(keywords))
                        else:
                            st.info(keywords)
                    
                else:
                    # Fallback: display raw evaluation output
                    st.markdown("#### 📄 Evaluation Report")
                    st.code(evaluation, language="json")
