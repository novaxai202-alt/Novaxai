"""
NovaX AI Voice Service
Handles speech-to-text and text-to-speech functionality
"""

import os
import asyncio
import tempfile
from typing import Optional, Dict, Any
import speech_recognition as sr
from gtts import gTTS
import pygame
from io import BytesIO
import base64

class VoiceService:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Initialize pygame mixer for audio playback
        pygame.mixer.init()
        
        # Supported languages for TTS
        self.tts_languages = {
            'en': 'English',
            'es': 'Spanish', 
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'ru': 'Russian',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese'
        }
    
    async def speech_to_text(self, audio_data: bytes, language: str = 'en-US') -> Dict[str, Any]:
        """Convert speech audio to text"""
        try:
            # Save audio data to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Load audio file
            with sr.AudioFile(temp_file_path) as source:
                audio = self.recognizer.record(source)
            
            # Perform speech recognition
            try:
                text = self.recognizer.recognize_google(audio, language=language)
                confidence = 0.9  # Google API doesn't return confidence, estimate high
                
                return {
                    'success': True,
                    'text': text,
                    'confidence': confidence,
                    'language': language
                }
            except sr.UnknownValueError:
                return {
                    'success': False,
                    'error': 'Could not understand the audio',
                    'text': '',
                    'confidence': 0.0
                }
            except sr.RequestError as e:
                return {
                    'success': False,
                    'error': f'Speech recognition service error: {str(e)}',
                    'text': '',
                    'confidence': 0.0
                }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Audio processing error: {str(e)}',
                'text': '',
                'confidence': 0.0
            }
        finally:
            # Clean up temporary file
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass
    
    async def text_to_speech(self, text: str, language: str = 'en', voice_speed: float = 1.0) -> Dict[str, Any]:
        """Convert text to speech audio"""
        try:
            # Create TTS object
            tts = gTTS(text=text, lang=language, slow=(voice_speed < 0.8))
            
            # Save to BytesIO buffer
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            
            # Convert to base64 for transmission
            audio_base64 = base64.b64encode(audio_buffer.getvalue()).decode('utf-8')
            
            return {
                'success': True,
                'audio_data': audio_base64,
                'format': 'mp3',
                'language': language,
                'text_length': len(text),
                'estimated_duration': len(text) * 0.1  # Rough estimate
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Text-to-speech error: {str(e)}',
                'audio_data': None
            }
    
    async def live_speech_recognition(self, duration: int = 5, language: str = 'en-US') -> Dict[str, Any]:
        """Perform live speech recognition from microphone"""
        try:
            # Adjust for ambient noise
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            print(f"Listening for {duration} seconds...")
            
            # Listen for audio
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=duration, phrase_time_limit=duration)
            
            # Recognize speech
            try:
                text = self.recognizer.recognize_google(audio, language=language)
                return {
                    'success': True,
                    'text': text,
                    'confidence': 0.9,
                    'language': language,
                    'duration': duration
                }
            except sr.UnknownValueError:
                return {
                    'success': False,
                    'error': 'No speech detected or could not understand',
                    'text': '',
                    'confidence': 0.0
                }
            except sr.RequestError as e:
                return {
                    'success': False,
                    'error': f'Speech service error: {str(e)}',
                    'text': '',
                    'confidence': 0.0
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Microphone error: {str(e)}',
                'text': '',
                'confidence': 0.0
            }
    
    def get_supported_languages(self) -> Dict[str, str]:
        """Get list of supported TTS languages"""
        return self.tts_languages
    
    async def play_audio(self, audio_base64: str) -> Dict[str, Any]:
        """Play audio from base64 data"""
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(audio_base64)
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_file_path = temp_file.name
            
            # Play audio using pygame
            pygame.mixer.music.load(temp_file_path)
            pygame.mixer.music.play()
            
            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.1)
            
            return {
                'success': True,
                'message': 'Audio played successfully'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Audio playback error: {str(e)}'
            }
        finally:
            # Clean up temporary file
            if 'temp_file_path' in locals():
                try:
                    os.unlink(temp_file_path)
                except:
                    pass

# Global voice service instance
voice_service = VoiceService()

def get_voice_service() -> VoiceService:
    """Get the global voice service instance"""
    return voice_service
