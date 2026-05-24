import os
from PIL import Image, ImageDraw

def make_icon(size):
    img = Image.new('RGB', (size, size), (16, 185, 129))
    draw = ImageDraw.Draw(img)
    s = size
    draw.rectangle([s//4, s//4, s*3//4, s//4 + s//8], fill=(255, 255, 255))
    draw.rectangle([s*7//16, s//4, s*9//16, s*3//4], fill=(255, 255, 255))
    return img

sizes = {
    'mipmap-mdpi': 48,
    'mipmap-hdpi': 72,
    'mipmap-xhdpi': 96,
    'mipmap-xxhdpi': 144,
    'mipmap-xxxhdpi': 192,
}

base = 'titan_v2_fixed/android/app/src/main/res'
os.makedirs('titan_v2_fixed/assets/icons', exist_ok=True)

for folder, size in sizes.items():
    os.makedirs(f'{base}/{folder}', exist_ok=True)
    make_icon(size).save(f'{base}/{folder}/ic_launcher.png', 'PNG')
    print(f'OK: {folder}/ic_launcher.png ({size}x{size})')

make_icon(512).save('titan_v2_fixed/assets/icons/app_logo.png', 'PNG')
print('OK: assets/icons/app_logo.png')
