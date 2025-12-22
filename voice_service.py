"""NovaX AI Voice Service - Deployment-safe version"""

import base64
from typing import Dict, Any
from gtts import gTTS
from io import BytesIO

class VoiceService:
    def __init__(self):
        self.tts_languages = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'ja': 'Japanese'
        }
    
    async def text_to_speech(self, text: str, language: str = 'en', voice_speed: float = 1.0) -> Dict[str, Any]:
        try:
            tts = gTTS(text=text, lang=language, slow=(voice_speed < 0.8))
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode('utf-8')
            
            return {
                'success': True,
                'audio_data': audio_base64,
                'format': 'mp3',
                'language': language
            }
        except Exception as e:
            return {'success': False, 'error': str(e), 'audio_data': None}
    
    def get_supported_languages(self) -> Dict[str, str]:
        return self.tts_languages

voice_service = VoiceService()

def get_voice_service() -> VoiceService:
    return voice_service
