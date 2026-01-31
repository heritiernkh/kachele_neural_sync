// ============================================
// NEURALSYNC LIVE - WORKSPACE INTERACTION
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
const workspaceArea = document.getElementById('workspaceArea');
const backBtn = document.getElementById('backBtn');
const fileInput = document.getElementById('fileInput');
const browseBtn = document.getElementById('browseBtn');
const uploadCard = document.querySelector('.upload-card');
const uploadSection = document.getElementById('uploadSection');
const analysisSection = document.getElementById('analysisSection');
const chatInputSection = document.getElementById('chatInputSection');
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
        // On garde les classes Bootstrap pour l'animation
        progressFill.className = 'progress-bar progress-bar-striped progress-bar-animated';
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

// ============================================
// ANALYSIS SPINNER (In-page spinner)
// ============================================
function showAnalysisSpinner() {
    // Afficher les zones de chat et d'analyse
    chatInputSection.style.display = 'none'; // On cache l'input pour l'instant
    analysisSection.style.display = 'block';
    chatSection.style.display = 'block';

    // Vider le contenu précédent
    chatMessages.innerHTML = '';

    // Créer le spinner d'analyse élégant
    const spinnerHtml = `
        <div id="analysisSpinner" class="text-center py-5">
            <div class="mb-4">
                <div class="spinner-border text-primary" style="width: 3rem; height: 3rem;" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
            </div>
            <h4 class="h5 text-primary mb-2">
                <i class="fas fa-brain me-2"></i>Analyse en cours avec Gemini
            </h4>
            <p class="text-muted small">
                Génération d'une question socratique personnalisée...
            </p>
        </div>
    `;

    chatMessages.innerHTML = spinnerHtml;
}

function hideAnalysisSpinner() {
    const spinner = document.getElementById('analysisSpinner');
    if (spinner) {
        spinner.remove();
    }
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

    // Hide mode selector, show workspace area
    modeSelectorSection.style.display = 'none';
    workspaceArea.style.display = 'block';

    // Reset visibility of work sections
    uploadSection.className = 'upload-section h-100 d-flex align-items-start justify-content-center pt-4';
    uploadSection.style.display = 'flex';

    // Restore original upload card HTML
    const uploadCard = uploadSection.querySelector('.upload-card');
    if (uploadCard) {
        uploadCard.className = 'upload-card text-center w-100 p-5 border-2 border-dashed border-secondary border-opacity-25 rounded-4 transition-base hover-glow';
        uploadCard.style.maxWidth = '500px';
        uploadCard.innerHTML = `
            <div class="mb-4 text-primary display-4">
                <i class="fas fa-cloud-upload-alt"></i>
            </div>
            <h2 class="h3 mb-3">Upload Content</h2>
            <p class="text-muted mb-4" id="uploadHint">
                Drag and drop your file here, or click to browse
            </p>
            <input type="file" id="fileInput" accept="" style="display: none;">
            
            <!-- Speed Mode Toggle -->
            <div class="mb-4">
                <div class="form-check form-switch d-inline-flex align-items-center gap-2 px-4 py-2 rounded-pill bg-dark bg-opacity-25 border border-secondary border-opacity-25">
                    <input class="form-check-input" type="checkbox" id="speedModeToggle" style="cursor: pointer;">
                    <label class="form-check-label small text-muted" for="speedModeToggle" style="cursor: pointer;">
                        ⚡ Mode Rapide <span class="text-info">(~40% plus rapide)</span>
                    </label>
                </div>
                <div class="small text-muted mt-2 px-3" style="max-width: 400px; margin: 0 auto;">
                    Le mode rapide sacrifie légèrement la profondeur d'analyse pour une vitesse maximale
                </div>
            </div>
            
            <button class="btn btn-primary btn-lg px-4 rounded-pill mb-3" id="browseBtn">
                <i class="fas fa-folder-open me-2"></i> Browse Files
            </button>
            <div class="mb-3">
                <span class="text-muted small">OR</span>
            </div>
            <button class="btn btn-outline-primary rounded-pill px-4" id="startWithTextBtn">
                <i class="fas fa-keyboard me-2"></i> Démarrer par texte
            </button>
            <div class="d-flex justify-content-center gap-2 mt-4 flex-wrap" id="fileTypes"></div>
        `;
        // Re-bind events
        const newFileInput = document.getElementById('fileInput');
        newFileInput.onchange = (e) => {
            if (e.target.files.length > 0) {
                handleFileUpload(e.target.files[0]);
            }
        };

        document.getElementById('browseBtn').onclick = (e) => {
            e.stopPropagation();
            newFileInput.click();
        };
        document.getElementById('startWithTextBtn').onclick = (e) => {
            e.stopPropagation();
            switchToTextMode();
        };
        uploadCard.onclick = () => newFileInput.click();
    }

    chatInputSection.style.display = 'none';
    analysisSection.style.display = 'none';
    chatSection.style.display = 'none';
    chatMessages.innerHTML = ''; // Clear previous messages

    // Create session
    createSession(mode);

    // Scroll to top
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

// ============================================
// 2. SESSION MANAGEMENT
// ============================================
function switchToTextMode() {
    uploadSection.style.display = 'none';
    chatInputSection.style.display = 'block';
    chatSection.style.display = 'block';

    // Welcome message for text mode
    const welcomeMsg = `Bonjour ! Je suis ton tuteur Kachele Neural Sync Live. Comment puis-je t'aider aujourd'hui ? Tu peux me poser une question sur n'importe quel sujet.`;
    addMessage('ai', welcomeMsg);
    chatInput.focus();
}

// Initial binding for the button present in HTML
const initialStartWithTextBtn = document.getElementById('startWithTextBtn');
if (initialStartWithTextBtn) {
    initialStartWithTextBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        switchToTextMode();
    });
}

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
        window.KacheleNeuralSync.showToast('Failed to create session', 'error');
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
        window.KacheleNeuralSync.showToast('No active session', 'error');
        return;
    }
    window.currentFileName = file.name;

    // Show loading modal
    const speedModeEnabled = document.getElementById('speedModeToggle')?.checked || false;
    const speedModeText = speedModeEnabled ? ' (Mode Rapide ⚡)' : '';
    showLoadingModal(`Analyse de ${file.name}${speedModeText}...`);
    const progressFill = document.getElementById('progressFill');
    if (progressFill) progressFill.style.width = '0%';

    const formData = new FormData();
    formData.append('file', file);
    formData.append('session_id', currentSessionId);
    formData.append('context', '');
    formData.append('speed_mode', speedModeEnabled.toString());

    return new Promise((resolve, reject) => {
        const xhr = new XMLHttpRequest();

        // Progress event
        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percentComplete = Math.round((e.loaded / e.total) * 100);
                if (progressFill) {
                    progressFill.style.width = `${percentComplete}%`;

                    if (percentComplete === 100) {
                        updateLoadingMessage('Analyse par Gemini 3 en cours...');
                        progressFill.classList.add('progress-bar-striped', 'progress-bar-animated');
                    } else {
                        updateLoadingMessage(`Téléchargement: ${percentComplete}%`);
                    }
                }
            }
        });

        // Load event (Upload finished, waiting for server response)
        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const data = JSON.parse(xhr.responseText);

                    // ✅ NOUVEAU: Fermer le modal immédiatement après l'upload
                    hideLoadingModal();

                    if (data.success) {
                        // ✅ NOUVEAU: Afficher spinner d'analyse dans la zone de travail
                        showAnalysisSpinner();

                        // Afficher l'analyse et générer la question
                        window.KacheleNeuralSync.showToast('Analysis complete!', 'success');
                        displayAnalysis(data.analysis);
                        resolve(data);
                    } else {
                        displayError(data.error || 'Upload failed');
                        reject(new Error(data.error));
                    }
                } catch (e) {
                    hideLoadingModal();
                    displayError('Invalid server response');
                    reject(e);
                }
            } else {
                hideLoadingModal();
                let errorMsg = 'Upload failed';
                try {
                    const errData = JSON.parse(xhr.responseText);
                    errorMsg = errData.error || errorMsg;
                } catch (e) { }

                displayError(errorMsg);
                reject(new Error(errorMsg));
            }
        });

        // Error event
        xhr.addEventListener('error', () => {
            hideLoadingModal();
            displayError('Network error during upload');
            reject(new Error('Network error'));
        });

        // Send request
        xhr.open('POST', '/api/upload/');
        xhr.send(formData);
    });
}

function displayError(message) {
    uploadSection.style.display = 'none';
    analysisSection.style.display = 'block';

    const analysisContent = document.getElementById('analysisContent');
    analysisContent.innerHTML = `
        <div class="result-card animate-slide-up border-danger border-opacity-25">
            <div class="result-header">
                <div class="result-icon bg-danger bg-opacity-10 text-danger"><i class="fas fa-exclamation-triangle"></i></div>
                <h3 class="result-title text-danger">Oups ! Une erreur est survenue</h3>
            </div>
            <p class="text-secondary">${message}</p>
            <div class="mt-4 pt-3 border-top border-secondary border-opacity-10">
                <button class="btn btn-outline-primary btn-sm rounded-pill" onclick="location.reload()">
                    <i class="fas fa-redo me-2"></i>Réessayer
                </button>
            </div>
        </div>
    `;
    hideLoadingModal();
}

// ============================================
// 4. DISPLAY ANALYSIS
// ============================================
function displayAnalysis(analysis) {
    // DO NOT hide uploadSection, we will compact it instead later
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

    // Compact the upload area to save space
    if (uploadSection) {
        uploadSection.classList.remove('h-100', 'pt-4');
        const uploadCard = uploadSection.querySelector('.upload-card');
        if (uploadCard) {
            uploadCard.classList.remove('p-5');
            uploadCard.classList.add('p-3');
            uploadCard.innerHTML = `
                <div class="d-flex align-items-center justify-content-center gap-3">
                    <div class="text-primary h5 mb-0"><i class="fas fa-file-check"></i></div>
                    <h2 class="h6 mb-0">Fichier : <span class="text-primary">${window.currentFileName || 'Chargé'}</span></h2>
                    <button class="btn btn-outline-primary btn-sm rounded-pill ms-auto px-3" onclick="document.getElementById('fileInput').click()">Changer</button>
                </div>
            `;
        }
    }

    // Show everything
    chatInputSection.style.display = 'block';
    analysisSection.style.display = 'block';
    chatSection.style.display = 'block';

    analysisContent.innerHTML = html;

    // Trigger KaTeX rendering for analysis
    if (window.renderMathInElement) {
        renderMathInElement(analysisContent, {
            delimiters: [
                { left: '$$', right: '$$', display: true },
                { left: '$', right: '$', display: false },
                { left: '\\(', right: '\\)', display: false },
                { left: '\\[', right: '\\]', display: true }
            ],
            throwOnError: false
        });
    }

    // 🎯 NOUVEAU: Générer automatiquement la première question socratique
    // Le spinner est déjà affiché, on génère juste la question
    generateAndDisplayFirstQuestion();

    document.querySelectorAll('.answer-question-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            const question = decodeURIComponent(btn.dataset.question);
            const answer = decodeURIComponent(btn.dataset.answer);
            startInteractiveChat(question, answer);
        });
    });
}

// 🎯 NOUVELLE FONCTION: Génère et affiche proactivement la première question socratique
async function generateAndDisplayFirstQuestion() {
    if (!currentSessionId || !currentMode) {
        console.warn('No session or mode available for first question generation');
        hideAnalysisSpinner(); // Cacher le spinner même en cas d'erreur
        return;
    }

    try {
        const response = await fetch('/api/first-question/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                session_id: currentSessionId,
                mode: currentMode
            })
        });

        const data = await response.json();

        // ✅ Cacher le spinner d'analyse
        hideAnalysisSpinner();

        if (data.success && data.question) {
            // Afficher la question générée
            const questionIntro = data.is_fallback
                ? '🤔 Pendant que Gemini réfléchit, commençons par ceci :'
                : '🧠 J\'ai analysé ton contenu. Voici ma première question pour toi :';

            addMessage('ai', `${questionIntro}\n\n${data.question}`);
        } else {
            // Fallback message si ça échoue
            addMessage('ai', "Bonjour ! J'ai terminé l'analyse. De quoi souhaites-tu discuter ?");
        }
    } catch (error) {
        console.error('Error generating first question:', error);

        // ✅ Cacher le spinner même en cas d'erreur
        hideAnalysisSpinner();

        // Message de fallback en cas d'erreur réseau
        const fallback = {
            'video': "Après avoir analysé cette vidéo, qu'en as-tu retenu comme point le plus important ?",
            'problem': "Avant de te guider, dis-moi : par où commencerais-tu pour résoudre ce problème ?",
            'document': "Maintenant que j'ai parcouru ce document, quelles sont les idées principales que tu en tires ?",
            'creative': "Peux-tu m'expliquer ce que tu as cherché à exprimer dans ce travail ?"
        };
        addMessage('ai', `🤔 ${fallback[currentMode] || "De quoi aimerais-tu discuter ?"}`);
    }

    // Scroller vers le bas et focus sur l'input
    chatMessages.scrollTop = chatMessages.scrollHeight;
    chatInput.focus();
}

// ============================================
// 5. INTERACTIVE CHAT
// ============================================
function startInteractiveChat(initialQuestion = null, correctAnswer = null) {
    chatInputSection.style.display = 'block';
    chatSection.style.display = 'block';

    if (initialQuestion) {
        addMessage('ai', initialQuestion);
        // Store the correct answer for evaluation
        chatInput.dataset.currentQuestion = initialQuestion;
        chatInput.dataset.correctAnswer = correctAnswer || '';
    }

    chatInput.focus();
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('input', function () {
    this.style.height = 'auto';
    this.style.height = (this.scrollHeight) + 'px';

    // Empêcher que ça devienne trop grand
    if (this.scrollHeight > 200) {
        this.style.overflowY = 'auto';
        this.style.height = '200px';
    } else {
        this.style.overflowY = 'hidden';
    }
});

chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
        // Reset height after sending
        chatInput.style.height = '48px';
    }
});

async function sendMessage() {
    const message = chatInput.value.trim();
    if (!message) return;

    if (!currentSessionId) {
        window.KacheleNeuralSync.showToast('Veuillez d\'abord sélectionner un mode et uploader un fichier.', 'warning');
        return;
    }

    // Add user message
    addMessage('user', message);
    chatInput.value = '';
    chatInput.style.height = '48px';

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
        addMessage('ai', `Désolé, une erreur est survenue : ${error.message}`);
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
        window.KacheleNeuralSync.showToast('No active question', 'info');
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
        window.KacheleNeuralSync.showToast('Failed to get hint', 'error');
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
            <div class="message-bubble"></div>
            <div class="message-time">${timeStr}</div>
        </div>
    `;

    chatMessages.appendChild(messageDiv);
    const bubble = messageDiv.querySelector('.message-bubble');

    if (sender === 'ai') {
        // Typing effect for AI
        let i = 0;
        bubble.classList.add('typing');

        // Prepare the full HTML first but show incrementally
        // Or better: render markdown then type it? 
        // Rendering markdown first is safer for structure
        const rawHtml = marked.parse(text);

        // For a more natural feel, we type the text or use a CSS transition
        // But for hackathon wow factor, let's do a smooth reveal
        bubble.innerHTML = rawHtml;

        // Trigger KaTeX rendering
        if (window.renderMathInElement) {
            renderMathInElement(bubble, {
                delimiters: [
                    { left: '$$', right: '$$', display: true },
                    { left: '$', right: '$', display: false },
                    { left: '\\(', right: '\\)', display: false },
                    { left: '\\[', right: '\\]', display: true }
                ],
                throwOnError: false
            });
        }
    } else {
        bubble.innerHTML = text.replace(/\n/g, '<br>');
    }

    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Si la zone de messages grandit, on s'assure que le champ de texte en bas est visible
    setTimeout(() => {
        chatInput.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }, 100);
}



// ============================================
// 7. BACK BUTTON
// ============================================
backBtn.addEventListener('click', () => {
    // Reset UI
    workspaceArea.style.display = 'none';
    modeSelectorSection.style.display = 'block';

    // Reset Everything
    if (currentMode) {
        selectMode(currentMode); // Use selectMode to reset the UI state
    }

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

console.log('%c🎯 KacheleNeuralSync Live Workspace Ready!', 'color: #6366f1; font-size: 16px; font-weight: bold;');
