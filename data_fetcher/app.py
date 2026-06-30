import urllib.parse
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import Flask, request, jsonify
from flask_cors import CORS

from chatbot import (
    search_similar_places, 
    generate_chat_response, 
    is_route_request, 
    parse_stops_from_query, 
    generate_route_from_stops, 
    SUPPORTED_CITIES, 
    CATEGORY_KEYWORDS
)

app = Flask(__name__)
CORS(app)  # Arayüzün bu server'a bağlanabilmesi için izin verir

# --- VERİTABANI AYARLARI ---
DB_CONFIG = {
    "dbname": "sustainable_travel",
    "user": "postgres",
    "password": "postgres", 
    "host": "localhost",
    "port": "5432"
}

def get_db_connection():
    return psycopg2.connect(**DB_CONFIG)

chat_history = []  # Geçici hafıza

# --- CHAT ENDPOINT ---
@app.route('/chat', methods=['POST'])
def chat_endpoint():
    data = request.json
    user_query = data.get('message')

    if not user_query:
        return jsonify({"error": "Mesaj boş olamaz"}), 400

    gizli_kural = "\n(ÖNEMLİ KURAL: Lütfen önereceğin mekanların adresini mutlaka yeni bir satırda tam olarak 'Konum: [İl/İlçe/Adres]' formatında yaz. Başka kelime kullanma.)"
    ai_sorgusu = user_query + gizli_kural

    if is_route_request(user_query):
        # Rota analizi için orijinal sorguyu kullan
        stops = parse_stops_from_query(user_query, SUPPORTED_CITIES, CATEGORY_KEYWORDS)
        if stops:
            response_text = generate_route_from_stops(stops)
        else:
            response_text = "Rota isteğini tam anlayamadım, biraz daha detay verir misin?"
    else:
        places = search_similar_places(user_query)
        
        response_text = generate_chat_response(ai_sorgusu, places, chat_history)

    chat_history.append(f"Kullanıcı: {user_query}")
    chat_history.append(f"Asistan: {response_text}")

    return jsonify({"response": response_text})

# --- NAVBAR KATEGORİ SORGUSU ---
@app.route('/api/yerler', methods=['GET'])
def get_places_by_category():
    kategori_adi = request.args.get('kategori')
    
    if not kategori_adi:
        return jsonify({"results": []}), 400

    kategori_temiz = kategori_adi.strip().lower()

    # db kategorilerine eşleştirme sözlüğü 
    kategori_haritasi = {
        "kale": "kale",
        "tiyatro": "tiyatro",
        "anıt": "anıt",
        "cami": "camii",
        "kilise": "kilise",
        "sinagog": "sinagog",
        "müze": "müze",
        "sanat galerisi": "sanat galerisi",
        "göl": "göl",
        "orman": "orman",
        "milli park": "park",
        "tabiat parkı": "park",
        "kanyon": "şelale",
        "piknik alanı": "piknik",
        "kamp alanı": "kamp",
        "botanik bahçesi": "botanik bahçesi",
        "hayvanat bahçesi": "hayvanat bahçesi",
        "akvaryum": "akvaryum",
        "plaj": "plaj",
        "restoran": "restoran",
        "kafe": "kafe",
        "pastane": "pastane",
        "meyhane": "bar",
        "çay bahçesi": "kafe",
        "yöresel ürün noktası": "pazar"
    }

    isimden_aranacaklar = ["antik kent", "köprü", "saat kulesi", "hamam", "kütüphane"]

    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Eğer kategori isminden aranması gereken gruptaysa direkt isimde ara
        if kategori_temiz in isimden_aranacaklar:
            query = """
                SELECT * 
                FROM places 
                WHERE name ILIKE %s
                LIMIT 15;
            """
            cur.execute(query, (f"%{kategori_temiz}%",))
        
        # Diğer tüm kategoriler için normal akış
        else:
            db_kategori_adi = kategori_haritasi.get(kategori_temiz, kategori_temiz)
            query = """
                SELECT p.* 
                FROM places p
                JOIN place_categories pc ON p.id = pc.place_id
                JOIN categories c ON c.id = pc.category_id
                WHERE c.name ILIKE %s
                LIMIT 15;
            """
            cur.execute(query, (f"%{db_kategori_adi}%",))

        results = cur.fetchall()
        
        # --- GARANTİLİ YEDEK LİNK ÜRETİCİ ---
        for row in results:
            arama_metni = f"{row['name']} {row['city']}"
            encoded_metin = urllib.parse.quote(arama_metni)
            row['map_url'] = f"https://www.google.com/maps/search/?api=1&query={encoded_metin}"
            
        cur.close()
        conn.close()
        
        return jsonify({"results": results})
        
    except Exception as e:
        print(f"Veritabanı hatası: {e}")
        return jsonify({"error": "Veritabanına bağlanılamadı"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)