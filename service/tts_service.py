"""
TTS Service - Text-to-Speech for Arabic
Uses edge-tts (Microsoft Azure Neural TTS) as the primary engine.
Falls back to gTTS, then browser Speech Synthesis if unavailable.

Voices:
  - Female: ar-SA-ZariyahNeural (Saudi Arabic female)
  - Male:   ar-SA-HamedNeural   (Saudi Arabic male)
"""

import asyncio
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


# Map friendly names to edge-tts voice IDs
EDGE_VOICES = {
    'female': 'ar-SA-ZariyahNeural',
    'male': 'ar-SA-HamedNeural',
}

# Speed rate strings for edge-tts SSML
EDGE_SPEED = {
    'slow': '-30%',
    'normal': '+0%',
    'fast': '+25%',
}


class TTSService:
    """Arabic Text-to-Speech service using edge-tts (Microsoft Neural TTS)."""

    MAX_TEXT_LENGTH = 2000

    def __init__(self):
        self.output_dir = getattr(
            settings, 'TTS_OUTPUT_DIR',
            os.path.join(settings.MEDIA_ROOT, 'tts_audio'),
        )
        os.makedirs(self.output_dir, exist_ok=True)

        # Detect available engines
        self._edge_available = False
        try:
            import edge_tts  # noqa: F401
            self._edge_available = True
        except ImportError:
            pass

        self._gtts_available = False
        if not self._edge_available:
            try:
                from gtts import gTTS  # noqa: F401
                self._gtts_available = True
            except ImportError:
                pass

    # --------------------------------------------------
    # Cache helpers
    # --------------------------------------------------

    def _cache_key(self, text, voice, speed):
        engine = 'edge' if self._edge_available else 'gtts'
        raw = f'{engine}:{text}:{voice}:{speed}'
        h = hashlib.md5(raw.encode()).hexdigest()[:16]
        return f'tts_{engine}_{voice}_{speed}_{h}.mp3'

    def _cache_path(self, text, voice, speed='normal'):
        return os.path.join(self.output_dir, self._cache_key(text, voice, speed))

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

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
            raise ValueError(
                f'النص طويل جداً (الحد الأقصى {self.MAX_TEXT_LENGTH} حرف)'
            )

        if voice not in ('male', 'female'):
            voice = 'female'
        if speed not in ('slow', 'normal', 'fast'):
            speed = 'normal'

        path = self._cache_path(text, voice, speed)

        if os.path.exists(path):
            return path

        # Try edge-tts first (AI neural voices)
        if self._edge_available:
            return self._synthesize_edge(text, voice, speed, path)

        # Fallback to gTTS
        if self._gtts_available:
            return self._synthesize_gtts(text, voice, speed, path)

        raise RuntimeError(
            'خدمة TTS غير متاحة. يرجى تثبيت edge-tts: pip install edge-tts'
        )

    def synthesize_to_bytes(self, text, voice='female', speed='normal'):
        """Synthesize and return raw audio bytes."""
        audio_path = self.synthesize(text, voice, speed)
        with open(audio_path, 'rb') as f:
            return f.read()

    def get_available_voices(self):
        """Return list of available voice options."""
        voices = [
            {
                'id': 'female',
                'name': 'زارية - صوت أنثوي',
                'lang': 'ar-SA',
                'engine': 'edge-tts' if self._edge_available else 'gtts',
            },
            {
                'id': 'male',
                'name': 'حامد - صوت ذكوري',
                'lang': 'ar-SA',
                'engine': 'edge-tts' if self._edge_available else 'gtts',
            },
        ]
        return voices

    def get_engine_info(self):
        """Return info about which TTS engine is active."""
        if self._edge_available:
            return {
                'engine': 'edge-tts',
                'label': 'Microsoft Azure Neural TTS',
                'voices': {
                    'female': EDGE_VOICES['female'],
                    'male': EDGE_VOICES['male'],
                },
            }
        if self._gtts_available:
            return {
                'engine': 'gtts',
                'label': 'Google Text-to-Speech',
                'voices': {'female': 'ar (com)', 'male': 'ar (co.uk)'},
            }
        return {'engine': None, 'label': 'غير متاح'}

    # --------------------------------------------------
    # edge-tts engine (primary)
    # --------------------------------------------------

    def _synthesize_edge(self, text, voice, speed, output_path):
        """Generate audio using Microsoft Edge Neural TTS."""
        import edge_tts

        voice_id = EDGE_VOICES.get(voice, EDGE_VOICES['female'])
        rate = EDGE_SPEED.get(speed, '+0%')

        async def _generate():
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice_id,
                rate=rate,
            )
            await communicate.save(output_path)

        # Run async in a new event loop (safe in sync Django views)
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    pool.submit(lambda: asyncio.run(_generate())).result()
            else:
                loop.run_until_complete(_generate())
        except RuntimeError:
            asyncio.run(_generate())

        return output_path

    # --------------------------------------------------
    # gTTS engine (fallback)
    # --------------------------------------------------

    def _synthesize_gtts(self, text, voice, speed, output_path):
        """Generate audio using Google Text-to-Speech (fallback)."""
        from gtts import gTTS

        slow = speed == 'slow'
        tld = 'com' if voice == 'female' else 'co.uk'

        tts = gTTS(text=text, lang='ar', tld=tld, slow=slow)
        tts.save(output_path)
        return output_path

    # --------------------------------------------------
    # Cache management
    # --------------------------------------------------

    def clear_cache(self):
        """Remove all cached audio files."""
        count = 0
        for f in Path(self.output_dir).glob('tts_*.mp3'):
            f.unlink(missing_ok=True)
            count += 1
        return count
