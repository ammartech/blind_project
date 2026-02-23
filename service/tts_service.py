"""
TTS Service - Text-to-Speech for Arabic
Uses gTTS (Google Text-to-Speech) as the primary engine.
Falls back gracefully when unavailable.
"""

import hashlib
import os
from pathlib import Path

from django.conf import settings

_tts_instance = None


def get_tts_service():
    global _tts_instance
    if _tts_instance is None:
        _tts_instance = TTSService()
    return _tts_instance


def get_audio_url(audio_path):
    """Convert an absolute audio file path to a media URL."""
    rel_path = os.path.relpath(audio_path, settings.MEDIA_ROOT)
    return f'{settings.MEDIA_URL}{rel_path}'


class TTSService:
    """Arabic Text-to-Speech service using gTTS."""

    MAX_TEXT_LENGTH = 2000

    def __init__(self):
        self.output_dir = getattr(
            settings, 'TTS_OUTPUT_DIR',
            os.path.join(settings.MEDIA_ROOT, 'tts_audio'),
        )
        os.makedirs(self.output_dir, exist_ok=True)

        self._gtts_available = False
        try:
            from gtts import gTTS  # noqa: F401
            self._gtts_available = True
        except ImportError:
            pass

    def _cache_key(self, text, voice, speed):
        """Generate a deterministic filename from text + voice + speed."""
        raw = f'{text}:{voice}:{speed}'
        h = hashlib.md5(raw.encode()).hexdigest()[:16]
        return f'tts_{voice}_{speed}_{h}.mp3'

    def _cache_path(self, text, voice, speed='normal'):
        return os.path.join(self.output_dir, self._cache_key(text, voice, speed))

    def synthesize(self, text, voice='female', speed='normal'):
        """
        Synthesize Arabic text to speech.

        Args:
            text: Arabic text to speak.
            voice: 'male' or 'female'.
            speed: 'slow', 'normal', or 'fast'.

        Returns:
            Absolute path to the generated MP3 file.
        """
        text = text.strip()
        if not text:
            raise ValueError('النص مطلوب')

        if len(text) > self.MAX_TEXT_LENGTH:
            raise ValueError(f'النص طويل جداً (الحد الأقصى {self.MAX_TEXT_LENGTH} حرف)')

        path = self._cache_path(text, voice, speed)

        if os.path.exists(path):
            return path

        if self._gtts_available:
            return self._synthesize_gtts(text, voice, speed, path)

        raise RuntimeError(
            'خدمة TTS غير متاحة. يرجى تثبيت gTTS: pip install gTTS'
        )

    def synthesize_to_bytes(self, text, voice='female', speed='normal'):
        """Synthesize and return raw audio bytes."""
        audio_path = self.synthesize(text, voice, speed)
        with open(audio_path, 'rb') as f:
            return f.read()

    def get_available_voices(self):
        """Return list of available voice options."""
        return [
            {'id': 'female', 'name': 'صوت أنثوي', 'lang': 'ar'},
            {'id': 'male', 'name': 'صوت ذكوري', 'lang': 'ar'},
        ]

    def _synthesize_gtts(self, text, voice, speed, output_path):
        """Generate audio using Google Text-to-Speech."""
        from gtts import gTTS

        slow = speed == 'slow'

        # Use different TLD for slight voice variation
        tld = 'com' if voice == 'female' else 'co.uk'

        tts = gTTS(text=text, lang='ar', tld=tld, slow=slow)
        tts.save(output_path)
        return output_path

    def clear_cache(self):
        """Remove all cached audio files."""
        count = 0
        for f in Path(self.output_dir).glob('tts_*.mp3'):
            f.unlink(missing_ok=True)
            count += 1
        return count
