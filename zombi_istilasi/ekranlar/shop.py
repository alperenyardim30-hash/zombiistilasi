import pygame
import random
from ayarlar import (
    GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI, YESIL,
    SARI, ALTIN, CAMGOBEGI,
    SILAHLAR, SILAH_SIRASI, YUKSELTMELER, DURBUNLER
)

# Silah kategorileri
KATEGORILER = [
    ("TABANCA",   ["cift","revolver","deagle","glock18","mateba"]),
    ("SMG",       ["smg","vector","pp90","bizon"]),
    ("TUFEK",     ["ak47","m4a1","aug","scar","famas","an94","galil"]),
    ("SHOTGUN",   ["shotgun","aa12","ksg","spas","striker","saiga"]),
    ("SNIPER",    ["sniper","awm","barrett","intervention","cheytac"]),
    ("LAZER",     ["lazer","lazer_mk2","ion","taser_xl","phaser"]),
    ("PLAZMA",    ["plazma","plazma_mk2","void","antimatter"]),
    ("AGIR",      ["minigun","vulcan","chaingun"]),
    ("ALEV",      ["alev","napalm","drakon"]),
    ("PATLAYICI", ["bomba","roket","thermobarik","rail","thor","orbital"]),
    ("EFSANEVI",  ["widowmaker","apocalypse","zeus","mjolnir","nemesis","the_end"]),
]

class Shop:
    def __init__(self):
        self.font_baslik = pygame.font.SysFont("Impact", 40)
        self.font_kart   = pygame.font.SysFont("Consolas", 14, bold=True)
        self.font_kucuk  = pygame.font.SysFont("Consolas", 12)
        self.font_buton  = pygame.font.SysFont("Consolas", 22, bold=True)
        self.mesaj = ""
        self.mesaj_sayac = 0.0
        self.zaman = 0.0
        self.scroll_y = 0
        self.hedef_scroll = 0
        self.aktif_kategori = 0
        # Firsat sistemi
        self.firsat_silahlar = []
        self.firsat_carpani = 0.6
        self.firsat_yenile()

    def firsat_yenile(self):
        havuz = [k for k in SILAH_SIRASI if k != "tabanca"]
        self.firsat_silahlar = random.sample(havuz, min(3, len(havuz)))

    def guncelle(self, dt):
        self.zaman += dt
        if self.mesaj_sayac > 0:
            self.mesaj_sayac -= dt
        self.scroll_y += (self.hedef_scroll - self.scroll_y) * min(1.0, 12 * dt)

    def _mesaj(self, txt):
        self.mesaj = txt
        self.mesaj_sayac = 2.5

    # ── CIZ ──────────────────────────────────────────────────
    def ciz(self, ekran, oyuncu, puan_sis):
        ekran.fill((12, 14, 18))
        # Ust bar
        pygame.draw.rect(ekran, (18, 22, 30), (0, 0, GENISLIK, 60))
        t = self.font_baslik.render("-- MAGAZIN --", True, SARI)
        ekran.blit(t, (GENISLIK//2 - t.get_width()//2, 8))
        pt = self.font_kart.render(f"PARA: {puan_sis.para}$", True, ALTIN)
        ekran.blit(pt, (GENISLIK - pt.get_width() - 20, 20))

        # Kategori sekmeleri (sol panel)
        self._ciz_kategoriler(ekran)

        # Icerik alani (sag)
        clip = pygame.Rect(180, 65, GENISLIK - 195, YUKSEKLIK - 140)
        ekran.set_clip(clip)
        self._ciz_silahlar(ekran, oyuncu, puan_sis, clip)
        ekran.set_clip(None)

        # Yukseltme + durbun alt panel
        self._ciz_alt_panel(ekran, oyuncu, puan_sis)

        # Devam butonu
        self._ciz_devam_butonu(ekran)

        # Mesaj
        if self.mesaj_sayac > 0:
            mt = self.font_kart.render(self.mesaj, True, YESIL)
            ekran.blit(mt, (GENISLIK//2 - mt.get_width()//2, YUKSEKLIK - 30))

    def _ciz_kategoriler(self, ekran):
        bx, by = 5, 70
        bw, bh = 165, 32
        for i, (isim, _) in enumerate(KATEGORILER):
            aktif = i == self.aktif_kategori
            bg = (40, 55, 70) if aktif else (22, 26, 34)
            border = SARI if aktif else (50, 55, 65)
            rect = pygame.Rect(bx, by + i * (bh + 4), bw, bh)
            pygame.draw.rect(ekran, bg, rect, border_radius=6)
            pygame.draw.rect(ekran, border, rect, 2, border_radius=6)
            t = self.font_kucuk.render(isim, True, SARI if aktif else (160,160,160))
            ekran.blit(t, (rect.x + 10, rect.y + 8))

    def _ciz_silahlar(self, ekran, oyuncu, puan_sis, clip):
        _, silah_keys = KATEGORILER[self.aktif_kategori]
        kw, kh, gap = 200, 110, 12
        cols = max(1, (clip.width - gap) // (kw + gap))
        sx = clip.x + gap
        sy = clip.y + gap - int(self.scroll_y)
        fare = pygame.mouse.get_pos()

        for idx, key in enumerate(silah_keys):
            if key not in SILAHLAR:
                continue
            v = SILAHLAR[key]
            col = idx % cols
            row = idx // cols
            kx = sx + col * (kw + gap)
            ky = sy + row * (kh + gap)

            # Firsat kontrolu
            firsat = key in self.firsat_silahlar
            sahip = key in oyuncu.envanter
            hover = pygame.Rect(kx, ky, kw, kh).collidepoint(fare)

            # Kart arkaplan
            if sahip:
                bg = (30, 50, 35)
            elif firsat:
                bg = (50, 40, 20)
            else:
                bg = (25, 28, 35)

            border = YESIL if sahip else (SARI if firsat else ((100,100,140) if hover else (45,48,58)))

            pygame.draw.rect(ekran, bg, (kx, ky, kw, kh), border_radius=10)
            pygame.draw.rect(ekran, border, (kx, ky, kw, kh), 2 if not hover else 3, border_radius=10)

            # Renk noktasi
            pygame.draw.circle(ekran, v["renk"], (kx + 18, ky + 20), 8)

            # Isim
            it = self.font_kart.render(v["isim"][:18], True, BEYAZ)
            ekran.blit(it, (kx + 34, ky + 10))

            # Hasar bilgi
            ht = self.font_kucuk.render(f"DMG:{v['hasar']}  SPD:{v['ates_hizi']}", True, (160,160,160))
            ekran.blit(ht, (kx + 10, ky + 38))

            # Fiyat veya sahip
            if sahip:
                st = self.font_kucuk.render("[SAHIPSIN]", True, CAMGOBEGI)
                ekran.blit(st, (kx + 10, ky + kh - 24))
            else:
                fiyat = v["fiyat"]
                if firsat:
                    fiyat = int(fiyat * self.firsat_carpani)
                    ft = self.font_kucuk.render(f"FIRSAT: {fiyat}$", True, SARI)
                else:
                    ft = self.font_kucuk.render(f"{fiyat}$", True, ALTIN)
                ekran.blit(ft, (kx + 10, ky + kh - 24))

            # Firsat etiketi
            if firsat and not sahip:
                pygame.draw.rect(ekran, (200,160,0), (kx+kw-50, ky+2, 48, 16), border_radius=4)
                tt = self.font_kucuk.render("-40%", True, SIYAH)
                ekran.blit(tt, (kx+kw-46, ky+3))

    def _ciz_alt_panel(self, ekran, oyuncu, puan_sis):
        py = YUKSEKLIK - 70
        pygame.draw.rect(ekran, (18, 22, 30), (0, py, GENISLIK, 70))
        pygame.draw.line(ekran, (50, 55, 65), (0, py), (GENISLIK, py), 2)

        # Yukseltmeler
        bx = 15
        for key, veri in YUKSELTMELER.items():
            seviye = oyuncu.yukseltmeler.get(key, 0)
            maks = veri["max_seviye"]
            fiyat = veri["fiyat"] * (seviye + 1)
            renk = CAMGOBEGI if seviye < maks else (80,80,80)
            txt = f"{veri['isim']} Lv{seviye}/{maks}"
            t = self.font_kucuk.render(txt, True, renk)
            ekran.blit(t, (bx, py + 8))
            ft = self.font_kucuk.render(f"{fiyat}$", True, ALTIN if seviye < maks else (80,80,80))
            ekran.blit(ft, (bx, py + 24))
            bx += 120

    def _ciz_devam_butonu(self, ekran):
        bw, bh = 260, 44
        bx = GENISLIK // 2 - bw // 2
        by = YUKSEKLIK - 118
        fare = pygame.mouse.get_pos()
        hover = pygame.Rect(bx, by, bw, bh).collidepoint(fare)
        bg = (40, 180, 60) if hover else (30, 120, 40)
        pygame.draw.rect(ekran, bg, (bx, by, bw, bh), border_radius=12)
        pygame.draw.rect(ekran, (80, 220, 100), (bx, by, bw, bh), 2, border_radius=12)
        t = self.font_buton.render(">> SONRAKI DALGA >>", True, BEYAZ)
        ekran.blit(t, (bx + bw//2 - t.get_width()//2, by + 8))

    # ── TIK ISLE ─────────────────────────────────────────────
    def tik_isle(self, event, oyuncu, puan_sis):
        if event.type == pygame.MOUSEWHEEL:
            self.hedef_scroll = max(0, self.hedef_scroll - event.y * 40)
            return None

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return None

        fx, fy = event.pos

        # Devam butonu
        bw, bh = 260, 44
        bx = GENISLIK // 2 - bw // 2
        by = YUKSEKLIK - 118
        if pygame.Rect(bx, by, bw, bh).collidepoint(fx, fy):
            return "devam"

        # Kategori sekmeleri
        kbx, kby = 5, 70
        kbw, kbh = 165, 32
        for i in range(len(KATEGORILER)):
            r = pygame.Rect(kbx, kby + i * (kbh + 4), kbw, kbh)
            if r.collidepoint(fx, fy):
                self.aktif_kategori = i
                self.hedef_scroll = 0
                self.scroll_y = 0
                return None

        # Silah kartlari
        clip = pygame.Rect(180, 65, GENISLIK - 195, YUKSEKLIK - 140)
        if clip.collidepoint(fx, fy):
            _, silah_keys = KATEGORILER[self.aktif_kategori]
            kw, kh, gap = 200, 110, 12
            cols = max(1, (clip.width - gap) // (kw + gap))
            sx = clip.x + gap
            sy = clip.y + gap - int(self.scroll_y)

            for idx, key in enumerate(silah_keys):
                if key not in SILAHLAR:
                    continue
                col = idx % cols
                row = idx // cols
                kx = sx + col * (kw + gap)
                ky = sy + row * (kh + gap)
                if pygame.Rect(kx, ky, kw, kh).collidepoint(fx, fy):
                    self._satin_al(key, oyuncu, puan_sis)
                    return None

        # Yukseltme tiklama
        alt_y = YUKSEKLIK - 70
        if fy >= alt_y:
            bx = 15
            for key, veri in YUKSELTMELER.items():
                r = pygame.Rect(bx, alt_y, 115, 50)
                if r.collidepoint(fx, fy):
                    self._yukseltme_al(key, oyuncu, puan_sis)
                    return None
                bx += 120

        return None

    def _satin_al(self, key, oyuncu, puan_sis):
        if key in oyuncu.envanter:
            self._mesaj("Zaten sahipsin!")
            return
        v = SILAHLAR[key]
        fiyat = v["fiyat"]
        if key in self.firsat_silahlar:
            fiyat = int(fiyat * self.firsat_carpani)
        if puan_sis.harca(fiyat):
            oyuncu.silah_al(key)
            self._mesaj(f"{v['isim']} alindi!")
        else:
            self._mesaj(f"Yeterli para yok! ({fiyat}$ gerekli)")

    def _yukseltme_al(self, key, oyuncu, puan_sis):
        veri = YUKSELTMELER[key]
        seviye = oyuncu.yukseltmeler.get(key, 0)
        if seviye >= veri["max_seviye"]:
            self._mesaj("Maks seviye!")
            return
        fiyat = veri["fiyat"] * (seviye + 1)
        if puan_sis.harca(fiyat):
            oyuncu.yukseltmeler[key] = seviye + 1
            self._mesaj(f"{veri['isim']} Lv{seviye+1}!")
        else:
            self._mesaj(f"Yeterli para yok! ({fiyat}$ gerekli)")
