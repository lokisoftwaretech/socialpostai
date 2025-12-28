"""
AI News Selector - OpenAI kullanarak en kritik haberi seçer.
"""

import os
from openai import OpenAI
from typing import List, Dict, Optional
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SELECTION_PROMPT = """Sen deneyimli bir haber editörüsün. Polonya'da yaşayan Türk göçmenler için en önemli haberi seçmelisin.

Aşağıdaki haberleri analiz et ve aralarından EN KRİTİK olanı seç. Seçim kriterlerim:

1. **Öncelik Sırası (Yukarıdan aşağıya):**
   - Ülke genelini etkileyen politik/ekonomik kararlar
   - Göçmenleri/mültecileri doğrudan etkileyen haberler
   - Yasal düzenlemeler ve vize/oturum izni değişiklikleri
   - Ekonomik haberler (enflasyon, asgari ücret, vergi)
   - Güvenlik ve kamu sağlığı haberleri
   - Sosyal olaylar

2. **Eleme Kriterleri:**
   - Spor haberleri → DÜŞÜK öncelik
   - Magazin/eğlence haberleri → DÜŞÜK öncelik
   - Yerel/bölgesel olaylar (ülke genelini etkilemiyorsa) → DÜŞÜK öncelik

3. **Seçim Kriterleri:**
   - Ciddiyet derecesi en yüksek olan
   - En geniş kitleyi etkileyen
   - Aciliyet içeren (yeni yürürlüğe giren yasalar, yaklaşan son tarihler)

HABERLERİ ANALİZ ET:
{news_list}

YANIT FORMATI (Sadece JSON döndür):
{{
    "selected_index": <seçilen haberin index numarası (0'dan başlar)>,
    "reason": "<neden bu haberi seçtiğinin kısa açıklaması>",
    "importance_score": <1-10 arası önem puanı>
}}
"""


def create_news_list_text(news_items: List[Dict]) -> str:
    """Haber listesini prompt için formatlar."""
    news_text = ""
    for i, item in enumerate(news_items):
        content = item.get('content') or item.get('description', '')
        # İçeriği kısalt
        if len(content) > 500:
            content = content[:500] + "..."
        
        news_text += f"""
---
[{i}] BAŞLIK: {item.get('title', 'Başlık yok')}
TARİH: {item.get('published', 'Tarih yok')}
KAYNAK: {item.get('source', 'Kaynak yok')}
KATEGORİ: {item.get('category', 'Kategori yok')}
İÇERİK: {content}
---
"""
    return news_text


def select_most_important_news(news_items: List[Dict]) -> Optional[Dict]:
    """OpenAI ile en kritik haberi seçer."""
    if not news_items:
        print("Haber listesi boş!")
        return None
    
    if len(news_items) == 1:
        print("Tek haber var, direkt seçildi.")
        return news_items[0]
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    news_list_text = create_news_list_text(news_items)
    prompt = SELECTION_PROMPT.format(news_list=news_list_text)
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen bir haber editörüsün. Sadece JSON formatında yanıt ver."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # JSON parse
        # Markdown code block varsa temizle
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        result = json.loads(result_text)
        
        selected_index = result.get("selected_index", 0)
        print(f"AI Seçimi: [{selected_index}] - {result.get('reason')}")
        print(f"Önem Puanı: {result.get('importance_score')}/10")
        
        if 0 <= selected_index < len(news_items):
            return news_items[selected_index]
        else:
            print(f"Geçersiz index: {selected_index}, ilk haber seçildi.")
            return news_items[0]
            
    except json.JSONDecodeError as e:
        print(f"JSON parse hatası: {e}")
        print(f"Ham yanıt: {result_text}")
        return news_items[0]
    except Exception as e:
        print(f"OpenAI API hatası: {e}")
        return news_items[0]


if __name__ == "__main__":
    # Test
    from rss_parser import get_poland_news_all
    
    news = get_poland_news_all()
    if news:
        selected = select_most_important_news(news[:10])  # İlk 10 haberi gönder
        if selected:
            print(f"\nSeçilen haber: {selected['title']}")
