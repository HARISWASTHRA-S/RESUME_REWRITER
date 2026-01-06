# 🎯 AI-Powered Resume Reviewer

An intelligent web-based tool that analyzes resumes against job descriptions and provides personalized improvement suggestions. This application helps job seekers optimize their resumes for ATS (Applicant Tracking Systems) compatibility and better recruiter visibility.

## ✨ Features

- **📄 Multi-format Support**: Upload resumes in PDF, DOCX, or TXT formats
- **🤖 Smart Analysis**: Uses advanced keyword matching and NLP techniques for intelligent resume evaluation
- **📊 Comprehensive Scoring**: Get overall match score and ATS compatibility rating
- **💡 Personalized Suggestions**: Receive actionable recommendations categorized by priority
- **🔑 Keyword Analysis**: Identify missing keywords from the job description
- **✅ Strengths & Weaknesses**: Clear breakdown of what's working and what needs improvement
- **🎨 Modern UI**: Clean, responsive interface with intuitive design
- **⚡ Fast Processing**: Instant analysis with real-time feedback
- **🔓 No API Keys Required**: Works completely offline without external dependencies

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- No API keys needed!

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd RESUME_REWRITER
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
python app.py
```

5. **Open in browser**
```
http://localhost:5000
```

## 📖 Usage

1. **Upload Resume**: Click or drag-and-drop your resume file (PDF, DOCX, or TXT)
2. **Paste Job Description**: Copy and paste the complete job description (minimum 50 characters)
3. **Analyze**: Click "Analyze Resume" and wait for AI-powered insights
4. **Review Results**: Get comprehensive feedback including:
   - Overall match score
   - ATS compatibility score
   - Strengths and weaknesses
   - Missing keywords
   - Prioritized suggestions with examples
   - ATS optimization tips
   - Recommended sections to add/improve

## 🏗️ Project Structure

```
RESUME_REWRITER/
├── app.py                  # Flask backend application
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── templates/
│   └── index.html         # Main HTML template
├── static/
│   ├── style.css          # Stylesheet
│   └── script.js          # Frontend JavaScript
└── uploads/               # Temporary file storage (auto-created)
```

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `FLASK_ENV`: Set to `development` or `production`
- `FLASK_DEBUG`: Set to `True` for development

### File Upload Settings

- Maximum file size: 16MB
- Allowed formats: PDF, DOCX, TXT
- Te
**Request:**
- `resume`: File (multipart/form-data)
- `job_description`: String (form data)

**Response:**
```json
{
  "success": true,
  "analysis": {
    "overall_score": 85,
    "ats_compatibility_score": 90,
    "match_summary": "Your resume shows strong alignment...",
    "strengths": [...],
    "weaknesses": [...],
    "missing_keywords": [...],
    "suggestions": [...],
    "ats_tips": [...],
    "recommended_sections": [...]
  }
}
```

### `GET /api/health`
Health check endpoint

**Response:**
```json
{
  "status": "healthy",
  "service": "Resume Reviewer API"
}
```

## 🎨 Customization

### Modify AI Analysis

Edit the `analyze_resume_with_ai()` function in `app.py` to:
- Adjust the analysis prompt
- Change the AI model (currently using `gpt-4o-mini`)
- Modify scoring criteria
- Add customnalysis Algorithm

Edit the `analyze_resume_with_ai()` function in `app.py` to:
- Adjust keyword matching algorithms
- Modify scoring criteria and weights
- Add custom evaluation categories
- Customize ATS compatibility check
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    /* ... more colors */
}
```

## 🐛 Troubleshooting

### Common Issues

**Issue**: "No module named 'PyPDF2'"
- **Solution**: Run `pip install -r requirements.txt`

**Issue**: "OpenAI API key not found"
- **Solution**: Ensure `.env` file exists with valid `OPENAI_API_KEY`

**Issue**: "Could not extract text from resume"
- **Solution**: Ensure resume is not password-protected or corrupted

**Issue**: Fpment

### Running in Development Mode

```bash
export FLASK_ENV=development
export FLASK_DEBUG=True
python app.py
```

### Testing the API

```bash
# Health check
curl http://localhost:5000/api/health

# Analyze resume
curl -X POST http://localhost:5000/api/analyze \
  -F "resume=@/path/to/resume.pdf" \
  -F "job_description=Job description text here..."
```

## 🚢 Deployment

### Deploy to Production

1. Set environment to production:
```bash
FLASK_ENV=production
FLASK_DEBUG=False
```

2. Use a production WSGI server (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. Set up reverse proxy (Nginx/Apache) for HTTPS

### Environment Variables for Production

- Use secure secret keys
- Enable HTTPS only
- Set proper CORS origins
- Use environment-specific API keys

## 📄 License

ThisProduction Best Practices

- Use secure secret keys
- Enable HTTPS only
- Set proper CORS origins
- Implement rate limiting for API endpoint
## 💬 Support

For issues, questions, or suggestions, please open an issue in the repository.

## 🙏 Acknowledgments

- OpenAI for GPT-4 API
- Flask framework
- All open-source libraries used in this project

---

Built with ❤️ to help job seekers land their dream roles!
Flask framework
- PyPDF2 and python-docx libraries
- All open-source libraries used in this project

## 🧠 How It Works

The application uses intelligent keyword matching and natural language processing to:
1. Extract and analyze keywords from both resume and job description
2. Calculate match percentages based on keyword overlap
3. Check ATS compatibility factors (formatting, sections, contact info)
4. Identify missing important keywords
5. Generate personalized suggestions based on analysis
6. Provide actionable tips for improvement

No external AI APIs required - all processing happens locally!