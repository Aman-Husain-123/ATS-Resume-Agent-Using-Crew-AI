"""
ATS Resume Task Definitions
This module defines tasks for each agent in the resume optimization pipeline.
Tasks include text truncation to manage token limits and clear instructions for agents.
"""

from crewai import Task


def parse_resume_task(agent, raw_resume_text):
    """
    Create a task for parsing and cleaning raw resume text.
    
    This task instructs the agent to:
    - Remove formatting artifacts and noise
    - Normalize bullet points to standard format (-)
    - Preserve all important content
    - Work quickly and efficiently
    
    Args:
        agent: The parser agent to execute this task
        raw_resume_text: Raw text extracted from resume file
        
    Returns:
        Task: Configured parsing task with truncated input
    """
    # Truncate if too long to manage token limits
    truncated_text = raw_resume_text[:1500] + "..." if len(raw_resume_text) > 1500 else raw_resume_text
    
    return Task(
        description=(
            f"Clean this resume text quickly:\n\n{truncated_text}\n\n"
            "Remove artifacts, normalize bullets to '-', keep all content. Be fast and direct."
        ),
        agent=agent,
        expected_output=("Clean resume text with proper structure.")
    )

    
def rewrite_for_ats_task(agent, cleaned_resume_text, job_title, job_description):
    """
    Create a task for rewriting resume to match job requirements.
    
    This task instructs the agent to:
    - Match keywords from job description
    - Use strong action verbs
    - Add quantifiable metrics
    - Target 80+ ATS compatibility score
    - Optimize for ATS parsing
    
    Args:
        agent: The ATS writer agent to execute this task
        cleaned_resume_text: Cleaned resume text from parsing stage
        job_title: Target job title for optimization
        job_description: Full job description to match against
        
    Returns:
        Task: Configured rewriting task with truncated inputs
    """
    # Truncate inputs if too long to manage token limits
    truncated_resume = cleaned_resume_text[:1200] + "..." if len(cleaned_resume_text) > 1200 else cleaned_resume_text
    truncated_jd = job_description[:300] + "..." if len(job_description) > 300 else job_description
    
    return Task(
        description=(
            f"Rewrite resume for {job_title}:\n\n"
            f"JOB: {truncated_jd}\n\n"
            f"RESUME: {truncated_resume}\n\n"
            "Match keywords, use action verbs, add metrics. Target 80+ ATS score. Be direct and fast."
        ),
        agent=agent,
        expected_output="ATS-optimized resume with keyword placement and metrics."
    )

    
def refine_bullets_task(agent, rewritten_resume_text):
    """
    Create a task for refining bullet points with impact and metrics.
    
    This task instructs the agent to:
    - Add strong action verbs (Led, Achieved, Drove, etc.)
    - Quantify achievements with specific numbers
    - Follow CAR format (Context-Action-Result)
    - Create high-impact statements
    - Work efficiently
    
    Args:
        agent: The refiner agent to execute this task
        rewritten_resume_text: ATS-optimized resume from rewriting stage
        
    Returns:
        Task: Configured refinement task with truncated input
    """
    # Truncate if too long to manage token limits
    truncated_text = rewritten_resume_text[:1000] + "..." if len(rewritten_resume_text) > 1000 else rewritten_resume_text
    
    return Task(
        description=(
            f"Polish these bullets with action verbs and metrics:\n\n{truncated_text}\n\n"
            "Add strong verbs and numbers. Be fast and direct."
        ),
        agent=agent,
        expected_output="Resume with enhanced bullet points and metrics."
    )

    
def evaluate_ats_task(agent, final_resume_text, job_title, job_description):
    """
    Create a task for evaluating ATS compatibility and scoring.
    
    This task instructs the agent to:
    - Score resume on 5 criteria (keywords, structure, metrics, verbs, format)
    - Calculate overall ATS score (0-100)
    - Identify missing keywords from job description
    - Provide quick wins for improvement
    - Return structured JSON output
    
    Scoring criteria (1-5 each):
    - Keywords: Relevance and density of job-specific terms
    - Structure: Section organization and ATS-friendly formatting
    - Metrics: Quantifiable achievements and impact
    - Verbs: Strong action verbs usage
    - Format: Overall ATS compatibility
    
    Args:
        agent: The evaluator agent to execute this task
        final_resume_text: Final refined resume text
        job_title: Target job title for evaluation
        job_description: Job description to compare against
        
    Returns:
        Task: Configured evaluation task with truncated inputs and JSON output format
    """
    # Truncate inputs if too long to manage token limits
    truncated_resume = final_resume_text[:800] + "..." if len(final_resume_text) > 800 else final_resume_text
    truncated_jd = job_description[:200] + "..." if len(job_description) > 200 else job_description
    
    return Task(
        description=(
            f"Score this resume for {job_title}:\n\n"
            f"JOB: {truncated_jd}\n\n"
            f"RESUME: {truncated_resume}\n\n"
            "Rate 1-5: keywords, structure, metrics, verbs, format. "
            "Return JSON with overall_score (0-100), breakdown, missing_keywords, quick_wins."
        ),
        agent=agent,
        expected_output="JSON evaluation with scores and recommendations."
    )

