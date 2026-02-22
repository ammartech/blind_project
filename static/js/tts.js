/**
 * Arabic TTS Player - مشغل القراءة الصوتية
 * static/js/tts.js
 * 
 * Usage in templates:
 * 
 * 1. Include this script in base.html:
 *    <script src="{% static 'js/tts.js' %}"></script>
 * 
 * 2. Add TTS buttons:
 *    <button class="tts-btn" onclick="playTTS('مرحباً بكم', 'female')">
 *      🔊 استماع
 *    </button>
 * 
 * 3. For glossary terms:
 *    <button onclick="playGlossaryTTS({{ term.pk }}, 'full', 'female')">
 *      🔊 قراءة المصطلح
 *    </button>
 * 
 * 4. For inquiry answers:
 *    <button onclick="playInquiryTTS({{ inquiry.pk }}, 'female')">
 *      🔊 استماع للإجابة
 *    </button>
 */

// Global audio element
let currentAudio = null;
let isPlaying = false;

/**
 * Get CSRF token from cookies
 */
function getCSRFToken() {
    const name = 'csrftoken';
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        cookie = cookie.trim();
        if (cookie.startsWith(name + '=')) {
            return decodeURIComponent(cookie.substring(name.length + 1));
        }
    }
    return '';
}

/**
 * Get selected voice from radio buttons
 */
function getSelectedVoice() {
    const selected = document.querySelector('input[name="tts-voice"]:checked');
    return selected ? selected.value : 'female';
}

/**
 * Play TTS for any Arabic text
 * 
 * @param {string} text - Arabic text to speak
 * @param {string} voice - 'male' or 'female' (optional, uses selected if not provided)
 * @param {HTMLElement} button - Optional button element to show loading state
 */
async function playTTS(text, voice = null, button = null) {
    // Get voice from parameter or selection
    voice = voice || getSelectedVoice();
    
    // Get button from event if not passed
    if (!button && event && event.target) {
        button = event.target.closest('.tts-btn');
    }
    
    // Stop current audio if playing
    if (currentAudio && isPlaying) {
        currentAudio.pause();
        currentAudio = null;
        isPlaying = false;
        
        // Reset button state
        document.querySelectorAll('.tts-btn.playing').forEach(btn => {
            btn.classList.remove('playing');
        });
        return;
    }
    
    // Show loading state
    let originalHTML = '';
    if (button) {
        originalHTML = button.innerHTML;
        button.innerHTML = '<span class="tts-loading">⏳</span> جاري التحميل...';
        button.disabled = true;
        button.classList.add('loading');
    }
    
    try {
        const response = await fetch('/service/tts/synthesize/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ text, voice })
        });
        
        const data = await response.json();
        
        if (data.success) {
            // Create and play audio
            currentAudio = new Audio(data.audio_url);
            
            currentAudio.onplay = () => {
                isPlaying = true;
                if (button) {
                    button.innerHTML = '⏹️ إيقاف';
                    button.classList.remove('loading');
                    button.classList.add('playing');
                    button.disabled = false;
                }
            };
            
            currentAudio.onended = () => {
                isPlaying = false;
                if (button) {
                    button.innerHTML = originalHTML;
                    button.classList.remove('playing');
                }
            };
            
            currentAudio.onerror = () => {
                console.error('Audio playback error');
                isPlaying = false;
                if (button) {
                    button.innerHTML = originalHTML;
                    button.classList.remove('loading', 'playing');
                    button.disabled = false;
                }
            };
            
            await currentAudio.play();
            
        } else {
            throw new Error(data.error || 'فشل في إنشاء الصوت');
        }
        
    } catch (error) {
        console.error('TTS Error:', error);
        alert('حدث خطأ في القراءة الصوتية: ' + error.message);
        
        if (button) {
            button.innerHTML = originalHTML;
            button.classList.remove('loading', 'playing');
            button.disabled = false;
        }
    }
}

/**
 * Play TTS for glossary term
 * 
 * @param {number} termId - Glossary term ID
 * @param {string} type - 'term', 'definition', or 'full'
 * @param {string} voice - 'male' or 'female' (optional)
 */
async function playGlossaryTTS(termId, type = 'full', voice = null) {
    voice = voice || getSelectedVoice();
    const button = event?.target?.closest('.tts-btn');
    
    // Stop current audio if playing
    if (currentAudio && isPlaying) {
        currentAudio.pause();
        currentAudio = null;
        isPlaying = false;
        document.querySelectorAll('.tts-btn.playing').forEach(btn => {
            btn.classList.remove('playing');
        });
        return;
    }
    
    // Show loading
    let originalHTML = '';
    if (button) {
        originalHTML = button.innerHTML;
        button.innerHTML = '<span class="tts-loading">⏳</span> جاري التحميل...';
        button.disabled = true;
        button.classList.add('loading');
    }
    
    try {
        const formData = new FormData();
        formData.append('type', type);
        formData.append('voice', voice);
        
        const response = await fetch(`/service/glossary/${termId}/tts/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentAudio = new Audio(data.audio_url);
            
            currentAudio.onplay = () => {
                isPlaying = true;
                if (button) {
                    button.innerHTML = '⏹️ إيقاف';
                    button.classList.remove('loading');
                    button.classList.add('playing');
                    button.disabled = false;
                }
            };
            
            currentAudio.onended = () => {
                isPlaying = false;
                if (button) {
                    button.innerHTML = originalHTML;
                    button.classList.remove('playing');
                }
            };
            
            await currentAudio.play();
            
            // Update play count display if exists
            const countEl = document.querySelector('.tts-play-count .count');
            if (countEl && data.play_count) {
                countEl.textContent = data.play_count;
            }
            
        } else {
            throw new Error(data.error || 'فشل في إنشاء الصوت');
        }
        
    } catch (error) {
        console.error('Glossary TTS Error:', error);
        alert('حدث خطأ: ' + error.message);
        
        if (button) {
            button.innerHTML = originalHTML;
            button.classList.remove('loading', 'playing');
            button.disabled = false;
        }
    }
}

/**
 * Play TTS for inquiry answer
 * 
 * @param {number} inquiryId - Inquiry ID
 * @param {string} voice - 'male' or 'female' (optional)
 */
async function playInquiryTTS(inquiryId, voice = null) {
    voice = voice || getSelectedVoice();
    const button = event?.target?.closest('.tts-btn');
    
    // Stop current audio if playing
    if (currentAudio && isPlaying) {
        currentAudio.pause();
        currentAudio = null;
        isPlaying = false;
        document.querySelectorAll('.tts-btn.playing').forEach(btn => {
            btn.classList.remove('playing');
        });
        return;
    }
    
    let originalHTML = '';
    if (button) {
        originalHTML = button.innerHTML;
        button.innerHTML = '<span class="tts-loading">⏳</span> جاري التحميل...';
        button.disabled = true;
        button.classList.add('loading');
    }
    
    try {
        const formData = new FormData();
        formData.append('voice', voice);
        
        const response = await fetch(`/service/inquiry/${inquiryId}/tts/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCSRFToken()
            },
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentAudio = new Audio(data.audio_url);
            
            currentAudio.onplay = () => {
                isPlaying = true;
                if (button) {
                    button.innerHTML = '⏹️ إيقاف';
                    button.classList.remove('loading');
                    button.classList.add('playing');
                    button.disabled = false;
                }
            };
            
            currentAudio.onended = () => {
                isPlaying = false;
                if (button) {
                    button.innerHTML = originalHTML;
                    button.classList.remove('playing');
                }
            };
            
            await currentAudio.play();
            
        } else {
            throw new Error(data.error || 'فشل في إنشاء الصوت');
        }
        
    } catch (error) {
        console.error('Inquiry TTS Error:', error);
        alert('حدث خطأ: ' + error.message);
        
        if (button) {
            button.innerHTML = originalHTML;
            button.classList.remove('loading', 'playing');
            button.disabled = false;
        }
    }
}

/**
 * Stop current audio playback
 */
function stopTTS() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
        isPlaying = false;
        
        // Reset all playing buttons
        document.querySelectorAll('.tts-btn.playing').forEach(btn => {
            btn.classList.remove('playing');
        });
    }
}

/**
 * Initialize TTS buttons with data attributes
 */
function initTTSButtons() {
    // Auto-attach to buttons with data-tts-text attribute
    document.querySelectorAll('[data-tts-text]').forEach(button => {
        if (!button.hasAttribute('data-tts-initialized')) {
            button.addEventListener('click', function(e) {
                e.preventDefault();
                const text = this.dataset.ttsText;
                const voice = this.dataset.ttsVoice || getSelectedVoice();
                playTTS(text, voice, this);
            });
            button.setAttribute('data-tts-initialized', 'true');
        }
    });
    
    // Voice selector highlight
    document.querySelectorAll('.voice-option input[type="radio"]').forEach(radio => {
        radio.addEventListener('change', function() {
            document.querySelectorAll('.voice-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            this.closest('.voice-option').classList.add('selected');
        });
    });
}

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTTSButtons);
} else {
    initTTSButtons();
}

// Re-initialize on dynamic content load (for AJAX-loaded content)
if (typeof MutationObserver !== 'undefined') {
    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.addedNodes.length) {
                initTTSButtons();
            }
        });
    });
    
    document.addEventListener('DOMContentLoaded', () => {
        observer.observe(document.body, { childList: true, subtree: true });
    });
}

async function playGlossaryTTSFromUrl(button, mode='full') {
    const url = button.getAttribute('data-tts-url');
    const voice = getSelectedVoice ? getSelectedVoice() : 'female';

    if (!url) {
        alert('مسار TTS غير موجود.');
        return;
    }

    try {
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken(),
            },
            body: JSON.stringify({ mode, voice }),
        });

        const raw = await response.text();

        if (!response.ok) {
            console.error("TTS HTTP Error:", response.status, raw);
            alert("خطأ في السيرفر.");
            return;
        }

        const data = JSON.parse(raw);

        if (!data.success || !data.audio_url) {
            console.error("Bad response:", data);
            alert("تعذر توليد الصوت.");
            return;
        }

        const audio = new Audio(data.audio_url);
        await audio.play();

    } catch (err) {
        console.error("Glossary TTS Error:", err);
        alert("حدث خطأ أثناء تشغيل الصوت.");
    }
}
