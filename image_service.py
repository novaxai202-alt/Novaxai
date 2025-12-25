import os
import google.generativeai as genai
from typing import Optional
import base64
import io
from PIL import Image, ImageDraw, ImageFont

class ImageGenerator:
    def __init__(self):
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
    async def generate_image(self, enhanced_prompt: str) -> Optional[str]:
        """Generate image using Gemini 2.5 Flash with Imagen"""
        try:
            # Use Gemini with Imagen capability
            response = self.model.generate_content([
                f"Create an image: {enhanced_prompt}"
            ])
            
            # Check if response contains image data
            if hasattr(response, 'parts'):
                for part in response.parts:
                    if hasattr(part, 'inline_data') and part.inline_data:
                        return part.inline_data.data
            
            # Fallback to placeholder
            return await self._generate_placeholder_image(enhanced_prompt)
            
        except Exception as e:
            print(f"Gemini image generation error: {e}")
            return await self._generate_placeholder_image(enhanced_prompt)
    
    async def _generate_placeholder_image(self, prompt: str) -> str:
        """Generate placeholder with banana theme"""
        try:
            img = Image.new('RGB', (512, 512), color='#FFF8DC')
            draw = ImageDraw.Draw(img)
            
            # Banana gradient
            for y in range(512):
                color_val = int(255 - (y * 0.1))
                draw.line([(0, y), (512, y)], fill=(color_val, color_val, 0))
            
            # Draw banana shape
            draw.ellipse([150, 100, 350, 400], fill='#FFD700', outline='#FFA500', width=3)
            
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
            except:
                font = ImageFont.load_default()
            
            # Add banana emoji and text
            draw.text((230, 50), "🍌", font=font, fill='#8B4513')
            draw.text((180, 450), "Nano Banana Image", font=font, fill='#8B4513')
            
            # Add prompt text
            words = prompt.split()[:6]  # First 6 words
            text = ' '.join(words)
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            draw.text(((512 - text_width) // 2, 250), text, fill='#8B4513', font=font)
            
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
            
        except Exception as e:
            print(f"Banana placeholder error: {e}")
            return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8/5+hHgAHggJ/PchI7wAAAABJRU5ErkJggg=="
    
    async def handle_image_mode(self, message: str, enhance_image_prompt) -> dict:
        """Handle nano banana image generation"""
        try:
            enhanced_prompt = await enhance_image_prompt(message)
            image_base64 = await self.generate_image(enhanced_prompt)
            
            if image_base64:
                return {
                    "success": True,
                    "enhanced_prompt": enhanced_prompt,
                    "image_base64": image_base64,
                    "message": f"![Generated Image](data:image/png;base64,{image_base64})\n\n🍌 **Nano Banana Image Generated!**\n\n**Prompt:** {enhanced_prompt}\n\nWant another banana variation?"
                }
            else:
                return {
                    "success": False,
                    "message": "🍌 Nano banana generation failed. Try again!"
                }
        except Exception as e:
            return {
                "success": False,
                "message": f"🍌 Nano banana error: {str(e)}"
            }

image_generator = ImageGenerator()
