import os
from db import get_connection
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv
from route_planner import generate_route_from_stops, generate_route_for_queries, parse_stops_from_query

load_dotenv()

client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={'api_version': 'v1alpha'}
)

print("🧠 Yapay Zeka modelleri yükleniyor... Lütfen bekleyin.")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

# ---------------------------------------------------------------
# DESTEKLENEN ŞEHİRLER (Marmara & Ege Bölgesi)
# ---------------------------------------------------------------
SUPPORTED_CITIES = {
    "istanbul": "İstanbul",
    "i̇stanbul": "İstanbul",
    "izmir": "İzmir",
    "i̇zmir": "İzmir",
    "bursa": "Bursa",
    "çanakkale": "Çanakkale",
    "balıkesir": "Balıkesir",
    "aydın": "Aydın",
    "muğla": "Muğla",
    "manisa": "Manisa",
    "tekirdağ": "Tekirdağ",
    "kocaeli": "Kocaeli"
}

OUT_OF_SCOPE_CITIES = [
    "ankara", "antalya", "konya", "adana", "trabzon",
    "samsun", "gaziantep", "diyarbakır", "erzurum", "kayseri",
    "eskişehir", "mersin", "malatya", "isparta", "düzce"
]

CATEGORY_KEYWORDS = {
    "kafe": "kafe",
    "cafe": "kafe",
    "coffee": "kafe",
    "kahve": "kafe",
    "kahvaltı": "kafe",
    "restoran": "restoran",
    "yemek": "restoran",
    "yeme": "restoran",
    "akşam yemeği": "restoran",
    "öğle yemeği": "restoran",
    "vegan": "vegan",
    "vejeteryan": "vejeteryan",
    "vejetaryen": "vejeteryan",
    "organik": "organik",
    "deniz ürünleri": "deniz ürünleri",
    "balık": "deniz ürünleri",
    "müze": "müze",
    "tarihi": "tarihi yer",
    "tarih": "tarihi yer",
    "arkeoloji": "arkeoloji",
    "kale": "kale",
    "camii": "camii",
    "cami": "camii",
    "kilise": "kilise",
    "plaj": "plaj",
    "sahil": "plaj",
    "kumsal": "plaj",
    "deniz": "plaj",
    "park": "park",
    "orman": "orman",
    "doğa": "park",
    "yürüyüş": "doğa yürüyüşü",
    "kamp": "kamp",
    "otel": "otel",
    "konaklama": "otel",
    "hostel": "hostel",
    "apart": "apart",
    "çarşı": "çarşı",
    "avm": "alışveriş merkezi",
    "alışveriş": "çarşı",
    "pazar": "pazar",
    "antika": "antika",
    "bar": "bar",
    "gece": "gece kulübü",
    "tiyatro": "tiyatro",
    "sinema": "sinema",
    "spa": "spa",
    "botanik": "botanik bahçesi",
    "hayvanat": "hayvanat bahçesi",
    "akvaryum": "akvaryum",
}

ROUTE_KEYWORDS = [
    "rota", "güzergah", "güzergâh", "optimize",
    "sırayla", "nasıl gidebilirim", "gidip", "geçip",
    "ardından", "sonra", "önce"
]

ROUTE_PLACE_KEYWORDS = [
    "müze", "arkeoloji", "tarihi", "plaj", "sahil", "kumsal",
    "restoran", "yemek", "vegan", "vejeteryan", "kafe", "cafe",
    "coffee", "kahve", "park", "camii", "kilise", "kale", "çarşı",
    "pazar", "otel", "hostel", "bar", "tiyatro", "spa", "orman",
    "akşam yemeği", "öğle yemeği"
]


def detect_city(text):
    """Sorguda geçen desteklenen şehri döndürür."""
    text_lower = text.lower()
    for key, value in SUPPORTED_CITIES.items():
        if key in text_lower:
            return value
    return None


def detect_all_cities(text):
    """Sorguda geçen tüm desteklenen şehirleri döndürür."""
    text_lower = text.lower()
    found = []
    for key, value in SUPPORTED_CITIES.items():
        if key in text_lower and value not in found:
            found.append(value)
    return found


def detect_category(text):
    """Sorguda geçen kategori kelimesini döndürür."""
    text_lower = text.lower()
    for keyword in sorted(CATEGORY_KEYWORDS.keys(), key=len, reverse=True):
        if keyword in text_lower:
            return CATEGORY_KEYWORDS[keyword]
    return None


def is_route_request(text):
    """
    Kullanıcının rota isteği yapıp yapmadığını tespit eder.
    Birden fazla şehir veya rota kelimesi varsa True döner.
    """
    text_lower = text.lower()

    # Açık rota kelimeleri
    if any(word in text_lower for word in ["rota", "güzergah", "optimize"]):
        return True

    # Birden fazla şehir geçiyorsa rota isteği
    cities_found = detect_all_cities(text)
    if len(cities_found) >= 2:
        return True

    # "ardından", "sonra", "önce" gibi sıralama kelimeleri + kategori varsa
    sequence_words = ["ardından", "sonra", "önce", "gidip", "geçip", "oradan"]
    has_sequence = any(w in text_lower for w in sequence_words)
    has_category = any(kw in text_lower for kw in ROUTE_PLACE_KEYWORDS)
    if has_sequence and has_category:
        return True

    return False


def search_similar_places(query_text, limit=5, exclude_names=None):
    """
    Kullanıcının sorgusuna en uygun mekanları veritabanından bulur.
    """
    query_vector = model.encode(query_text).tolist()
    city_filter = detect_city(query_text)
    category_filter = detect_category(query_text)

    conn = get_connection()
    cur = conn.cursor()

    try:
        category_ids = []
        if category_filter:
            cur.execute(
                "SELECT id FROM categories WHERE name ILIKE %s",
                (f"%{category_filter}%",)
            )
            category_ids = [row[0] for row in cur.fetchall()]

        def run_query(use_city, use_category):
            sql = """
                SELECT p.name, p.description, p.address,
                       p.sustainability_score, p.city
                FROM places p
                WHERE p.embedding IS NOT NULL
            """
            params = []

            if exclude_names:
                sql += " AND p.name != ALL(%s)"
                params.append(exclude_names)

            if use_city and city_filter:
                sql += " AND unaccent(lower(p.city)) = unaccent(lower(%s))"
                params.append(city_filter)

            if use_category and category_ids:
                sql += " AND p.id IN (SELECT place_id FROM place_categories WHERE category_id = ANY(%s))"
                params.append(category_ids)

            sql += " ORDER BY p.embedding <=> %s::vector LIMIT %s"
            params.extend([query_vector, limit])
            cur.execute(sql, params)
            return cur.fetchall()

        results = run_query(use_city=True, use_category=True)
        if not results:
            results = run_query(use_city=True, use_category=False)
        if not results:
            results = run_query(use_city=False, use_category=True)
        if not results:
            results = run_query(use_city=False, use_category=False)

        return [r[:5] for r in results]

    except Exception as e:
        print(f"Arama Hatası: {e}")
        return []
    finally:
        cur.close()
        conn.close()


def generate_chat_response(user_query, places, chat_history):
    if not places:
        return "Üzgünüm, aradığın kriterlere uygun bir mekan bulamadım. Farklı bir kategori veya şehir deneyin!"

    context = "İşte kullanıcının isteğine en uygun gerçek mekan verileri:\n\n"
    for i, p in enumerate(places, 1):
        name, desc, addr, score, cat = p
        context += (
            f"{i}. Mekan: {name}\n"
            f"   Kategori: {cat or 'Belirtilmemiş'}\n"
            f"   Sürdürülebilirlik Skoru: {score}/100\n"
            f"   Adres: {addr}\n"
            f"   Açıklama: {desc or 'Bilgi mevcut değil'}\n\n"
        )

    history_text = ""
    if chat_history:
        history_text = "Önceki konuşma:\n" + "\n".join(chat_history[-6:]) + "\n\n"

    system_instruction = """
    Sen 'Gezirota Sürdürülebilir Gezi Asistanı'sın.
    Sadece Marmara ve Ege bölgesindeki şu şehirleri kapsıyorsun:
    İstanbul, İzmir, Bursa, Muğla, Çanakkale, Balıkesir, Aydın, Manisa, Tekirdağ, Kocaeli.

    KURALLAR:
    1. SADECE sana sunulan gerçek mekan verilerini kullan, asla uydurma.
    2. Sana sunulan TÜM mekanları tek tek anlat.
    3. Kullanıcı belirli bir şehir istiyorsa SADECE o şehirdeki mekanları öner.
    4. Sürdürülebilirlik puanı 70+ ise 'çevre dostu' olarak öv.
    5. Samimi, sıcak ve yardımsever bir dil kullan.
    6. Cevabın sonunda kullanıcıyı başka bir şey sormaya teşvik et.
    """

    prompt = f"{system_instruction}\n\n{history_text}Mekan Verileri:\n{context}\nKullanıcı Sorusu: {user_query}"

    try:
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        return response.text
    except Exception as e:
        return f"Gemini API Hatası: {e}"


def chat():
    print("\n" + "="*55)
    print("🌱  GEZIROTA SÜRDÜRÜLEBİLİR GEZİ ASİSTANI  🌱")
    print("📍  Kapsanan Bölge: Marmara & Ege")
    print("💡  'q' yazarak çıkabilirsin.")
    print("="*55)

    chat_history = []
    shown_places = []

    while True:
        user_input = input("\n👤 Sen: ").strip()

        if user_input.lower() in ['q', 'exit', 'çıkış']:
            print("\n👋 İyi yolculuklar!")
            break

        if not user_input:
            continue

        print("🤖 Asistan: Veritabanını analiz ediyorum...")

        # ---------------------------------------------------------
        # 1. KAPSAM DIŞI ŞEHİR KONTROLÜ
        # ---------------------------------------------------------
        if any(city in user_input.lower() for city in OUT_OF_SCOPE_CITIES):
            msg = (
                "Üzgünüm, bu şehir projemizin kapsadığı Marmara ve Ege "
                "bölgesinin dışında kalıyor. Sana şu şehirler için yardımcı olabilirim:\n"
                "İstanbul, İzmir, Bursa, Muğla, Çanakkale, Balıkesir, "
                "Aydın, Manisa, Tekirdağ, Kocaeli 🗺️"
            )
            print(f"\n🤖 Asistan:\n{msg}")
            continue

        # ---------------------------------------------------------
        # 2. ROTA İSTEĞİ KONTROLÜ
        # ---------------------------------------------------------
        if is_route_request(user_input):
            stops = parse_stops_from_query(
                user_input,
                SUPPORTED_CITIES,
                CATEGORY_KEYWORDS
            )

            if stops:
                route_result = generate_route_from_stops(stops)
            else:
                city = detect_city(user_input)
                queries = []
                for kw in ROUTE_PLACE_KEYWORDS:
                    if kw in user_input.lower():
                        cat = CATEGORY_KEYWORDS.get(kw, kw)
                        queries.append(f"{cat} {city or ''}")
                if not queries:
                    queries = [user_input]
                route_result = generate_route_for_queries(queries, city_filter=city)

            # Rotayı Gemini ile güzelleştir
            try:
                route_prompt = f"""
                Sen 'Gezirota Sürdürülebilir Gezi Asistanı'sın.
                Aşağıdaki rota bilgilerini kullanarak kullanıcıya samimi, sıcak ve heyecanlı bir dille anlat.
                Her durağı kısaca tanıt, sürdürülebilirlik puanı 70+ olanları 'çevre dostu' olarak öv.
                Rotayı olduğu gibi koru, mekan ekleyip çıkarma.
                
                Rota Verisi:
                {route_result}
                
                Kullanıcı İsteği: {user_input}
                """
                gemini_response = client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=route_prompt,
                )
                print(f"\n🤖 Asistan:\n{gemini_response.text}")
                chat_history.append(f"Kullanıcı: {user_input}")
                chat_history.append(f"Asistan: {gemini_response.text}")
            except Exception as e:
                # Gemini hata verirse direkt rotayı göster
                print(f"\n🤖 Asistan:\n{route_result}")
                chat_history.append(f"Kullanıcı: {user_input}")
                chat_history.append(f"Asistan: {route_result}")
            continue


if __name__ == "__main__":
    chat()