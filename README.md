# 🤖 AI Social Media Automation

Polonya haberlerini AI ile seçip özetleyen ve Instagram'a paylaşan GitHub Actions tabanlı otomasyon sistemi.

## 🚀 Özellikler

- **RSS Feed Parsing**: Polonya haberlerini otomatik filtreler
- **AI Haber Seçimi**: OpenAI GPT-4 ile en kritik haberi seçer
- **AI Özetleme**: 3 satırlık profesyonel haber özeti (5N1K formatında)
- **Görsel Arama**: Haber için uygun görsel bulur
- **Template Görseli**: 1080x1080 Instagram formatında görsel üretir
- **Instagram Paylaşımı**: Otomatik paylaşım

## 📁 Proje Yapısı

```
social_automation/
├── .github/workflows/
│   └── daily-post.yml      # GitHub Actions workflow
├── assets/
│   ├── background.png      # Template arka planı
│   ├── flag.png            # Bayrak ikonu
│   └── ggicon.png          # Gurbetci ikonu
├── src/
│   ├── main.py             # Ana orchestrator
│   ├── rss_parser.py       # RSS okuma
│   ├── ai_selector.py      # AI haber seçimi
│   ├── ai_summarizer.py    # AI özetleme
│   ├── image_search.py     # Görsel arama
│   ├── image_generator.py  # Template görsel oluşturma
│   └── instagram_poster.py # Instagram API
├── output/                 # Oluşturulan görseller
├── requirements.txt
└── README.md
```

## ⚙️ Kurulum

### 1. GitHub Secrets Ayarlama

Repository Settings → Secrets and variables → Actions → New repository secret

| Secret Adı | Açıklama |
|------------|----------|
| `OPENAI_API_KEY` | OpenAI API anahtarı |
| `INSTAGRAM_ACCESS_TOKEN` | Instagram Graph API erişim token'ı |
| `INSTAGRAM_ACCOUNT_ID` | Instagram İşletme Hesabı ID'si |
| `IMGBB_API_KEY` | imgbb görsel hosting API (opsiyonel) |
| `UNSPLASH_ACCESS_KEY` | Unsplash API (opsiyonel) |
| `PEXELS_API_KEY` | Pexels API (opsiyonel) |

### 2. Instagram Entegrasyonu

Instagram Graph API kullanmak için:

1. **Facebook Developer Hesabı**: [developers.facebook.com](https://developers.facebook.com) adresinden hesap oluşturun
2. **Uygulama Oluşturun**: My Apps → Create App → Business
3. **Instagram Graph API Ekleyin**: Add Product → Instagram Graph API
4. **İzinler**:
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_read_engagement`
5. **Access Token**: Graph API Explorer'dan uzun süreli token alın
6. **Account ID**: Instagram İşletme Hesabı ID'sini alın

## 🏃 Manuel Çalıştırma

```bash
# Bağımlılıkları yükle
pip install -r requirements.txt

# Environment variables ayarla
export OPENAI_API_KEY="your-key"
export INSTAGRAM_ACCESS_TOKEN="your-token"
export INSTAGRAM_ACCOUNT_ID="your-id"

# Çalıştır
python src/main.py
```

## ⏰ Zamanlama

Varsayılan olarak her gün **08:00 UTC** (Polonya saati 09:00) çalışır.

Değiştirmek için `.github/workflows/daily-post.yml` dosyasındaki cron ifadesini düzenleyin:

```yaml
schedule:
  - cron: '0 8 * * *'  # Her gün 08:00 UTC
```

## 📸 Template Örneği

Oluşturulan Instagram görseli şu yapıda olacak:
- **Boyut**: 1080x1080 piksel
- **Sağ üst**: Polonya bayrağı (küçük)
- **Orta**: Haber görseli (rounded corners)
- **Alt**: 3 satır haber özeti
- **Sağ alt**: Gurbetci ikonu
- **En alt**: "Daha fazlası için..." sabit metin

## 📄 Lisans

MIT License
