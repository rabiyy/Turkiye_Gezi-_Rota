import math
from db import get_connection
from sentence_transformers import SentenceTransformer

model = None

def get_model():
    global model
    if model is None:
        model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')
    return model

def calculate_distance(lon1, lat1, lon2, lat2):
    """İki koordinat arasındaki mesafeyi metre cinsinden hesaplar (Haversine)."""
    R = 6371000
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def find_best_place(query_text, city_filter=None, exclude_names=None):
    """
    Verilen sorgu, şehir ve hariç tutulacak mekan listesine göre
    veritabanından en uygun mekanı bulur.
    """
    m = get_model()
    vector = m.encode(query_text).tolist()
    conn = get_connection()
    cur = conn.cursor()

    try:
        sql = """
            SELECT p.name, p.address, p.sustainability_score,
                   ST_X(p.location::geometry) as lon,
                   ST_Y(p.location::geometry) as lat,
                   c.name as category,
                   p.city
            FROM places p
            LEFT JOIN place_categories pc ON p.id = pc.place_id
            LEFT JOIN categories c ON pc.category_id = c.id
            WHERE p.embedding IS NOT NULL
            AND p.location IS NOT NULL
        """
        params = []

        if exclude_names:
            sql += " AND p.name != ALL(%s)"
            params.append(exclude_names)

        if city_filter:
            sql += " AND unaccent(lower(p.city)) = unaccent(lower(%s))"
            params.append(city_filter)

        sql += " ORDER BY p.embedding <=> %s::vector LIMIT 1"
        params.append(vector)

        cur.execute(sql, params)
        result = cur.fetchone()

        # Şehir filtresiyle bulunamazsa filtresiz dene
        if not result and city_filter:
            sql2 = """
                SELECT p.name, p.address, p.sustainability_score,
                       ST_X(p.location::geometry) as lon,
                       ST_Y(p.location::geometry) as lat,
                       c.name as category,
                       p.city
                FROM places p
                LEFT JOIN place_categories pc ON p.id = pc.place_id
                LEFT JOIN categories c ON pc.category_id = c.id
                WHERE p.embedding IS NOT NULL
                AND p.location IS NOT NULL
            """
            params2 = []
            if exclude_names:
                sql2 += " AND p.name != ALL(%s)"
                params2.append(exclude_names)
            sql2 += " ORDER BY p.embedding <=> %s::vector LIMIT 1"
            params2.append(vector)
            cur.execute(sql2, params2)
            result = cur.fetchone()

        return result

    finally:
        cur.close()
        conn.close()


def optimize_route(places):
    """
    Nearest Neighbor algoritmasıyla en kısa rotayı hesaplar.
    Sırayı kullanıcının istediği gibi korur — optimize sadece
    aynı şehirdeki duraklar arasında yapılır.
    """
    if not places:
        return []
    if len(places) == 1:
        return places

    # Şehirleri grupla: aynı şehirdeki durakları kendi aralarında optimize et
    # ama farklı şehirler arası sırayı koru
    result = []
    i = 0
    while i < len(places):
        current_city = places[i][6]  # city kolonu
        group = [places[i]]
        j = i + 1
        while j < len(places) and places[j][6] == current_city:
            group.append(places[j])
            j += 1

        # Grup içinde Nearest Neighbor uygula
        if len(group) > 1:
            unvisited = group[1:]
            current = group[0]
            optimized = [current]
            while unvisited:
                nearest = min(unvisited, key=lambda p: calculate_distance(
                    current[3], current[4], p[3], p[4]
                ))
                unvisited.remove(nearest)
                optimized.append(nearest)
                current = nearest
            result.extend(optimized)
        else:
            result.extend(group)

        i = j

    return result


def parse_stops_from_query(user_input, supported_cities, category_keywords):
    """
    Kullanıcının mesajından durak listesi çıkarır.
    Her durak: (sorgu_metni, şehir, kategori) şeklinde.
    
    Örnek:
    "kocaelide kahvemi içip istanbulda plajda takılacağım ve akşam yemeği yiyeceğim"
    → [("kafe Kocaeli", "Kocaeli", "kafe"),
       ("plaj İstanbul", "İstanbul", "plaj"),
       ("restoran İstanbul", "İstanbul", "restoran")]
    """
    text = user_input.lower()
    stops = []
    
    # Metni şehir geçişlerine göre böl
    # Önce tüm şehir pozisyonlarını bul
    city_positions = []
    for key, value in supported_cities.items():
        idx = text.find(key)
        if idx != -1:
            city_positions.append((idx, value, key))
    
    # Pozisyona göre sırala
    city_positions.sort(key=lambda x: x[0])
    
    if not city_positions:
        # Şehir bulunamazsa kategorileri çıkar
        for keyword in sorted(category_keywords.keys(), key=len, reverse=True):
            if keyword in text:
                cat = category_keywords[keyword]
                stops.append((keyword, None, cat))
        return stops
    
    # Her şehir bölümündeki kategorileri bul
    # Metin parçalarını şehir pozisyonlarına göre böl
    segments = []
    for i, (pos, city, key) in enumerate(city_positions):
        if i + 1 < len(city_positions):
            next_pos = city_positions[i+1][0]
            segment_text = text[pos:next_pos]
        else:
            segment_text = text[pos:]
        segments.append((city, segment_text))
    
    # Şehirden önce de kategori olabilir (ilk şehirden önceki kısım)
    first_city_pos = city_positions[0][0]
    if first_city_pos > 0:
        pre_text = text[:first_city_pos]
        first_city = city_positions[0][1]
        for keyword in sorted(category_keywords.keys(), key=len, reverse=True):
            if keyword in pre_text:
                cat = category_keywords[keyword]
                query = f"{keyword} {first_city}"
                stops.append((query, first_city, cat))
    
    # Her segmentteki kategorileri bul
    for city, segment in segments:
        found_cats = []
        for keyword in sorted(category_keywords.keys(), key=len, reverse=True):
            if keyword in segment:
                cat = category_keywords[keyword]
                if cat not in found_cats:
                    found_cats.append(cat)
                    query = f"{keyword} {city}"
                    stops.append((query, city, cat))
    
    return stops


def generate_route_for_queries(queries: list[str], city_filter=None) -> str:
    """
    Basit sorgu listesinden rota oluşturur.
    Her sorgu "kafe İstanbul" gibi mekan tipi + şehir içerir.
    """
    print(f"\n🗺️  {len(queries)} durak için rota hesaplanıyor...")

    places = []
    found_names = []

    for query in queries:
        # Sorgudan şehri çıkar
        city = city_filter
        if not city:
            from chatbot import detect_city
            city = detect_city(query)

        place = find_best_place(query, city_filter=city, exclude_names=found_names)
        if place:
            places.append(place)
            found_names.append(place[0])
            print(f"   ✅ '{query}' → {place[0]} ({place[6]})")
        else:
            print(f"   ⚠️  '{query}' için mekan bulunamadı.")

    return _format_route(optimize_route(places))


def generate_route_from_stops(stops: list[tuple]) -> str:
    """
    (sorgu, şehir, kategori) listesinden rota oluşturur.
    Çoklu şehir desteği var.
    """
    print(f"\n🗺️  {len(stops)} durak için rota hesaplanıyor...")

    places = []
    found_names = []

    for query, city, category in stops:
        place = find_best_place(query, city_filter=city, exclude_names=found_names)
        if place:
            places.append(place)
            found_names.append(place[0])
            print(f"   ✅ '{query}' ({city or 'Tüm bölge'}) → {place[0]}")
        else:
            print(f"   ⚠️  '{query}' için mekan bulunamadı.")

    if not places:
        return "Rota oluşturmak için yeterli mekan bulunamadı."

    route = optimize_route(places)
    return _format_route(route)


def _format_route(route: list) -> str:
    """Rota listesini okunabilir metne çevirir."""
    if not route:
        return "Rota oluşturulamadı."

    result = "\n🗺️  OPTİMİZE SÜRDÜRÜLEBİLİR ROTA\n"
    result += "=" * 45 + "\n"

    total_distance = 0
    prev_city = None

    for i, place in enumerate(route, 1):
        name, address, score, lon, lat, category, city = place
        cat = category or "Genel"
        eco = "🌿 Çevre Dostu" if score and score >= 70 else "📍"

        # Şehir değişimi varsa belirt
        if city != prev_city:
            result += f"\n📌 {city or 'Bilinmeyen Şehir'}\n"
            result += "-" * 30 + "\n"
            prev_city = city

        result += f"\n{i}. DURAK: {name}\n"
        result += f"   Kategori  : {cat}\n"
        result += f"   Puan      : {score}/100 {eco}\n"
        result += f"   Adres     : {address}\n"

        if i < len(route):
            next_place = route[i]
            dist = calculate_distance(lon, lat, next_place[3], next_place[4])
            total_distance += dist
            next_city = next_place[6]
            if next_city != city:
                result += f"   ⬇️  {next_city}'e geçiş: {dist/1000:.1f} km\n"
            else:
                result += f"   ⬇️  Sonraki durağa: {dist/1000:.1f} km\n"

    result += f"\n{'='*45}\n"
    result += f"📏 Toplam Mesafe : {total_distance/1000:.1f} km\n"

    valid_scores = [p[2] for p in route if p[2] and p[2] > 0]
    if valid_scores:
        avg_score = sum(valid_scores) / len(valid_scores)
        result += f"🌱 Ort. Sürd. Puanı: {avg_score:.0f}/100\n"

    cities_in_route = list(dict.fromkeys(p[6] for p in route if p[6]))
    if len(cities_in_route) > 1:
        result += f"🏙️  Geçilen Şehirler: {' → '.join(cities_in_route)}\n"

    return result


if __name__ == "__main__":
    result = generate_route_for_queries([
        "kafe Kocaeli",
        "plaj İstanbul",
        "restoran İstanbul"
    ])
    print(result)