"""
AI News Summarizer - OpenAI kullanarak haberi 3 satırda özetler.
"""

import os
from openai import OpenAI
from typing import Dict, Optional
import json

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

SUMMARY_PROMPT = """Sen deneyimli bir haber yazarısın. Aşağıdaki haberi Türkçe olarak TAM OLARAK 3 SATIRDA özetleyeceksin.

ÖNEMLİ KURALLAR:

1. **YAPI (Her satır ayrı bir paragraf):**
   - 1. Satır: HÜKÜM-GİRİŞ → Ana olay, ne oldu? (Kim ne yaptı?)
   - 2. Satır: DETAY-BAĞLAM → 5N1K bilgileri (Nerede, ne zaman, nasıl, neden)
   - 3. Satır: SONUÇ-ETKİ → Bu olayın sonucu veya etkisi ne olacak?

2. **KORUNACAK BİLGİLER:**
   - Sayısal veriler (tarihler, yüzdeler, para miktarları, istatistikler)
   - Resmi makam isimleri (Başbakan, Bakan, Cumhurbaşkanı ismi)
   - Kurum/kuruluş isimleri
   - Yer isimleri

3. **DİL VE ÜSLUP:**
   - Profesyonel haber dili kullan
   - Zaman kiplerini doğru kullan:
     * "planlanıyor" (gelecekte olacak)
     * "gerçekleşti/gerçekleşecek" (olmuş/olacak)
     * "açıklandı/duyuruldu" (resmi açıklama)
   - Kısa ve öz cümleler kur
   - Pasif yapıdan kaçın, aktif yapı kullan

4. **FORMAT:**
   - Her satır maksimum 80 karakter olmalı (görsel şablona sığması için)
   - Toplam 3 satır, nokta ile bitir
   - "Kim:", "Ne:", gibi etiketler KULLANMA, direkt haberi yaz

HABER:
Başlık: {title}
İçerik: {content}
Kaynak: {source}
Tarih: {date}

YANIT FORMATI (Sadece JSON döndür):
{{
    "line1": "<1. satır - Hüküm/Giriş>",
    "line2": "<2. satır - Detay/Bağlam>",
    "line3": "<3. satır - Sonuç/Etki>",
    "keywords": ["<haber için 3-5 anahtar kelime>"]
}}
"""


def summarize_news(news_item: Dict) -> Optional[Dict]:
    """Haberi 3 satırda özetler."""
    if not news_item:
        print("Haber boş!")
        return None
    
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    content = news_item.get('content') or news_item.get('description', '')
    
    prompt = SUMMARY_PROMPT.format(
        title=news_item.get('title', ''),
        content=content,
        source=news_item.get('source', ''),
        date=news_item.get('published', '')
    )
    
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Sen profesyonel bir haber yazarısın. Sadece JSON formatında yanıt ver."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.4,
            max_tokens=500
        )
        
        result_text = response.choices[0].message.content.strip()
        
        # Markdown code block varsa temizle
        if result_text.startswith("```"):
            result_text = result_text.split("```")[1]
            if result_text.startswith("json"):
                result_text = result_text[4:]
        
        result = json.loads(result_text)
        
        summary = {
            "line1": result.get("line1", ""),
            "line2": result.get("line2", ""),
            "line3": result.get("line3", ""),
            "full_text": f"{result.get('line1', '')}\n{result.get('line2', '')}\n{result.get('line3', '')}",
            "keywords": result.get("keywords", [])
        }
        
        print("--- ÖZET ---")
        print(summary["full_text"])
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
