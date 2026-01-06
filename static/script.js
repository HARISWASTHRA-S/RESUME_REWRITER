// DOM Elements
const resumeForm = document.getElementById('resumeForm');
const resumeFile = document.getElementById('resumeFile');
const jobDescription = document.getElementById('jobDescription');
const analyzeBtn = document.getElementById('analyzeBtn');
const uploadSection = document.getElementById('uploadSection');
const resultsSection = document.getElementById('resultsSection');
const errorMessage = document.getElementById('errorMessage');
const newAnalysisBtn = document.getElementById('newAnalysisBtn');
const fileUploadDisplay = document.querySelector('.file-upload-display');

// File upload display update
resumeFile.addEventListener('change', function(e) {
    const fileName = e.target.files[0]?.name || 'Choose a file or drag it here';
    fileUploadDisplay.querySelector('.file-text').textContent = fileName;
});

// Form submission
resumeForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    
    // Hide any previous errors
    hideError();
    
    // Validate form
    if (!resumeFile.files[0]) {
        showError('Please select a resume file');
        return;
    }
    
    if (jobDescription.value.trim().length < 50) {
        showError('Please provide a detailed job description (at least 50 characters)');
        return;
    }
    
    // Show loading state
    setLoadingState(true);
    
    // Prepare form data
    const formData = new FormData();
    formData.append('resume', resumeFile.files[0]);
    formData.append('job_description', jobDescription.value);
    
    try {
        // Send request to backend
        const response = await fetch('/api/analyze', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to analyze resume');
        }
        
        // Display results
        displayResults(data.analysis);
        
    } catch (error) {
        showError(error.message);
        setLoadingState(false);
    }
});

// New analysis button
newAnalysisBtn.addEventListener('click', function() {
    // Reset form
    resumeForm.reset();
    fileUploadDisplay.querySelector('.file-text').textContent = 'Choose a file or drag it here';
    
    // Hide results and show upload section
    resultsSection.style.display = 'none';
    uploadSection.style.display = 'block';
    
    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// Display results
function displayResults(analysis) {
    // Hide upload section and show results
    uploadSection.style.display = 'none';
    resultsSection.style.display = 'block';
    setLoadingState(false);
    
    // Scroll to results
    setTimeout(() => {
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }, 100);
    
    // Update scores
    updateScore('overallScore', 'overallScoreFill', analysis.overall_score || 0);
    updateScore('atsScore', 'atsScoreFill', analysis.ats_compatibility_score || 0);
    
    // Update summary
    document.getElementById('summaryText').textContent = analysis.match_summary || 'No summary available';
    
    // Update strengths
    const strengthsList = document.getElementById('strengthsList');
    strengthsList.innerHTML = '';
    (analysis.strengths || []).forEach(strength => {
        const li = document.createElement('li');
        li.textContent = strength;
        strengthsList.appendChild(li);
    });
    
    // Update weaknesses
    const weaknessesList = document.getElementById('weaknessesList');
    weaknessesList.innerHTML = '';
    (analysis.weaknesses || []).forEach(weakness => {
        const li = document.createElement('li');
        li.textContent = weakness;
        weaknessesList.appendChild(li);
    });
    
    // Update keywords
    const keywordsList = document.getElementById('keywordsList');
    const keywordsBox = document.getElementById('keywordsBox');
    keywordsList.innerHTML = '';
    
    if (analysis.missing_keywords && analysis.missing_keywords.length > 0) {
        keywordsBox.style.display = 'block';
        analysis.missing_keywords.forEach(keyword => {
            const tag = document.createElement('span');
            tag.className = 'keyword-tag';
            tag.textContent = keyword;
            keywordsList.appendChild(tag);
        });
    } else {
        keywordsBox.style.display = 'none';
    }
    
    // Update suggestions
    const suggestionsList = document.getElementById('suggestionsList');
    suggestionsList.innerHTML = '';
    (analysis.suggestions || []).forEach(suggestion => {
        const item = createSuggestionItem(suggestion);
        suggestionsList.appendChild(item);
    });
    
    // Update ATS tips
    const atsTipsList = document.getElementById('atsTipsList');
    atsTipsList.innerHTML = '';
    (analysis.ats_tips || []).forEach(tip => {
        const li = document.createElement('li');
        li.textContent = tip;
        atsTipsList.appendChild(li);
    });
    
    // Update recommended sections
    const sectionsList = document.getElementById('sectionsList');
    const sectionsBox = document.getElementById('sectionsBox');
    sectionsList.innerHTML = '';
    
    if (analysis.recommended_sections && analysis.recommended_sections.length > 0) {
        sectionsBox.style.display = 'block';
        analysis.recommended_sections.forEach(section => {
            const tag = document.createElement('span');
            tag.className = 'section-tag';
            tag.textContent = section;
            sectionsList.appendChild(tag);
        });
    } else {
        sectionsBox.style.display = 'none';
    }
}

// Create suggestion item
function createSuggestionItem(suggestion) {
    const item = document.createElement('div');
    item.className = 'suggestion-item';
    
    const header = document.createElement('div');
    header.className = 'suggestion-header';
    
    const category = document.createElement('div');
    category.className = 'suggestion-category';
    category.textContent = suggestion.category || 'General';
    
    const badge = document.createElement('span');
    badge.className = `priority-badge priority-${(suggestion.priority || 'medium').toLowerCase()}`;
    badge.textContent = suggestion.priority || 'Medium';
    
    header.appendChild(category);
    header.appendChild(badge);
    
    const text = document.createElement('div');
    text.className = 'suggestion-text';
    text.textContent = suggestion.suggestion || '';
    
    item.appendChild(header);
    item.appendChild(text);
    
    if (suggestion.example) {
        const example = document.createElement('div');
        example.className = 'suggestion-example';
        example.textContent = suggestion.example;
        item.appendChild(example);
    }
    
    return item;
}

// Update score display
function updateScore(scoreId, fillId, value) {
    const scoreElement = document.getElementById(scoreId);
    const fillElement = document.getElementById(fillId);
    
    // Animate score
    let currentValue = 0;
    const increment = value / 50;
    const interval = setInterval(() => {
        currentValue += increment;
        if (currentValue >= value) {
            currentValue = value;
            clearInterval(interval);
        }
        scoreElement.textContent = Math.round(currentValue);
    }, 20);
    
    // Animate fill bar
    setTimeout(() => {
        fillElement.style.width = value + '%';
    }, 100);
}

// Show error message
function showError(message) {
    const errorText = document.getElementById('errorText');
    errorText.textContent = message;
    errorMessage.style.display = 'flex';
    
    // Scroll to error
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideError();
    }, 5000);
}

// Hide error message
function hideError() {
    errorMessage.style.display = 'none';
}

// Set loading state
function setLoadingState(isLoading) {
    const btnText = analyzeBtn.querySelector('.btn-text');
    const btnLoader = analyzeBtn.querySelector('.btn-loader');
    
    if (isLoading) {
        btnText.style.display = 'none';
        btnLoader.style.display = 'flex';
        analyzeBtn.disabled = true;
    } else {
        btnText.style.display = 'inline';
        btnLoader.style.display = 'none';
        analyzeBtn.disabled = false;
    }
}

// Drag and drop support
const fileUploadWrapper = document.querySelector('.file-upload-wrapper');

['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    fileUploadWrapper.addEventListener(eventName, preventDefaults, false);
});

function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

['dragenter', 'dragover'].forEach(eventName => {
    fileUploadWrapper.addEventListener(eventName, () => {
        fileUploadDisplay.style.borderColor = 'var(--primary-color)';
        fileUploadDisplay.style.background = '#f1f5f9';
    }, false);
});

['dragleave', 'drop'].forEach(eventName => {
    fileUploadWrapper.addEventListener(eventName, () => {
        fileUploadDisplay.style.borderColor = 'var(--border-color)';
        fileUploadDisplay.style.background = 'var(--bg-color)';
    }, false);
});

fileUploadWrapper.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        resumeFile.files = files;
        fileUploadDisplay.querySelector('.file-text').textContent = files[0].name;
    }
}, false);
