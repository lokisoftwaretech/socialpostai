"""
Main Orchestrator - Tüm modülleri koordine eder.
GitHub Actions tarafından çalıştırılır.
"""

import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rss_parser import get_poland_news_today, get_poland_news_all
from ai_selector import select_most_important_news
from ai_summarizer import summarize_news
from image_search import find_news_image, use_default_image
from image_generator import generate_instagram_post
from instagram_poster import post_to_instagram


def run_automation():
    """Ana otomasyon fonksiyonu."""
    print("=" * 60)
    print(f"🚀 Social Automation Başlatılıyor - {datetime.now()}")
    print("=" * 60)
    
    # 1. RSS Feed'den Polonya haberlerini çek
    print("\n📰 [1/6] RSS Feed okunuyor...")
    news = get_poland_news_today()
    
    # Bugün haber yoksa son haberleri al
    if not news:
        print("⚠️ Bugün haber yok, son Polonya haberlerinden seçim yapılacak...")
        news = get_poland_news_all()
    
    if not news:
        print("❌ Hiç haber bulunamadı! Otomasyon sonlandırılıyor.")
        return False
    
    print(f"✅ {len(news)} haber bulundu.")
    
    # 2. En kritik haberi seç
    print("\n🎯 [2/6] AI ile en kritik haber seçiliyor...")
    selected_news = select_most_important_news(news[:15])  # İlk 15 haberi gönder
    
    if not selected_news:
        print("❌ Haber seçilemedi! Otomasyon sonlandırılıyor.")
        return False
    
    print(f"✅ Seçilen haber: {selected_news['title'][:50]}...")
    
    # 3. Haberi özetle (3 satır)
    print("\n✍️ [3/6] Haber özetleniyor...")
    summary = summarize_news(selected_news)
    
    if not summary:
        print("❌ Özet oluşturulamadı! Otomasyon sonlandırılıyor.")
        return False
    
    print(f"✅ Özet oluşturuldu:\n{summary['full_text']}")
    
    # 4. Haber için görsel bul
    print("\n🖼️ [4/6] Haber görseli aranıyor...")
    news_image_path = "output/news_image.jpg"
    os.makedirs("output", exist_ok=True)
    
    image_path = find_news_image(
        summary.get('keywords', []),
        selected_news['title'],
        news_image_path
    )
    
    if not image_path:
        print("⚠️ Görsel bulunamadı, varsayılan görsel kullanılıyor...")
        image_path = use_default_image(news_image_path)
    
    if not image_path:
        print("❌ Görsel yüklenemedi! Otomasyon sonlandırılıyor.")
        return False
    
    print(f"✅ Görsel hazır: {image_path}")
    
    # 5. Instagram görseli oluştur
    print("\n🎨 [5/6] Instagram görseli oluşturuluyor...")
    output_path = "output/instagram_post.png"
    
    post_image = generate_instagram_post(
        summary['full_text'],
        image_path,
        output_path
    )
    
    if not post_image:
        print("❌ Görsel oluşturulamadı! Otomasyon sonlandırılıyor.")
        return False
    
    print(f"✅ Instagram görseli oluşturuldu: {post_image}")
    
    # 6. Instagram'a paylaş
    print("\n📱 [6/6] Instagram'a paylaşılıyor...")
    
    # Instagram credentials kontrolü
    if not os.getenv("INSTAGRAM_ACCESS_TOKEN") or not os.getenv("INSTAGRAM_ACCOUNT_ID"):
        print("⚠️ Instagram credentials eksik! Paylaşım atlanıyor.")
        print(f"📁 Görsel kaydedildi: {post_image}")
        print("\n" + "=" * 60)
        print("✅ Otomasyon tamamlandı (Instagram paylaşımı hariç)")
        print("=" * 60)
        return True
    
    post_id = post_to_instagram(post_image)
    
    if post_id:
        print(f"✅ Paylaşım başarılı! Post ID: {post_id}")
    else:
        print("❌ Paylaşım başarısız!")
        return False
    
    print("\n" + "=" * 60)
    print("✅ Otomasyon başarıyla tamamlandı!")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    success = run_automation()
    sys.exit(0 if success else 1)
