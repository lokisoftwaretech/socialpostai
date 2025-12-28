"""
Image Generator - 1080x1080 Instagram şablonu oluşturur.
Template'e göre: arka plan, bayrak, ikon, haber görseli ve metin.
SF Pro Medium font, -0.5 letter spacing.
Metin ayırıcı çizgiden hizalı (bottom-aligned).
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, List

# Sabit değerler (template'e göre)
CANVAS_SIZE = (1080, 1080)
BACKGROUND_PATH = "assets/background.png"
FLAG_PATH = "assets/flag.png"
ICON_PATH = "assets/ggicon.png"

# Font - repo'daki font dosyası (macOS SFNS kopyası)
FONT_PATH = "assets/fonts/SF-Pro.ttf"

# Fallback fonts
FALLBACK_FONTS = [
    "/System/Library/Fonts/SFNS.ttf",  # macOS SF NS
    "/System/Library/Fonts/SFNSDisplay.ttf",  # macOS SF NS Display
    "/System/Library/Fonts/Supplemental/Arial.ttf",  # macOS Arial
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",  # Linux
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Linux fallback
]

# Letter spacing
LETTER_SPACING = -0.5

# Pozisyonlar (template'e göre - referans görselden ölçüldü)
FLAG_POSITION = (1010, 40)
FLAG_SIZE = (45, 45)

ICON_POSITION = (940, 940)
ICON_SIZE = (110, 110)

NEWS_IMAGE_POSITION = (165, 100)
NEWS_IMAGE_SIZE = (750, 420)
NEWS_IMAGE_RADIUS = 16

# Text bottom-aligned - çizgiden yukarı doğru
DIVIDER_Y = 825
TEXT_BOTTOM_Y = DIVIDER_Y - 25  # Çizgiden 25px yukarıda bitecek
TEXT_LEFT_X = 55
TEXT_MAX_WIDTH = 970
TEXT_LINE_HEIGHT = 58
TEXT_FONT_SIZE = 36

DIVIDER_START = 55
DIVIDER_END = 350

FOOTER_Y = 855
FOOTER_FONT_SIZE = 22


def get_font(size: int) -> ImageFont.FreeTypeFont:
    """SF Pro Medium fontunu yükler, yoksa fallback kullanır."""
    # Önce repo'daki fontu dene
    if os.path.exists(FONT_PATH):
        try:
            font = ImageFont.truetype(FONT_PATH, size)
            print(f"✅ Font yüklendi: {FONT_PATH}")
            return font
        except Exception as e:
            print(f"⚠️ Repo fontu yüklenemedi: {e}")
    
    # Fallback fontları dene
    for font_path in FALLBACK_FONTS:
        if os.path.exists(font_path):
            try:
                font = ImageFont.truetype(font_path, size)
                print(f"✅ Fallback font yüklendi: {font_path}")
                return font
            except:
                continue
    
    print("⚠️ Hiçbir font bulunamadı, varsayılan kullanılıyor")
    return ImageFont.load_default()


def draw_text_with_spacing(draw: ImageDraw.Draw, pos: tuple, text: str, font: ImageFont.FreeTypeFont, 
                           fill: tuple, letter_spacing: float = LETTER_SPACING) -> float:
    """Letter spacing ile metin çizer. Satır genişliğini döndürür."""
    x, y = pos
    total_width = 0
    
    for char in text:
        draw.text((x, y), char, font=font, fill=fill)
        bbox = font.getbbox(char)
        char_width = bbox[2] - bbox[0]
        x += char_width + letter_spacing
        total_width += char_width + letter_spacing
    
    return total_width


def get_text_width_with_spacing(text: str, font: ImageFont.FreeTypeFont, letter_spacing: float = LETTER_SPACING) -> float:
    """Letter spacing ile metin genişliğini hesaplar."""
    total_width = 0
    for char in text:
        bbox = font.getbbox(char)
        char_width = bbox[2] - bbox[0]
        total_width += char_width + letter_spacing
    return total_width - letter_spacing if total_width > 0 else 0


def wrap_text_with_spacing(text: str, font: ImageFont.FreeTypeFont, max_width: float, 
                           letter_spacing: float = LETTER_SPACING) -> List[str]:
    """Letter spacing ile metni satırlara böler."""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip() if current_line else word
        width = get_text_width_with_spacing(test_line, font, letter_spacing)
        
        if width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines


def add_rounded_corners(image: Image.Image, radius: int) -> Image.Image:
    """Görsele yuvarlatılmış köşeler ekler."""
    mask = Image.new('L', image.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle([(0, 0), image.size], radius=radius, fill=255)
    
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    
    output = Image.new('RGBA', image.size, (0, 0, 0, 0))
    output.paste(image, mask=mask)
    
    return output


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
        
        img_ratio = news_img.width / news_img.height
        target_ratio = NEWS_IMAGE_SIZE[0] / NEWS_IMAGE_SIZE[1]
        
        if img_ratio > target_ratio:
            new_height = NEWS_IMAGE_SIZE[1]
            new_width = int(new_height * img_ratio)
        else:
            new_width = NEWS_IMAGE_SIZE[0]
            new_height = int(new_width / img_ratio)
        
        news_img = news_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        left = (new_width - NEWS_IMAGE_SIZE[0]) // 2
        top = (new_height - NEWS_IMAGE_SIZE[1]) // 2
        news_img = news_img.crop((left, top, left + NEWS_IMAGE_SIZE[0], top + NEWS_IMAGE_SIZE[1]))
        
        news_img = add_rounded_corners(news_img, NEWS_IMAGE_RADIUS)
        canvas.paste(news_img, NEWS_IMAGE_POSITION, news_img)
    except Exception as e:
        print(f"Haber görseli yüklenemedi: {e}")
        draw.rounded_rectangle(
            [NEWS_IMAGE_POSITION, (NEWS_IMAGE_POSITION[0] + NEWS_IMAGE_SIZE[0], NEWS_IMAGE_POSITION[1] + NEWS_IMAGE_SIZE[1])],
            radius=NEWS_IMAGE_RADIUS,
            fill=(50, 55, 75, 255)
        )
    
    # 4. Haber metnini ekle (SF Pro Medium, -0.5 letter spacing, BOTTOM-ALIGNED)
    font = get_font(TEXT_FONT_SIZE)
    
    # Metni satırlara böl
    lines = wrap_text_with_spacing(news_text, font, TEXT_MAX_WIDTH, LETTER_SPACING)
    
    # BOTTOM-ALIGNED: Çizgiden yukarı doğru hesapla
    total_text_height = len(lines) * TEXT_LINE_HEIGHT
    text_start_y = TEXT_BOTTOM_Y - total_text_height
    
    # Metni çiz (yukarıdan aşağı)
    y = text_start_y
    for line in lines:
        draw_text_with_spacing(draw, (TEXT_LEFT_X, y), line, font, (255, 255, 255, 255), LETTER_SPACING)
        y += TEXT_LINE_HEIGHT
    
    # 5. Ayırıcı çizgi
    draw.line([(DIVIDER_START, DIVIDER_Y), (DIVIDER_END, DIVIDER_Y)], fill=(255, 255, 255, 120), width=2)
    
    # 6. Alt yazı (sabit metin)
    footer_font = get_font(FOOTER_FONT_SIZE)
    footer_lines = [
        "Daha fazlası için Google Play veya App Store'dan",
        "Gurbetci SuperApp'i ücretsiz indir."
    ]
    
    footer_y = FOOTER_Y
    for line in footer_lines:
        draw_text_with_spacing(draw, (DIVIDER_START, footer_y), line, footer_font, (170, 170, 170, 255), LETTER_SPACING)
        footer_y += 28
    
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
    
    print(f"✅ Instagram postu oluşturuldu: {output_path}")
    return output_path


if __name__ == "__main__":
    # Test
    test_text = "Başbakan Tusk, Ukrayna için güvenlik garantileri çağrısı yaptı. Avrupa liderleriyle video konferans gerçekleştirdi."
    
    test_img = Image.new('RGB', (800, 500), (100, 100, 150))
    test_img.save("test_news_image.jpg")
    
    result = generate_instagram_post(test_text, "test_news_image.jpg", "output/test_post.png")
    print(f"Sonuç: {result}")
