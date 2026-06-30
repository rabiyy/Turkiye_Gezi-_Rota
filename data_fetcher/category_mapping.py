# Kullanıcı dostu Türkçe kategorilerin Google Places API (New) karşılıkları
# Kaynak: https://developers.google.com/maps/documentation/places/web-service/place-types

CATEGORY_MAP = {
    # Doğa & Açık Hava
    "plaj": ["beach"],
    "park": ["park", "national_park", "state_park"],
    "şelale": ["tourist_attraction", "park"],
    "dağ": ["national_park", "state_park", "tourist_attraction"],
    "orman": ["national_park", "state_park", "park"],
    "göl": ["tourist_attraction", "park"],
    "kamp": ["campground", "rv_park"],
    "piknik": ["park", "picnic_ground"],
    "botanik bahçesi": ["botanical_garden"],
    "hayvanat bahçesi": ["zoo"],
    "akvaryum": ["aquarium"],
    "doğa yürüyüşü": ["hiking_area", "national_park"],

    # Kültür & Tarih
    "müze": ["museum", "art_gallery"],
    "tarihi yer": ["historical_landmark", "cultural_landmark"],
    "sanat galerisi": ["art_gallery"],
    "anıt": ["monument", "historical_landmark"],
    "arkeoloji": ["archaeological_site"],
    "kale": ["historical_landmark", "tourist_attraction"],
    "camii": ["mosque"],
    "kilise": ["church"],
    "sinagog": ["synagogue"],
    "tapınak": ["hindu_temple", "buddhist_temple"],

    # Yeme & İçme
    "restoran": ["restaurant"],
    "deniz ürünleri": ["seafood_restaurant"],
    "vejeteryan": ["vegetarian_restaurant"],
    "vegan": ["vegan_restaurant"],
    "kafe": ["cafe", "coffee_shop"],
    "pastane": ["bakery", "dessert_shop"],
    "fast food": ["fast_food_restaurant"],
    "bar": ["bar", "pub"],
    "sokak yemeği": ["food_court", "sandwich_shop"],
    "organik": ["health_food_store", "vegetarian_restaurant"],

    # Konaklama
    "otel": ["hotel"],
    "hostel": ["hostel"],
    "apart": ["extended_stay_hotel", "apartment_complex"],
    "butik otel": ["boutique_hotel"],
    "kamp alanı": ["campground"],
    "tatil köyü": ["resort_hotel"],

    # Alışveriş
    "çarşı": ["shopping_mall", "market"],
    "pazar": ["market", "farmers_market"],
    "alışveriş merkezi": ["shopping_mall"],
    "hediyelik": ["gift_shop", "tourist_attraction"],
    "antika": ["antique_shop"],

    # Eğlence & Aktivite
    "eğlence parkı": ["amusement_park"],
    "sinema": ["movie_theater"],
    "tiyatro": ["performing_arts_theater"],
    "konser": ["concert_hall", "performing_arts_theater"],
    "gece kulübü": ["night_club"],
    "bowling": ["bowling_alley"],
    "spor": ["sports_complex", "stadium"],
    "spa": ["spa"],
    "plaj aktivitesi": ["beach", "tourist_attraction"],

    # Ulaşım & Pratik
    "havalimanı": ["airport"],
    "otogar": ["bus_station"],
    "tren istasyonu": ["train_station"],
    "metro": ["subway_station"],
    "eczane": ["pharmacy"],
    "hastane": ["hospital"],
    "atm": ["atm"],
}

# Türkçe eş anlamlılar — farklı yazımları ana kategoriye yönlendirir
SYNONYMS = {
    "sahil": "plaj",
    "kumsal": "plaj",
    "yeme": "restoran",
    "yemek": "restoran",
    "içmek": "bar",
    "kahve": "kafe",
    "kahvaltı": "kafe",
    "tarih": "tarihi yer",
    "tarihi": "tarihi yer",
    "antik": "arkeoloji",
    "gezi": "tarihi yer",
    "doğa": "park",
    "yeşil alan": "park",
    "yürüyüş": "doğa yürüyüşü",
    "trekking": "doğa yürüyüşü",
    "alışveriş": "çarşı",
    "market": "pazar",
    "konaklama": "otel",
    "kal": "otel",
    "eğlence": "eğlence parkı",
    "ibadet": "camii",
    "dua": "camii",
}


def get_google_types(user_input: str) -> list[str]:
    """
    Kullanıcının girdiği Türkçe kelimeyi Google Places API tiplerine çevirir.
    Eş anlamlıları da destekler.
    """
    normalized = user_input.strip().lower()

    # Önce eş anlamlılara bak
    if normalized in SYNONYMS:
        normalized = SYNONYMS[normalized]

    # Sonra ana haritada ara
    if normalized in CATEGORY_MAP:
        return CATEGORY_MAP[normalized]

    # Kısmi eşleşme — örn. "tarihi müze" → "müze" bulur
    for key in CATEGORY_MAP:
        if key in normalized or normalized in key:
            return CATEGORY_MAP[key]

    # Hiçbir şey bulunamazsa genel cazibe merkezi döndür
    return ["tourist_attraction"]


if __name__ == "__main__":
    # Test
    test_inputs = ["sahil", "tarihi müze", "vegan restoran", "doğa yürüyüşü", "xyz"]
    for inp in test_inputs:
        print(f"{inp:20} → {get_google_types(inp)}")