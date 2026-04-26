# ============================================================
#  sistemler/gorev_sistemi.py — Mini Görev Sistemi
# ============================================================
import random

GOREVLER = [
    {"isim": "Hızlı Temizlik",  "hedef": "30 saniyede dalga bitir",    "bonus_para": 300, "tip": "sure",     "hedef_deger": 30},
    {"isim": "Buzlu Fırtına",   "hedef": "10 zombiyi donarak öldür",   "bonus_para": 250, "tip": "element",  "element": "donma", "hedef_deger": 10},
    {"isim": "El Bombacı",      "hedef": "5 zombiyi patlamayla öldür", "bonus_para": 400, "tip": "patlama",  "hedef_deger": 5},
    {"isim": "Hasarsız",        "hedef": "Hiç hasar almadan bitir",    "bonus_para": 500, "tip": "hasar",    "hedef_deger": 0},
    {"isim": "Combo Ustası",    "hedef": "10x combo yap",              "bonus_para": 300, "tip": "combo",    "hedef_deger": 10},
    {"isim": "Hızlı El",        "hedef": "Dalga boyunca 50 düşman vur","bonus_para": 350, "tip": "isabetler","hedef_deger": 50},
]


class GorevSistemi:
    def __init__(self):
        self.aktif_gorev = None
        self.sayac = {}      # İlerleme sayaçları
        self.sure_sayac = 0.0
        self.tamamlandi = False
        self.bonus_verildi = False
        self.bildirim_sayac = 0.0
        self.bildirim_metni = ""

    def yeni_gorev_sec(self):
        """Dalga başında yeni rastgele görev seçilir."""
        self.aktif_gorev = random.choice(GOREVLER).copy()
        self.sure_sayac = 0.0
        self.tamamlandi = False
        self.bonus_verildi = False
        self.sayac = {
            "sure": 0.0,
            "element": 0,
            "patlama": 0,
            "hasar_alindi": 0,
            "combo_max": 0,
            "isabetler": 0,
        }

    def guncelle(self, dt, puan_sis):
        """Her frame çağrılır."""
        if not self.aktif_gorev:
            return
        if self.bildirim_sayac > 0:
            self.bildirim_sayac -= dt
        self.sure_sayac += dt

    def zombi_oldu_bildir(self, efekt, patlama_mi=False):
        """Zombi öldüğünde hangi koşullarla öldüğünü bildir."""
        if not self.aktif_gorev or self.tamamlandi:
            return
        tip = self.aktif_gorev["tip"]
        if tip == "element" and efekt == self.aktif_gorev.get("element"):
            self.sayac["element"] += 1
        if tip == "patlama" and patlama_mi:
            self.sayac["patlama"] += 1

    def isabet_bildir(self):
        """Oyuncu bir zombiye mermi isabet ettirdiğinde."""
        if self.aktif_gorev and self.aktif_gorev["tip"] == "isabetler":
            self.sayac["isabetler"] += 1

    def hasar_alindi_bildir(self):
        """Oyuncu hasar aldığında."""
        if self.aktif_gorev:
            self.sayac["hasar_alindi"] += 1

    def combo_bildir(self, combo):
        """Mevcut combo değerini bildir."""
        if self.aktif_gorev:
            self.sayac["combo_max"] = max(self.sayac["combo_max"], combo)

    def dalga_bitti_kontrol(self, puan_sis):
        """Dalga bitince görevi değerlendir. Tamamlandıysa bonus para ver."""
        if not self.aktif_gorev or self.bonus_verildi:
            return False
        g = self.aktif_gorev
        tip = g["tip"]
        hedef = g["hedef_deger"]
        basarili = False

        if tip == "sure":
            basarili = self.sure_sayac <= hedef
        elif tip == "element":
            basarili = self.sayac["element"] >= hedef
        elif tip == "patlama":
            basarili = self.sayac["patlama"] >= hedef
        elif tip == "hasar":
            basarili = self.sayac["hasar_alindi"] == 0
        elif tip == "combo":
            basarili = self.sayac["combo_max"] >= hedef
        elif tip == "isabetler":
            basarili = self.sayac["isabetler"] >= hedef

        self.bonus_verildi = True
        if basarili:
            puan_sis.para += g["bonus_para"]
            self.tamamlandi = True
            self.bildirim_metni = f"✅ GÖREV TAMAM! +{g['bonus_para']}💰"
        else:
            self.bildirim_metni = "❌ Görev başarısız."
        self.bildirim_sayac = 3.0
        return basarili

    def ciz_hud(self, ekran, font, font_kucuk, genislik, yukseklik):
        """Sağ üst köşede mini görev göstergesi çizer."""
        import pygame
        if not self.aktif_gorev:
            return
        g = self.aktif_gorev
        tip = g["tip"]
        hedef = g["hedef_deger"]

        # İlerleme hesapla
        if tip == "sure":
            ilerleme = min(1.0, self.sure_sayac / hedef) if hedef > 0 else 0
            ilerleme_str = f"{self.sure_sayac:.0f}s / {hedef}s"
        elif tip == "element":
            ilerleme = min(1.0, self.sayac["element"] / hedef)
            ilerleme_str = f"{self.sayac['element']}/{hedef}"
        elif tip == "patlama":
            ilerleme = min(1.0, self.sayac["patlama"] / hedef)
            ilerleme_str = f"{self.sayac['patlama']}/{hedef}"
        elif tip == "hasar":
            ilerleme = 1.0 if self.sayac["hasar_alindi"] == 0 else 0.0
            ilerleme_str = "✓" if self.sayac["hasar_alindi"] == 0 else "✗"
        elif tip == "combo":
            ilerleme = min(1.0, self.sayac["combo_max"] / hedef)
            ilerleme_str = f"{self.sayac['combo_max']}/{hedef}"
        elif tip == "isabetler":
            ilerleme = min(1.0, self.sayac["isabetler"] / hedef)
            ilerleme_str = f"{self.sayac['isabetler']}/{hedef}"
        else:
            ilerleme, ilerleme_str = 0, "?"

        # Panel
        px = genislik - 310
        py = 140
        pw, ph = 290, 90
        panel = pygame.Surface((pw, ph), pygame.SRCALPHA)
        pygame.draw.rect(panel, (10, 15, 20, 200), (0, 0, pw, ph), border_radius=12)
        pygame.draw.rect(panel, (255, 200, 50, 180) if not self.tamamlandi else (50, 220, 100, 180),
                         (0, 0, pw, ph), 2, border_radius=12)
        ekran.blit(panel, (px, py))

        # Başlık
        t1 = font.render(f"📋 {g['isim']}", True, (255, 220, 50) if not self.tamamlandi else (80, 255, 120))
        ekran.blit(t1, (px + 12, py + 8))

        t2 = font_kucuk.render(g["hedef"], True, (190, 190, 190))
        ekran.blit(t2, (px + 12, py + 32))

        # İlerleme çubuğu
        bar_w = pw - 24
        bar_renk = (80, 200, 80) if self.tamamlandi else (255, 200, 50)
        pygame.draw.rect(ekran, (40, 40, 40), (px + 12, py + 55, bar_w, 12), border_radius=5)
        if ilerleme > 0:
            pygame.draw.rect(ekran, bar_renk, (px + 12, py + 55, int(bar_w * ilerleme), 12), border_radius=5)

        il_t = font_kucuk.render(ilerleme_str, True, (230, 230, 230))
        ekran.blit(il_t, (px + pw - il_t.get_width() - 14, py + 54))

        # Tamamlanma / Başarısız bildirimi
        if self.bildirim_sayac > 0:
            alpha = min(255, int(255 * self.bildirim_sayac))
            bt = font.render(self.bildirim_metni, True, (80, 255, 100) if self.tamamlandi else (255, 80, 80))
            bt.set_alpha(alpha)
            ekran.blit(bt, (genislik // 2 - bt.get_width() // 2, yukseklik // 2 - 60))
