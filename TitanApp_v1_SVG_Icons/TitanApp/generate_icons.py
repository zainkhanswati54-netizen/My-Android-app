import os
from PIL import Image

def make_icon(size):
    # Load the Titan Studio logo
    src_path = os.path.join(os.path.dirname(__file__), 'TitanApp/assets/icons/logo.png')
    if os.path.exists(src_path):
        img = Image.open(src_path).convert('RGBA').resize((size, size), Image.LANCZOS)
        # Convert to RGB for PNG saving
        bg = Image.new('RGB', (size, size), (13, 17, 23))
        bg.paste(img, mask=img.split()[3])
        return bg
    # Fallback
    img = Image.new('RGB', (size, size), (13, 17, 23))
    return img

sizes = {
    'mipmap-mdpi': 48,
    'mipmap-hdpi': 72,
    'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144,
    'mipmap-xxxhdpi': 192,
}

base = 'TitanApp/android/app/src/main/res'
os.makedirs('TitanApp/assets/icons', exist_ok=True)

for folder, size in sizes.items():
    os.makedirs(f'{base}/{folder}', exist_ok=True)
    make_icon(size).save(f'{base}/{folder}/ic_launcher.png', 'PNG')
    print(f'OK: {folder}/ic_launcher.png ({size}x{size})')

make_icon(512).save('TitanApp/assets/icons/app_logo.png', 'PNG')
print('OK: assets/icons/app_logo.png')
