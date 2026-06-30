# Sürdürülebilirlik Odaklı Türkiye Gezi Rota Rehberi

Marmara ve Ege bölgelerini kapsayan, çevre dostu ve sürdürülebilir turizmi teşvik etmek amacıyla geliştirilmiş yapay zeka destekli akıllı seyahat asistanı. Bu proje, bilgisayar mühendisliği mezuniyet çalışması olarak geliştirilmiştir.

## Proje Hakkında
Bu seyahat asistanı, geleneksel rota planlayıcılardan farklı olarak destinasyonların **sürdürülebilirlik skorlarını** göz önünde bulundurur. Kullanıcılara çevre dostu rota alternatifleri sunarken, büyük dil modellerinin ürettiği bilgilerin doğruluğunu garanti altına almak için özel bir yapay zeka mimarisi kullanır.

### Öne Çıkan Özellikler
* **Sürdürülebilirlik Skorlaması:** Destinasyonların çevresel etki, kültürel mirasın korunması ve yerel kalkınmaya katkı kriterlerine göre puanlanması.
* **Hibrit RAG (Retrieval-Augmented Generation) Mimarisi:** Dil modellerinin halüsinasyon (bilgi uydurma) riskini en aza indiren, doğrulanmış yerel veri setleriyle beslenen bilgi üretim mekanizması.
* **Akıllı Rota Optimizasyonu:** Kullanıcı tercihlerine göre Marmara ve Ege bölgeleri için optimize edilmiş gezi rotaları.

## Teknoloji Yığını
Proje, modern web teknolojileri ile ileri düzey yapay zeka/veri yönetimi araçlarının entegrasyonuyla geliştirilmiştir:

* **Backend:** Flask (Python)
* **Yapay Zeka / LLM:** Google Gemini API
* **Vektör Veritabanı:** PostgreSQL & `pgvector` eklentisi (Anlamsal arama ve veri eşleştirme için)
* **Frontend:** HTML5, CSS3, JavaScript (Figma tabanlı responsive tasarım)
* **Veri Seti:** Bölgesel turizm ve sürdürülebilirlik verilerini içeren özelleştirilmiş veri havuzu

## Proje Yapısı

gezirota/
│
├── data_fetcher/          # Yapay zeka ve veri işleme motoru
│   ├── app.py             # Backend API ve ana sunucu kontrolü
│   ├── chatbot.py         # Hibrit RAG ve Gemini entegrasyonu
│   └── build_db.py        # Veritabanı vektör indeksleme süreçleri
│
├── frontend/              # Kullanıcı arayüzü bileşenleri
│   ├── index.html         # Ana sayfa
│   ├── app.js             # Dinamik arayüz yönetimi
│   └── style.css          # Görsel tasarım ve stil dosyaları
│
├── migrations/            # Veritabanı göç ve şema yönetim dosyaları
└── .env.example           # Güvenli çevre değişkenleri şablonu
