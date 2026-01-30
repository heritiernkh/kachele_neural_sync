// ============================================
// NEURALSYNC LIVE - MAIN JAVASCRIPT
// ============================================

// ============================================
// 1. NAVIGATION
// ============================================
document.addEventListener('DOMContentLoaded', () => {
    const menuToggle = document.getElementById('menuToggle');
    const navMenu = document.getElementById('navMenu');

    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            menuToggle.classList.toggle('active');
        });

        // Close menu when clicking outside
        document.addEventListener('click', (e) => {
            if (!navMenu.contains(e.target) && !menuToggle.contains(e.target)) {
                navMenu.classList.remove('active');
                menuToggle.classList.remove('active');
            }
        });
    }
});

// ============================================
// 2. SMOOTH SCROLLING
// ============================================
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// ============================================
// 3. NAVBAR SCROLL EFFECT
// ============================================
let lastScrollY = 0;
const navbar = document.getElementById('navbar');

window.addEventListener('scroll', () => {
    const currentScrollY = window.scrollY;

    if (currentScrollY > 100) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }

    lastScrollY = currentScrollY;
});

// ============================================
// 4. INTERSECTION OBSERVER FOR ANIMATIONS
// ============================================
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry, index) => {
        if (entry.isIntersecting) {
            setTimeout(() => {
                entry.target.classList.add('animate-in');
            }, index * 100); // Stagger animation
        }
    });
}, observerOptions);

// Observe all animatable elements
document.querySelectorAll('.feature-card, .step, .why-feature, .stats-item').forEach(el => {
    observer.observe(el);
});

// ============================================
// 5. UTILITY FUNCTIONS
// ============================================

/**
 * Format file size to human readable format
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format duration to MM:SS format
 */
function formatDuration(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Show loading spinner
 */
function showLoading(element) {
    if (!element) return;
    element.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Processing with Gemini 3...</p>
        </div>
    `;
}

/**
 * Show error message
 */
function showError(element, message) {
    if (!element) return;
    element.innerHTML = `
        <div class="error-message">
            <i class="fas fa-exclamation-circle"></i>
            <p>${message}</p>
        </div>
    `;
}

/**
 * Show success message
 */
function showSuccess(element, message) {
    if (!element) return;
    element.innerHTML = `
        <div class="success-message">
            <i class="fas fa-check-circle"></i>
            <p>${message}</p>
        </div>
    `;
}

/**
 * Create notification toast
 */
/**
 * Create notification toast
 * @param {string} message - Message to display
 * @param {string} type - Type of notification (info, success, error)
 * @param {number} duration - Duration in ms (default: 3000 for info/success, 5000 for error)
 */
function showToast(message, type = 'info', duration = null) {
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'times' : 'info'}-circle"></i>
        <span>${message}</span>
    `;

    document.body.appendChild(toast);

    // Trigger animation
    setTimeout(() => toast.classList.add('show'), 10);

    // Determine duration
    const timeoutDuration = duration || (type === 'error' ? 10000 : 5000); // 10s pour erreurs, 5s pour le reste

    let timeoutId;

    const startTimer = () => {
        timeoutId = setTimeout(() => {
            removeToast();
        }, timeoutDuration);
    };

    const removeToast = () => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    };

    // Start initial timer
    startTimer();

    // Pause on hover
    toast.addEventListener('mouseenter', () => {
        clearTimeout(timeoutId);
    });

    // Resume on mouse leave
    toast.addEventListener('mouseleave', () => {
        startTimer();
    });

    // Click to close immediately
    toast.addEventListener('click', () => {
        clearTimeout(timeoutId);
        removeToast();
    });
}

// ============================================
// 6. COPY TO CLIPBOARD
// ============================================
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'error');
    });
}

// ============================================
// 7. LOCAL STORAGE HELPERS
// ============================================
const Storage = {
    set(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.error('Error saving to localStorage:', e);
        }
    },

    get(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.error('Error reading from localStorage:', e);
            return null;
        }
    },

    remove(key) {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.error('Error removing from localStorage:', e);
        }
    },

    clear() {
        try {
            localStorage.clear();
        } catch (e) {
            console.error('Error clearing localStorage:', e);
        }
    }
};

// ============================================
// 8. KEYBOARD SHORTCUTS
// ============================================
document.addEventListener('keydown', (e) => {
    // Ctrl/Cmd + K to focus search
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.querySelector('[data-search]');
        if (searchInput) {
            searchInput.focus();
        }
    }

    // Escape to close modals
    if (e.key === 'Escape') {
        const activeModal = document.querySelector('.modal.active');
        if (activeModal) {
            activeModal.classList.remove('active');
        }
    }
});

// ============================================
// 9. PERFORMANCE MONITORING
// ============================================
if ('PerformanceObserver' in window) {
    const perfObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
            // Log slow interactions (> 100ms)
            if (entry.duration > 100) {
                console.warn('Slow interaction detected:', entry.name, entry.duration);
            }
        }
    });

    try {
        perfObserver.observe({ entryTypes: ['measure'] });
    } catch (e) {
        // Ignore errors from unsupported browsers
    }
}

// ============================================
// 10. EXPORT UTILITIES
// ============================================
window.KacheleNeuralSync = {
    formatFileSize,
    formatDuration,
    showLoading,
    showError,
    showSuccess,
    showToast,
    copyToClipboard,
    Storage
};

console.log('%c🧠 KacheleNeuralSync Live %cpowered by Gemini 3',
    'color: #6366f1; font-size: 20px; font-weight: bold;',
    'color: #a855f7; font-size: 14px;'
);
