# ============================================================
#  sistemler/perk_sistemi.py — Perk Seçim Sistemi (Her 3 Dalgada)
# ============================================================
import random

PERKLER = {
    "vampir":     {"isim": "[V] Vampir Mermi",   "aciklama": "Her oldürmede +5 can",         "etki": "vampir"},
    "patlama":    {"isim": "[P] Zincir Patlama", "aciklama": "Zombi olunce yanindakine hasar","etki": "zincir"},
    "adrenalin":  {"isim": "[A] Adrenalin",      "aciklama": "Hasar alininca +20% hiz (3sn)",  "etki": "adrenalin"},
    "manyetik":   {"isim": "[M] Manyetik Alan",  "aciklama": "Drop'lar sana dogru gelir",     "etki": "manyetik"},
    "soguk_kan":  {"isim": "[S] Soguk Kan",      "aciklama": "Nisanda zaman yavaslar",        "etki": "zaman"},
    "para_avcisi":{"isim": "[G] Para Avcisi",    "aciklama": "Her oldürmede +50% para",       "etki": "para"},
    "ikiz_namlu": {"isim": "[I] Ikiz Namlu",     "aciklama": "Her atista 2 mermi cikar",      "etki": "ikiz"},
    "bumerang":   {"isim": "[B] Bumerang",       "aciklama": "Mermiler geri döner",           "etki": "bumerang"},
}


class PerkSistemi:
    def __init__(self):
        self.aktif_perkler = []      # Seçilen perk anahtarları
        self.secim_bekliyor = False  # Seçim ekranı gösterilsin mi?
        self.secenekler = []         # Sunulan 3 perk anahtarı

    def perk_sec_hazirla(self):
        """Her 3 dalgada çağrılır — 3 rastgele perk seçeceği hazırlar."""
        havuz = [k for k in PERKLER if k not in self.aktif_perkler]
        if not havuz:
            havuz = list(PERKLER.keys())  # Hepsini aldıysa tekrar sun
        self.secenekler = random.sample(havuz, min(3, len(havuz)))
        self.secim_bekliyor = True

    def perk_sec(self, indeks):
        """Oyuncu bir seçenek seçtiğinde çağrılır."""
        if 0 <= indeks < len(self.secenekler):
            secilen = self.secenekler[indeks]
            if secilen not in self.aktif_perkler:
                self.aktif_perkler.append(secilen)
            self.secim_bekliyor = False
            self.secenekler = []
            return secilen
        return None

    def uygula_olum(self, oyuncu, zombi):
        """Zombi öldüğünde uygulanacak perk efektleri."""
        if "vampir" in self.aktif_perkler:
            oyuncu.can_doldur(5)
        if "para_avcisi" in self.aktif_perkler:
            zombi.para = int(zombi.para * 1.5)

    def uygula_hasar_alindi(self, oyuncu):
        """Oyuncu hasar aldığında uygulanacak perk efektleri."""
        if "adrenalin" in self.aktif_perkler:
            oyuncu._adrenalin_sayac = 3.0  # oyuncu.update bu sayacı okur

    def drop_manyetik_mi(self):
        return "manyetik" in self.aktif_perkler

    def zaman_yavaslatma_mi(self, oyuncu):
        return "soguk_kan" in self.aktif_perkler and getattr(oyuncu, "nisan_aktif", False)

    def ikiz_namlu_mu(self):
        return "ikiz_namlu" in self.aktif_perkler

    def ciz_secim_ekrani(self, ekran, font_buyuk, font_kart, font_kucuk, genislik, yukseklik):
        """Perk seçim ekranı — 3 kart yan yana."""
        import pygame
        if not self.secim_bekliyor:
            return

        # Karartma
        overlay = pygame.Surface((genislik, yukseklik), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        ekran.blit(overlay, (0, 0))

        # Başlık
        t = font_buyuk.render("=== PERK SEC ===", True, (255, 220, 0))
        ekran.blit(t, (genislik // 2 - t.get_width() // 2, yukseklik // 2 - 240))

        sub = font_kucuk.render("Bir yetenek sec - kalici olarak kazanirsin! (1/2/3 veya tikla)", True, (200, 200, 200))
        ekran.blit(sub, (genislik // 2 - sub.get_width() // 2, yukseklik // 2 - 185))

        kart_gen, kart_yuk, bosluk = 280, 220, 40
        toplam_gen = len(self.secenekler) * (kart_gen + bosluk) - bosluk
        sx = genislik // 2 - toplam_gen // 2
        sy = yukseklik // 2 - kart_yuk // 2

        fare = pygame.mouse.get_pos()
        for i, key in enumerate(self.secenekler):
            p = PERKLER[key]
            kx, ky = sx + i * (kart_gen + bosluk), sy

            hover = pygame.Rect(kx, ky, kart_gen, kart_yuk).collidepoint(fare)
            bg = (50, 50, 80) if hover else (30, 30, 50)
            border = (255, 220, 0) if hover else (100, 100, 160)

            pygame.draw.rect(ekran, bg, (kx, ky, kart_gen, kart_yuk), border_radius=20)
            pygame.draw.rect(ekran, border, (kx, ky, kart_gen, kart_yuk), 3 if hover else 2, border_radius=20)

            isim_t = font_kart.render(p["isim"], True, (255, 220, 80))
            ekran.blit(isim_t, (kx + kart_gen // 2 - isim_t.get_width() // 2, ky + 30))

            acik_t = font_kucuk.render(p["aciklama"], True, (200, 200, 200))
            ekran.blit(acik_t, (kx + kart_gen // 2 - acik_t.get_width() // 2, ky + 80))

            num_t = font_kucuk.render(f"[{i+1}] veya tikla", True, (150, 150, 150))
            ekran.blit(num_t, (kx + kart_gen // 2 - num_t.get_width() // 2, ky + 175))
