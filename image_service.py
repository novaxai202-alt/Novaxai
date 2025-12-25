import os
import google.generativeai as genai
from typing import Optional

class ImageGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    async def generate_image(self, enhanced_prompt: str) -> Optional[str]:
        """Generate image using Gemini 2.5 Flash with enhanced prompt"""
        try:
            response = self.model.generate_content(f"Create a detailed image of: {enhanced_prompt}")
            return response.text
        except Exception as e:
            print(f"Gemini image generation error: {e}")
            return None
    
    async def handle_image_mode(self, message: str, enhance_image_prompt) -> dict:
        """Handle image generation mode"""
        try:
            enhanced_prompt = await enhance_image_prompt(message)
            generated_image = await self.generate_image(enhanced_prompt)
            
            if generated_image:
                return {
                    "success": True,
                    "enhanced_prompt": enhanced_prompt,
                    "generated_image": generated_image,
                    "message": f"🎨 **Image Generated Successfully!**\n\n**Enhanced Prompt:** {enhanced_prompt}\n\n**Generated Description:**\n{generated_image}\n\nWant a different style or variation?"
                }
            else:
                return {
                    "success": False,
                    "message": "🎨 Image generation failed. Please try again."
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"🎨 Image generation error: {str(e)}"
            }

image_generator = ImageGenerator()
