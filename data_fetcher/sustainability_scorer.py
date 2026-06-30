from db import get_connection

# 1. Kategori bazlı taban puanlar
CATEGORY_BASE_SCORES = {
    # Doğa & Açık Hava (en yüksek)
    "orman": 70, "kamp": 70, "doğa yürüyüşü": 65,
    "botanik bahçesi": 65, "park": 60, "piknik": 60,
    "göl": 58, "şelale": 58, "dağ": 58,
    "plaj": 50, "akvaryum": 45, "hayvanat bahçesi": 40,

    # Kültür & Tarih
    "tarihi yer": 55, "arkeoloji": 55, "müze": 50,
    "sanat galerisi": 50, "anıt": 50, "kale": 50,
    "camii": 48, "kilise": 48, "sinagog": 48, "tapınak": 48,

    # Yeme & İçme
    "organik": 60, "vegan": 58, "vejeteryan": 55,
    "deniz ürünleri": 35, "kafe": 30, "restoran": 25,
    "pastane": 25, "sokak yemeği": 20,
    "bar": 15, "fast food": 10,

    # Konaklama
    "kamp alanı": 60, "hostel": 40, "butik otel": 35,
    "apart": 30, "otel": 25, "tatil köyü": 20,

    # Alışveriş
    "pazar": 40, "antika": 35, "hediyelik": 25,
    "çarşı": 20, "alışveriş merkezi": 10,

    # Eğlence
    "tiyatro": 40, "konser": 38, "sinema": 30,
    "spor": 30, "spa": 28, "eğlence parkı": 20,
    "bowling": 15, "gece kulübü": 10,
}

DEFAULT_BASE_SCORE = 25

# 2. İsim/açıklama anahtar kelime bonusları
KEYWORD_BONUSES = {
    "milli park": 20, "tabiat parkı": 20, "koruma alanı": 18,
    "doğa dostu": 18, "organik": 15, "sürdürülebilir": 15,
    "mavi bayrak": 15, "ekolojik": 15, "yeşil": 10,
    "vegan": 12, "vejetaryen": 10, "yerel üretici": 12,
    "geri dönüşüm": 10, "güneş enerjisi": 12,
    "bisiklet": 8, "yürüyüş": 5, "sakin": 5, "huzurlu": 5,
}

def calculate_score(name, description, category, rating, 
                   user_ratings_total, price_level, 
                   permanently_closed, is_near_transit):
    # Kalıcı kapalıysa direkt 0
    if permanently_closed:
        return 0

    score = CATEGORY_BASE_SCORES.get(category, DEFAULT_BASE_SCORE) if category else DEFAULT_BASE_SCORE

    # Google puanı bonusu (max 20)
    if rating:
        if rating >= 4.5:
            score += 20
        elif rating >= 4.0:
            score += 14
        elif rating >= 3.5:
            score += 8
        elif rating < 3.0:
            score -= 10

    # Popülerlik bonusu (max 10)
    if user_ratings_total:
        if user_ratings_total >= 10000:
            score += 10
        elif user_ratings_total >= 1000:
            score += 6
        elif user_ratings_total >= 100:
            score += 3

    # Fiyat bonusu (ücretsiz/ucuz mekanlar daha erişilebilir)
    if price_level is not None:
        if price_level == 0:
            score += 10
        elif price_level == 1:
            score += 6
        elif price_level == 3:
            score -= 5
        elif price_level == 4:
            score -= 10

    # Toplu taşıma bonusu
    if is_near_transit:
        score += 25

    # Anahtar kelime bonusu
    text = f"{name or ''} {description or ''}".lower()
    for keyword, bonus in KEYWORD_BONUSES.items():
        if keyword in text:
            score += bonus

    return max(0, min(100, score))


def update_scores():
    conn = get_connection()
    cur = conn.cursor()

    print("🌱 Gelişmiş sürdürülebilirlik puanları hesaplanıyor...")

    try:
        cur.execute("""
            SELECT p.id, p.name, p.description, c.name as category,
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
        updated = 0
        transit_count = 0
        score_distribution = {
            "0-30": 0, "31-50": 0, "51-70": 0, "71-100": 0
        }

        for place in places:
            (place_id, name, description, category, rating,
             user_ratings_total, price_level, permanently_closed,
             is_near_transit) = place

            score = calculate_score(
                name, description, category, rating,
                user_ratings_total, price_level,
                permanently_closed, is_near_transit
            )

            cur.execute("""
                UPDATE places SET sustainability_score = %s WHERE id = %s;
            """, (score, place_id))

            updated += 1
            if is_near_transit:
                transit_count += 1

            if score <= 30:
                score_distribution["0-30"] += 1
            elif score <= 50:
                score_distribution["31-50"] += 1
            elif score <= 70:
                score_distribution["51-70"] += 1
            else:
                score_distribution["71-100"] += 1

        conn.commit()

        print(f"\n✅ {updated} mekan puanlandı!")
        print(f"🚇 {transit_count} mekan toplu taşımaya yakın (+25 bonus)")
        print(f"\n📊 Puan Dağılımı:")
        for range_name, count in score_distribution.items():
            bar = "█" * (count // 50)
            print(f"   {range_name}: {count:4d} mekan {bar}")

    except Exception as e:
        print(f"❌ Hata: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    update_scores()