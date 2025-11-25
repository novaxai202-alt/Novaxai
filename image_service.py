import os
import base64
import requests
from typing import Optional

class ImageGenerator:
    def __init__(self):
        pass
        
    async def generate_image(self, prompt: str) -> Optional[str]:
        """Generate image using multiple services"""
        try:
            print(f"Generating image with prompt: {prompt}")
            
            # Clean prompt
            clean_prompt = prompt.replace("generate image of", "").replace("create image of", "").strip()
            
            # Try Pollinations first with very short timeout
            try:
                import urllib.parse
                encoded_prompt = urllib.parse.quote(clean_prompt)
                url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=512&height=512"
                
                response = requests.get(url, timeout=8)
                
                if response.status_code == 200:
                    image_data = base64.b64encode(response.content).decode()
                    print("Image generated successfully with Pollinations AI")
                    return image_data
            except:
                print("Pollinations timeout, trying fallback...")
            
            # Fallback to DummyJSON placeholder
            try:
                fallback_url = f"https://dummyjson.com/image/512x512/008080/ffffff?text={clean_prompt[:15]}"
                response = requests.get(fallback_url, timeout=5)
                
                if response.status_code == 200:
                    image_data = base64.b64encode(response.content).decode()
                    print("Generated fallback image")
                    return image_data
            except:
                pass
            
            print("All image generation services failed")
            return None
                
        except Exception as e:
            print(f"Image generation error: {e}")
            return None

image_generator = ImageGenerator()