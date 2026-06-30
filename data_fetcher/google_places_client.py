import requests
import os
from dotenv import load_dotenv
from category_mapping import get_google_types

load_dotenv()

API_KEY = os.getenv("GOOGLE_PLACES_API_KEY")
PLACES_API_URL = "https://places.googleapis.com/v1/places:searchNearby"

def search_nearby_places(
    category: str,
    lat: float,
    lng: float,
    radius_meters: int = 5000,
    max_results: int = 20
) -> list[dict]:
    """
    Verilen koordinat ve kategoriye göre Google Places API'den mekan çeker.
    """
    google_types = get_google_types(category)

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.rating,"
            "places.userRatingCount,"
            "places.types,"
            "places.websiteUri,"
            "places.regularOpeningHours"
        )
    }

    body = {
        "includedTypes": google_types,
        "maxResultCount": max_results,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": lat,
                    "longitude": lng
                },
                "radius": radius_meters
            }
        }
    }

    try:
        response = requests.post(PLACES_API_URL, json=body, headers=headers)
        response.raise_for_status()
        data = response.json()
        places = data.get("places", [])
        print(f"✅ {len(places)} mekan bulundu ({category} → {google_types})")
        return places
    except requests.exceptions.HTTPError as e:
        print(f"❌ HTTP Hatası: {e.response.status_code} - {e.response.text}")
        return []
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")
        return []


if __name__ == "__main__":
    # Test: İstanbul'da müze ara
    results = search_nearby_places(
        category="müze",
        lat=41.0082,
        lng=28.9784,
        radius_meters=3000,
        max_results=5
    )
    for place in results:
        name = place.get("displayName", {}).get("text", "?")
        address = place.get("formattedAddress", "?")
        rating = place.get("rating", "?")
        print(f"  📍 {name} | {address} | ⭐ {rating}")