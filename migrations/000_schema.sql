-- Kategori Tablosu (Örn: Plaj, Müze, Restoran)
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT
);

-- Etiket Tablosu (Örn: Sakin, Romantik, Sürdürülebilir)
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE
);

-- Ana Mekanlar Tablosu
CREATE TABLE IF NOT EXISTS places (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    address TEXT,
    location geometry(Point, 4326),
    description TEXT,
    sustainability_score NUMERIC(5,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Mekan ve Kategori İlişkisi (Çoka Çok)
CREATE TABLE IF NOT EXISTS place_categories (
    place_id UUID REFERENCES places(id) ON DELETE CASCADE,
    category_id INTEGER REFERENCES categories(id) ON DELETE CASCADE,
    PRIMARY KEY (place_id, category_id)
);

-- Coğrafi aramaları hızlandırmak için uzamsal indeks
CREATE INDEX IF NOT EXISTS places_location_idx ON places USING GIST (location);