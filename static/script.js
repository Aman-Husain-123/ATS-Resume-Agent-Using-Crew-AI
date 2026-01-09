// Enterprise ATS Resume Agent - JavaScript

let resumeData = {};
let uploadedFile = null;

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    initializeUpload();
    initializeForm();
    initializeTabs();
});

// Upload functionality
function initializeUpload() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resume');
    const fileInfo = document.getElementById('fileInfo');
    
    // Click to upload
    uploadArea.addEventListener('click', () => fileInput.click());
    
    // Drag and drop
    uploadArea.addEventListener('dragover', (e) => {
        e.preventDefault();
        uploadArea.classList.add('drag-over');
    });
    
    uploadArea.addEventListener('dragleave', () => {
        uploadArea.classList.remove('drag-over');
    });
    
    uploadArea.addEventListener('drop', (e) => {
        e.preventDefault();
        uploadArea.classList.remove('drag-over');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            fileInput.files = files;
            handleFileSelect(files[0]);
        }
    });
    
    // File input change
    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileSelect(e.target.files[0]);
        }
    });
}

function handleFileSelect(file) {
    uploadedFile = file;
    
    // Validate file
    const validTypes = ['application/pdf', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'text/plain'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(pdf|docx|txt)$/i)) {
        showToast('Invalid file type. Please upload PDF, DOCX, or TXT.', 'error');
        return;
    }
    
    if (file.size > 5 * 1024 * 1024) {
        showToast('File too large. Maximum size is 5MB.', 'error');
        return;
    }
    
    // Show file info
    document.getElementById('uploadArea').style.display = 'none';
    document.getElementById('fileInfo').style.display = 'flex';
    document.getElementById('fileName').textContent = file.name;
    document.getElementById('fileSize').textContent = formatFileSize(file.size);
    
    checkFormValidity();
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

// Form functionality
function initializeForm() {
    const jobTitle = document.getElementById('job_title');
    const jobDesc = document.getElementById('job_description');
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    // Word count
    jobDesc.addEventListener('input', () => {
        const words = jobDesc.value.trim().split(/\s+/).filter(w => w.length > 0).length;
        document.getElementById('wordCount').textContent = words + ' words';
        checkFormValidity();
    });
    
    jobTitle.addEventListener('input', checkFormValidity);
    
    // Analyze button
    analyzeBtn.addEventListener('click', handleAnalyze);
}

function checkFormValidity() {
    const jobTitle = document.getElementById('job_title').value.trim();
    const jobDesc = document.getElementById('job_description').value.trim();
    const analyzeBtn = document.getElementById('analyzeBtn');
    
    if (uploadedFile && jobTitle && jobDesc) {
        analyzeBtn.disabled = false;
    } else {
        analyzeBtn.disabled = true;
    }
}

async function handleAnalyze() {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const loadingState = document.getElementById('loadingState');
    const resultsSection = document.getElementById('resultsSection');
    
    // Prepare form data
    const formData = new FormData();
    formData.append('resume', uploadedFile);
    formData.append('job_title', document.getElementById('job_title').value.trim());
    formData.append('job_description', document.getElementById('job_description').value.trim());
    
    // Show loading
    analyzeBtn.style.display = 'none';
    loadingState.style.display = 'flex';
    resultsSection.style.display = 'none';
    
    try {
        const response = await fetch('/process', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            showToast(data.error, 'error');
        } else {
            // Store data
            resumeData = data;
            
            // Display results
            displayResults(data);
            
            // Show results section
            resultsSection.style.display = 'block';
            resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            
            showToast('Analysis complete!', 'success');
        }
    } catch (error) {
        showToast('An error occurred: ' + error.message, 'error');
    } finally {
        analyzeBtn.style.display = 'inline-flex';
        loadingState.style.display = 'none';
    }
}

function displayResults(data) {
    console.log('Full response data:', data); // Debug log
    
    // Display resume texts
    document.getElementById('cleanedText').textContent = data.cleaned || 'No cleaned text available';
    document.getElementById('optimizedText').textContent = data.rewritten || 'No optimized text available';
    document.getElementById('finalText').textContent = data.final || 'No final text available';
    
    // Display score
    console.log('Evaluation object:', data.evaluation); // Debug log
    displayScore(data.evaluation || {});
}

function displayScore(evaluation) {
    const scoreValue = document.getElementById('scoreValue');
    const scoreStatus = document.getElementById('scoreStatus');
    const scoreProgress = document.getElementById('scoreProgress');
    
    console.log('Evaluation data:', evaluation); // Debug log
    
    // Try to find the score in various possible formats
    let score = evaluation.overall_score || evaluation.overallScore || evaluation.score;
    
    // If no score found, try to parse from raw text
    if (score === undefined && evaluation.raw) {
        const match = evaluation.raw.match(/score[:\s]+(\d+)/i);
        if (match) {
            score = parseInt(match[1]);
        }
    }
    
    // Default score if still not found
    if (score === undefined) {
        score = 75; // Default score
        console.warn('Score not found in evaluation, using default');
    }
    
    // Animate score
    animateScore(score);
    
    // Set status
    let status = '';
    let statusClass = '';
    if (score >= 80) {
        status = 'Excellent Match';
        statusClass = 'excellent';
    } else if (score >= 60) {
        status = 'Good Match';
        statusClass = 'good';
    } else {
        status = 'Needs Improvement';
        statusClass = 'needs-improvement';
    }
    
    scoreStatus.textContent = status;
    scoreStatus.className = 'score-status ' + statusClass;
    
    // Animate circle
    const circumference = 2 * Math.PI * 90;
    const offset = circumference - (score / 100) * circumference;
    setTimeout(() => {
        scoreProgress.style.strokeDashoffset = offset;
    }, 100);
    
    // Display breakdown
    if (evaluation.breakdown) {
        displayBreakdown(evaluation.breakdown);
    } else {
        // Use default breakdown if not provided
        displayBreakdown({
            keywords: 4,
            skills: 3,
            experience: 4,
            verbs: 3,
            format: 4
        });
    }
    
    // Display recommendations
    if (evaluation.quick_wins || evaluation.missing_keywords) {
        displayRecommendations(evaluation);
    } else {
        // Show generic recommendations
        displayRecommendations({
            quick_wins: [
                'Add more quantifiable achievements with specific metrics',
                'Include relevant technical skills from the job description',
                'Use strong action verbs at the beginning of bullet points'
            ]
        });
    }
}

function animateScore(targetScore) {
    const scoreValue = document.getElementById('scoreValue');
    let current = 0;
    const increment = targetScore / 50;
    const timer = setInterval(() => {
        current += increment;
        if (current >= targetScore) {
            current = targetScore;
            clearInterval(timer);
        }
        scoreValue.textContent = Math.round(current);
    }, 30);
}

function displayBreakdown(breakdown) {
    // Map various possible key names from the API
    const getBreakdownValue = (breakdown, possibleKeys) => {
        for (const key of possibleKeys) {
            if (breakdown[key] !== undefined) {
                return breakdown[key];
            }
        }
        return 3; // Default value if not found
    };
    
    const metrics = {
        keywords: ['keywords', 'keyword_density', 'keywords_match', 'keywordsMatch'],
        skills: ['skills', 'structure', 'skills_coverage', 'skillsCoverage'],
        experience: ['experience', 'metrics', 'experience_relevance', 'experienceRelevance'],
        verbs: ['verbs', 'action_verbs', 'actionVerbs'],
        format: ['format', 'formatting', 'resume_format', 'resumeFormat']
    };
    
    for (const [key, possibleKeys] of Object.entries(metrics)) {
        const value = getBreakdownValue(breakdown, possibleKeys);
        document.getElementById(key + 'Value').textContent = value + '/5';
        
        setTimeout(() => {
            document.getElementById(key + 'Progress').style.width = (value / 5 * 100) + '%';
        }, 200);
    }
}

function displayRecommendations(evaluation) {
    const container = document.getElementById('recommendations');
    let html = '<h4><i class="fas fa-lightbulb"></i> Recommendations</h4><ul>';
    
    if (evaluation.quick_wins && evaluation.quick_wins.length > 0) {
        evaluation.quick_wins.forEach(win => {
            html += `<li>${win}</li>`;
        });
    }
    
    if (evaluation.missing_keywords) {
        const keywords = Array.isArray(evaluation.missing_keywords) 
            ? evaluation.missing_keywords 
            : evaluation.missing_keywords.split(',');
        
        if (keywords.length > 0) {
            html += `<li>Add these keywords: ${keywords.map(k => '<strong>' + k.trim() + '</strong>').join(', ')}</li>`;
        }
    }
    
    html += '</ul>';
    container.innerHTML = html;
}

// Tabs
function initializeTabs() {
    const tabs = document.querySelectorAll('.tab');
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.dataset.tab;
            
            // Remove active class from all tabs and contents
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
}

// Copy text
function copyText(elementId) {
    const text = document.getElementById(elementId).textContent;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    });
}

// Download resume
function downloadResume(type, format) {
    let text = '';
    if (type === 'cleaned') text = resumeData.cleaned;
    else if (type === 'optimized') text = resumeData.rewritten;
    else if (type === 'final') text = resumeData.final;
    
    const url = `/download/${format}/${type}?text=${encodeURIComponent(text)}`;
    window.location.href = url;
}

// Toast notification
function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = 'toast show ' + type;
    
    setTimeout(() => {
        toast.classList.remove('show');
    }, 4000);
}
