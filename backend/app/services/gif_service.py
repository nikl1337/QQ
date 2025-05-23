import os
from PIL import Image, ImageDraw, ImageFont # Added ImageFont
import imageio
import secrets
from app.services.price_service import get_current_mock_prices # Import price service

# Define directories at the module level for clarity
# BASE_DIR should resolve to /app/backend
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) # Changed from '..' , '..'
UPLOADS_DIR = os.path.join(BASE_DIR, 'uploads')
GENERATED_GIFS_DIR = os.path.join(BASE_DIR, 'generated_gifs')

# Price Thresholds
BTC_HIGH_THRESHOLD = 36000
BTC_LOW_THRESHOLD = 34000
SOL_HIGH_THRESHOLD = 130
SOL_LOW_THRESHOLD = 110

def ensure_directories_exist():
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    os.makedirs(GENERATED_GIFS_DIR, exist_ok=True)

def get_font(size=20):
    """Attempts to load a font, falling back to a default if specific paths fail."""
    try:
        # Common path for DejaVu Sans on Linux systems
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except IOError:
        try:
            return ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size)
        except IOError:
            print("Specific font not found, loading default font. Text size might be small.")
            try:
                # For older Pillow versions, size might not be supported in load_default
                return ImageFont.load_default() 
            except TypeError: # Newer Pillow versions might support size here
                 return ImageFont.load_default(size=size) # Try with size
            except: # Catch all for font loading issues
                return ImageFont.load_default() # Final fallback


def create_gif_from_image(image_path, output_filename_no_ext, duration_seconds=5, fps=10):
    ensure_directories_exist()
    output_path = os.path.join(GENERATED_GIFS_DIR, f"{output_filename_no_ext}.gif")

    try:
        if not os.path.abspath(image_path).startswith(os.path.abspath(UPLOADS_DIR)):
            print(f"Error: Image path {image_path} is outside of the allowed uploads directory.")
            return None

        original_img = Image.open(image_path).convert("RGBA")
        orig_w, orig_h = original_img.size

        padding = 60 # Increased padding to make space for text
        canvas_w = orig_w + 2 * padding
        canvas_h = orig_h + 2 * padding
        
        paste_x = (canvas_w - orig_w) // 2
        paste_y = (canvas_h - orig_h) // 2

        # Fetch prices and determine sentiment
        prices = get_current_mock_prices()
        btc_price = prices.get('btc_usd', 0)
        sol_price = prices.get('sol_usd', 0)

        btc_is_high = btc_price > BTC_HIGH_THRESHOLD
        btc_is_low = btc_price < BTC_LOW_THRESHOLD
        sol_is_high = sol_price > SOL_HIGH_THRESHOLD
        sol_is_low = sol_price < SOL_LOW_THRESHOLD

        num_frames = duration_seconds * fps
        frames = []
        tile_size = 20
        font = get_font(size=18) # Load font once

        for i in range(num_frames):
            frame_image = Image.new('RGBA', (canvas_w, canvas_h))
            draw = ImageDraw.Draw(frame_image)

            # Generate Background Pattern influenced by price sentiment
            for x_coord in range(0, canvas_w, tile_size):
                for y_coord in range(0, canvas_h, tile_size):
                    r, g, b = secrets.randbelow(256), secrets.randbelow(256), secrets.randbelow(256) # Default random

                    # Alternate influence for variety, or could use tile position
                    if (x_coord // tile_size % 2 == 0) ^ (y_coord // tile_size % 2 == 0) : # BTC influence
                        if btc_is_high:
                            g = secrets.randbelow(106) + 150; r = secrets.randbelow(100); b = secrets.randbelow(100)
                        elif btc_is_low:
                            r = secrets.randbelow(106) + 150; g = secrets.randbelow(100); b = secrets.randbelow(100)
                    else: # SOL influence
                        if sol_is_high:
                            b = secrets.randbelow(106) + 150; r = secrets.randbelow(100); g = secrets.randbelow(100) # Blues/Purples
                        elif sol_is_low:
                            r = secrets.randbelow(106) + 150; g = secrets.randbelow(106) + 150; b = secrets.randbelow(50) # Yellows/Oranges
                    
                    draw.rectangle(
                        [x_coord, y_coord, x_coord + tile_size, y_coord + tile_size],
                        fill=(r, g, b)
                    )
            
            # Add Price Text Overlay
            btc_text = f"BTC: ${btc_price:.2f}"
            sol_text = f"SOL: ${sol_price:.2f}"
            
            # Simple text shadow by drawing text twice with offset
            shadow_offset = 2
            text_color = 'white'
            shadow_color = 'black'

            draw.text((padding + shadow_offset, 10 + shadow_offset), btc_text, font=font, fill=shadow_color)
            draw.text((padding, 10), btc_text, font=font, fill=text_color)
            
            draw.text((padding + shadow_offset, 35 + shadow_offset), sol_text, font=font, fill=shadow_color) # Adjusted y for second line
            draw.text((padding, 35), sol_text, font=font, fill=text_color) # Adjusted y

            # Composite Original Image
            frame_image.paste(original_img, (paste_x, paste_y), original_img) 
            frames.append(frame_image)

        frame_duration = 1.0 / fps 
        imageio.mimsave(output_path, frames, duration=frame_duration, loop=0)
        
        return output_path
    except FileNotFoundError:
        print(f"Error creating GIF: Input image not found at {image_path}")
        return None
    except Exception as e:
        print(f"Error creating GIF: {e}")
        return None

if __name__ == '__main__':
    ensure_directories_exist()
    dummy_image_path = os.path.join(UPLOADS_DIR, "test_image_prices.png")
    
    # --- Test with different price scenarios ---
    # To truly test, you'd mock get_current_mock_prices or temporarily change it.
    # For this example, we'll just run with the default mock prices.
    # You can manually change thresholds above or prices in price_service.py for testing.

    print(f"Current mock prices (from service): {get_current_mock_prices()}")
    print(f"BTC High: {BTC_HIGH_THRESHOLD}, BTC Low: {BTC_LOW_THRESHOLD}")
    print(f"SOL High: {SOL_HIGH_THRESHOLD}, SOL Low: {SOL_LOW_THRESHOLD}")

    try:
        img = Image.new('RGBA', (120, 90), color = (0, 0, 0, 0)) # Transparent base
        draw = ImageDraw.Draw(img)
        # Draw something distinct on the test image
        draw.ellipse([10,10, 110,80], fill=(255,255,0,200), outline=(0,0,0,255), width=3) # Yellow ellipse
        draw.text((30,40), "TEST", fill="black", font=get_font(15))
        img.save(dummy_image_path)
        print(f"Dummy image created at {dummy_image_path}")

        generated_gif_path = create_gif_from_image(dummy_image_path, "test_price_influenced_gif", duration_seconds=3, fps=5)
        if generated_gif_path:
            print(f"Price-influenced GIF generated successfully: {generated_gif_path}")
        else:
            print("Price-influenced GIF generation failed.")
    except Exception as e:
        print(f"Error in test script: {e}")
    finally:
        if os.path.exists(dummy_image_path):
            os.remove(dummy_image_path)
            print(f"Dummy image {dummy_image_path} removed.")
