/* ============================================================
   نظام التنقل الصوتي العالمي - منصة إيبان
   Global Voice Navigation System for Iban platform
   يسمح للمستخدم من ذوي الإعاقة البصرية بتصفح الموقع كاملاً
   باستخدام الأوامر الصوتية فقط دون الحاجة لاستخدام اليد.
   ============================================================ */
(function() {
  'use strict';

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  const HAS_SR = !!SpeechRecognition;
  if (!HAS_SR) {
    console.warn('[VoiceNav] المتصفح لا يدعم التعرف على الصوت. سيظهر الزر مع رسالة توجيهية.');
  }

  const URLS = (window.IBAN_URLS || {});
  const IS_AUTH = !!window.IBAN_AUTH;

  function go(url) {
    if (!url) return;
    window.location.href = url;
  }

  function norm(s) {
    return (s || '')
      .replace(/[ًٌٍَُِّْـ]/g, '')
      .replace(/[إأآا]/g, 'ا')
      .replace(/ى/g, 'ي')
      .replace(/ة/g, 'ه')
      .replace(/\s+/g, ' ')
      .trim()
      .toLowerCase();
  }

  function matches(text, keywords) {
    const n = norm(text);
    return keywords.some(k => n.includes(norm(k)));
  }

  const COMMANDS = [
    {
      keywords: ['الرئيسية', 'الصفحه الرئيسيه', 'الرئيسيه', 'home', 'البيت', 'الرئيسة'],
      action: () => go(URLS.home),
      announce: 'الانتقال إلى الصفحة الرئيسية'
    },
    {
      keywords: ['الخدمات', 'صفحة الخدمات', 'services', 'خدمات'],
      action: () => go(URLS.services),
      announce: 'الانتقال إلى صفحة الخدمات'
    },
    {
      keywords: ['المصطلحات', 'قاموس المصطلحات', 'القاموس', 'المعجم', 'glossary'],
      action: () => go(URLS.glossary),
      announce: 'الانتقال إلى قاموس المصطلحات'
    },
    {
      keywords: ['من نحن', 'عن الموقع', 'عن المنصة', 'about'],
      action: () => go(URLS.about),
      announce: 'الانتقال إلى صفحة من نحن'
    },
    {
      keywords: ['تواصل', 'اتصل بنا', 'تواصل معنا', 'بيانات التواصل', 'contact'],
      action: () => go(URLS.contact),
      announce: 'الانتقال إلى صفحة التواصل'
    },
    {
      keywords: ['تسجيل الدخول', 'الدخول', 'دخول', 'login', 'سجل دخول'],
      action: () => go(URLS.login),
      condition: () => !IS_AUTH,
      announce: 'الانتقال إلى صفحة تسجيل الدخول'
    },
    {
      keywords: ['تسجيل جديد', 'انشاء حساب', 'حساب جديد', 'تسجيل', 'register', 'sign up'],
      action: () => go(URLS.register),
      condition: () => !IS_AUTH,
      announce: 'الانتقال إلى صفحة إنشاء حساب جديد'
    },
    {
      keywords: ['لوحة التحكم', 'اللوحه', 'حسابي', 'dashboard'],
      action: () => go(URLS.dashboard),
      condition: () => IS_AUTH,
      announce: 'الانتقال إلى لوحة التحكم'
    },
    {
      keywords: ['استفسار جديد', 'سؤال جديد', 'اطرح سؤال', 'اسال', 'اسئل', 'new inquiry'],
      action: () => go(URLS.inquiry_new),
      condition: () => IS_AUTH,
      announce: 'الانتقال إلى صفحة استفسار جديد'
    },
    {
      keywords: ['الملف الشخصي', 'حسابي الشخصي', 'بياناتي', 'profile'],
      action: () => go(URLS.profile),
      condition: () => IS_AUTH,
      announce: 'الانتقال إلى الملف الشخصي'
    },
    {
      keywords: ['تسجيل الخروج', 'خروج', 'اخرج', 'logout'],
      action: () => {
        const f = document.createElement('form');
        f.method = 'POST';
        f.action = URLS.logout;
        const t = document.createElement('input');
        t.type = 'hidden';
        t.name = 'csrfmiddlewaretoken';
        t.value = getCSRF();
        f.appendChild(t);
        document.body.appendChild(f);
        f.submit();
      },
      condition: () => IS_AUTH,
      announce: 'تسجيل الخروج'
    },
    {
      keywords: ['اقرا الصفحه', 'اقرأ الصفحة', 'قراءة الصفحة', 'اقرا', 'read page'],
      action: () => {
        const btn = document.getElementById('a11y-read-page');
        if (btn) btn.click();
      },
      announce: 'بدء قراءة محتوى الصفحة'
    },
    {
      keywords: ['ايقاف القراءه', 'ايقاف', 'توقف', 'قف', 'stop'],
      action: () => {
        const stop = document.getElementById('a11y-stop');
        if (stop && !stop.disabled) stop.click();
        if ('speechSynthesis' in window) speechSynthesis.cancel();
      },
      announce: 'تم إيقاف القراءة'
    },
    {
      keywords: ['ساعدني', 'المساعده', 'الاوامر', 'مساعده', 'help'],
      action: () => speakHelp(),
      announce: ''
    }
  ];

  function getCSRF() {
    for (let c of document.cookie.split(';')) {
      c = c.trim();
      if (c.startsWith('csrftoken=')) return decodeURIComponent(c.substring(10));
    }
    return '';
  }

  function speak(text) {
    if (!text || !('speechSynthesis' in window)) return;
    try { speechSynthesis.cancel(); } catch (e) {}
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'ar-SA';
    u.rate = 0.95;
    const voices = speechSynthesis.getVoices();
    const ar = voices.find(v => v.lang && v.lang.startsWith('ar'));
    if (ar) u.voice = ar;
    speechSynthesis.speak(u);
  }

  function speakHelp() {
    const helpText = [
      'الأوامر الصوتية المتاحة:',
      'قل الرئيسية للذهاب إلى الصفحة الرئيسية.',
      'قل الخدمات لعرض الخدمات.',
      'قل المصطلحات لفتح قاموس المصطلحات.',
      'قل من نحن أو تواصل لمعرفة المزيد.',
      IS_AUTH
        ? 'قل لوحة التحكم أو استفسار جديد أو الملف الشخصي أو خروج.'
        : 'قل تسجيل الدخول أو حساب جديد.',
      'قل اقرأ الصفحة لتشغيل القراءة الصوتية.',
      'قل توقف لإيقاف الاستماع.'
    ].join(' ');
    speak(helpText);
  }

  // ==== UI ====
  const fab = document.createElement('button');
  fab.id = 'voice-nav-fab';
  fab.className = 'voice-nav-fab';
  fab.type = 'button';
  fab.setAttribute('aria-label', 'تشغيل الأوامر الصوتية');
  fab.title = HAS_SR
    ? 'الأوامر الصوتية - اضغط أو استخدم Alt+V'
    : 'الأوامر الصوتية غير متاحة في هذا المتصفح - استخدم Chrome أو Edge';
  fab.innerHTML = '🎙️';

  const status = document.createElement('div');
  status.id = 'voice-nav-status';
  status.className = 'voice-nav-status hidden';
  status.setAttribute('role', 'status');
  status.setAttribute('aria-live', 'polite');
  status.innerHTML = '<span class="voice-nav-pulse"></span><span id="voice-nav-status-text">جاهز</span>';

  function injectUI() {
    if (!document.body) return false;
    if (!document.getElementById('voice-nav-fab')) {
      document.body.appendChild(fab);
      document.body.appendChild(status);
      fab.addEventListener('click', toggleListening);
    }
    return true;
  }

  // حقن واجهة المستخدم في أقرب وقت ممكن: مباشرةً إذا كان body جاهزاً، وإلا انتظر DOMContentLoaded
  if (!injectUI()) {
    document.addEventListener('DOMContentLoaded', injectUI);
  }

  let recognition = null;
  let listening = false;
  let manuallyStopped = false;

  function setStatus(text, autoHide) {
    const el = document.getElementById('voice-nav-status-text');
    if (el) el.textContent = text;
    status.classList.remove('hidden');
    if (autoHide) {
      setTimeout(() => {
        if (!listening) status.classList.add('hidden');
      }, 4000);
    }
  }

  function startListening() {
    if (listening) return;

    if (!HAS_SR) {
      setStatus('⚠ هذا المتصفح لا يدعم الأوامر الصوتية — يرجى استخدام Chrome أو Edge على Android/Windows', true);
      speak('عذراً، متصفحك الحالي لا يدعم الأوامر الصوتية. يرجى استخدام Chrome أو Edge.');
      return;
    }

    manuallyStopped = false;

    recognition = new SpeechRecognition();
    recognition.lang = 'ar-SA';
    recognition.continuous = true;
    recognition.interimResults = true;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      listening = true;
      fab.classList.add('listening');
      fab.setAttribute('aria-label', 'إيقاف الأوامر الصوتية');
      setStatus('🔴 يستمع... قل أمراً مثل: الرئيسية، تواصل، ساعدني');
      speak('أنا أستمع');
    };

    recognition.onresult = (event) => {
      for (let i = event.resultIndex; i < event.results.length; i++) {
        if (!event.results[i].isFinal) {
          const interim = event.results[i][0].transcript;
          setStatus('🔴 ' + interim);
          continue;
        }
        const transcript = event.results[i][0].transcript;
        handleCommand(transcript);
      }
    };

    recognition.onerror = (e) => {
      if (e.error === 'no-speech') return;
      if (e.error === 'not-allowed') {
        setStatus('⚠ لم يتم السماح باستخدام الميكروفون', true);
        speak('يرجى السماح باستخدام الميكروفون من إعدادات المتصفح');
        stopListening();
      } else if (e.error === 'aborted') {
        // expected when manually stopped
      } else {
        setStatus('⚠ خطأ: ' + e.error, true);
      }
    };

    recognition.onend = () => {
      if (listening && !manuallyStopped) {
        try { recognition.start(); } catch (e) { stopListening(); }
      } else {
        listening = false;
        fab.classList.remove('listening');
        fab.setAttribute('aria-label', 'تشغيل الأوامر الصوتية');
      }
    };

    try {
      recognition.start();
    } catch (e) {
      setStatus('⚠ تعذر بدء الاستماع', true);
    }
  }

  function stopListening() {
    manuallyStopped = true;
    listening = false;
    if (recognition) {
      try { recognition.stop(); } catch (e) {}
      recognition = null;
    }
    fab.classList.remove('listening');
    fab.setAttribute('aria-label', 'تشغيل الأوامر الصوتية');
    setStatus('⏹ تم إيقاف الاستماع', true);
  }

  function toggleListening() {
    if (listening) stopListening();
    else startListening();
  }

  function handleCommand(text) {
    const cleaned = (text || '').trim();
    if (!cleaned) return;
    setStatus('🎯 سمعت: ' + cleaned);

    for (const cmd of COMMANDS) {
      if (cmd.condition && !cmd.condition()) continue;
      if (matches(cleaned, cmd.keywords)) {
        if (cmd.announce) {
          speak(cmd.announce);
          setStatus('✅ ' + cmd.announce);
        }
        try {
          setTimeout(() => cmd.action(), 600);
        } catch (e) {
          console.error('[VoiceNav] command error', e);
        }
        return;
      }
    }

    setStatus('❓ لم أفهم. قل "ساعدني" لمعرفة الأوامر');
  }

  // اختصار لوحة المفاتيح: Alt+V لتشغيل/إيقاف الاستماع
  document.addEventListener('keydown', (e) => {
    if (e.altKey && (e.key === 'v' || e.key === 'V')) {
      e.preventDefault();
      toggleListening();
    }
  });

  // الإعلان عن الصفحة عند تحميلها (مرة واحدة فقط لكل جلسة)
  document.addEventListener('DOMContentLoaded', () => {
    const announced = sessionStorage.getItem('iban_voice_announced');
    if (!announced) {
      sessionStorage.setItem('iban_voice_announced', '1');
      setTimeout(() => {
        const title = document.title.split('|')[0].trim() || 'صفحة';
        if (HAS_SR) {
          speak(
            'مرحباً بك في منصة إيبان. أنت الآن في ' + title + '. ' +
            'اضغط على زر الميكروفون أسفل الشاشة، أو اضغط Alt و V، ثم قل أمراً صوتياً للتنقل. قل ساعدني لمعرفة الأوامر.'
          );
        } else {
          speak(
            'مرحباً بك في منصة إيبان. أنت الآن في ' + title + '. ' +
            'متصفحك الحالي لا يدعم الأوامر الصوتية، يرجى استخدام Chrome أو Edge للحصول على التجربة الكاملة.'
          );
        }
      }, 800);
    }
  });

  window.IbanVoiceNav = { start: startListening, stop: stopListening, toggle: toggleListening, speak };
})();
