"""
RSS Feed Parser - Polonya haberlerini filtreler ve bugünün haberlerini döner.
"""

import feedparser
from datetime import datetime, timezone
from dateutil import parser as date_parser
from typing import List, Dict, Optional
import re

RSS_FEED_URL = "https://iwjkgmvorjtxgjiebkll.supabase.co/storage/v1/object/public/rss-feeds/news-feed.xml"


def parse_rss_feed(url: str = RSS_FEED_URL) -> List[Dict]:
    """RSS feed'i parse eder ve tüm haberleri döner."""
    feed = feedparser.parse(url)
    
    if feed.bozo:
        print(f"RSS parse hatası: {feed.bozo_exception}")
        return []
    
    news_items = []
    for entry in feed.entries:
        # Country alanını bul
        country = None
        if hasattr(entry, 'country'):
            country = entry.country
        else:
            # Raw XML'den country çek
            if hasattr(entry, 'get'):
                country = entry.get('country')
        
        # Alternatif: summary veya content içinden country çıkar
        if not country:
            for key in dir(entry):
                if key == 'country':
                    country = getattr(entry, key)
                    break
        
        news_item = {
            'title': entry.get('title', ''),
            'description': entry.get('description', ''),
            'content': entry.get('content', [{}])[0].get('value', '') if entry.get('content') else entry.get('summary', ''),
            'link': entry.get('link', ''),
            'published': entry.get('published', ''),
            'published_parsed': entry.get('published_parsed'),
            'country': country,
            'category': entry.get('category', ''),
            'source': entry.get('dc_creator', entry.get('author', ''))
        }
        news_items.append(news_item)
    
    return news_items


def filter_poland_news(news_items: List[Dict]) -> List[Dict]:
    """Sadece Polonya (country: pl) haberlerini filtreler."""
    return [item for item in news_items if item.get('country') == 'pl']


def filter_today_news(news_items: List[Dict]) -> List[Dict]:
    """Sadece bugün yayımlanan haberleri filtreler."""
    today = datetime.now(timezone.utc).date()
    today_news = []
    
    for item in news_items:
        try:
            if item.get('published_parsed'):
                pub_date = datetime(*item['published_parsed'][:6], tzinfo=timezone.utc).date()
            elif item.get('published'):
                pub_date = date_parser.parse(item['published']).date()
            else:
                continue
            
            if pub_date == today:
                today_news.append(item)
        except Exception as e:
            print(f"Tarih parse hatası: {e}")
            continue
    
    return today_news


def get_poland_news_today() -> List[Dict]:
    """Ana fonksiyon: Bugünkü Polonya haberlerini döner."""
    all_news = parse_rss_feed()
    poland_news = filter_poland_news(all_news)
    today_news = filter_today_news(poland_news)
    
    print(f"Toplam haber: {len(all_news)}")
    print(f"Polonya haberleri: {len(poland_news)}")
    print(f"Bugünkü Polonya haberleri: {len(today_news)}")
    
    return today_news


def get_poland_news_all() -> List[Dict]:
    """Tüm Polonya haberlerini döner (tarih filtresi olmadan)."""
    all_news = parse_rss_feed()
    poland_news = filter_poland_news(all_news)
    
    print(f"Toplam haber: {len(all_news)}")
    print(f"Polonya haberleri: {len(poland_news)}")
    
    return poland_news


if __name__ == "__main__":
    # Test
    news = get_poland_news_today()
    if not news:
        print("Bugün haber yok, tüm Polonya haberlerini çekiyorum...")
        news = get_poland_news_all()
    
    for item in news[:3]:
        print(f"\n--- {item['title']} ---")
        print(f"Tarih: {item['published']}")
        print(f"Kaynak: {item['source']}")
