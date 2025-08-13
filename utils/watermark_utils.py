import os
import aiohttp
import asyncio
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
from database.watermark_db import watermark_db

async def download_image(url):
    """Download an image from a URL"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.read()
                return None
    except Exception as e:
        print(f"Error downloading image: {e}")
        return None

async def download_file_cover(client, file_id):
    """Download file cover from Telegram"""
    try:
        if not file_id:
            return None
        file_path = await client.download_media(file_id)
        if file_path:
            with open(file_path, "rb") as f:
                content = f.read()
            os.remove(file_path)  # Clean up the file
            return content
        return None
    except Exception as e:
        print(f"Error downloading file cover: {e}")
        return None

async def apply_watermark(image_data, client=None):
    """Apply watermark text and logo to an image"""
    try:
        # Get watermark settings
        watermark_text = await watermark_db.get_watermark_text()
        file_cover_id = await watermark_db.get_file_cover()
        
        # Open the image
        img = Image.open(BytesIO(image_data))
        
        # Convert to RGB if needed
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Create a drawing context
        draw = ImageDraw.Draw(img)
        width, height = img.size
        
        # Apply watermark text if available
        if watermark_text:
            # Try to load a nice font, fall back to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except IOError:
                font = ImageFont.load_default()
            
            # Calculate text size and position (bottom center)
            text_width = draw.textlength(watermark_text, font=font)
            text_position = ((width - text_width) // 2, height - 50)
            
            # Draw text with shadow for better visibility
            draw.text((text_position[0]+2, text_position[1]+2), watermark_text, font=font, fill="black")
            draw.text(text_position, watermark_text, font=font, fill="white")
        
        # Apply logo if available
        if file_cover_id and client:
            logo_data = await download_file_cover(client, file_cover_id)
            if logo_data:
                logo = Image.open(BytesIO(logo_data))
                
                # Resize logo to reasonable size (max 20% of image width)
                logo_max_width = int(width * 0.2)
                logo_ratio = min(logo_max_width / logo.width, logo_max_width / logo.height)
                logo_width = int(logo.width * logo_ratio)
                logo_height = int(logo.height * logo_ratio)
                logo = logo.resize((logo_width, logo_height), Image.LANCZOS)
                
                # Position logo at top-right corner with padding
                logo_position = (width - logo_width - 10, 10)
                
                # Create transparent background for logo
                if logo.mode == 'RGBA':
                    img.paste(logo, logo_position, logo)
                else:
                    img.paste(logo, logo_position)
        
        # Save the watermarked image
        output = BytesIO()
        img.save(output, format='JPEG', quality=95)
        output.seek(0)
        return output.getvalue()
    
    except Exception as e:
        print(f"Error applying watermark: {e}")
        return image_data  # Return original image if watermarking fails

async def append_username_to_filename(filename):
    """Append watermark username to filename"""
    try:
        watermark_username = await watermark_db.get_watermark_username()
        if not watermark_username:
            return filename
            
        # Split filename and extension
        name, ext = os.path.splitext(filename)
        
        # Check if username is already in the filename
        if watermark_username in name:
            return filename
            
        # Append username to filename
        return f"{name} {watermark_username}{ext}"
    except Exception as e:
        print(f"Error appending username to filename: {e}")
        return filename  # Return original filename if error occurs