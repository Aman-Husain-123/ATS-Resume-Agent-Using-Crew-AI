"""
ATS Resume Optimization Crew
This module orchestrates multiple AI agents to optimize resumes for Applicant Tracking Systems (ATS).
The crew follows a sequential pipeline: Parse -> Rewrite -> Refine -> Evaluate
"""

import os
from crewai import Crew, Process

# Import agent builders for each stage of the pipeline
from agents import (
    build_parser_agent,      # Cleans and structures raw resume text
    build_ats_writer_agent,  # Rewrites resume for ATS optimization
    build_evaluator_agent,   # Scores and evaluates ATS compatibility
    build_refiner_agent      # Refines bullet points with metrics
)

# Import task definitions for each agent
from tasks import (
    parse_resume_task,       # Task: Extract clean text from resume
    rewrite_for_ats_task,    # Task: Rewrite resume with ATS keywords
    evaluate_ats_task,       # Task: Score resume against job description
    refine_bullets_task      # Task: Enhance bullet points with impact
)

def build_crew(raw_resume_text: str, job_title: str, job_description: str):
    """
    Build a crew with all agents and tasks (legacy approach - not recommended).
    
    Note: This function uses placeholder strings for task dependencies which may not work
    correctly with CrewAI's sequential processing. Use run_pipeline() instead for reliable results.
    
    Args:
        raw_resume_text: Raw text extracted from resume file
        job_title: Target job title for optimization
        job_description: Full job description to match against
        
    Returns:
        Crew: Configured crew with all agents and tasks
    """
    # Initialize all agents for the pipeline
    parser = build_parser_agent()
    writer = build_ats_writer_agent()
    refiner = build_refiner_agent()
    evaluator = build_evaluator_agent()

    # Create tasks with dependencies (using placeholder strings)
    t_parse = parse_resume_task(parser, raw_resume_text)
    # Note: These are placeholders; actual results need to be passed after execution
    t_rewrite = rewrite_for_ats_task(writer, "{t_parse}", job_title, job_description)
    t_refine = refine_bullets_task(refiner, "{{ewrite_fr_ats_task}}")
    t_eval = evaluate_ats_task(evaluator, "{{refine_bullets_task}}", job_title, job_description)

    # Assemble crew with sequential processing
    crew = Crew(
        agents=[parser, writer, refiner, evaluator],
        tasks=[t_parse, t_rewrite, t_refine, t_eval],
        process=Process.sequential,  # Execute tasks in order
        verbose=True  # Enable detailed logging
    )
    return crew


def run_pipeline(raw_resume_text: str, job_title: str, job_description: str):
    """
    Execute the complete ATS resume optimization pipeline with proper task chaining.
    
    This function runs each stage sequentially, passing actual results between stages
    instead of using placeholders. This ensures reliable data flow through the pipeline.
    
    Pipeline stages:
    1. Parse: Clean and structure the raw resume text
    2. Rewrite: Optimize resume for ATS with job-specific keywords
    3. Refine: Enhance bullet points with metrics and impact statements
    4. Evaluate: Score the final resume and provide recommendations
    
    Args:
        raw_resume_text: Raw text extracted from resume file (PDF/DOCX)
        job_title: Target job title for optimization
        job_description: Full job description to match keywords and requirements
        
    Returns:
        tuple: (cleaned_resume, rewritten_resume, final_resume, evaluation_report)
            - cleaned_resume: Parsed and cleaned resume text
            - rewritten_resume: ATS-optimized version with keywords
            - final_resume: Final version with refined bullet points
            - evaluation_report: ATS score and improvement recommendations
    """
    
    # ========== STAGE 1: PARSE RESUME ==========
    # Initialize parser agent to clean and structure resume text
    parser = build_parser_agent()
    writer = build_ats_writer_agent()
    refiner = build_refiner_agent()
    evaluator = build_evaluator_agent()

    # Create parsing task with raw resume text
    t_parse = parse_resume_task(parser, raw_resume_text)
    
    # Build crew for parsing stage
    parse_crew = Crew(
        agents=[parser],
        tasks=[t_parse],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute parsing and extract cleaned text
    parse_result = parse_crew.kickoff()
    cleaned = str(parse_result).strip()

    # ========== STAGE 2: REWRITE FOR ATS ==========
    # Create rewrite task with cleaned resume and job requirements
    t_rewrite = rewrite_for_ats_task(writer, cleaned, job_title, job_description)
    rewrite_crew = Crew(
        agents=[writer],
        tasks=[t_rewrite],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute rewriting with ATS optimization
    rewrite_result = rewrite_crew.kickoff()
    rewritten = str(rewrite_result).strip()

    # ========== STAGE 3: REFINE BULLET POINTS ==========
    # Create refine task to enhance bullet points with metrics
    t_refine = refine_bullets_task(refiner, rewritten)
    refine_crew = Crew(
        agents=[refiner],
        tasks=[t_refine],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute refinement for high-impact statements
    refine_result = refine_crew.kickoff()
    final_resume = str(refine_result).strip()

    # ========== STAGE 4: EVALUATE ATS SCORE ==========
    # Create evaluation task to score final resume
    t_eval = evaluate_ats_task(evaluator, final_resume, job_title, job_description)
    eval_crew = Crew(
        agents=[evaluator],
        tasks=[t_eval],
        process=Process.sequential,
        verbose=True
    )
    
    # Execute evaluation and get ATS score with recommendations
    eval_result = eval_crew.kickoff()
    evaluation = str(eval_result).strip()

    # Return all pipeline outputs for review
    return cleaned, rewritten, final_resume, evaluation
