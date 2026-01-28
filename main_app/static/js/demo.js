// ============================================
// NEURALSYNC LIVE - DEMO INTERACTIVE
// ============================================

// Global state
let currentMode = null;
let currentSessionId = null;
let sessionStats = {
    questionsAsked: 0,
    correctAnswers: 0,
    hintsUsed: 0
};

// DOM Elements
const modeCards = document.querySelectorAll('.mode-card');
const modeSelectorSection = document.querySelector('.mode-selector-section');
const demoArea = document.getElementById('demoArea');
const backBtn = document.getElementById('backBtn');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadCard = document.querySelector('.upload-card');
const uploadSection = document.getElementById('uploadSection');
const analysisSection = document.getElementById('analysisSection');
const chatSection = document.getElementById('chatSection');
const loadingModal = document.getElementById('loadingModal');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const chatMessages = document.getElementById('chatMessages');
const requestHintBtn = document.getElementById('requestHintBtn');

// ============================================
// LOADING MODAL LOGIC (Moved here to avoid hoisting issues)
// ============================================
let bsLoadingModal = null;

function showLoadingModal(message = 'Processing...') {
    const modalEl = document.getElementById('loadingModal');
    if (!bsLoadingModal) {
        bsLoadingModal = new bootstrap.Modal(modalEl);
    }

    document.getElementById('loadingMessage').textContent = message;

    // Reset progress bar
    const progressFill = document.getElementById('progressFill');
    if (progressFill) {
        progressFill.style.width = '0%';
        progressFill.className = 'progress-bar bg-gradient-primary'; // Reset animations
    }

    bsLoadingModal.show();
}

function hideLoadingModal() {
    if (bsLoadingModal) {
        bsLoadingModal.hide();
        // Force cleanup backdrop if needed
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) backdrop.remove();
        document.body.classList.remove('modal-open');
        document.body.style = '';
    }
}

function updateLoadingMessage(message) {
    document.getElementById('loadingMessage').textContent = message;
}

// Mode configurations
const modeConfig = {
    video: {
        title: 'Learn While You Watch',
        icon: 'fa-video',
        description: 'Upload educational videos and get interactive questions at key moments',
        accept: '.mp4,.mov,.avi,.webm',
        fileTypes: ['MP4', 'MOV', 'AVI', 'WEBM']
    },
    problem: {
        title: 'Visual Problem Solver',
        icon: 'fa-calculator',
        description: 'Snap photos of problems and get step-by-step Socratic guidance',
        accept: '.jpg,.jpeg,.png,.gif,.webp',
        fileTypes: ['JPG', 'PNG', 'GIF', 'WEBP']
    },
    document: {
        title: 'Document Intelligence',
        icon: 'fa-file-alt',
        description: 'Transform documents into interactive concept maps and quizzes',
        accept: '.pdf,.txt,.doc,.docx',
        fileTypes: ['PDF', 'TXT', 'DOC', 'DOCX']
    },
    creative: {
        title: 'Creative Workshop',
        icon: 'fa-palette',
        description: 'Get expert feedback and suggestions for your creative work',
        accept: '.jpg,.jpeg,.png,.gif,.webp',
        fileTypes: ['JPG', 'PNG', 'GIF', 'WEBP']
    }
};

// ============================================
// 1. MODE SELECTION
// ============================================
modeCards.forEach(card => {
    const selectBtn = card.querySelector('.mode-select-btn');
    selectBtn.addEventListener('click', () => {
        const mode = card.dataset.mode;
        selectMode(mode);
    });
});

function selectMode(mode) {
    currentMode = mode;
    const config = modeConfig[mode];

    // Update UI
    document.getElementById('modeTitle').textContent = config.title;
    document.getElementById('modeDesc').textContent = config.description;
    document.getElementById('modeIcon').className = `fas ${config.icon}`;

    // Update file input
    fileInput.accept = config.accept;
    document.getElementById('uploadHint').textContent =
        `Upload a ${mode === 'video' ? 'video' : mode === 'document' ? 'document' : 'image'} file to get started`;

    // Update file type tags
    const fileTypesContainer = document.getElementById('fileTypes');
    fileTypesContainer.innerHTML = config.fileTypes
        .map(type => `<span class="file-type-tag">${type}</span>`)
        .join('');

    // Hide mode selector, show demo area
    modeSelectorSection.style.display = 'none';
    demoArea.style.display = 'block';

    // Create session
    createSession(mode);

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// 2. SESSION MANAGEMENT
// ============================================
async function createSession(mode) {
    try {
        const response = await fetch('/api/session/create/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                mode: mode,
                title: `New ${mode} session - ${new Date().toLocaleString()}`
            })
        });

        const data = await response.json();

        if (data.success) {
            currentSessionId = data.session_id;
            console.log('Session created:', currentSessionId);
        } else {
            throw new Error(data.error || 'Failed to create session');
        }
    } catch (error) {
        console.error('Error creating session:', error);
        window.NeuralSync.showToast('Failed to create session', 'error');
    }
}

function updateSessionStats() {
    document.getElementById('questionsAsked').textContent = sessionStats.questionsAsked;
    document.getElementById('correctAnswers').textContent = sessionStats.correctAnswers;
    document.getElementById('hintsUsed').textContent = sessionStats.hintsUsed;

    const accuracy = sessionStats.questionsAsked > 0
        ? Math.round((sessionStats.correctAnswers / sessionStats.questionsAsked) * 100)
        : 0;
    document.getElementById('accuracy').textContent = `${accuracy}%`;
}

// ============================================
// 3. FILE UPLOAD
// ============================================
browseBtn.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileUpload(e.target.files[0]);
    }
});

// Drag and drop
uploadCard.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadCard.classList.add('drag-over');
});

uploadCard.addEventListener('dragleave', () => {
    uploadCard.classList.remove('drag-over');
});

uploadCard.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadCard.classList.remove('drag-over');

    if (e.dataTransfer.files.length > 0) {
        handleFileUpload(e.dataTransfer.files[0]);
    }
});

async function handleFileUpload(file) {
    if (!currentSessionId) {
        window.NeuralSync.showToast('No active session', 'error');
        return;
    }

    // Show loading modal
    showLoadingModal(`Uploading ${file.name}...`);
    const progressFill = document.getElementById('progressFill');
    if (progressFill) progressFill.style.width = '0%';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', currentSessionId);
    formData.append('context', '');

    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        // Progress event
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                if (progressFill) {
                    progressFill.style.width = `${percentComplete}%`;

                    if (percentComplete === 100) {
                        updateLoadingMessage('Analyzing with Gemini 3 (this may take a moment)...');
                        progressFill.classList.add('progress-bar-striped', 'progress-bar-animated');
                    } else {
                        updateLoadingMessage(`Uploading: ${percentComplete}%`);
                    }
                }
            }
        });

        // Load event (Upload finished, waiting for server response)
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    hideLoadingModal();

                    if (data.success) {
                        window.NeuralSync.showToast('Analysis complete!', 'success');
                        displayAnalysis(data.analysis);
                        resolve(data);
                    } else {
                        window.NeuralSync.showToast(data.error || 'Upload failed', 'error');
                        reject(new Error(data.error));
                    }
                } catch (e) {
                    hideLoadingModal();
                    window.NeuralSync.showToast('Invalid server response', 'error');
                    reject(e);
                }
            } else {
                hideLoadingModal();
                let errorMsg = 'Upload failed';
                try {
                    const errData = JSON.parse(xhr.responseText);
                    errorMsg = errData.error || errorMsg;
                } catch (e) { }

                window.NeuralSync.showToast(errorMsg, 'error');
                reject(new Error(errorMsg));
            }
        });

        // Error event
        xhr.addEventListener('error', () => {
            hideLoadingModal();
            window.NeuralSync.showToast('Network error during upload', 'error');
            reject(new Error('Network error'));
        });

        // Send request
        xhr.open('POST', '/api/upload/');
        xhr.send(formData);
    });
}

// ============================================
// 4. DISPLAY ANALYSIS
// ============================================
function displayAnalysis(analysis) {
    uploadSection.style.display = 'none';
    analysisSection.style.display = 'block';

    const analysisContent = document.getElementById('analysisContent');
    let html = '<div class="analysis-container">';

    // Summary
    if (analysis.summary) {
        html += `
            <div class="result-card animate-slide-up">
                <div class="result-header">
                    <div class="result-icon"><i class="fas fa-lightbulb"></i></div>
                    <h3 class="result-title">Executive Summary</h3>
                </div>
                <p class="text-secondary">${analysis.summary}</p>
            </div>
        `;
    }

    // Key Concepts
    if (analysis.key_concepts && analysis.key_concepts.length > 0) {
        html += `
            <div class="result-card animate-slide-up" style="animation-delay: 0.1s">
                <div class="result-header">
                    <div class="result-icon"><i class="fas fa-brain"></i></div>
                    <h3 class="result-title">Key Concepts</h3>
                </div>
                <div class="d-flex flex-wrap gap-2">
                    ${analysis.key_concepts.map(concept =>
            `<span class="concept-tag">${concept}</span>`
        ).join('')}
                </div>
            </div>
        `;
    }

    // Interactive Questions
    if (analysis.interactive_questions && analysis.interactive_questions.length > 0) {
        html += `
            <div class="result-card animate-slide-up" style="animation-delay: 0.2s">
                <div class="result-header">
                    <div class="result-icon"><i class="fas fa-question-circle"></i></div>
                    <h3 class="result-title">Interactive Questions</h3>
                </div>
                <p class="text-secondary small mb-3">
                    Answer these questions to deepen your understanding
                </p>
                ${analysis.interactive_questions.slice(0, 3).map((q, idx) => `
                    <div class="question-item">
                        <div class="question-text">${idx + 1}. ${q.question}</div>
                        <div class="d-flex justify-content-end">
                            <button class="btn btn-primary btn-sm action-btn answer-question-btn" 
                                    data-question="${encodeURIComponent(q.question)}"
                                    data-answer="${encodeURIComponent(q.answer || '')}">
                                <i class="fas fa-comment-dots me-2"></i>Answer Now
                            </button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Document-specific: Quiz Questions
    if (analysis.quiz_questions && analysis.quiz_questions.length > 0) {
        html += `
            <div class="result-card animate-slide-up" style="animation-delay: 0.2s">
                <div class="result-header">
                    <div class="result-icon"><i class="fas fa-graduation-cap"></i></div>
                    <h3 class="result-title">Quiz Time</h3>
                </div>
                ${analysis.quiz_questions.slice(0, 3).map((q, idx) => `
                    <div class="question-item border-start-0 border-top pt-3">
                        <div class="question-text">${idx + 1}. ${q.question}</div>
                        ${q.options ? `
                            <div class="d-flex flex-column gap-2 mb-2">
                                ${q.options.map((opt, oidx) => `
                                    <div class="text-secondary small">
                                        <strong class="text-primary">${String.fromCharCode(65 + oidx)}.</strong> ${opt}
                                    </div>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
        `;
    }

    // Creative-specific: Suggestions
    if (analysis.improvements && analysis.improvements.length > 0) {
        html += `
            <div class="result-card animate-slide-up" style="animation-delay: 0.2s">
                <div class="result-header">
                    <div class="result-icon"><i class="fas fa-magic"></i></div>
                    <h3 class="result-title">Suggestions for Improvement</h3>
                </div>
                <div class="list-group list-group-flush bg-transparent">
                    ${analysis.improvements.slice(0, 5).map(imp =>
            `<div class="list-group-item bg-transparent border-secondary border-opacity-25 px-0">
                            <strong class="d-block text-white mb-1">${imp.aspect}</strong>
                            <span class="text-secondary small">${imp.suggestion}</span>
                        </div>`
        ).join('')}
                </div>
            </div>
        `;
    }

    html += '</div>';

    analysisContent.innerHTML = html;

    // Add event listeners to question buttons
    document.querySelectorAll('.answer-question-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const question = decodeURIComponent(btn.dataset.question);
            const answer = decodeURIComponent(btn.dataset.answer);
            startInteractiveChat(question, answer);
        });
    });
}

// ============================================
// 5. INTERACTIVE CHAT
// ============================================
function startInteractiveChat(initialQuestion = null, correctAnswer = null) {
    analysisSection.style.display = 'none';
    chatSection.style.display = 'flex';

    if (initialQuestion) {
        addMessage('ai', initialQuestion);
        // Store the correct answer for evaluation
        chatInput.dataset.currentQuestion = initialQuestion;
        chatInput.dataset.correctAnswer = correctAnswer || '';
    }

    chatInput.focus();
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message || !currentSessionId) return;

    // Add user message
    addMessage('user', message);
    chatInput.value = '';

    // Check if this is an answer to a question
    const currentQuestion = chatInput.dataset.currentQuestion;
    const correctAnswer = chatInput.dataset.correctAnswer;

    if (currentQuestion && correctAnswer) {
        // Submit answer for evaluation
        await submitAnswer(currentQuestion, message, correctAnswer);
        chatInput.dataset.currentQuestion = '';
        chatInput.dataset.correctAnswer = '';
    } else {
        // Regular question
        await askQuestion(message);
    }
}

async function askQuestion(question) {
    try {
        const response = await fetch('/api/ask/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                question: question,
                context: {}
            })
        });

        const data = await response.json();

        if (data.success) {
            addMessage('ai', data.response);
            sessionStats.questionsAsked++;
            updateSessionStats();
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error asking question:', error);
        addMessage('ai', 'Sorry, I encountered an error. Please try again.');
    }
}

async function submitAnswer(question, userAnswer, correctAnswer) {
    try {
        const response = await fetch('/api/answer/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                question: question,
                user_answer: userAnswer,
                correct_answer: correctAnswer,
                context: {}
            })
        });

        const data = await response.json();

        if (data.success) {
            const evaluation = data.evaluation;

            // Update stats
            sessionStats.questionsAsked++;
            if (evaluation.is_correct) {
                sessionStats.correctAnswers++;
            }
            updateSessionStats();

            // Display feedback
            const feedbackMsg = `
                ${evaluation.is_correct ? '✅ Correct!' : '❌ Not quite right.'} 
                ${evaluation.feedback}
                ${evaluation.encouragement ? `\n\n${evaluation.encouragement}` : ''}
            `;
            addMessage('ai', feedbackMsg);
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error submitting answer:', error);
        addMessage('ai', 'Sorry, I couldn\'t evaluate your answer. Please try again.');
    }
}

requestHintBtn.addEventListener('click', async () => {
    const currentQuestion = chatInput.dataset.currentQuestion;
    if (!currentQuestion) {
        window.NeuralSync.showToast('No active question', 'info');
        return;
    }

    try {
        const response = await fetch('/api/hint/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                problem: currentQuestion,
                current_progress: ''
            })
        });

        const data = await response.json();

        if (data.success) {
            addMessage('ai', `💡 Hint: ${data.hint}`);
            sessionStats.hintsUsed++;
            updateSessionStats();
        } else {
            throw new Error(data.error);
        }
    } catch (error) {
        console.error('Error requesting hint:', error);
        window.NeuralSync.showToast('Failed to get hint', 'error');
    }
});

function addMessage(sender, text) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${sender}`;

    const now = new Date();
    const timeStr = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

    messageDiv.innerHTML = `
        <div class="message-avatar">
            ${sender === 'ai' ? '🧠' : '👤'}
        </div>
        <div class="message-content">
            <div class="message-bubble">${text.replace(/\n/g, '<br>')}</div>
            <div class="message-time">${timeStr}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}



// ============================================
// 7. BACK BUTTON
// ============================================
backBtn.addEventListener('click', () => {
    // Reset UI
    demoArea.style.display = 'none';
    modeSelectorSection.style.display = 'block';
    uploadSection.style.display = 'flex';
    analysisSection.style.display = 'none';
    chatSection.style.display = 'none';
    chatMessages.innerHTML = '';

    // Reset state
    currentMode = null;
    currentSessionId = null;
    sessionStats = {
        questionsAsked: 0,
        correctAnswers: 0,
        hintsUsed: 0
    };
    updateSessionStats();

    window.scrollTo({ top: 0, behavior: 'smooth' });
});

// ============================================
// 8. URL PARAMETER HANDLING
// ============================================
window.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const mode = urlParams.get('mode');

    if (mode && modeConfig[mode]) {
        selectMode(mode);
    }
});

console.log('%c🎯 NeuralSync Live Demo Ready!', 'color: #6366f1; font-size: 16px; font-weight: bold;');
