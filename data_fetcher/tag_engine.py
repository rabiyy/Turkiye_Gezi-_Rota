from db import get_connection

# ================================================================
# GEZIROTA ETİKET MOTORU
# Her mekan için kategori, puan, popülerlik, fiyat, konum ve
# isim analizine göre otomatik etiket atar.
# ================================================================

# ---------------------------------------------------------------
# 1. KATEGORİ BAZLI ETİKETLER
# Her kategori için o kategorinin doğasına uygun etiketler
# ---------------------------------------------------------------
CATEGORY_TAGS = {
    # DOĞA & AÇIK HAVA
    "park": [
        "Doğa Dostu", "Açık Hava", "Yeşil Alan",
        "Aile Dostu", "Yürüyüş İmkânı", "Fotoğrafçılık"
    ],
    "ulusal park": [
        "Doğa Koruma Alanı", "Doğa Dostu", "Açık Hava",
        "Biyoçeşitlilik", "Yürüyüş İmkânı", "Vahşi Yaşam",
        "Fotoğrafçılık", "Ekoturizm"
    ],
    "orman": [
        "Doğa Dostu", "Açık Hava", "Yüksek Oksijen",
        "Biyoçeşitlilik", "Huzurlu", "Yürüyüş İmkânı",
        "Ekoturizm", "Düşük Karbon"
    ],
    "plaj": [
        "Su Kenarı", "Açık Hava", "Doğa",
        "Yaz Aktivitesi", "Güneşlenme", "Yüzme",
        "Fotoğrafçılık", "Romantik"
    ],
    "kamp": [
        "Ekoturizm", "Doğa Dostu", "Düşük Karbon",
        "Açık Hava", "Macera", "Yıldız Gözlemi",
        "Bütçe Dostu"
    ],
    "kamp alanı": [
        "Ekoturizm", "Doğa Dostu", "Düşük Karbon",
        "Açık Hava", "Macera", "Bütçe Dostu", "Konaklama"
    ],
    "doğa yürüyüşü": [
        "Doğa Dostu", "Aktif Yaşam", "Açık Hava",
        "Macera", "Sağlıklı Yaşam", "Fotoğrafçılık",
        "Ekoturizm"
    ],
    "botanik bahçesi": [
        "Doğa Dostu", "Eğitici", "Yeşil Alan",
        "Aile Dostu", "Fotoğrafçılık", "Bilim",
        "Huzurlu", "Erişilebilir"
    ],
    "hayvanat bahçesi": [
        "Aile Dostu", "Eğitici", "Çocuk Dostu",
        "Vahşi Yaşam", "Bilim"
    ],
    "akvaryum": [
        "Aile Dostu", "Eğitici", "Çocuk Dostu",
        "Su Altı Dünyası", "Bilim", "Kapalı Alan"
    ],
    "göl": [
        "Su Kenarı", "Doğa Dostu", "Açık Hava",
        "Fotoğrafçılık", "Huzurlu", "Balık Avı"
    ],
    "şelale": [
        "Doğa Dostu", "Su Kenarı", "Açık Hava",
        "Fotoğrafçılık", "Huzurlu", "Doğal Güzellik"
    ],
    "dağ": [
        "Doğa Dostu", "Açık Hava", "Macera",
        "Yürüyüş İmkânı", "Fotoğrafçılık", "Panoramik Manzara",
        "Aktif Yaşam"
    ],
    "piknik": [
        "Aile Dostu", "Açık Hava", "Yeşil Alan",
        "Sosyal Alan", "Çocuk Dostu", "Bütçe Dostu"
    ],

    # KÜLTÜR & TARİH
    "müze": [
        "Kültürel Miras", "Eğitici", "Tarihi",
        "Sanat", "Bilim", "Kapalı Alan",
        "Yağmurlu Hava Alternatifi"
    ],
    "tarihi yer": [
        "Kültürel Miras", "Tarihi", "Eğitici",
        "Fotoğrafçılık", "Turizm", "Mimari"
    ],
    "arkeoloji": [
        "Kültürel Miras", "Tarihi", "Eğitici",
        "Bilim", "Antik", "Keşif"
    ],
    "sanat galerisi": [
        "Kültürel", "Sanat", "Eğitici",
        "Modern Sanat", "Yaratıcılık", "Kapalı Alan"
    ],
    "anıt": [
        "Tarihi", "Kültürel Miras", "Fotoğrafçılık",
        "Turizm", "Mimari"
    ],
    "kale": [
        "Tarihi", "Kültürel Miras", "Mimari",
        "Fotoğrafçılık", "Panoramik Manzara", "Eğitici"
    ],
    "camii": [
        "Tarihi", "Kültürel Miras", "İbadet",
        "Mimari", "Manevi", "Fotoğrafçılık"
    ],
    "kilise": [
        "Tarihi", "Kültürel Miras", "İbadet",
        "Mimari", "Manevi", "Fotoğrafçılık"
    ],
    "sinagog": [
        "Tarihi", "Kültürel Miras", "İbadet",
        "Mimari", "Manevi"
    ],
    "tapınak": [
        "Tarihi", "Kültürel Miras", "İbadet",
        "Mimari", "Manevi", "Fotoğrafçılık"
    ],
    "kültürel landmark": [
        "Kültürel Miras", "Tarihi", "Turizm",
        "Fotoğrafçılık", "Eğitici"
    ],

    # YEME & İÇME
    "restoran": [
        "Yeme & İçme", "Sosyal Alan", "Lezzetli"
    ],
    "deniz ürünleri": [
        "Yeme & İçme", "Deniz Ürünleri", "Taze Ürün",
        "Yerel Lezzet", "Balık"
    ],
    "vejeteryan": [
        "Yeme & İçme", "Vejetaryen Dostu", "Sağlıklı Yaşam",
        "Sürdürülebilir Tarım", "Bitkisel Beslenme"
    ],
    "vegan": [
        "Yeme & İçme", "Vegan Dostu", "Sağlıklı Yaşam",
        "Düşük Karbon Ayak İzi", "Hayvan Dostu",
        "Bitkisel Beslenme", "Sürdürülebilir Tarım"
    ],
    "organik": [
        "Yeme & İçme", "Organik", "Yerel Üretim",
        "Doğa Dostu", "Sağlıklı Yaşam", "Sürdürülebilir Tarım",
        "Kimyasal İçermez"
    ],
    "kafe": [
        "Yeme & İçme", "Sosyal Alan", "Kahve",
        "Çalışma Alanı", "Buluşma Noktası"
    ],
    "pastane": [
        "Yeme & İçme", "Tatlı", "Fırın Ürünleri",
        "Kahvaltı", "Yerel Lezzet"
    ],
    "fast food": [
        "Yeme & İçme", "Hızlı Servis", "Uygun Fiyatlı"
    ],
    "bar": [
        "Eğlence", "Sosyal Alan", "Gece Hayatı",
        "İçecek"
    ],
    "pub": [
        "Eğlence", "Sosyal Alan", "Gece Hayatı",
        "Geleneksel", "İçecek"
    ],
    "sokak yemeği": [
        "Yeme & İçme", "Yerel Lezzet", "Bütçe Dostu",
        "Otantik", "Hızlı Servis"
    ],

    # KONAKLAMA
    "otel": [
        "Konaklama", "Konforlu", "Hizmet"
    ],
    "hostel": [
        "Konaklama", "Bütçe Dostu", "Sosyal Ortam",
        "Genç Gezginler", "Paylaşımlı Alan"
    ],
    "apart": [
        "Konaklama", "Uzun Konaklamaya Uygun",
        "Bağımsız", "Mutfak İmkânı"
    ],
    "butik otel": [
        "Konaklama", "Özel Deneyim", "Tasarım",
        "Otantik", "Kişisel Hizmet"
    ],
    "tatil köyü": [
        "Konaklama", "Tatil", "Havuzlu",
        "Aile Dostu", "Her Şey Dahil"
    ],

    # ALIŞVERİŞ
    "çarşı": [
        "Alışveriş", "Yerel Kültür", "Otantik",
        "El Sanatları", "Pazarlık Yapılabilir"
    ],
    "pazar": [
        "Alışveriş", "Yerel Üretim", "Taze Ürün",
        "Organik", "Otantik", "Bütçe Dostu",
        "Yerel Kültür"
    ],
    "alışveriş merkezi": [
        "Alışveriş", "Kapalı Alan", "Yağmurlu Hava Alternatifi",
        "Marka Mağazaları", "Yeme & İçme"
    ],
    "hediyelik": [
        "Alışveriş", "Hatıra", "Turizm",
        "El Sanatları", "Yerel Kültür"
    ],
    "antika": [
        "Alışveriş", "Tarihi", "Koleksiyon",
        "Nadir Eserler", "Kültürel"
    ],

    # EĞLENCE & AKTİVİTE
    "eğlence parkı": [
        "Eğlence", "Aile Dostu", "Çocuk Dostu",
        "Macera", "Heyecan"
    ],
    "sinema": [
        "Eğlence", "Kapalı Alan", "Kültürel",
        "Yağmurlu Hava Alternatifi"
    ],
    "tiyatro": [
        "Sanat", "Kültürel", "Eğlence",
        "Canlı Performans", "Akşam Aktivitesi"
    ],
    "konser": [
        "Sanat", "Eğlence", "Müzik",
        "Canlı Performans", "Akşam Aktivitesi"
    ],
    "gece kulübü": [
        "Eğlence", "Gece Hayatı", "Müzik",
        "Dans", "Sosyal Alan"
    ],
    "bowling": [
        "Eğlence", "Aile Dostu", "Kapalı Alan",
        "Yağmurlu Hava Alternatifi"
    ],
    "spa": [
        "Sağlık & Wellness", "Dinlenme", "Lüks",
        "Masaj", "Rahatlama", "Özel Deneyim"
    ],
    "spor": [
        "Aktif Yaşam", "Sağlık", "Spor",
        "Fitness"
    ],
}

# ---------------------------------------------------------------
# 2. RATING BAZLI ETİKETLER
# Google puanına göre kalite etiketi
# ---------------------------------------------------------------
RATING_TAGS = [
    (4.7, ["Mükemmel Puanlı", "Çok Yüksek Puanlı", "Kesinlikle Tavsiye"]),
    (4.5, ["Çok Yüksek Puanlı", "Kesinlikle Tavsiye"]),
    (4.2, ["Yüksek Puanlı", "Tavsiye Edilir"]),
    (4.0, ["Yüksek Puanlı"]),
    (3.5, ["İyi Puanlı"]),
    (3.0, ["Orta Puanlı"]),
]

# ---------------------------------------------------------------
# 3. POPÜLERLİK BAZLI ETİKETLER
# Yorum sayısına göre popülerlik etiketi
# ---------------------------------------------------------------
POPULARITY_TAGS = [
    (50000, ["Efsane Mekan", "Çok Popüler", "İkonik"]),
    (10000, ["Çok Popüler", "Turistik"]),
    (5000,  ["Popüler", "Çok Ziyaret Edilen"]),
    (1000,  ["Popüler"]),
    (500,   ["Bilinir"]),
    (100,   ["Keşfedilmemiş Mücevher"]),
]

# ---------------------------------------------------------------
# 4. FİYAT BAZLI ETİKETLER
# Google'ın 0-4 fiyat ölçeğine göre
# ---------------------------------------------------------------
PRICE_TAGS = {
    0: ["Ücretsiz", "Bütçe Dostu", "Herkese Açık"],
    1: ["Bütçe Dostu", "Uygun Fiyatlı"],
    2: ["Orta Fiyat", "Makul Fiyat"],
    3: ["Yüksek Fiyat", "Premium"],
    4: ["Lüks", "Üst Segment", "Özel Deneyim"],
}

# ---------------------------------------------------------------
# 5. MEKAN İSMİ / ADRESİNDEKİ ANAHTAR KELİMELERE GÖRE ETİKETLER
# ---------------------------------------------------------------
NAME_KEYWORD_TAGS = {
    # Doğa & Çevre
    "milli park": ["Doğa Koruma Alanı", "Doğa Dostu", "Korunan Alan"],
    "tabiat parkı": ["Doğa Koruma Alanı", "Doğa Dostu", "Korunan Alan"],
    "tabiat anıtı": ["Doğa Koruma Alanı", "Doğa Dostu", "Nadir"],
    "koruma alanı": ["Korunan Alan", "Doğa Dostu"],
    "mavi bayrak": ["Mavi Bayraklı Plaj", "Çevre Sertifikalı", "Temiz Plaj"],
    "organik": ["Organik", "Doğa Dostu"],
    "ekolojik": ["Ekolojik", "Doğa Dostu", "Sürdürülebilir"],
    "eko": ["Ekoturizm", "Doğa Dostu"],
    "yeşil": ["Yeşil Alan", "Doğa Dostu"],
    "botanik": ["Botanik", "Doğa Dostu", "Bilim"],
    "orman": ["Orman", "Doğa Dostu", "Açık Hava"],

    # Aktivite & Spor
    "bisiklet": ["Bisiklet Dostu", "Aktif Yaşam"],
    "yürüyüş": ["Yürüyüş İmkânı", "Aktif Yaşam"],
    "trekking": ["Trekking", "Macera", "Aktif Yaşam"],
    "kayak": ["Kayak", "Kış Sporları", "Macera"],
    "dalış": ["Dalış", "Su Altı", "Macera"],
    "sörf": ["Sörf", "Su Sporları", "Macera"],

    # Yiyecek & İçecek
    "vegan": ["Vegan Dostu", "Bitkisel Beslenme"],
    "vejetaryen": ["Vejetaryen Dostu", "Bitkisel Beslenme"],
    "vejeteryan": ["Vejetaryen Dostu", "Bitkisel Beslenme"],
    "glutensiz": ["Glutensiz Seçenek", "Sağlıklı Yaşam"],
    "helal": ["Helal Sertifikalı"],
    "balık": ["Deniz Ürünleri", "Taze Ürün", "Yerel Lezzet"],
    "deniz": ["Deniz Manzarası", "Su Kenarı"],

    # Konum & Özellik
    "tarihi": ["Tarihi", "Kültürel Miras"],
    "antik": ["Antik", "Tarihi", "Arkeolojik"],
    "osmanlı": ["Osmanlı Dönemi", "Tarihi", "Kültürel Miras"],
    "bizans": ["Bizans Dönemi", "Tarihi", "Kültürel Miras"],
    "çarşı": ["Yerel Kültür", "Otantik"],
    "kapalı çarşı": ["Tarihi Çarşı", "Otantik", "Kültürel Miras"],
    "bedesten": ["Tarihi Çarşı", "Otantik", "Kültürel Miras"],
    "han": ["Tarihi", "Kültürel Miras", "Otantik"],
    "hamam": ["Tarihi", "Kültürel Miras", "Geleneksel", "Spa"],
    "konak": ["Tarihi", "Kültürel Miras", "Otantik"],
    "köy": ["Otantik", "Yerel Kültür", "Huzurlu"],
    "köşk": ["Tarihi", "Mimari", "Kültürel Miras"],
    "saray": ["Tarihi", "Mimari", "Kültürel Miras", "İkonik"],
    "kale": ["Tarihi", "Panoramik Manzara", "Fotoğrafçılık"],
    "liman": ["Su Kenarı", "Deniz", "Turizm"],
    "marina": ["Su Kenarı", "Yat", "Lüks"],
    "körfez": ["Su Kenarı", "Doğal Güzellik", "Fotoğrafçılık"],
    "ada": ["Ada", "Deniz", "Keşif", "Huzurlu"],
    "şelale": ["Şelale", "Doğal Güzellik", "Fotoğrafçılık"],
    "kanyon": ["Kanyon", "Doğal Güzellik", "Macera"],
    "mağara": ["Mağara", "Doğal Güzellik", "Keşif"],

    # Manzara & Deneyim
    "panoramik": ["Panoramik Manzara", "Fotoğrafçılık"],
    "manzara": ["Manzaralı", "Fotoğrafçılık"],
    "seyir": ["Panoramik Manzara", "Fotoğrafçılık"],
    "gün batımı": ["Gün Batımı Manzarası", "Romantik", "Fotoğrafçılık"],
    "rooftop": ["Çatı Katı", "Panoramik Manzara", "Şehir Manzarası"],
    "terrace": ["Teras", "Açık Hava", "Manzaralı"],

    # Sosyal & Aile
    "çocuk": ["Çocuk Dostu", "Aile Dostu"],
    "aile": ["Aile Dostu"],
    "engelli": ["Engelli Erişimli", "Erişilebilir"],
    "wifi": ["Ücretsiz WiFi", "Çalışma Alanı"],
    "cafe": ["Kahve", "Sosyal Alan"],
    "lounge": ["Dinlenme Alanı", "Rahat Ortam"],
}

# ---------------------------------------------------------------
# 6. BÖLGE / SEMT BAZLI ETİKETLER
# Adresteki semte göre ek etiket
# ---------------------------------------------------------------
DISTRICT_TAGS = {
    # İstanbul
    "beyoğlu": ["Şehir Merkezi", "Kültürel", "Gece Hayatı"],
    "fatih": ["Tarihi Yarımada", "Tarihi", "Turistik"],
    "sultanahmet": ["Tarihi Yarımada", "İkonik", "Turistik"],
    "kadıköy": ["Anadolu Yakası", "Genç & Dinamik", "Sosyal Alan"],
    "beşiktaş": ["Avrupa Yakası", "Canlı", "Sosyal Alan"],
    "üsküdar": ["Anadolu Yakası", "Tarihi", "Huzurlu"],
    "adalar": ["Ada", "Arabasız", "Huzurlu", "Doğa Dostu"],
    "sarıyer": ["Boğaz Manzarası", "Doğa", "Huzurlu"],
    "bebek": ["Boğaz Kenarı", "Şık", "Lüks"],
    "ortaköy": ["Boğaz Kenarı", "Sosyal Alan", "Fotoğrafçılık"],

    # İzmir
    "alsancak": ["Şehir Merkezi", "Canlı", "Sosyal Alan"],
    "konak": ["Şehir Merkezi", "Tarihi", "Turistik"],
    "karşıyaka": ["Sahil", "Aile Dostu", "Huzurlu"],
    "çeşme": ["Tatil", "Plaj", "Su Sporları"],
    "alaçatı": ["Otantik", "Şık", "Romantik", "Rüzgar Sörfü"],
    "foça": ["Tarihi", "Sakin", "Doğa Dostu"],

    # Muğla
    "bodrum": ["Tatil", "Lüks", "Gece Hayatı", "Deniz"],
    "marmaris": ["Tatil", "Deniz", "Su Sporları"],
    "fethiye": ["Doğa", "Deniz", "Macera", "Tatil"],
    "öludeniz": ["İkonik", "Plaj", "Doğal Güzellik"],
    "göcek": ["Marina", "Lüks", "Sakin", "Yelken"],

    # Çanakkale
    "truva": ["Antik", "Tarihi", "Arkeolojik", "İkonik"],
    "gelibolu": ["Tarihi", "Anıt", "Eğitici"],
    "bozcaada": ["Ada", "Şarap", "Huzurlu", "Otantik"],
    "gökçeada": ["Ada", "Doğa", "Dalış", "Huzurlu"],
}


def generate_tags(name, category, address, city, rating,
                  user_ratings_total, price_level,
                  is_near_transit, permanently_closed):
    """
    Mekan bilgilerine göre kapsamlı etiket listesi oluşturur.
    """
    if permanently_closed:
        return ["Kapalı"]

    tags = set()

    # 1. Kategori bazlı etiketler
    if category:
        cat_lower = category.lower().strip()
        if cat_lower in CATEGORY_TAGS:
            for tag in CATEGORY_TAGS[cat_lower]:
                tags.add(tag)

    # 2. Rating bazlı etiketler
    if rating and rating > 0:
        for min_rating, rating_tag_list in RATING_TAGS:
            if rating >= min_rating:
                for tag in rating_tag_list:
                    tags.add(tag)
                break

    # 3. Popülerlik bazlı etiketler
    if user_ratings_total and user_ratings_total > 0:
        for min_count, pop_tag_list in POPULARITY_TAGS:
            if user_ratings_total >= min_count:
                for tag in pop_tag_list:
                    tags.add(tag)
                break

    # 4. Fiyat bazlı etiketler
    if price_level is not None and price_level in PRICE_TAGS:
        for tag in PRICE_TAGS[price_level]:
            tags.add(tag)

    # 5. Toplu taşıma etiketi
    if is_near_transit:
        tags.add("Toplu Taşımaya Yakın")
        tags.add("Ulaşımı Kolay")

    # 6. İsim bazlı anahtar kelime etiketleri
    name_lower = (name or "").lower()
    for keyword, keyword_tags in NAME_KEYWORD_TAGS.items():
        if keyword in name_lower:
            for tag in keyword_tags:
                tags.add(tag)

    # 7. Adres / semt bazlı etiketler
    address_lower = (address or "").lower()
    for district, district_tags in DISTRICT_TAGS.items():
        if district in address_lower:
            for tag in district_tags:
                tags.add(tag)

    # 8. Şehir bazlı genel etiket
    if city:
        tags.add(f"{city}'da")

    return sorted(list(tags))


def run_tag_engine():
    print("🏷️  Gezirota Etiket Motoru Başlatılıyor...")
    print("=" * 55)

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT 
                p.id, p.name, c.name as category,
                p.address, p.city,
                p.rating, p.user_ratings_total, p.price_level,
                p.permanently_closed,
                EXISTS (
                    SELECT 1 FROM public_transit pt
                    WHERE ST_DWithin(p.location::geography, pt.location::geography, 800)
                ) as is_near_transit
            FROM places p
            LEFT JOIN place_categories pc ON p.id = pc.place_id
            LEFT JOIN categories c ON pc.category_id = c.id;
        """)

        places = cur.fetchall()
        total = len(places)
        print(f"📍 {total} mekan için etiket oluşturuluyor...\n")

        tag_stats = {}
        updated = 0
        transit_count = 0

        for place in places:
            (place_id, name, category, address, city,
             rating, user_ratings_total, price_level,
             permanently_closed, is_near_transit) = place

            tags = generate_tags(
                name=name,
                category=category,
                address=address,
                city=city,
                rating=rating,
                user_ratings_total=user_ratings_total,
                price_level=price_level,
                is_near_transit=is_near_transit,
                permanently_closed=permanently_closed or False
            )

            # İstatistik topla
            for tag in tags:
                tag_stats[tag] = tag_stats.get(tag, 0) + 1

            if is_near_transit:
                transit_count += 1

            cur.execute("""
                UPDATE places SET green_tags = %s WHERE id = %s;
            """, (tags, place_id))

            updated += 1

            # Her 500 kayıtta bir kaydet ve ilerlemeyi göster
            if updated % 500 == 0:
                conn.commit()
                print(f"⏳ İlerleme: {updated}/{total} mekan tamamlandı...")

        conn.commit()

        # Sonuç raporu
        print(f"\n✅ {updated} mekanın etiketi güncellendi!")
        print(f"🚇 {transit_count} mekan toplu taşımaya yakın bulundu.")
        print(f"\n📊 En Sık Kullanılan İlk 20 Etiket:")
        print("-" * 45)
        for tag, count in sorted(tag_stats.items(), key=lambda x: x[1], reverse=True)[:20]:
            bar = "█" * (count // 50)
            print(f"  {tag:35} {count:5d} {bar}")

    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    run_tag_engine()