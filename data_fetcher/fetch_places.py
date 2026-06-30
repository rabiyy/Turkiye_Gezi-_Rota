import requests
import psycopg2
import argparse
import json
from db import get_connection

# GOOGLE API ANAHTARINI BURAYA YAZ
GOOGLE_API_KEY = "AIzaSyDOP3tIBNC2spK655uGM6VwjwDJmhTkgYk"

def fetch_and_store_places(city, category, limit):
    print(f"[{city}] için '{category}' kategorisinde mekanlar aranıyor...")
    
    # Google Text Search API Endpoint
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    
    # Arama sorgusunu oluştur (Örn: "İstanbul plaj")
    query = f"{city} {category}"
    
    params = {
        'query': query,
        'key': GOOGLE_API_KEY,
        'language': 'tr'
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # --- GOOGLE'IN GİZLİ HATALARINI YAKALAYALIM ---
        status = data.get('status')
        if status != 'OK' and status != 'ZERO_RESULTS':
            error_msg = data.get('error_message', 'Bilinmeyen bir API hatası.')
            print(f"❌ GOOGLE API İZNİ REDDETTİ: Durum: {status} | Mesaj: {error_msg}")
            return
        # ---------------------------------------------
        
        results = data.get('results', [])
        
        if not results:
            print("Mekan gerçekten bulunamadı.")
            return

        conn = get_connection()
        cur = conn.cursor()
        
        saved_count = 0
        
        # Limiti uygula
        for place in results[:limit]:
            name = place.get('name')
            address = place.get('formatted_address', 'Adres bulunamadı')
            lat = place['geometry']['location']['lat']
            lng = place['geometry']['location']['lng']
            rating = place.get('rating', 0.0)
            user_ratings_total = place.get('user_ratings_total', 0)
            
            # --- YENİ EKLENEN VERİLERİN İŞLENMESİ ---
            
            # 1. Fiyat Seviyesi (0-4 arası, yoksa None)
            price_level = place.get('price_level')
            
            # 2. Mekan Kapalı mı? (Business status'u kontrol et)
            business_status = place.get('business_status', 'OPERATIONAL')
            permanently_closed = True if business_status == 'CLOSED_PERMANENTLY' else False
            
            # 3. Direkt Google Maps Linki
            place_id = place.get('place_id')
            google_maps_url = f"https://www.google.com/maps/place/?q=place_id:{place_id}" if place_id else None
            
            # 4. Fotoğraflar
            photos = place.get('photos', [])
            photo_refs = [photo['photo_reference'] for photo in photos[:3]] 
            photo_references_json = json.dumps(photo_refs) if photo_refs else None
            
            # --- 1. MEKANI VERİTABANINA KAYDET ---
            try:
                cur.execute("""
                    INSERT INTO places (
                        name, address, location, rating, user_ratings_total,
                        price_level, permanently_closed, google_maps_url, photo_references
                    ) VALUES (
                        %s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s, %s,
                        %s, %s, %s, %s
                    ) RETURNING id;
                """, (name, address, lng, lat, rating, user_ratings_total,
                      price_level, permanently_closed, google_maps_url, photo_references_json))
                
                new_place_id = cur.fetchone()[0]
                
                # --- 2. KATEGORİ İŞLEMLERİ (İlişkiyi Kurma) ---
                # Önce bu kategori veritabanında var mı diye bak, yoksa oluştur
                cur.execute("SELECT id FROM categories WHERE name = %s;", (category,))
                cat_result = cur.fetchone()
                
                if cat_result:
                    category_id = cat_result[0]
                else:
                    cur.execute("INSERT INTO categories (name) VALUES (%s) RETURNING id;", (category,))
                    category_id = cur.fetchone()[0]
                
                # Mekan ile Kategoriyi birbirine bağla
                cur.execute("""
                    INSERT INTO place_categories (place_id, category_id)
                    VALUES (%s, %s) ON CONFLICT DO NOTHING;
                """, (new_place_id, category_id))
                
                saved_count += 1
                
            except Exception as db_err:
                print(f"Kayıt atlandı ({name}): {db_err}")
                conn.rollback() # Hata olan kaydı geri al, döngüye devam et
                continue
            
        conn.commit()
        print(f"✅ {saved_count} mekan başarıyla kaydedildi!")
        
    except Exception as e:
        print(f"API veya Bağlantı Hatası: {e}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Terminalden gönderilen argümanları yakala
    parser = argparse.ArgumentParser(description="Google Places'den mekan çeker.")
    parser.add_argument("--city", required=True, help="Aranacak şehir")
    parser.add_argument("--category", required=True, help="Aranacak kategori")
    parser.add_argument("--limit", type=int, default=20, help="Çekilecek maksimum mekan sayısı")
    
    args = parser.parse_args()
    
    fetch_and_store_places(args.city, args.category, args.limit)