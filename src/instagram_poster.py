"""
Instagram Poster - Instagram Graph API ile paylaşım yapar.
"""

import os
import requests
from typing import Optional
import time

# Environment variables
INSTAGRAM_ACCESS_TOKEN = os.getenv("INSTAGRAM_ACCESS_TOKEN")
INSTAGRAM_ACCOUNT_ID = os.getenv("INSTAGRAM_ACCOUNT_ID")

# Instagram Graph API endpoint
GRAPH_API_URL = "https://graph.facebook.com/v18.0"

# Sabit caption
INSTAGRAM_CAPTION = """Daha fazlası için Google Play veya App Store'dan
Gurbetci SuperApp'i ücretsiz indir. Link biyografide.
#gurbetci #gurbetcisuperapp"""


def upload_image_to_hosting(image_path: str) -> Optional[str]:
    """
    Görseli geçici bir hosting'e yükler.
    Instagram API, resmi URL olarak ister.
    
    Not: Production'da Supabase Storage veya imgbb gibi bir servis kullanılmalı.
    """
    # imgbb kullan (ücretsiz, API key gerekli)
    imgbb_api_key = os.getenv("IMGBB_API_KEY", "")
    
    if imgbb_api_key:
        url = "https://api.imgbb.com/1/upload"
        
        with open(image_path, "rb") as file:
            payload = {
                "key": imgbb_api_key,
                "expiration": 86400  # 24 saat
            }
            files = {
                "image": file
            }
            
            try:
                response = requests.post(url, data=payload, files=files)
                response.raise_for_status()
                data = response.json()
                
                if data.get("success"):
                    image_url = data["data"]["url"]
                    print(f"Görsel yüklendi: {image_url}")
                    return image_url
            except Exception as e:
                print(f"imgbb yükleme hatası: {e}")
    
    # Alternatif: Supabase Storage kullan
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = os.getenv("SUPABASE_SERVICE_KEY", "")
    
    if supabase_url and supabase_key:
        bucket = "instagram-posts"
        filename = f"post_{int(time.time())}.png"
        
        url = f"{supabase_url}/storage/v1/object/{bucket}/{filename}"
        headers = {
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "image/png"
        }
        
        try:
            with open(image_path, "rb") as file:
                response = requests.post(url, headers=headers, data=file)
                response.raise_for_status()
                
                # Public URL
                public_url = f"{supabase_url}/storage/v1/object/public/{bucket}/{filename}"
                print(f"Supabase'e yüklendi: {public_url}")
                return public_url
        except Exception as e:
            print(f"Supabase yükleme hatası: {e}")
    
    print("Görsel hosting yapılandırılmamış!")
    return None


def create_media_container(image_url: str, caption: str = INSTAGRAM_CAPTION) -> Optional[str]:
    """Instagram media container oluşturur."""
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("Instagram credentials eksik!")
        return None
    
    url = f"{GRAPH_API_URL}/{INSTAGRAM_ACCOUNT_ID}/media"
    
    payload = {
        "image_url": image_url,
        "caption": caption,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        
        container_id = data.get("id")
        print(f"Media container oluşturuldu: {container_id}")
        return container_id
    except Exception as e:
        print(f"Media container hatası: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None


def publish_media(container_id: str) -> Optional[str]:
    """Media container'ı yayınlar."""
    if not INSTAGRAM_ACCESS_TOKEN or not INSTAGRAM_ACCOUNT_ID:
        print("Instagram credentials eksik!")
        return None
    
    url = f"{GRAPH_API_URL}/{INSTAGRAM_ACCOUNT_ID}/media_publish"
    
    payload = {
        "creation_id": container_id,
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        data = response.json()
        
        post_id = data.get("id")
        print(f"Post yayınlandı! ID: {post_id}")
        return post_id
    except Exception as e:
        print(f"Publish hatası: {e}")
        if hasattr(e, 'response'):
            print(f"Response: {e.response.text}")
        return None


def wait_for_container_ready(container_id: str, max_wait: int = 60) -> bool:
    """Container'ın hazır olmasını bekler."""
    if not INSTAGRAM_ACCESS_TOKEN:
        return False
    
    url = f"{GRAPH_API_URL}/{container_id}"
    params = {
        "fields": "status_code",
        "access_token": INSTAGRAM_ACCESS_TOKEN
    }
    
    waited = 0
    while waited < max_wait:
        try:
            response = requests.get(url, params=params)
            data = response.json()
            
            status = data.get("status_code")
            if status == "FINISHED":
                print("Container hazır!")
                return True
            elif status == "ERROR":
                print(f"Container hatası: {data}")
                return False
            
            print(f"Container status: {status}, bekleniyor...")
            time.sleep(5)
            waited += 5
        except Exception as e:
            print(f"Status check hatası: {e}")
            time.sleep(5)
            waited += 5
    
    print("Container timeout!")
    return False


def post_to_instagram(image_path: str, caption: str = INSTAGRAM_CAPTION) -> Optional[str]:
    """
    Ana fonksiyon: Görseli Instagram'a paylaşır.
    
    Args:
        image_path: Lokal görsel dosyası yolu
        caption: Paylaşım açıklaması
    
    Returns:
        Post ID veya None
    """
    print(f"Instagram'a paylaşılıyor: {image_path}")
    
    # 1. Görseli hosting'e yükle
    image_url = upload_image_to_hosting(image_path)
    if not image_url:
        print("Görsel yüklenemedi!")
        return None
    
    # 2. Media container oluştur
    container_id = create_media_container(image_url, caption)
    if not container_id:
        print("Container oluşturulamadı!")
        return None
    
    # 3. Container'ın hazır olmasını bekle
    if not wait_for_container_ready(container_id):
        print("Container hazır olmadı!")
        return None
    
    # 4. Yayınla
    post_id = publish_media(container_id)
    if post_id:
        print(f"✅ Instagram paylaşımı başarılı! Post ID: {post_id}")
        return post_id
    else:
        print("❌ Paylaşım başarısız!")
        return None


if __name__ == "__main__":
    # Test (credentials gerekli)
    print("Instagram Poster Test")
    print(f"Access Token: {'✓' if INSTAGRAM_ACCESS_TOKEN else '✗'}")
    print(f"Account ID: {'✓' if INSTAGRAM_ACCOUNT_ID else '✗'}")
