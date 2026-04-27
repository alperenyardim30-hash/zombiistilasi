# 🧟 Zombi İstilası

Pygame ile geliştirilmiş, 2D yukarıdan bakışlı (top-down) zombi hayatta kalma ve aksiyon oyunu. Oyuncular çeşitli silahlar, farklı element güçleri (Ateş, Buz, Zehir, Elektrik) kullanarak giderek zorlaşan zombi dalgalarına karşı hayatta kalmaya çalışır.

## Özellikler
- **55 Farklı Silah:** Tabancalar, pompalı tüfekler, taarruz tüfekleri, keskin nişancı tüfekleri, enerji silahları ve daha fazlası.
- **Element Sistemi:** Ateş (yakıcı), Buz (yavaşlatıcı), Zehir (zamanla hasar), Elektrik (seken hasar) ve Kinetik (itme kuvveti) efektleriyle stratejik savaş.
- **Gelişmiş Zombi Yapay Zekası:** Çeşitli zombi tipleri (Hızlı, Tank, Menzilli, vb.) ve sürü davranışları.
- **Market (Shop) Sistemi:** Dalgalar arasında veya oyun içinde silah satın alma, mermi yenileme ve can doldurma imkanı.
- **Açık Dünya / Arena Karışımı:** Geniş ve keşfedilebilir devasa harita, farklı bölgeler.
- **Gelişmiş Görsel Efektler:** Silahlara ve elementlere özel mermi izleri, çarpma efektleri (kan, parçacık, duman, lazer) ve kamera sarsıntısı.

## Kurulum

Projeyi bilgisayarınızda çalıştırmak için Python 3.8+ yüklü olmalıdır.

```bash
# Sanal ortam oluşturun
python -m venv .venv
# Windows için sanal ortamı aktifleştirme:
.venv\Scripts\activate
# Mac/Linux için:
# source .venv/bin/activate

# Gerekli bağımlılıkları yükleyin
pip install -r requirements.txt
```

*(Eğer `requirements.txt` bulunmuyorsa, sadece `pip install pygame` komutunu çalıştırmanız yeterlidir.)*

## Çalıştırma

Oyunu başlatmak için aşağıdaki komutu kullanın:

```bash
python zombi_istilasi/main.py
```

## Kontroller

- **WASD / Yön Tuşları**: Karakteri hareket ettirir.
- **Fare (Mouse)**: Nişan alma.
- **Sol Tık**: Ateş etme (Basılı tutarak otomatik silahlarda sürekli ateş).
- **Sağ Tık**: Odaklanarak (Aim) nişan alma (İsabet oranını artırır).
- **Shift**: Koşma (Stamina harcar).
- **Space**: Dash / Hızlı Kaçış (veya karakterin Ultimate yeteneği).
- **B Tuşu**: Market (Shop) menüsünü açar/kapatır.
- **ESC Tuşu**: Oyunu duraklatır (Pause) ve menüyü açar.
- **F1 Tuşu**: Geliştirici (Cheat/Debug) konsolunu veya debug arayüzünü açar.
- **1-9 Tuşları**: Envanterdeki silahlara hızlı geçiş.
- **Fare Tekerleği**: Silahlar arasında ileri/geri geçiş.

## Katkıda Bulunma
Bu proje geliştirilmeye devam etmektedir. Herhangi bir hata bulursanız veya özellik eklemek isterseniz, Pull Request (PR) gönderebilirsiniz.

## Lisans
Bu proje açık kaynaklıdır ve eğitim/eğlence amaçlı geliştirilmiştir.
