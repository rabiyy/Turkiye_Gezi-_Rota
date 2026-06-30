from db import get_connection
from sentence_transformers import SentenceTransformer

print("🧠 Yapay Zeka Modeli Yükleniyor (paraphrase-multilingual-mpnet-base-v2)...")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')


def update_embeddings():
    conn = get_connection()
    cur = conn.cursor()

    print("🚀 Mekanlar anlamsal vektörlere çevriliyor...")

    try:
        # Embedding'i boş olan mekanları çek (etiketler dahil)
        cur.execute("""
            SELECT 
                p.id,
                p.name,
                p.description,
                p.address,
                p.city,
                p.green_tags,
                c.name as category_name
            FROM places p
            LEFT JOIN place_categories pc ON p.id = pc.place_id
            LEFT JOIN categories c ON pc.category_id = c.id
            WHERE p.embedding IS NULL;
        """)

        places = cur.fetchall()

        if not places:
            print("✨ Vektörleştirilecek yeni mekan bulunamadı. Zaten hepsi akıllı!")
            return

        updated_count = 0
        total = len(places)

        for place in places:
            place_id, name, description, address, city, green_tags, category = place

            # Metin parçalarını hazırla
            name_text = name or "Bilinmeyen Mekan"
            cat_text = category or "Genel Gezi Noktası"
            city_text = city or ""
            address_text = address or "Adres bilgisi mevcut değil."
            desc_text = description or ""

            # Etiketleri metne çevir
            tags_text = ""
            if green_tags and len(green_tags) > 0:
                tags_text = ", ".join(green_tags)

            # Zengin context metni oluştur
            context_text = (
                f"Mekan Adı: {name_text}. "
                f"Kategori: {cat_text}. "
                f"Şehir: {city_text}. "
                f"Adres: {address_text}. "
                f"Açıklama: {desc_text}. "
                f"Özellikler: {tags_text}."
            )

            # Vektörü oluştur (768 boyutlu)
            vector = model.encode(context_text).tolist()

            # Veritabanına kaydet
            cur.execute("""
                UPDATE places 
                SET embedding = %s 
                WHERE id = %s;
            """, (vector, place_id))

            updated_count += 1

            # Her 100 kayıtta bir ekrana yaz ve kaydet
            if updated_count % 100 == 0:
                conn.commit()
                print(f"⏳ İlerleme: {updated_count} / {total} mekan tamamlandı...")

        conn.commit()
        print(f"\n✅ MÜKEMMEL! Toplam {updated_count} mekanın yapay zeka vektörü güncellendi!")

    except Exception as e:
        print(f"❌ Veritabanı hatası: {e}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    update_embeddings()