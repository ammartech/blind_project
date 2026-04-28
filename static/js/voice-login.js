/* ============================================================
   تسجيل الدخول الصوتي - منصة إبان
   Voice Login for Iban platform
   يسمح للمستخدم من ذوي الإعاقة البصرية بتسجيل الدخول صوتياً.
   ============================================================ */
(function() {
  'use strict';

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SpeechRecognition) return;

  function speak(text, onend) {
    if (!('speechSynthesis' in window)) { if (onend) onend(); return; }
    try { speechSynthesis.cancel(); } catch (e) {}
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'ar-SA';
    u.rate = 0.95;
    const voices = speechSynthesis.getVoices();
    const ar = voices.find(v => v.lang && v.lang.startsWith('ar'));
    if (ar) u.voice = ar;
    if (onend) u.onend = onend;
    speechSynthesis.speak(u);
  }

  function norm(s) {
    return (s || '')
      .replace(/[ًٌٍَُِّْـ]/g, '')
      .replace(/[إأآا]/g, 'ا')
      .replace(/ى/g, 'ي')
      .replace(/ة/g, 'ه')
      .replace(/\s+/g, '')
      .trim()
      .toLowerCase();
  }

  function matches(text, keywords) {
    const n = norm(text);
    return keywords.some(k => n.includes(norm(k)));
  }

  // تحويل الأرقام العربية المنطوقة إلى أرقام
  const NUMBERS = {
    'صفر': '0', 'واحد': '1', 'اثنان': '2', 'اثنين': '2', 'ثلاثة': '3', 'ثلاثه': '3',
    'اربعة': '4', 'اربعه': '4', 'خمسة': '5', 'خمسه': '5', 'ستة': '6', 'سته': '6',
    'سبعة': '7', 'سبعه': '7', 'ثمانية': '8', 'ثمانيه': '8', 'تسعة': '9', 'تسعه': '9',
    'zero': '0', 'one': '1', 'two': '2', 'three': '3', 'four': '4',
    'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9'
  };

  function spokenToText(speech) {
    // إزالة المسافات وتحويل الأرقام المنطوقة
    let result = (speech || '').trim();
    Object.keys(NUMBERS).forEach(word => {
      const re = new RegExp('\\b' + word + '\\b', 'gi');
      result = result.replace(re, NUMBERS[word]);
    });
    // إزالة الفواصل والمسافات لاسم المستخدم/كلمة المرور
    return result.replace(/\s+/g, '').replace(/[،,.]/g, '');
  }

  document.addEventListener('DOMContentLoaded', () => {
    const usernameField = document.getElementById('id_username');
    const passwordField = document.getElementById('id_password');
    const form = document.querySelector('.auth-card form');
    if (!usernameField || !passwordField || !form) return;

    // إنشاء لوحة التحكم الصوتي
    const panel = document.createElement('div');
    panel.className = 'voice-login-panel';
    panel.innerHTML = `
      <div class="voice-login-header">
        <span class="voice-login-icon">🎙️</span>
        <strong>تسجيل الدخول الصوتي</strong>
      </div>
      <p class="voice-login-hint">
        اضغط على الزر أو قل "ابدأ" لبدء تسجيل الدخول صوتياً.
        سأطلب منك اسم المستخدم ثم كلمة المرور.
      </p>
      <div class="voice-login-controls">
        <button type="button" id="voice-login-start" class="btn primary w-full">
          🎤 ابدأ تسجيل الدخول الصوتي
        </button>
        <button type="button" id="voice-login-stop" class="btn outline w-full hidden">
          ⏹ إيقاف
        </button>
      </div>
      <div id="voice-login-status" class="voice-login-status" role="status" aria-live="polite"></div>
    `;
    form.parentNode.insertBefore(panel, form);

    const startBtn = document.getElementById('voice-login-start');
    const stopBtn = document.getElementById('voice-login-stop');
    const statusEl = document.getElementById('voice-login-status');

    function setStatus(text) { statusEl.textContent = text; }

    let recognition = null;
    let step = 'idle'; // idle | username | password | confirm
    let captured = { username: '', password: '' };

    function createRecognition() {
      const r = new SpeechRecognition();
      r.lang = 'ar-SA';
      r.continuous = false;
      r.interimResults = false;
      r.maxAlternatives = 1;
      return r;
    }

    function listenOnce(prompt, onResult) {
      speak(prompt, () => {
        try {
          recognition = createRecognition();
          recognition.onresult = (e) => {
            const transcript = e.results[0][0].transcript;
            onResult(transcript);
          };
          recognition.onerror = (e) => {
            setStatus('⚠ ' + (e.error === 'no-speech' ? 'لم أسمع شيئاً' : e.error));
            if (e.error === 'no-speech') {
              speak('لم أسمع شيئاً. حاول مرة أخرى.', () => listenOnce(prompt, onResult));
            } else {
              resetUI();
            }
          };
          recognition.onend = () => { recognition = null; };
          recognition.start();
        } catch (err) {
          setStatus('⚠ تعذر بدء الاستماع');
          resetUI();
        }
      });
    }

    function resetUI() {
      step = 'idle';
      startBtn.classList.remove('hidden');
      stopBtn.classList.add('hidden');
      startBtn.disabled = false;
    }

    function startVoiceLogin() {
      captured = { username: '', password: '' };
      step = 'username';
      startBtn.classList.add('hidden');
      stopBtn.classList.remove('hidden');
      setStatus('🎙️ جاري الاستماع...');

      listenOnce(
        'مرحباً بك في منصة إبان. من فضلك قل اسم المستخدم.',
        (text) => {
          const username = spokenToText(text);
          if (matches(text, ['الغاء', 'توقف', 'cancel', 'stop'])) {
            speak('تم إلغاء تسجيل الدخول');
            resetUI();
            return;
          }
          captured.username = username;
          usernameField.value = username;
          setStatus('✅ اسم المستخدم: ' + username);

          step = 'password';
          listenOnce(
            'سمعت اسم المستخدم: ' + username + '. الآن قل كلمة المرور.',
            (pwText) => {
              const password = spokenToText(pwText);
              if (matches(pwText, ['الغاء', 'توقف', 'cancel', 'stop'])) {
                speak('تم إلغاء تسجيل الدخول');
                resetUI();
                return;
              }
              captured.password = password;
              passwordField.value = password;
              setStatus('🔐 تم استلام كلمة المرور.');

              step = 'confirm';
              listenOnce(
                'هل تريد تسجيل الدخول الآن؟ قل نعم للتأكيد، أو لا للإلغاء.',
                (confirmText) => {
                  if (matches(confirmText, ['نعم', 'اكد', 'تاكيد', 'دخول', 'سجل', 'yes', 'ok'])) {
                    speak('جاري تسجيل الدخول', () => {
                      setStatus('⏳ جاري تسجيل الدخول...');
                      form.submit();
                    });
                  } else {
                    speak('تم الإلغاء. يمكنك المحاولة مرة أخرى.');
                    usernameField.value = '';
                    passwordField.value = '';
                    setStatus('❌ تم الإلغاء');
                    resetUI();
                  }
                }
              );
            }
          );
        }
      );
    }

    function stopVoiceLogin() {
      if (recognition) {
        try { recognition.stop(); } catch (e) {}
        recognition = null;
      }
      try { speechSynthesis.cancel(); } catch (e) {}
      speak('تم إيقاف تسجيل الدخول الصوتي');
      setStatus('⏹ تم الإيقاف');
      resetUI();
    }

    startBtn.addEventListener('click', startVoiceLogin);
    stopBtn.addEventListener('click', stopVoiceLogin);

    // الترحيب التلقائي عند فتح صفحة تسجيل الدخول
    setTimeout(() => {
      const announced = sessionStorage.getItem('iban_login_announced');
      if (!announced) {
        sessionStorage.setItem('iban_login_announced', '1');
        speak(
          'أهلاً بك في صفحة تسجيل الدخول لمنصة إبان. ' +
          'اضغط على زر "ابدأ تسجيل الدخول الصوتي" لتسجيل الدخول بصوتك.'
        );
      }
    }, 1200);
  });
})();
