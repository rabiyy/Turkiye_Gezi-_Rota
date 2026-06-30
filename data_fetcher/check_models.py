import os
import requests
from dotenv import load_dotenv

# .env dosyasından API anahtarını alıyoruz
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Doğrudan Google'ın REST API'sine soruyoruz
url = f"https://generativelanguage.googleapis.com/v1beta/models?key={api_key}"

print("Google sunucusuna bağlanılıyor...\n")

try:
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Senin API Anahtarınla Kullanabileceğin Metin Modelleri:")
        print("-" * 50)
        
        # Sadece metin üretebilen (generateContent destekleyen) modelleri filtrele
        for model in data.get("models", []):
            if "generateContent" in model.get("supportedGenerationMethods", []):
                # 'models/' önekini temizleyerek sadece modelin asıl adını yazdır
                model_name = model['name'].replace('models/', '')
                print(f"- {model_name}")
                
        print("-" * 50)
        print("💡 Yukarıdaki listeden gözüne en güncel/stabil görünen (örn: gemini-1.5-pro vb.)")
        print("model adını kopyalayıp chatbot.py dosyasındaki model='...' kısmına yapıştırabilirsin.")
    else:
        print(f"❌ API Hatası ({response.status_code}): {response.text}")
except Exception as e:
    print(f"❌ Bağlantı Hatası: {e}")