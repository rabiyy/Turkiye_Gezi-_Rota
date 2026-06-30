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

<img width="760" height="378" alt="image" src="https://github.com/user-attachments/assets/edf06703-95c3-4cb2-8b0a-37ea3f711031" />

