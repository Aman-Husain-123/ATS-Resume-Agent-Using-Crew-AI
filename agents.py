"""
ATS Resume Agent Definitions
This module defines specialized AI agents for resume optimization and ATS scoring.
Each agent has a specific role in the resume optimization pipeline.
"""

from crewai import Agent
import os

# ========== CONFIGURATION ==========
# Load EURI API key from environment variable
# Set your OPENAI_API_KEY (EURI token) and OPENAI_API_BASE in your .env file
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("OPENAI_API_KEY environment variable is not set")

# Configure EURI API base URL if provided
if "OPENAI_API_BASE" in os.environ:
    os.environ["OPENAI_API_BASE"] = os.environ["OPENAI_API_BASE"]

# Model configuration - using EURI's gpt-4.1-nano for cost-effective processing
MODEL = "gpt-4.1-nano"


# ========== AGENT BUILDERS ==========

def build_parser_agent():
    """
    Build the Resume Parsing Agent.
    
    This agent cleans and structures raw resume text by:
    - Removing formatting artifacts and noise
    - Normalizing bullet points and spacing
    - Preserving all important content
    - Preparing text for ATS optimization
    
    Returns:
        Agent: Configured parser agent with deterministic behavior (temperature=0.0)
    """
    return Agent(
        role="Resume Parsing Specialist",
        goal="Extract clean, structured text from a resume suitable for ATS optimization.",
        backstory=(
            "You efficiently clean resume text by removing artifacts and normalizing formatting. "
            "Focus on speed and accuracy - preserve all important content while removing noise."
        ),
        model=MODEL,
        temperature=0.0,   # Deterministic output - no hallucination
        max_iter=1,        # Single pass for efficiency
        max_execution_time=120,  # 2-minute timeout
    )

    
def build_ats_writer_agent():
    """
    Build the ATS Optimization Writer Agent.
    
    This agent rewrites resumes for ATS compatibility by:
    - Matching keywords from job descriptions
    - Using strong action verbs (Led, Achieved, Implemented, etc.)
    - Quantifying achievements with metrics
    - Structuring content for ATS parsing
    - Targeting 80+ ATS compatibility score
    
    Returns:
        Agent: Configured writer agent with moderate creativity (temperature=0.3)
    """
    return Agent(
        role="ATS Optimization Writer",
        goal="Create a high-scoring ATS-optimized resume that matches job requirements perfectly.",
        backstory=(
            "You are an expert at transforming resumes into ATS-friendly formats that score 80+ points. "
            "You strategically place keywords, use strong action verbs, and quantify all achievements. "
            "You work quickly and deliver results that pass ATS systems."
        ),
        model=MODEL,
        temperature=0.3,   # Slight creativity for natural language
        max_iter=1,        # Single pass for efficiency
        max_execution_time=120  # 2-minute timeout
    )

    
def build_evaluator_agent():
    """
    Build the ATS Evaluator Agent.
    
    This agent scores resumes against job descriptions by analyzing:
    - Keyword density and relevance
    - Section structure and formatting
    - Measurable achievements and metrics
    - Action verb usage
    - Overall ATS compatibility (0-100 score)
    
    Provides actionable recommendations for improvement.
    
    Returns:
        Agent: Configured evaluator agent with deterministic scoring (temperature=0.0)
    """
    return Agent(
        role="ATS Evaluator",
        goal="Provide accurate ATS scores and actionable improvement recommendations.",
        backstory=(
            "You are a precise ATS scoring expert who quickly identifies gaps and provides specific, "
            "actionable recommendations. You focus on keyword density, section structure, and measurable achievements."
        ),
        model=MODEL,
        temperature=0.0,   # Deterministic scoring - consistent results
        max_iter=1,        # Single evaluation pass
        max_execution_time=120  # 2-minute timeout
    )


def build_refiner_agent():
    """
    Build the Bullet Point Refiner Agent.
    
    This agent enhances bullet points by:
    - Adding strong action verbs (Spearheaded, Orchestrated, Drove, etc.)
    - Quantifying achievements with specific metrics
    - Following the CAR format (Context-Action-Result)
    - Creating high-impact statements
    - Maximizing ATS keyword matching
    
    Example transformation:
    Before: "Worked on team projects"
    After: "Led cross-functional team of 5 engineers, delivering 3 projects 20% ahead of schedule"
    
    Returns:
        Agent: Configured refiner agent with low creativity (temperature=0.2)
    """
    return Agent(
        role="Bullet Point Refiner",
        goal="Transform bullet points into high-impact, ATS-optimized statements with strong metrics.",
        backstory=(
            "You excel at creating powerful bullet points that combine action verbs, specific achievements, "
            "and quantified results. You work efficiently to maximize impact."
        ),
        model=MODEL,
        temperature=0.2,   # Low creativity - focused on structure
        max_iter=1,        # Single refinement pass
        max_execution_time=120  # 2-minute timeout
    )
