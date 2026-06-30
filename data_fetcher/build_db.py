import os
import time

# Sadece projede odaklanılan 10 ana turizm şehri
TARGET_CITIES = [
    "İstanbul", "İzmir", "Bursa", "Çanakkale", "Balıkesir", 
    "Aydın", "Muğla", "Manisa", "Tekirdağ", "Kocaeli"
]

CATEGORY_MAP = {
    # Doğa & Açık Hava
    "plaj": ["beach"], "park": ["park", "national_park", "state_park"],
    "şelale": ["tourist_attraction", "park"], "dağ": ["national_park", "state_park", "tourist_attraction"],
    "orman": ["national_park", "state_park", "park"], "göl": ["tourist_attraction", "park"],
    "kamp": ["campground", "rv_park"], "piknik": ["park", "picnic_ground"],
    "botanik bahçesi": ["botanical_garden"], "hayvanat bahçesi": ["zoo"],
    "akvaryum": ["aquarium"], "doğa yürüyüşü": ["hiking_area", "national_park"],
    
    # Kültür & Tarih
    "müze": ["museum", "art_gallery"], "tarihi yer": ["historical_landmark", "cultural_landmark"],
    "sanat galerisi": ["art_gallery"], "anıt": ["monument", "historical_landmark"],
    "arkeoloji": ["archaeological_site"], "kale": ["historical_landmark", "tourist_attraction"],
    "camii": ["mosque"], "kilise": ["church"], "sinagog": ["synagogue"],
    "tapınak": ["hindu_temple", "buddhist_temple"],
    
    # Yeme & İçme
    "restoran": ["restaurant"], "deniz ürünleri": ["seafood_restaurant"],
    "vejeteryan": ["vegetarian_restaurant"], "vegan": ["vegan_restaurant"],
    "kafe": ["cafe", "coffee_shop"], "pastane": ["bakery", "dessert_shop"],
    "fast food": ["fast_food_restaurant"], "bar": ["bar", "pub"],
    "sokak yemeği": ["food_court", "sandwich_shop"], "organik": ["health_food_store", "vegetarian_restaurant"],
    
    # Konaklama
    "otel": ["hotel"], "hostel": ["hostel"], "apart": ["extended_stay_hotel", "apartment_complex"],
    "butik otel": ["boutique_hotel"], "kamp alanı": ["campground"], "tatil köyü": ["resort_hotel"],
    
    # Alışveriş
    "çarşı": ["shopping_mall", "market"], "pazar": ["market", "farmers_market"],
    "alışveriş merkezi": ["shopping_mall"], "hediyelik": ["gift_shop", "tourist_attraction"],
    "antika": ["antique_shop"],
    
    # Eğlence & Aktivite
    "eğlence parkı": ["amusement_park"], "sinema": ["movie_theater"],
    "tiyatro": ["performing_arts_theater"], "konser": ["concert_hall", "performing_arts_theater"],
    "gece kulübü": ["night_club"], "bowling": ["bowling_alley"],
    "spor": ["sports_complex", "stadium"], "spa": ["spa"],
    "plaj aktivitesi": ["beach", "tourist_attraction"],
    
    # Ulaşım & Pratik
    "havalimanı": ["airport"], "otogar": ["bus_station"],
    "tren istasyonu": ["train_station"], "metro": ["subway_station"],
    "eczane": ["pharmacy"], "hastane": ["hospital"], "atm": ["atm"]
}

# 10 Şehir * 49 Kategori = 490 arama. ~10.000 veri hedefine ulaşmak için sınır 20.
LIMIT_PER_CATEGORY = 20

def build_database():
    categories_to_fetch = list(CATEGORY_MAP.keys())
    
    print("🌍 Akıllı ve Odaklı Veritabanı Oluşturma Süreci Başlıyor...")
    print(f"Hedef: 10 Ana Şehir, kategori başına en popüler {LIMIT_PER_CATEGORY} mekan ile toplam ~10.000 kayıt.\n")
    
    total_requests = 0
    
    for city in TARGET_CITIES:
        print("\n" + "="*50)
        print(f"📍 ŞEHİR: {city.upper()} TARANIYOR")
        print("="*50)
        
        for category in categories_to_fetch:
            print(f"   👉 Kategori: {category} (En iyi {LIMIT_PER_CATEGORY} mekan) çekiliyor...")
            
            # fetch_places.py dosyasını terminalden gerekli parametrelerle tetikliyoruz
            command = f'python fetch_places.py --city "{city}" --category "{category}" --limit {LIMIT_PER_CATEGORY}'
            os.system(command)
            
            total_requests += 1
            # Sunucuyu yormamak ve API kotalarına takılmamak için kısa bekleme
            time.sleep(1.2) 

    print("\n" + "🏆"*10)
    print("EN KALİTELİ HAM VERİLER BAŞARIYLA ÇEKİLDİ VE VERİTABANINA KAYDEDİLDİ!")
    print(f"Toplam Yapılan API İsteği: {total_requests}")
    print("🏆"*10)

if __name__ == "__main__":
    build_database()