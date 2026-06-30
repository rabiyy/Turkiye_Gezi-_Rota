import requests
import psycopg2
from db import get_connection

def fetch_transit_from_osm(city_name):
    print(f"{city_name} için OpenStreetMap'ten toplu taşıma verileri çekiliyor... Lütfen bekleyin.")
    
    # HTTP yerine güvenli HTTPS kullanıyoruz
    overpass_url = "https://overpass-api.de/api/interpreter"
    
    # Şehre ait metro, tren ve vapur iskelelerini getiren Overpass sorgusu
    overpass_query = f"""
    [out:json][timeout:50];
    area["name"="{city_name}"]->.searchArea;
    (
      node["railway"="station"](area.searchArea);
      node["station"="subway"](area.searchArea);
      node["amenity"="ferry_terminal"](area.searchArea);
    );
    out center;
    """
    
    # OSM sunucularına kendimizi tanıtıyoruz (406 hatasını çözen kısım)
    headers = {
        "User-Agent": "Surdurulebilir_Gezi_Rota_Bitirme_Projesi/1.0 (Student Project)",
        "Accept": "*/*"
    }
    
    try:
        # Sorguyu string olarak encode edip yolluyoruz
        response = requests.post(overpass_url, data=overpass_query.encode('utf-8'), headers=headers)
        response.raise_for_status()
        data = response.json()
        
        elements = data.get('elements', [])
        if not elements:
            print("İstasyon bulunamadı. Şehir adını kontrol edin.")
            return
            
        print(f"Toplam {len(elements)} adet istasyon/iskele bulundu. Veritabanına kaydediliyor...")
        
        conn = get_connection()
        cur = conn.cursor()
        
        saved_count = 0
        for element in elements:
            # İstasyon adı yoksa 'Bilinmeyen İstasyon' yaz
            name = element.get('tags', {}).get('name', 'Bilinmeyen İstasyon')
            lat = element.get('lat')
            lon = element.get('lon')
            
            # Etiketlere göre tipini belirle
            transit_type = "metro/tren"
            if element.get('tags', {}).get('amenity') == 'ferry_terminal':
                transit_type = "vapur"
                
            # Veritabanına kaydet (PostGIS Point formatında)
            cur.execute("""
                INSERT INTO public_transit (name, transit_type, location, city)
                VALUES (%s, %s, ST_SetSRID(ST_MakePoint(%s, %s), 4326), %s)
            """, (name, transit_type, lon, lat, city_name)) # Dikkat: Önce Boylam, Sonra Enlem
            
            saved_count += 1
            
        conn.commit()
        print(f"✅ {saved_count} istasyon başarıyla 'public_transit' tablosuna eklendi!")
        
    except Exception as e:
        print(f"Hata oluştu: {e}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Marmara ve Ege bölgesindeki ana hedef şehirlerimiz
    target_cities = [
        "İstanbul", "İzmir", "Bursa", "Çanakkale", "Balıkesir", 
        "Aydın", "Muğla", "Manisa", "Tekirdağ", "Kocaeli"
    ]
    
    print("🌍 Ege ve Marmara bölgeleri toplu taşıma verisi indirmesi başlatılıyor...\n")
    
    for city in target_cities:
        fetch_transit_from_osm(city)
        
    print("\n🏆 Tüm hedef şehirlerin ulaşım verileri veritabanına başarıyla kaydedildi!")