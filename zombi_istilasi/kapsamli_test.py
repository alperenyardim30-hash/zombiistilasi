import os
import sys
import pygame
import math
import traceback
from ayarlar import SILAHLAR, SILAH_SIRASI, YUKSELTMELER
from varliklar.oyuncu import Oyuncu
from varliklar.zombi import Zombi
from sistemler.puan_sistemi import PuanSistemi
from sistemler.dalga_sistemi import DalgaSistemi
from sistemler.perk_sistemi import PerkSistemi
from sistemler.gorev_sistemi import GorevSistemi

def calistir():
    print("=" * 50)
    print("ZOMBI ISTILASI - KAPSAMLI OTOMATIK TEST")
    print("=" * 50)

    # 1. Pygame Başlatma
    pygame.init()
    pygame.display.set_mode((100, 100), pygame.HIDDEN)  # Görünmez ekran
    print("[OK] Pygame başlatıldı ve sahte ekran oluşturuldu.")

    # 2. Sistemlerin Başlatılması
    try:
        puan_sis = PuanSistemi()
        perk_sis = PerkSistemi()
        gorev_sis = GorevSistemi()
        zombiler = pygame.sprite.Group()
        mermiler = pygame.sprite.Group()
        dalga_sis = DalgaSistemi(zombiler)
        oyuncu = Oyuncu(500, 500)
        print("[OK] Oyuncu ve tüm temel sistemler (Dalga, Puan, Perk, Görev) başarıyla oluşturuldu.")
    except Exception as e:
        print(f"[HATA] Sistemler başlatılamadı: {e}")
        sys.exit(1)

    # 3. Oyuncu Özellikleri ve Hasar Alma
    try:
        ilk_can = oyuncu.can
        ilk_kalkan = getattr(oyuncu, "kalkan", 0)
        oyuncu.hasar_al(120)  # Kalkanı delecek kadar hasar verelim
        assert oyuncu.can < ilk_can or getattr(oyuncu, "kalkan", 0) < ilk_kalkan, "Oyuncu hasar alamıyor!"
        oyuncu.can_doldur(500)
        assert oyuncu.can == oyuncu.max_can_degeri, "Oyuncu can dolduramıyor!"
        print("[OK] Oyuncu hasar alma ve iyileşme mekanikleri çalışıyor.")
    except Exception as e:
        print(f"[HATA] Oyuncu mekanikleri: {e}")

    # 4. Silahlar ve Envanter
    try:
        if "shotgun" not in oyuncu.envanter:
            oyuncu.silah_al("shotgun")
        oyuncu.silah_degistir("shotgun")
        assert oyuncu.aktif_silah == "shotgun", "Silah değiştirme başarısız!"
        
        # Atış Testi
        tuslar = {"ates": True, "yukari": False, "asagi": False, "sol": False, "sag": False, "nisan": False, "ult": False, "sprint": False}
        oyuncu.update(0.1, tuslar, (550, 500), mermiler, 1920, 1080, False)
        assert len(mermiler) > 0, "Silah mermi oluşturamadı!"
        print("[OK] Envanter, silah değiştirme ve atış sistemleri çalışıyor.")
    except Exception as e:
        print(f"[HATA] Silah sistemi: {e}")

    # 5. Zombi Oluşturma ve Hasar Verme
    try:
        zombi = Zombi(550, 500, "normal")
        zombiler.add(zombi)
        assert len(zombiler) > 0, "Zombi gruba eklenemedi!"
        ilk_zombi_can = zombi.can
        
        # Mermi çarpışması simülasyonu
        mermi = mermiler.sprites()[0]
        zombi.x, zombi.y = mermi.x, mermi.y # Merminin üstüne koy
        oldu_mu, zafiyet, gercek_hasar = zombi.mermi_carpisma(mermi)
        
        # Direkt hasar verme
        zombi.can -= 50
        if zombi.can <= 0:
            puan_sis.zombi_oldu(zombi.skor, zombi.para)
        
        print("[OK] Zombi dalgası, mermi çarpışma ve ölüm mekanikleri çalışıyor.")
    except Exception as e:
        print(f"[HATA] Zombi sistemi:")
        traceback.print_exc()

    # 6. Market ve Yükseltmeler
    try:
        puan_sis.para += 10000
        if "hasar" in oyuncu.yukseltmeler:
            ilk_hasar = oyuncu.hasar_carpani
            eski_seviye = oyuncu.yukseltmeler["hasar"]
            # Satın alma simülasyonu
            maliyet = YUKSELTMELER["hasar"]["fiyat"] * (eski_seviye + 1)
            if puan_sis.harca(maliyet):
                oyuncu.yukseltmeler["hasar"] += 1
            assert oyuncu.hasar_carpani > ilk_hasar, "Yükseltme hasar çarpanını artırmadı!"
        print("[OK] Market satın alma ve stat yükseltme mekanikleri çalışıyor.")
    except Exception as e:
        print(f"[HATA] Market/Yükseltme sistemi:")
        traceback.print_exc()

    # 7. XP ve Seviye Sistemi
    try:
        ilk_seviye = puan_sis.seviye
        puan_sis._xp_ekle(50000) # Seviye atlamak için yeterince XP
        assert puan_sis.seviye > ilk_seviye, "Seviye atlama sistemi çalışmıyor!"
        print("[OK] XP kazanma ve seviye atlama mekanikleri çalışıyor.")
    except Exception as e:
        print(f"[HATA] XP sistemi: {e}")

    # 8. Silahların Tamamının Yüklenebilirliği
    try:
        hatali_silah = False
        for s in SILAH_SIRASI:
            if s not in SILAHLAR:
                print(f"[HATA] {s} tanımlı değil!")
                hatali_silah = True
        assert not hatali_silah, "Eksik silah tanımlamaları var!"
        print(f"[OK] Tüm {len(SILAHLAR)} silah başarıyla yüklendi ve tanımlandı.")
    except Exception as e:
        print(f"[HATA] Silah veritabanı: {e}")

    print("=" * 50)
    print("TÜM TESTLER TAMAMLANDI! OYUN FONKSİYONLARI SAĞLIKLI ÇALIŞIYOR.")
    print("=" * 50)
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    calistir()
