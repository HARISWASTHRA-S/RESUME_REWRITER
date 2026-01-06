from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import PyPDF2
import docx
import json
import re
from collections import Counter
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx', 'txt'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def extract_text_from_pdf(file_path):
    """Extract text from PDF file"""
    text = ""
    with open(file_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text

def extract_text_from_docx(file_path):
    """Extract text from DOCX file"""
    doc = docx.Document(file_path)
    text = ""
    for paragraph in doc.paragraphs:
        text += paragraph.text + "\n"
    return text

def extract_text_from_txt(file_path):
    """Extract text from TXT file"""
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()

def extract_resume_text(file_path):
    """Extract text from resume based on file type"""
    extension = file_path.rsplit('.', 1)[1].lower()
    
    if extension == 'pdf':
        return extract_text_from_pdf(file_path)
    elif extension == 'docx':
        return extract_text_from_docx(file_path)
    elif extension == 'txt':
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}")

def extract_keywords(text):
    """Extract important keywords from text"""
    # Remove common words and extract meaningful terms
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                  'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'be',
                  'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                  'should', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 
                  'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
                  'who', 'when', 'where', 'why', 'how', 'all', 'each', 'every', 'both',
                  'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not',
                  'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'our'}
    
    # Extract words and multi-word phrases
    words = re.findall(r'\b[a-zA-Z][a-zA-Z+#\-\.]*\b', text.lower())
    
    # Filter out stop words and short words
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Extract common technical terms and phrases
    tech_patterns = [
        r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b',  # Capitalized phrases
        r'\b[A-Z]{2,}\b',  # Acronyms
        r'\b\w+\+\+\b',  # C++, etc
        r'\b[A-Z][a-z]*\.[A-Z][a-z]*\b',  # Node.js, etc
    ]
    
    for pattern in tech_patterns:
        matches = re.findall(pattern, text)
        keywords.extend([m.lower() for m in matches])
    
    return keywords

def calculate_keyword_match(resume_keywords, job_keywords):
    """Calculate keyword match percentage"""
    if not job_keywords:
        return 100
    
    resume_set = set(resume_keywords)
    job_set = set(job_keywords)
    
    matched = resume_set.intersection(job_set)
    match_percentage = (len(matched) / len(job_set)) * 100 if job_set else 0
    
    return min(100, match_percentage)

def check_ats_compatibility(resume_text):
    """Check ATS compatibility factors"""
    score = 100
    issues = []
    
    # Check for special characters that might confuse ATS
    if re.search(r'[│┃║╔╗╚╝═]', resume_text):
        score -= 15
        issues.append("Contains special formatting characters that ATS may not parse correctly")
    
    # Check for common sections
    sections = ['experience', 'education', 'skills', 'work', 'employment']
    found_sections = sum(1 for s in sections if s in resume_text.lower())
    if found_sections < 2:
        score -= 20
        issues.append("Missing standard resume sections")
    
    # Check length
    word_count = len(resume_text.split())
    if word_count < 200:
        score -= 15
        issues.append("Resume appears too short")
    elif word_count > 1500:
        score -= 10
        issues.append("Resume might be too lengthy")
    
    # Check for contact information
    if not re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', resume_text):
        score -= 10
        issues.append("No email address detected")
    
    # Check for dates (experience timeline)
    date_patterns = r'\b(19|20)\d{2}\b|\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+(19|20)\d{2}\b'
    if not re.search(date_patterns, resume_text):
        score -= 10
        issues.append("No dates found for work experience")
    
    return max(0, score), issues

def analyze_resume_with_ai(resume_text, job_description):
    """Analyze resume against job description using rule-based approach"""
    
    # Extract keywords
    resume_keywords = extract_keywords(resume_text)
    job_keywords = extract_keywords(job_description)
    
    # Find missing keywords
    resume_set = set(resume_keywords)
    job_set = set(job_keywords)
    missing = list(job_set - resume_set)
    
    # Get most important missing keywords (those that appear frequently in job description)
    job_keyword_freq = Counter(job_keywords)
    important_missing = sorted(missing, key=lambda x: job_keyword_freq.get(x, 0), reverse=True)[:15]
    
    # Calculate scores
    keyword_match = calculate_keyword_match(resume_keywords, job_keywords)
    ats_score, ats_issues = check_ats_compatibility(resume_text)
    
    overall_score = int((keyword_match * 0.6) + (ats_score * 0.4))
    
    # Identify strengths
    strengths = []
    if keyword_match > 70:
        strengths.append("Strong keyword alignment with job requirements")
    if ats_score > 80:
        strengths.append("Resume follows ATS-friendly formatting")
    if len(resume_text.split()) > 300:
        strengths.append("Comprehensive resume with detailed information")
    if re.search(r'\b(achieved|improved|increased|reduced|managed|led|developed)\b', resume_text.lower()):
        strengths.append("Uses action verbs and achievement-focused language")
    if re.search(r'\d+%|\d+\+|increased|improved|reduced', resume_text.lower()):
        strengths.append("Includes quantifiable achievements")
    
    if not strengths:
        strengths.append("Resume has been submitted for analysis")
    
    # Identify weaknesses
    weaknesses = ats_issues.copy() if ats_issues else []
    if keyword_match < 40:
        weaknesses.append("Low keyword match with job description - consider incorporating more relevant terms")
    if keyword_match < 60:
        weaknesses.append("Could better align experience and skills with job requirements")
    if not re.search(r'\b(certified|certification|degree|bachelor|master)\b', resume_text.lower()):
        weaknesses.append("Educational qualifications or certifications not clearly highlighted")
    
    if not weaknesses:
        weaknesses.append("Consider adding more quantifiable achievements")
    
    # Generate suggestions
    suggestions = []
    
    if important_missing:
        suggestions.append({
            "category": "Keywords & Terminology",
            "priority": "High",
            "suggestion": f"Incorporate important keywords from the job description: {', '.join(important_missing[:5])}",
            "example": f"Add phrases like '{important_missing[0]}' to your skills or experience sections"
        })
    
    if keyword_match < 60:
        suggestions.append({
            "category": "Content Alignment",
            "priority": "High",
            "suggestion": "Tailor your resume to better match the job description by highlighting relevant experience",
            "example": "Review each requirement in the job posting and ensure your resume addresses it with specific examples"
        })
    
    if not re.search(r'\d+%|\d+\+', resume_text.lower()):
        suggestions.append({
            "category": "Quantifiable Achievements",
            "priority": "Medium",
            "suggestion": "Add metrics and numbers to demonstrate impact",
            "example": "Instead of 'Improved sales', write 'Increased sales by 25% over 6 months'"
        })
    
    suggestions.append({
        "category": "Action Verbs",
        "priority": "Medium",
        "suggestion": "Start bullet points with strong action verbs",
        "example": "Use words like: Led, Developed, Implemented, Optimized, Achieved, Spearheaded"
    })
    
    if ats_score < 80:
        suggestions.append({
            "category": "ATS Formatting",
            "priority": "High",
            "suggestion": "Ensure your resume uses standard section headers and simple formatting",
            "example": "Use clear headers like 'Work Experience', 'Education', 'Skills' instead of creative alternatives"
        })
    
    # ATS Tips
    ats_tips = [
        "Use standard fonts like Arial, Calibri, or Times New Roman (10-12pt)",
        "Avoid headers, footers, tables, and text boxes - use simple formatting",
        "Save resume as .docx or PDF (check job posting for preferred format)",
        "Include both acronyms and full spellings (e.g., 'Search Engine Optimization (SEO)')",
        "Use standard section headings that ATS can recognize",
        "Avoid using images, graphics, or special characters",
        "Include relevant keywords naturally throughout your resume"
    ]
    
    # Recommended sections
    recommended_sections = []
    if 'summary' not in resume_text.lower() and 'objective' not in resume_text.lower():
        recommended_sections.append("Professional Summary")
    if 'skills' not in resume_text.lower():
        recommended_sections.append("Technical Skills / Core Competencies")
    if 'certification' not in resume_text.lower():
        recommended_sections.append("Certifications & Licenses")
    if 'project' not in resume_text.lower():
        recommended_sections.append("Key Projects")
    
    # Match summary
    if overall_score >= 80:
        match_summary = f"Excellent match! Your resume aligns well with the job requirements ({int(keyword_match)}% keyword match). Focus on fine-tuning specific details."
    elif overall_score >= 60:
        match_summary = f"Good foundation with {int(keyword_match)}% keyword match. Enhance your resume by incorporating more relevant keywords and achievements from the job description."
    elif overall_score >= 40:
        match_summary = f"Moderate match ({int(keyword_match)}% keywords). Significant improvements needed - tailor your resume to highlight relevant experience and skills mentioned in the job posting."
    else:
        match_summary = f"Low match ({int(keyword_match)}% keywords). Consider restructuring your resume to better align with the job requirements. Focus on relevant skills, experience, and terminology."
    
    return {
        "overall_score": overall_score,
        "ats_compatibility_score": int(ats_score),
        "match_summary": match_summary,
        "strengths": strengths[:5],
        "weaknesses": weaknesses[:5],
        "missing_keywords": important_missing[:12],
        "suggestions": suggestions[:6],
        "ats_tips": ats_tips[:5],
        "recommended_sections": recommended_sections
    }

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/analyze', methods=['POST'])
def analyze_resume():
    """Analyze resume endpoint"""
    
    # Check if file is present
    if 'resume' not in request.files:
        return jsonify({'error': 'No resume file provided'}), 400
    
    file = request.files['resume']
    job_description = request.form.get('job_description', '')
    
    # Validate file
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload PDF, DOCX, or TXT'}), 400
    
    if not job_description or len(job_description.strip()) < 50:
        return jsonify({'error': 'Please provide a detailed job description (at least 50 characters)'}), 400
    
    try:
        # Save file
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Extract text from resume
        resume_text = extract_resume_text(file_path)
        
        # Clean up uploaded file
        os.remove(file_path)
        
        # Validate extracted text
        if not resume_text or len(resume_text.strip()) < 100:
            return jsonify({'error': 'Could not extract sufficient text from resume. Please ensure the file is not corrupted.'}), 400
        
        # Analyze with AI
        analysis = analyze_resume_with_ai(resume_text, job_description)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        })
    
    except Exception as e:
        return jsonify({'error': f'Error processing resume: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'service': 'Resume Reviewer API'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
