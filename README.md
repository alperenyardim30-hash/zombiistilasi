# 🧟 Zombi İstilası

Pygame ile yazılmış, dalga tabanlı bir zombi hayatta kalma oyunu altyapısı.

## Mevcut Durum
Bu repoda şu anda çekirdek başlatma ve ayar dosyaları bulunuyor:

- `zombi_istilasi/main.py`: Ana oyun döngüsü ve durum yönetimi.
- `zombi_istilasi/ayarlar.py`: Oyun sabitleri, silah/element tablosu ve genel ayarlar.

> Not: `main.py` içinde `ekranlar.*` modülleri import ediliyor. Bu klasör/projeler eksikse oyun başlatılamaz.

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install pygame
```

## Çalıştırma

```bash
python zombi_istilasi/main.py
```

## Kontroller

- **WASD / Ok tuşları**: Hareket
- **Sol tık**: Ateş
- **Sağ tık**: Nişan
- **Shift**: Sprint
- **Space**: Ultimate
- **B**: Shop
- **M (2D modda)**: Harita değiştir (Şehir / Laboratuvar)
- **ESC**: Duraklat / Menülerden çıkış
- **1-9**: Silah seçimi
- **Mouse wheel**: Silah değiştirme

## Bu turda yapılan teknik iyileştirmeler

- Oyun içi fare görünürlüğü/grab yönetimi tek bir yardımcı fonksiyonda toplandı.
- Eksik modül durumları için daha anlaşılır hata mesajı eklendi.
- Ortam değişkenleri `setdefault` ile daha güvenli hale getirildi.
- Ekran çözünürlüğü alma akışı fonksiyonlaştırıldı ve platformlar arası fallback netleştirildi.
- `highscore` dizini başlangıçta otomatik oluşturulacak şekilde güvence altına alındı.
- 2D mod için iki farklı harita teması eklendi (M tuşu ile anlık geçiş).
- Aim cone sistemi silah tipine göre (alev/roket/delici) ayrı davranacak şekilde iyileştirildi.
- Karakterin elinde görünen silah sprite'ı, aktif silaha göre dinamik değişecek hale getirildi.

## Önerilen Sonraki Adımlar

1. `ekranlar/` klasörünü ve alt sınıfları repoya ekle.
2. `requirements.txt` dosyası ekle (`pygame` sürüm pinlemesi ile).
3. `kayitlar/highscore.json` için okuma/yazma doğrulama ve bozuk dosya toleransı ekle.
4. Basit birim testleri (özellikle `ayarlar.py` üretim tabloları için) ekle.
