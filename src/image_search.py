"""
Image Search - Haber için uygun görsel bulur.
Unsplash API veya Google Custom Search API kullanır.
"""

import os
import requests
from typing import List, Optional
import re

# Unsplash API (ücretsiz, attribution gerekli)
UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

# Pexels API (alternatif, ücretsiz)
PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")


def search_unsplash(query: str, orientation: str = "landscape") -> Optional[str]:
    """Unsplash'tan görsel arar."""
    if not UNSPLASH_ACCESS_KEY:
        print("UNSPLASH_ACCESS_KEY bulunamadı")
        return None
    
    url = "https://api.unsplash.com/search/photos"
    params = {
        "query": query,
        "orientation": orientation,
        "per_page": 5
    }
    headers = {
        "Authorization": f"Client-ID {UNSPLASH_ACCESS_KEY}"
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("results"):
            # İlk uygun görseli döndür
            image_url = data["results"][0]["urls"]["regular"]
            print(f"Unsplash görsel bulundu: {image_url}")
            return image_url
        
        return None
    except Exception as e:
        print(f"Unsplash API hatası: {e}")
        return None


def search_pexels(query: str, orientation: str = "landscape") -> Optional[str]:
    """Pexels'tan görsel arar."""
    if not PEXELS_API_KEY:
        print("PEXELS_API_KEY bulunamadı")
        return None
    
    url = "https://api.pexels.com/v1/search"
    params = {
        "query": query,
        "orientation": orientation,
        "per_page": 5
    }
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    try:
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        if data.get("photos"):
            # İlk uygun görseli döndür
            image_url = data["photos"][0]["src"]["large"]
            print(f"Pexels görsel bulundu: {image_url}")
            return image_url
        
        return None
    except Exception as e:
        print(f"Pexels API hatası: {e}")
        return None


def download_image(url: str, output_path: str) -> bool:
    """Görseli indirir."""
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Görsel indirildi: {output_path}")
        return True
    except Exception as e:
        print(f"Görsel indirme hatası: {e}")
        return False


def extract_keywords_for_image(keywords: List[str], title: str) -> str:
    """Görsel araması için anahtar kelimeler oluşturur."""
    # Türkçe kelimeleri İngilizce'ye çevirmeden, genel terimlerle arama yap
    general_terms = {
        "politika": "politics government",
        "ekonomi": "economy finance",
        "göçmen": "immigration migrants",
        "mülteci": "refugees",
        "güvenlik": "security police",
        "sağlık": "health hospital",
        "eğitim": "education school",
        "ulaşım": "transport traffic",
        "ukrayna": "ukraine war",
        "polonya": "poland warsaw",
        "almanya": "germany berlin",
        "avrupa": "europe eu",
        "hükümet": "government parliament"
    }
    
    search_query = "Poland news "
    
    # Anahtar kelimelerden İngilizce karşılıkları bul
    for keyword in keywords[:3]:
        keyword_lower = keyword.lower()
        for tr_term, en_term in general_terms.items():
            if tr_term in keyword_lower:
                search_query += en_term + " "
                break
    
    # Yeterli anahtar kelime yoksa genel haber görseli ara
    if len(search_query.strip()) < 20:
        search_query = "Poland city news politics"
    
    return search_query.strip()


def find_news_image(keywords: List[str], title: str, output_path: str) -> Optional[str]:
    """Haber için görsel bulur ve indirir."""
    search_query = extract_keywords_for_image(keywords, title)
    print(f"Görsel arama sorgusu: {search_query}")
    
    # Önce Unsplash dene
    image_url = search_unsplash(search_query)
    
    # Unsplash'ta bulunamazsa Pexels dene
    if not image_url:
        image_url = search_pexels(search_query)
    
    # Hala bulunamazsa genel Polonya görseli ara
    if not image_url:
        image_url = search_unsplash("Poland city architecture")
    
    if not image_url:
        image_url = search_pexels("Poland warsaw")
    
    # Görseli indir
    if image_url:
        if download_image(image_url, output_path):
            return output_path
    
    return None


def use_default_image(output_path: str) -> str:
    """Varsayılan görsel kullanır (API olmadığında)."""
    # Placeholder görsel URL'i
    placeholder_url = "https://images.unsplash.com/photo-1519197924294-4ba991a11128?w=800&q=80"  # Poland related
    
    if download_image(placeholder_url, output_path):
        return output_path
    
    return None


if __name__ == "__main__":
    # Test
    keywords = ["hükümet", "göçmen", "yasa"]
    title = "Polonya yeni göçmenlik yasasını onayladı"
    
    result = find_news_image(keywords, title, "test_image.jpg")
    print(f"Sonuç: {result}")
