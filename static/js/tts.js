/**
 * Arabic TTS Player - مشغل القراءة الصوتية
 * static/js/tts.js
 *
 * Supports:
 *   - AI engine (edge-tts / gTTS backend)
 *   - Browser engine (Web Speech API fallback)
 *   - Voice selection (male / female)
 *   - Speed control (slow / normal / fast)
 */

// ──── Global State ────
let currentAudio = null;
let isPlaying = false;
let lastAudioUrl = null;

// ──── Helpers ────

function getCSRFToken() {
    for (let c of document.cookie.split(';')) {
        c = c.trim();
        if (c.startsWith('csrftoken=')) return decodeURIComponent(c.substring(10));
    }
    return '';
}

function getSelectedVoice() {
    const el = document.querySelector('input[name="tts-voice"]:checked');
    return el ? el.value : 'female';
}

function getSelectedSpeed() {
    const radio = document.querySelector('input[name="tts-speed"]:checked');
    if (radio) return radio.value;
    const sel = document.querySelector('select[name="tts-speed"]');
    if (sel) return sel.value;
    return 'normal';
}

function getSelectedEngine() {
    const el = document.querySelector('input[name="tts-engine"]:checked');
    return el ? el.value : 'ai';
}

// ──── Stop ────

function stopTTS() {
    if (currentAudio) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        currentAudio = null;
    }
    if ('speechSynthesis' in window) speechSynthesis.cancel();
    isPlaying = false;
    document.querySelectorAll('.tts-btn.playing').forEach(b => b.classList.remove('playing'));
}

// ──── Browser TTS (Web Speech API) ────

function playBrowserTTS(text, voice, speed) {
    if (!('speechSynthesis' in window)) {
        alert('المتصفح لا يدعم القراءة الصوتية. يرجى استخدام متصفح حديث.');
        return;
    }
    speechSynthesis.cancel();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = 'ar';

    const speedMap = { slow: 0.7, normal: 1.0, fast: 1.4 };
    utterance.rate = speedMap[speed] || 1.0;

    // Try to pick an Arabic voice
    const voices = speechSynthesis.getVoices();
    const arVoice = voices.find(v => v.lang.startsWith('ar'));
    if (arVoice) utterance.voice = arVoice;

    utterance.onend = () => {
        isPlaying = false;
        document.querySelectorAll('.tts-btn.playing').forEach(b => b.classList.remove('playing'));
    };

    speechSynthesis.speak(utterance);
    isPlaying = true;
}

// ──── AI TTS (Backend) ────

async function playAITTS(text, voice, speed, button) {
    const origHTML = button ? button.innerHTML : '';
    if (button) {
        button.innerHTML = '⏳ جاري التحميل...';
        button.disabled = true;
        button.classList.add('loading');
    }

    try {
        const res = await fetch('/service/tts/synthesize/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ text, voice, speed }),
        });
        const data = await res.json();

        if (!data.success || !data.audio_url) throw new Error(data.error || 'فشل');

        lastAudioUrl = data.audio_url;
        currentAudio = new Audio(data.audio_url);

        // Apply client-side playback rate tweak for speeds
        const rateMap = { slow: 0.85, normal: 1.0, fast: 1.2 };
        currentAudio.playbackRate = rateMap[speed] || 1.0;

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
                button.innerHTML = origHTML;
                button.classList.remove('playing');
            }
        };
        currentAudio.onerror = () => {
            isPlaying = false;
            if (button) {
                button.innerHTML = origHTML;
                button.classList.remove('loading', 'playing');
                button.disabled = false;
            }
            // Auto-fallback to browser
            playBrowserTTS(text, voice, speed);
        };

        await currentAudio.play();
    } catch (err) {
        console.error('AI TTS Error:', err);
        if (button) {
            button.innerHTML = origHTML;
            button.classList.remove('loading', 'playing');
            button.disabled = false;
        }
        playBrowserTTS(text, voice, speed);
    }
}

// ──── Main entry: play TTS text ────

async function playTTS(text, voice, button) {
    voice = voice || getSelectedVoice();
    if (!button && typeof event !== 'undefined' && event?.target) {
        button = event.target.closest('.tts-btn');
    }

    if (currentAudio && isPlaying) { stopTTS(); return; }

    const speed = getSelectedSpeed();
    const engine = getSelectedEngine();

    if (engine === 'browser') {
        playBrowserTTS(text, voice, speed);
    } else {
        await playAITTS(text, voice, speed, button);
    }
}

// ──── Glossary TTS ────

async function playGlossaryTTS(termId, type, voice) {
    voice = voice || getSelectedVoice();
    const button = (typeof event !== 'undefined') ? event?.target?.closest('.tts-btn') : null;

    if (currentAudio && isPlaying) { stopTTS(); return; }

    const speed = getSelectedSpeed();
    const engine = getSelectedEngine();

    const origHTML = button ? button.innerHTML : '';
    if (button) {
        button.innerHTML = '⏳ جاري التحميل...';
        button.disabled = true;
        button.classList.add('loading');
    }

    try {
        if (engine === 'browser') {
            // For browser engine, we need to get the text from the page
            // The button should have data attributes or we fetch from API
            if (button) {
                button.innerHTML = origHTML;
                button.classList.remove('loading');
                button.disabled = false;
            }
            // Fetch the text from the glossary TTS endpoint, but play via browser
            const formData = new FormData();
            formData.append('type', type || 'full');
            formData.append('voice', voice);
            // We'll just use the page text directly if available
            const termEl = document.querySelector('.term-title');
            const defEl = document.querySelector('.definition-text');
            let text = '';
            if (type === 'term' && termEl) text = termEl.textContent.trim();
            else if (type === 'definition' && defEl) text = defEl.textContent.trim();
            else text = (termEl ? termEl.textContent.trim() : '') + '. ' + (defEl ? defEl.textContent.trim() : '');
            playBrowserTTS(text, voice, speed);
            return;
        }

        // AI engine: use backend
        const res = await fetch(`/service/glossary/${termId}/tts/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRFToken() },
            body: JSON.stringify({ type: type || 'full', mode: type || 'full', voice, speed }),
        });
        const data = await res.json();

        if (!data.success || !data.audio_url) throw new Error(data.error || 'فشل');

        lastAudioUrl = data.audio_url;
        currentAudio = new Audio(data.audio_url);

        const rateMap = { slow: 0.85, normal: 1.0, fast: 1.2 };
        currentAudio.playbackRate = rateMap[speed] || 1.0;

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
            if (button) { button.innerHTML = origHTML; button.classList.remove('playing'); }
        };
        currentAudio.onerror = () => {
            isPlaying = false;
            if (button) { button.innerHTML = origHTML; button.classList.remove('loading', 'playing'); button.disabled = false; }
        };

        await currentAudio.play();

        // Update play count display
        const countEl = document.getElementById('tts-play-count');
        if (countEl && data.play_count != null) countEl.textContent = data.play_count;

    } catch (err) {
        console.error('Glossary TTS Error:', err);
        if (button) {
            button.innerHTML = origHTML;
            button.classList.remove('loading', 'playing');
            button.disabled = false;
        }
    }
}

// ──── Inquiry TTS ────

async function playInquiryTTS(inquiryId, voice) {
    voice = voice || getSelectedVoice();
    const button = (typeof event !== 'undefined') ? event?.target?.closest('.tts-btn') : null;

    if (currentAudio && isPlaying) { stopTTS(); return; }

    const origHTML = button ? button.innerHTML : '';
    if (button) {
        button.innerHTML = '⏳ جاري التحميل...';
        button.disabled = true;
        button.classList.add('loading');
    }

    try {
        const formData = new FormData();
        formData.append('voice', voice);

        const res = await fetch(`/service/inquiry/${inquiryId}/tts/`, {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() },
            body: formData,
        });
        const data = await res.json();

        if (!data.success || !data.audio_url) throw new Error(data.error || 'فشل');

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
            if (button) { button.innerHTML = origHTML; button.classList.remove('playing'); }
        };

        await currentAudio.play();
    } catch (err) {
        console.error('Inquiry TTS Error:', err);
        if (button) {
            button.innerHTML = origHTML;
            button.classList.remove('loading', 'playing');
            button.disabled = false;
        }
    }
}

// ──── Utility ────

function downloadLastAudio() {
    if (!lastAudioUrl) { alert('لا يوجد ملف صوتي للتحميل.'); return; }
    const a = document.createElement('a');
    a.href = lastAudioUrl;
    a.download = 'tts_audio.mp3';
    document.body.appendChild(a);
    a.click();
    a.remove();
}

function repeatLastAudio() {
    if (!lastAudioUrl) { alert('لا يوجد ملف صوتي لإعادة تشغيله.'); return; }
    stopTTS();
    currentAudio = new Audio(lastAudioUrl);
    const speed = getSelectedSpeed();
    const rateMap = { slow: 0.85, normal: 1.0, fast: 1.2 };
    currentAudio.playbackRate = rateMap[speed] || 1.0;
    currentAudio.onplay = () => { isPlaying = true; };
    currentAudio.onended = () => { isPlaying = false; };
    currentAudio.play();
}

// ──── Auto-init ────

function initTTSButtons() {
    // Data-attribute buttons
    document.querySelectorAll('[data-tts-text]').forEach(btn => {
        if (btn.hasAttribute('data-tts-initialized')) return;
        btn.addEventListener('click', function(e) {
            e.preventDefault();
            playTTS(this.dataset.ttsText, this.dataset.ttsVoice || getSelectedVoice(), this);
        });
        btn.setAttribute('data-tts-initialized', 'true');
    });

    // Voice selector highlight sync
    document.querySelectorAll('.voice-option input[type="radio"]').forEach(r => {
        r.addEventListener('change', function() {
            document.querySelectorAll('.voice-option').forEach(o => o.classList.remove('selected'));
            this.closest('.voice-option')?.classList.add('selected');
        });
    });

    // Engine selector highlight sync
    document.querySelectorAll('.engine-option input[type="radio"]').forEach(r => {
        r.addEventListener('change', function() {
            document.querySelectorAll('.engine-option').forEach(o => o.classList.remove('selected'));
            this.closest('.engine-option')?.classList.add('selected');
        });
    });

    // Speed selector highlight sync
    document.querySelectorAll('.speed-option input[type="radio"]').forEach(r => {
        r.addEventListener('change', function() {
            document.querySelectorAll('.speed-option').forEach(o => o.classList.remove('selected'));
            this.closest('.speed-option')?.classList.add('selected');
        });
    });
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initTTSButtons);
} else {
    initTTSButtons();
}

if (typeof MutationObserver !== 'undefined') {
    document.addEventListener('DOMContentLoaded', () => {
        new MutationObserver(() => initTTSButtons())
            .observe(document.body, { childList: true, subtree: true });
    });
}
