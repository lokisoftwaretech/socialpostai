"""
Image Generator - 1080x1080 Instagram şablonu oluşturur.
Template'e göre: arka plan, bayrak, ikon, haber görseli ve metin.
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from typing import Optional, Tuple
import textwrap

# Sabit değerler (template'e göre)
CANVAS_SIZE = (1080, 1080)
BACKGROUND_PATH = "assets/background.png"
FLAG_PATH = "assets/flag.png"
ICON_PATH = "assets/ggicon.png"

# Font ayarları
FONT_PATH = "/System/Library/Fonts/Supplemental/Arial.ttf"  # macOS
FONT_PATH_LINUX = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux/GitHub Actions

# Pozisyonlar (template'e göre ayarlandı)
FLAG_POSITION = (1000, 30)  # Sağ üst köşe
FLAG_SIZE = (50, 50)  # Küçük bayrak

ICON_POSITION = (950, 950)  # Sağ alt köşe
ICON_SIZE = (100, 100)

NEWS_IMAGE_POSITION = (190, 140)  # Ortada
NEWS_IMAGE_SIZE = (700, 400)  # Yatay görsel
NEWS_IMAGE_RADIUS = 20  # Rounded corners

TEXT_POSITION = (60, 600)  # Alt kısım
TEXT_MAX_WIDTH = 960
TEXT_LINE_HEIGHT = 55

DIVIDER_Y = 860  # Ayırıcı çizgi
FOOTER_Y = 890  # Alt yazı


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Font yükler."""
    font_path = FONT_PATH if os.path.exists(FONT_PATH) else FONT_PATH_LINUX
    
    try:
        return ImageFont.truetype(font_path, size)
    except:
        return ImageFont.load_default()


def add_rounded_corners(image: Image.Image, radius: int) -> Image.Image:
    """Görsele yuvarlatılmış köşeler ekler."""
    # Mask oluştur
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    
    # RGBA'ya çevir ve mask uygula
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    output = Image.new('RGBA', image.size, (0, 0, 0, 0))
    output.paste(image, mask=mask)
    
    return output


def wrap_text(text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
    """Metni satırlara böler."""
    lines = []
    for line in text.split('\n'):
        words = line.split()
        current_line = ""
        
        for word in words:
            test_line = f"{current_line} {word}".strip()
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
    
    return lines


def generate_instagram_post(
    news_text: str,
    news_image_path: str,
    output_path: str = "output/post.png"
) -> Optional[str]:
    """Instagram postu oluşturur."""
    
    # Output klasörünü oluştur
    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else "output", exist_ok=True)
    
    # 1. Arka planı yükle
    try:
        background = Image.open(BACKGROUND_PATH).convert('RGBA')
        background = background.resize(CANVAS_SIZE, Image.Resampling.LANCZOS)
    except Exception as e:
        print(f"Arka plan yüklenemedi: {e}")
        # Fallback: koyu mavi gradient benzeri arka plan
        background = Image.new('RGBA', CANVAS_SIZE, (20, 25, 45, 255))
    
    canvas = background.copy()
    draw = ImageDraw.Draw(canvas)
    
    # 2. Bayrağı ekle (sağ üst)
    try:
        flag = Image.open(FLAG_PATH).convert('RGBA')
        flag = flag.resize(FLAG_SIZE, Image.Resampling.LANCZOS)
        canvas.paste(flag, FLAG_POSITION, flag)
    except Exception as e:
        print(f"Bayrak yüklenemedi: {e}")
    
    # 3. Haber görselini ekle (ortada, rounded)
    try:
        news_img = Image.open(news_image_path).convert('RGBA')
        
        # Aspect ratio koruyarak resize
        img_ratio = news_img.width / news_img.height
        target_ratio = NEWS_IMAGE_SIZE[0] / NEWS_IMAGE_SIZE[1]
        
        if img_ratio > target_ratio:
            # Görsel daha geniş, yüksekliğe göre ölçekle
            new_height = NEWS_IMAGE_SIZE[1]
            new_width = int(new_height * img_ratio)
        else:
            # Görsel daha uzun, genişliğe göre ölçekle
            new_width = NEWS_IMAGE_SIZE[0]
            new_height = int(new_width / img_ratio)
        
        news_img = news_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Ortadan crop
        left = (new_width - NEWS_IMAGE_SIZE[0]) // 2
        top = (new_height - NEWS_IMAGE_SIZE[1]) // 2
        news_img = news_img.crop((left, top, left + NEWS_IMAGE_SIZE[0], top + NEWS_IMAGE_SIZE[1]))
        
        # Rounded corners
        news_img = add_rounded_corners(news_img, NEWS_IMAGE_RADIUS)
        
        canvas.paste(news_img, NEWS_IMAGE_POSITION, news_img)
    except Exception as e:
        print(f"Haber görseli yüklenemedi: {e}")
        # Placeholder rectangle
        draw.rounded_rectangle(
            [NEWS_IMAGE_POSITION, (NEWS_IMAGE_POSITION[0] + NEWS_IMAGE_SIZE[0], NEWS_IMAGE_POSITION[1] + NEWS_IMAGE_SIZE[1])],
            radius=NEWS_IMAGE_RADIUS,
            fill=(50, 55, 75, 255)
        )
    
    # 4. Haber metnini ekle
    font = get_font(38)
    
    # Metni satırlara böl
    lines = wrap_text(news_text, font, TEXT_MAX_WIDTH)
    
    # Maksimum 3 satır
    lines = lines[:3]
    
    y = TEXT_POSITION[1]
    for line in lines:
        draw.text((TEXT_POSITION[0], y), line, font=font, fill=(255, 255, 255, 255))
        y += TEXT_LINE_HEIGHT
    
    # 5. Ayırıcı çizgi
    line_y = DIVIDER_Y
    draw.line([(60, line_y), (400, line_y)], fill=(255, 255, 255, 100), width=2)
    
    # 6. Alt yazı (sabit metin)
    footer_font = get_font(24)
    footer_text = "Daha fazlası için Google Play veya App Store'dan\nGurbetci SuperApp'i ücretsiz indir."
    
    footer_y = FOOTER_Y
    for line in footer_text.split('\n'):
        draw.text((60, footer_y), line, font=footer_font, fill=(180, 180, 180, 255))
        footer_y += 30
    
    # 7. İkonu ekle (sağ alt)
    try:
        icon = Image.open(ICON_PATH).convert('RGBA')
        icon = icon.resize(ICON_SIZE, Image.Resampling.LANCZOS)
        canvas.paste(icon, ICON_POSITION, icon)
    except Exception as e:
        print(f"İkon yüklenemedi: {e}")
    
    # 8. Kaydet
    canvas = canvas.convert('RGB')
    canvas.save(output_path, 'PNG', quality=95)
    
    print(f"Instagram postu oluşturuldu: {output_path}")
    return output_path


if __name__ == "__main__":
    # Test
    test_text = """Polonya ordusu, bir Rus keşif uçağı yakaladı.
Bu olayla ilgili acil bir açıklamanın, Noel günü öğle
saatlerinde yapılması bekleniyor"""
    
    # Test için dummy görsel oluştur
    test_img = Image.new('RGB', (800, 500), (100, 100, 150))
    test_img.save("test_news_image.jpg")
    
    result = generate_instagram_post(test_text, "test_news_image.jpg", "output/test_post.png")
    print(f"Sonuç: {result}")
