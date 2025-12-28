"""
AI News Summarizer - OpenAI kullanarak haberi kısa ve öz şekilde özetler.
"""

import os
from openai import OpenAI
from typing import Dict, Optional
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SUMMARY_PROMPT = """Sen deneyimli bir Türk haber yazarısın. Aşağıdaki haberi Türkçe olarak KISA VE ÖZ şekilde özetleyeceksin.

KRİTİK KURALLAR:

1. **UZUNLUK SINIRI:**
   - TOPLAM maksimum 180 karakter (boşluklar dahil)
   - Bu sınırı ASLA aşma
   - 2-3 cümle yeterli

2. **CÜMLE YAPISI:**
   - Her cümle MUTLAKA nokta ile bitmeli
   - Yarım kalan cümle YASAK
   - Cümle ortasında kesme YASAK

3. **İÇERİK:**
   - Ana olay + Kim + Ne zaman (mümkünse)
   - Gereksiz detayları atla
   - En önemli bilgiyi ver

4. **KORUNACAKLAR:**
   - Resmi makam isimleri (Başbakan Tusk, Cumhurbaşkanı vb.)
   - Kritik sayısal veriler
   - Zaman kipleri doğru olmalı

5. **DİL:**
   - Profesyonel haber dili
   - Aktif cümleler
   - Kısa ve net

HABER:
Başlık: {title}
İçerik: {content}
Kaynak: {source}

ÖNEMLİ: Özet 180 karakteri geçmemeli ve her cümle nokta ile bitmeli!

YANIT FORMATI (Sadece JSON döndür):
{{
    "summary": "<maksimum 180 karakter özet, nokta ile biten tam cümleler>",
    "keywords": ["<3-5 anahtar kelime>"]
}}
"""


def summarize_news(news_item: Dict) -> Optional[Dict]:
    """Haberi kısa ve öz şekilde özetler."""
    if not news_item:
        print("Haber boş!")
        return None
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    content = news_item.get('content') or news_item.get('description', '')
    
    prompt = SUMMARY_PROMPT.format(
        title=news_item.get('title', ''),
        content=content,
        source=news_item.get('source', '')
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen profesyonel bir haber yazarısın. Kısa, öz ve tam cümlelerle yaz. Sadece JSON formatında yanıt ver."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=300
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Markdown code block varsa temizle
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        result = json.loads(result_text)
        
        summary_text = result.get("summary", "")
        
        # Son kontrol: nokta ile bitmiyor mu?
        if summary_text and not summary_text.endswith('.'):
            # Son cümleyi bul ve kes
            last_period = summary_text.rfind('.')
            if last_period > 0:
                summary_text = summary_text[:last_period + 1]
        
        summary = {
            "full_text": summary_text,
            "keywords": result.get("keywords", [])
        }
        
        print("--- ÖZET ---")
        print(f"Metin ({len(summary_text)} karakter): {summary_text}")
        print(f"Anahtar kelimeler: {summary['keywords']}")
        
        return summary
        
    except json.JSONDecodeError as e:
        print(f"JSON parse hatası: {e}")
        print(f"Ham yanıt: {result_text}")
        return None
    except Exception as e:
        print(f"OpenAI API hatası: {e}")
        return None


if __name__ == "__main__":
    # Test
    test_news = {
        "title": "Polonya, yeni göçmenlik yasasını onayladı",
        "content": "Polonya parlamentosu, yeni göçmenlik yasasını bugün oybirliğiyle kabul etti. Yasa, 1 Ocak 2026'da yürürlüğe girecek ve tüm yabancı uyrukluları etkileyecek. Başbakan Donald Tusk, yasanın Avrupa Birliği standartlarına uygun olduğunu açıkladı.",
        "source": "PAP",
        "published": "28 Aralık 2025"
    }
    
    summary = summarize_news(test_news)
