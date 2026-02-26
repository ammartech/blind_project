"""
STT Service - Speech-to-Text for Arabic
Uses SpeechRecognition library with Google's free speech API.
Falls back gracefully if the library is not installed.
"""

import os
import tempfile

from django.conf import settings

_stt_instance = None


def get_stt_service():
    global _stt_instance
    if _stt_instance is None:
        _stt_instance = STTService()
    return _stt_instance


class STTService:
    """Arabic Speech-to-Text service."""

    SUPPORTED_LANGUAGES = {
        'ar': 'ar-SA',
        'ar-SA': 'ar-SA',
        'en': 'en-US',
        'en-US': 'en-US',
    }

    def __init__(self):
        self._sr_available = False
        try:
            import speech_recognition  # noqa: F401
            self._sr_available = True
        except ImportError:
            pass

    @property
    def is_available(self):
        return self._sr_available

    def transcribe_audio_file(self, audio_file, language='ar-SA'):
        """
        Transcribe an uploaded audio file to text.

        Args:
            audio_file: Django UploadedFile or file-like object (WAV format preferred)
            language: Language code (ar-SA, en-US)

        Returns:
            dict: {'success': bool, 'text': str} or {'success': bool, 'error': str}
        """
        if not self._sr_available:
            return {
                'success': False,
                'error': 'خدمة التعرف على الصوت غير متاحة. يرجى تثبيت: pip install SpeechRecognition'
            }

        import speech_recognition as sr

        lang = self.SUPPORTED_LANGUAGES.get(language, 'ar-SA')

        # Save uploaded file to a temp WAV
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_path) as source:
                recognizer.adjust_for_ambient_noise(source, duration=0.3)
                audio = recognizer.record(source)

            text = recognizer.recognize_google(audio, language=lang)
            return {'success': True, 'text': text}

        except sr.UnknownValueError:
            return {
                'success': False,
                'error': 'لم يتم التعرف على الكلام. حاول التحدث بوضوح أكثر.'
            }
        except sr.RequestError as e:
            return {
                'success': False,
                'error': f'خطأ في خدمة التعرف على الصوت: {e}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'خطأ في معالجة الملف الصوتي: {e}'
            }
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def transcribe_bytes(self, audio_bytes, language='ar-SA'):
        """Transcribe raw audio bytes (WAV format)."""
        if not self._sr_available:
            return {
                'success': False,
                'error': 'خدمة التعرف على الصوت غير متاحة'
            }

        import speech_recognition as sr

        lang = self.SUPPORTED_LANGUAGES.get(language, 'ar-SA')

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            recognizer = sr.Recognizer()
            with sr.AudioFile(tmp_path) as source:
                audio = recognizer.record(source)
            text = recognizer.recognize_google(audio, language=lang)
            return {'success': True, 'text': text}
        except sr.UnknownValueError:
            return {'success': False, 'error': 'لم يتم التعرف على الكلام'}
        except sr.RequestError as e:
            return {'success': False, 'error': str(e)}
        except Exception as e:
            return {'success': False, 'error': str(e)}
        finally:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass

    def get_status(self):
        """Return status info about the STT service."""
        return {
            'available': self._sr_available,
            'engine': 'Google Speech Recognition' if self._sr_available else None,
            'languages': list(self.SUPPORTED_LANGUAGES.keys()) if self._sr_available else [],
        }
