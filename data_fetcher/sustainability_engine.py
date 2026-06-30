import psycopg2
from db import get_connection

# Kategorilere göre temel sürdürülebilirlik ve yeşil etiket atama kuralları
SCORING_RULES = {
    "doğa & açık hava": {"base_score": 85, "tags": ["Doğa Dostu", "Açık Hava", "Temiz Hava"]},
    "orman": {"base_score": 95, "tags": ["Doğa Dostu", "Yüksek Oksijen", "Biyoçeşitlilik"]},
    "park": {"base_score": 80, "tags": ["Yeşil Alan", "Açık Hava"]},
    "plaj": {"base_score": 75, "tags": ["Doğa", "Su Kenarı"]},
    "kamp": {"base_score": 90, "tags": ["Ekoturizm", "Doğa Dostu", "Düşük Karbon"]},
    "müze": {"base_score": 70, "tags": ["Kültürel Miras", "Eğitici"]},
    "tarihi yer": {"base_score": 75, "tags": ["Kültürel Miras", "Koruma Alanı"]},
    "vegan": {"base_score": 85, "tags": ["Vegan", "Düşük Karbon Ayak İzi", "Hayvan Dostu"]},
    "vejeteryan": {"base_score": 80, "tags": ["Vejetaryen", "Sürdürülebilir Tarım"]},
    "organik": {"base_score": 90, "tags": ["Organik", "Yerel Üretim", "Doğa Dostu"]},
    "fast food": {"base_score": 20, "tags": ["Yüksek Karbon", "Paketli Tüketim"]},
    "alışveriş merkezi": {"base_score": 30, "tags": ["Yüksek Enerji Tüketimi"]}
}

def run_sustainability_engine():
    print("🌱 Sürdürülebilirlik Motoru Başlatılıyor...")
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        # Tüm mekanları kategorileriyle birlikte çek
        cur.execute("""
            SELECT p.id, c.name 
            FROM places p
            JOIN place_categories pc ON p.id = pc.place_id
            JOIN categories c ON pc.category_id = c.id
        """)
        places = cur.fetchall()
        
        updated_count = 0
        
        for place_id, category_name in places:
            score = 50 # Varsayılan ortalama puan
            tags = []
            
            # Kategoriye göre puan ve etiket hesapla
            if category_name in SCORING_RULES:
                score = SCORING_RULES[category_name]["base_score"]
                tags = SCORING_RULES[category_name]["tags"]
            
            # TODO: İleride buraya PostGIS ile toplu taşıma duraklarına uzaklık hesaplaması eklenecek
            # ve durağa yakınsa skora +15 puan eklenecek.
            
            # Veritabanını güncelle
            cur.execute("""
                UPDATE places 
                SET sustainability_score = %s, green_tags = %s
                WHERE id = %s
            """, (score, tags, place_id))
            
            updated_count += 1
            
        conn.commit()
        print(f"✅ {updated_count} mekan başarıyla analiz edildi ve puanlandı!")
        
    except Exception as e:
        print(f"Hata: {e}")
        conn.rollback()
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    run_sustainability_engine()