-- Google'dan aynı veriyi tekrar tekrar çekmemek (Duplicate önlemek) için
-- Google'ın kendi ID'sini tutacağımız kolon.
ALTER TABLE places ADD COLUMN IF NOT EXISTS external_id VARCHAR(255) UNIQUE;