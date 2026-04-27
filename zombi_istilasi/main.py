import os
import sys

# ============================================================
#  main.py — Oyun döngüsü ve durum yönetimi
# ============================================================

# NVIDIA/AMD Harici Ekran Kartını Zorlamak İçin Sistem İpuçları
os.environ.setdefault("SDL_HINT_RENDER_DRIVER", "direct3d11")
os.environ.setdefault("SDL_HINT_RENDER_GPU_PRIORITY", "high")

import pygame
from ayarlar import (
    BASLIK,
    DURUM_BITTI,
    DURUM_MENU,
    DURUM_OYUN,
    DURUM_PAUSE,
    DURUM_SHOP,
    FPS,
    GENISLIK,
    SILAH_SIRASI,
    YUKSEKLIK,
)

DURUM_PERK = "perk"


def _fare_durumu_ayarla(aktif_oyun: bool) -> None:
    """Aktif oyunda imleci gizler, menülerde görünür yapar."""
    pygame.mouse.set_visible(not aktif_oyun)
    pygame.event.set_grab(aktif_oyun)


def _ekranlari_yukle():
    """
    Ekran sınıflarını geç import ile yükler.
    Modül eksikliği durumunda kullanıcıya net hata mesajı verir.
    """
    try:
        from ekranlar.ana_menu import AnaMenu
        from ekranlar.duraklama import Duraklama
        from ekranlar.oyun_bitti import OyunBitti
        from ekranlar.oyun_ekrani import OyunEkrani
        from ekranlar.shop import Shop
    except ModuleNotFoundError as exc:
        eksik = exc.name or "bilinmeyen modül"
        print(
            f"[HATA] Gerekli modül bulunamadı: '{eksik}'. "
            "Proje dosya yapısını kontrol edin.",
            file=sys.stderr,
        )
        raise

    return AnaMenu, OyunEkrani, Duraklama, OyunBitti, Shop

def main():
    pygame.init()
    pygame.display.set_caption(BASLIK)
    
    # SCALED kaldırıldı, artık Windows'tan alınan GERÇEK çözünürlükle piksel kusursuz çalışacak!
    # Donanım hızlandırma (GPU) ve Çift Tamponlama aktif edildi
    flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
    ekran = pygame.display.set_mode((GENISLIK, YUKSEKLIK), flags)
    saat  = pygame.time.Clock()

    AnaMenu, OyunEkrani, Duraklama, OyunBitti, Shop = _ekranlari_yukle()

    ana_menu    = AnaMenu()
    oyun_ekrani = OyunEkrani()
    duraklama   = Duraklama()
    oyun_bitti  = OyunBitti()
    shop        = Shop()

    durum = DURUM_MENU
    _fare_durumu_ayarla(aktif_oyun=False)
    cheat_mesaj = ""
    cheat_mesaj_sayac = 0.0
    _font_cheat = pygame.font.SysFont("Consolas", 20, bold=True)  # Font bir kez olustur, her frame degil

    while True:
        dt = min(saat.tick(FPS) / 1000.0, 0.05)
        fare_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if durum == DURUM_MENU:
                sonuc = ana_menu.tik_isle(event, 0)
                if sonuc == DURUM_OYUN:
                    oyun_ekrani.baslat(); durum = DURUM_OYUN
                elif sonuc == "cikis":
                    pygame.quit(); sys.exit()

            elif durum == DURUM_OYUN:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        durum = DURUM_PAUSE
                        _fare_durumu_ayarla(aktif_oyun=False)
                    elif event.key == pygame.K_b:
                        durum = DURUM_SHOP
                        _fare_durumu_ayarla(aktif_oyun=False)
                    elif event.key == pygame.K_m:
                        oyun_ekrani.harita_degistir()
                    elif pygame.K_1 <= event.key <= pygame.K_9:
                        idx = event.key - pygame.K_1
                        sahip = [k for k in SILAH_SIRASI if k in oyun_ekrani.oyuncu.envanter]
                        if idx < len(sahip):
                            oyun_ekrani.oyuncu.silah_degistir(sahip[idx])
                    # CHEAT: Artik tek kaynak oyun_ekrani.py'deki handler
                elif event.type == pygame.MOUSEWHEEL:
                    oyun_ekrani.oyuncu.siradaki_silah(-event.y)

            elif durum == DURUM_PAUSE:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    durum = DURUM_OYUN
                else:
                    sonuc = duraklama.tik_isle(event)
                    if sonuc == "devam":
                        durum = DURUM_OYUN
                    elif sonuc == "menu":  durum = DURUM_MENU
                    elif sonuc == "cikis": pygame.quit(); sys.exit()


            elif durum == DURUM_SHOP:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    durum = DURUM_OYUN
                    _fare_durumu_ayarla(aktif_oyun=False)
                
                sonuc = shop.tik_isle(event, oyun_ekrani.oyuncu, oyun_ekrani.puan_sis)
                if sonuc == "devam":
                    oyun_ekrani.oyuncu.mermileri_fulle()
                    oyun_ekrani.dalga_sis.yeni_dalga_hazirla()
                    oyun_ekrani.gorev_sis.yeni_gorev_sec()
                    # Her 3 dalgada Perk — seçim oyun ekranında overlay olarak açılır
                    if oyun_ekrani.dalga_sis.dalga_no > 0 and oyun_ekrani.dalga_sis.dalga_no % 3 == 0:
                        oyun_ekrani.perk_sis.perk_sec_hazirla()
                    durum = DURUM_OYUN
                    _fare_durumu_ayarla(aktif_oyun=False)

            # Perk seçimi hem klavye hem fare tıklamasıyla
            if durum == DURUM_OYUN and oyun_ekrani.perk_sis.secim_bekliyor:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1: oyun_ekrani.perk_sis.perk_sec(0)
                    elif event.key == pygame.K_2: oyun_ekrani.perk_sis.perk_sec(1)
                    elif event.key == pygame.K_3: oyun_ekrani.perk_sis.perk_sec(2)
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # Hangi karta tıklandı?
                    p = oyun_ekrani.perk_sis
                    kart_gen, kart_yuk, bosluk = 280, 220, 40
                    n = len(p.secenekler)
                    toplam = n * (kart_gen + bosluk) - bosluk
                    sx = GENISLIK // 2 - toplam // 2
                    sy = YUKSEKLIK // 2 - kart_yuk // 2
                    for i in range(n):
                        kx, ky = sx + i * (kart_gen + bosluk), sy
                        if pygame.Rect(kx, ky, kart_gen, kart_yuk).collidepoint(event.pos):
                            p.perk_sec(i)
                            break

            elif durum == DURUM_BITTI:
                sonuc = oyun_bitti.tik_isle(event)
                if sonuc == "oyun":
                    oyun_ekrani.baslat(); durum = DURUM_OYUN
                elif sonuc == "menu":
                    durum = DURUM_MENU

        # GÜNCELLEME
        if durum == DURUM_MENU:
            ana_menu.guncelle(dt)
        elif durum == DURUM_OYUN:
            keys = pygame.key.get_pressed()
            tuslar = {
                "yukari": keys[pygame.K_w] or keys[pygame.K_UP],
                "asagi":  keys[pygame.K_s] or keys[pygame.K_DOWN],
                "sol":    keys[pygame.K_a] or keys[pygame.K_LEFT],
                "sag":    keys[pygame.K_d] or keys[pygame.K_RIGHT],
                "ates":   pygame.mouse.get_pressed()[0],
                "nisan":  pygame.mouse.get_pressed()[2],  # Sağ tık (Aim)
                "ult":    keys[pygame.K_SPACE],
                "sprint": keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT],
            }
            oyun_ekrani.guncelle(dt, tuslar, fare_pos)

            if oyun_ekrani.oyuncu_oldu_mu:
                oyun_bitti.ayarla(oyun_ekrani.son_puan, oyun_ekrani.dalga_no, oyun_ekrani.yuksek_skorlar)
                durum = DURUM_BITTI
                _fare_durumu_ayarla(aktif_oyun=False)
            elif oyun_ekrani.dalga_bitti_mi:
                durum = DURUM_SHOP
                _fare_durumu_ayarla(aktif_oyun=False)

        elif durum == DURUM_SHOP:
            shop.guncelle(dt)
        elif durum == DURUM_BITTI:
            oyun_bitti.guncelle(dt)

        # ÇİZİM
        if durum == DURUM_MENU:
            ana_menu.ciz(ekran)
        elif durum == DURUM_OYUN:
            oyun_ekrani.ciz(ekran)
        elif durum == DURUM_PAUSE:
            oyun_ekrani.ciz(ekran)
            duraklama.ciz(ekran)
        elif durum == DURUM_SHOP:
            shop.ciz(ekran, oyun_ekrani.oyuncu, oyun_ekrani.puan_sis)
        elif durum == DURUM_BITTI:
            oyun_bitti.ciz(ekran)

        # Cheat mesaj countdown
        if cheat_mesaj_sayac > 0:
            cheat_mesaj_sayac -= dt

        # Cheat mesaji flip ONCESINDE cizilmeli (flip sonrasi gorunmez)
        if cheat_mesaj_sayac > 0 and durum == DURUM_OYUN:
            ct = _font_cheat.render(cheat_mesaj, True, (0, 255, 80))
            ekran.blit(ct, (GENISLIK // 2 - ct.get_width() // 2, 12))

        pygame.display.flip()


if __name__ == "__main__":
    main()
