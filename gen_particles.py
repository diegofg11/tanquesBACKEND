from PIL import Image, ImageDraw
import random
import os

def create_particles():
    print("Generating particles...")
    width = 1024
    height = 1024
    # Create transparent image (0,0,0,0) is fully transparent
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Draw small bright stars/dots
    for _ in range(200):
        x = random.randint(0, width)
        y = random.randint(0, height)
        r = random.randint(1, 4)
        # High opacity for core
        alpha = random.randint(150, 255)
        draw.ellipse((x-r, y-r, x+r, y+r), fill=(255, 255, 255, alpha))

    # Removed large soft glows as they looked like strange lights
    print("Skipping large glows...")

    output_path = "Magic_Particles_Alpha.png"
    img.save(output_path, "PNG")
    print(f"Saved {output_path}")

if __name__ == "__main__":
    try:
        create_particles()
    except ImportError:
        print("Pillow not found. Please install it with: pip install Pillow")
