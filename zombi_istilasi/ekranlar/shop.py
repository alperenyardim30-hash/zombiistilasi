# ============================================================
#  ekranlar/shop.py — Scroll Özellikli 60+ Silah Mağazası
# ============================================================
import pygame
import math
from ayarlar import (
    GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI, YESIL,
    SARI, ALTIN, ACIK_GRI, KOYU_GRI, MOR, CAMGOBEGI, PEMBE,
    SILAHLAR, SILAH_SIRASI, YUKSELTMELER, DURBUNLER
)

class Shop:
    def __init__(self):
        self.font_baslik = pygame.font.SysFont("Impact", 46)
        self.font_kart   = pygame.font.SysFont("Consolas", 15, bold=True)
        self.font_kucuk  = pygame.font.SysFont("Consolas", 13)
        self.font_buton  = pygame.font.SysFont("Consolas", 24, bold=True)
        self.mesaj = ""
        self.mesaj_sayac = 0.0
        self.zaman = 0.0
        
        self.kaydirma_y = 0
        self.hedef_kaydirma_y = 0

    def guncelle(self, dt):
        self.zaman += dt
        if self.mesaj_sayac > 0:
            self.mesaj_sayac -= dt
            
        # Yumuşak kaydırma
        self.kaydirma_y += (self.hedef_kaydirma_y - self.kaydirma_y) * 15 * dt

    def ciz(self, ekran, oyuncu, puan_sis):
        ekran.fill((14, 18, 22))
        self._ciz_arkaplan(ekran)
        
        # İçerik için ayrı yüzey (kaydırma için)
        icerik_yuzey = pygame.Surface((GENISLIK, max(YUKSEKLIK, 2800)), pygame.SRCALPHA)
        self._ciz_silahlar(icerik_yuzey, oyuncu, puan_sis)
        self._ciz_yukseltmeler(icerik_yuzey, oyuncu, puan_sis)
        self._ciz_durbunler(icerik_yuzey, oyuncu, puan_sis)
        
        ekran.blit(icerik_yuzey, (0, self.kaydirma_y))
        
        # Sabit UI elemanları (Üst başlık ve alt buton)
        self._ciz_ust_bar(ekran, puan_sis)
        self._ciz_devam_buton(ekran)
        
        if self.mesaj_sayac > 0:
            self._ciz_mesaj(ekran)

    def _ciz_arkaplan(self, ekran):
        for i in range(0, GENISLIK, 80):
            pygame.draw.line(ekran, (20, 24, 28), (i, 0), (i, YUKSEKLIK), 1)
        for j in range(int(self.kaydirma_y) % 80, YUKSEKLIK, 80):
            pygame.draw.line(ekran, (20, 24, 28), (0, j), (GENISLIK, j), 1)

    def _ciz_ust_bar(self, ekran, puan_sis):
        # Üst bar arkaplanı
        pygame.draw.rect(ekran, (10, 10, 15, 230), (0, 0, GENISLIK, 80))
        pygame.draw.line(ekran, PEMBE, (0, 80), (GENISLIK, 80), 2)
        
        t = self.font_baslik.render("KARA BORSA", True, PEMBE)
        ekran.blit(t, (40, 15))
        
        para_kutu = pygame.Surface((240, 50), pygame.SRCALPHA)
        pygame.draw.rect(para_kutu, (0, 0, 0, 150), (0, 0, 240, 50), border_radius=12)
        pygame.draw.rect(para_kutu, ALTIN, (0, 0, 240, 50), 2, border_radius=12)
        ekran.blit(para_kutu, (GENISLIK - 280, 15))
        
        para_t = self.font_baslik.render(f"💰 {puan_sis.para}", True, SARI)
        ekran.blit(para_t, (GENISLIK - 160 - para_t.get_width() // 2, 16))

    def _ciz_silahlar(self, ekran, oyuncu, puan_sis):
        baslik = self.font_baslik.render("— YENİ NESİL SİLAHLAR —", True, CAMGOBEGI)
        ekran.blit(baslik, (80, 120))

        kart_gen, kart_yuk, bosluk = 200, 180, 20
        bx, by = 80, 180
        
        fare_y = pygame.mouse.get_pos()[1] - self.kaydirma_y
        fare_x = pygame.mouse.get_pos()[0]

        for i, key in enumerate(SILAH_SIRASI):
            if key == "tabanca": continue
            idx = i - 1
            row, col = idx // 4, idx % 4  # 4 sütun!
            kx, ky = bx + col * (kart_gen + bosluk), by + row * (kart_yuk + bosluk)
            
            veri = SILAHLAR[key]
            sahip = key in oyuncu.envanter
            bg = (20, 35, 45) if sahip else (25, 25, 30)
            border = veri["renk"] if sahip else (50, 50, 60)
            
            hover = pygame.Rect(kx, ky, kart_gen, kart_yuk).collidepoint(fare_x, fare_y)
            if hover and not sahip: border = BEYAZ
            
            pygame.draw.rect(ekran, bg, (kx, ky, kart_gen, kart_yuk), border_radius=12)
            pygame.draw.rect(ekran, border, (kx, ky, kart_gen, kart_yuk), 2, border_radius=12)

            # Glow
            pygame.draw.circle(ekran, (*veri["renk"], 50), (kx + kart_gen // 2, ky + 30), 22)
            pygame.draw.circle(ekran, veri["renk"], (kx + kart_gen // 2, ky + 30), 12)

            isim = self.font_kart.render(veri["isim"], True, BEYAZ)
            ekran.blit(isim, (kx + kart_gen // 2 - isim.get_width() // 2, ky + 60))

            y_off = 85
            for line in veri["aciklama"]:
                t = self.font_kucuk.render(f"• {line}", True, (180, 180, 180))
                ekran.blit(t, (kx + 10, ky + y_off))
                y_off += 16

            if sahip:
                t = self.font_kucuk.render("SAHİPSİN ✓", True, CAMGOBEGI)
                ekran.blit(t, (kx + kart_gen // 2 - t.get_width() // 2, ky + kart_yuk - 25))
            else:
                karsi = puan_sis.para >= veri["fiyat"]
                btn_renk = YESIL if karsi else (80, 50, 50)
                self._mini_buton(ekran, f"{veri['fiyat']} 💰", kx + kart_gen // 2, ky + kart_yuk - 22, btn_renk)

    def _ciz_yukseltmeler(self, ekran, oyuncu, puan_sis):
        baslik = self.font_baslik.render("— BİYONİK GELİŞTİRMELER —", True, MOR)
        bx, by = GENISLIK - 600, 120
        ekran.blit(baslik, (bx, 120))

        kart_gen, kart_yuk, bosluk = 260, 110, 15

        fare_y = pygame.mouse.get_pos()[1] - self.kaydirma_y
        fare_x = pygame.mouse.get_pos()[0]

        keys = list(YUKSELTMELER.keys())
        for i, key in enumerate(keys):
            veri = YUKSELTMELER[key]
            row, col = i // 2, i % 2
            ky = by + 60 + row * (kart_yuk + bosluk)
            kx = bx + col * (kart_gen + bosluk)
            
            seviye = oyuncu.yukseltmeler.get(key, 0)
            max_sev = veri["max_seviye"]
            karsi = puan_sis.para >= veri["fiyat"]
            maxed = seviye >= max_sev

            bg = (35, 20, 45) if not maxed else (20, 35, 20)
            border = MOR if not maxed else YESIL
            
            hover = pygame.Rect(kx, ky, kart_gen, kart_yuk).collidepoint(fare_x, fare_y)
            if hover and not maxed: border = BEYAZ
            
            pygame.draw.rect(ekran, bg, (kx, ky, kart_gen, kart_yuk), border_radius=12)
            pygame.draw.rect(ekran, border, (kx, ky, kart_gen, kart_yuk), 2, border_radius=12)

            isim_t = self.font_kart.render(f"{veri['emoji']} {veri['isim']}", True, BEYAZ)
            ekran.blit(isim_t, (kx + 12, ky + 12))

            acik = self.font_kucuk.render(veri["aciklama"], True, (200, 180, 220))
            ekran.blit(acik, (kx + 12, ky + 35))

            # Seviye çubukları
            bar_w = (kart_gen - 24) / max_sev - 4
            for s in range(max_sev):
                renk = MOR if s < seviye else (50, 40, 60)
                pygame.draw.rect(ekran, renk, (kx + 12 + s * (bar_w + 4), ky + 60, bar_w, 8), border_radius=4)

            if maxed:
                btn_t = self.font_kucuk.render("MAKS ✓", True, YESIL)
                ekran.blit(btn_t, (kx + kart_gen - btn_t.get_width() - 12, ky + kart_yuk - 25))
            else:
                self._mini_buton(ekran, f"Yükselt {veri['fiyat']}💰", kx + kart_gen - 70, ky + kart_yuk - 20, (180, 80, 255) if karsi else (80, 60, 100))

    def _ciz_durbunler(self, ekran, oyuncu, puan_sis):
        baslik = self.font_baslik.render("— OPTİK SİSTEMLER —", True, ALTIN)
        bx, by = GENISLIK - 600, 680
        ekran.blit(baslik, (bx, by))

        kart_gen, kart_yuk, bosluk = 260, 80, 15
        
        fare_y = pygame.mouse.get_pos()[1] - self.kaydirma_y
        fare_x = pygame.mouse.get_pos()[0]

        keys = list(DURBUNLER.keys())
        for i, key in enumerate(keys):
            veri = DURBUNLER[key]
            row, col = i // 2, i % 2
            ky = by + 60 + row * (kart_yuk + bosluk)
            kx = bx + col * (kart_gen + bosluk)
            
            sahip = key in oyuncu.durbunler
            aktif = oyuncu.aktif_durbun == key
            
            bg = (40, 40, 20) if aktif else ((30, 30, 30) if sahip else (20, 20, 25))
            border = ALTIN if aktif else (ACIK_GRI if sahip else (50, 50, 60))
            
            hover = pygame.Rect(kx, ky, kart_gen, kart_yuk).collidepoint(fare_x, fare_y)
            if hover and not aktif: border = BEYAZ
            
            pygame.draw.rect(ekran, bg, (kx, ky, kart_gen, kart_yuk), border_radius=10)
            pygame.draw.rect(ekran, border, (kx, ky, kart_gen, kart_yuk), 2, border_radius=10)

            t = self.font_kart.render(f"{veri['emoji']} {veri['isim']}", True, BEYAZ)
            ekran.blit(t, (kx + 12, ky + 15))
            
            if aktif:
                st = self.font_kucuk.render("TAKILI ✓", True, ALTIN)
                ekran.blit(st, (kx + kart_gen - st.get_width() - 12, ky + 45))
            elif sahip:
                self._mini_buton(ekran, "TAK", kx + kart_gen - 50, ky + 50, (100, 100, 120))
            else:
                karsi = puan_sis.para >= veri["fiyat"]
                self._mini_buton(ekran, f"AL {veri['fiyat']}💰", kx + kart_gen - 70, ky + 50, (200, 180, 50) if karsi else (80, 70, 40))

    def _mini_buton(self, ekran, metin, cx, cy, renk):
        t = self.font_kucuk.render(metin, True, BEYAZ)
        bw, bh = t.get_width() + 24, 32
        bx, by = cx - bw // 2, cy - bh // 2
        pygame.draw.rect(ekran, renk, (bx, by, bw, bh), border_radius=8)
        ekran.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))

    def _ciz_devam_buton(self, ekran):
        fare = pygame.mouse.get_pos()
        bw, bh = 400, 70
        bx, by = GENISLIK // 2 - bw // 2, YUKSEKLIK - 110
        uzerinde = pygame.Rect(bx, by, bw, bh).collidepoint(fare)
        
        r = 60 + int(math.sin(self.zaman * 5) * 30)
        renk = (r, 220, r + 50) if uzerinde else (20, 180, 50)
        
        pygame.draw.rect(ekran, renk, (bx, by, bw, bh), border_radius=16)
        pygame.draw.rect(ekran, BEYAZ, (bx, by, bw, bh), 3, border_radius=16)
        t = self.font_buton.render("▶  SAVAŞA GERİ DÖN", True, SIYAH if not uzerinde else BEYAZ)
        ekran.blit(t, (GENISLIK // 2 - t.get_width() // 2, by + bh // 2 - t.get_height() // 2))

    def _ciz_mesaj(self, ekran):
        surf = self.font_kart.render(self.mesaj, True, BEYAZ)
        alpha = int(255 * min(1.0, self.mesaj_sayac / 0.5))
        bg = pygame.Surface((surf.get_width() + 60, surf.get_height() + 30), pygame.SRCALPHA)
        pygame.draw.rect(bg, (0, 0, 0, alpha), (0, 0, bg.get_width(), bg.get_height()), border_radius=12)
        ekran.blit(bg, (GENISLIK // 2 - bg.get_width() // 2, 100))
        
        surf.set_alpha(alpha)
        ekran.blit(surf, (GENISLIK // 2 - surf.get_width() // 2, 115))

    def tik_isle(self, event, oyuncu, puan_sis):
        if event.type == pygame.MOUSEWHEEL:
            # Sadece aşağı/yukarı kaydırma
            self.hedef_kaydirma_y += event.y * 60
            if self.hedef_kaydirma_y > 0: self.hedef_kaydirma_y = 0
            # Alt sınır: (Silah sayısı / 4) * 200 + offset
            min_y = -((len(SILAH_SIRASI) // 4) * 200) + YUKSEKLIK - 300
            if self.hedef_kaydirma_y < min_y: self.hedef_kaydirma_y = min_y
            return None

        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1: return None
        fare_x, fare_y_real = pygame.mouse.get_pos()
        fare_y = fare_y_real - self.kaydirma_y

        if pygame.Rect(GENISLIK // 2 - 200, YUKSEKLIK - 110, 400, 70).collidepoint(fare_x, fare_y_real):
            return "devam"

        bx, by, kart_gen, kart_yuk, bosluk = 80, 180, 200, 180, 20
        for i, key in enumerate(SILAH_SIRASI):
            if key == "tabanca": continue
            idx = i - 1
            kx, ky = bx + (idx % 4) * (kart_gen + bosluk), by + (idx // 4) * (kart_yuk + bosluk)
            if pygame.Rect(kx, ky, kart_gen, kart_yuk).collidepoint(fare_x, fare_y):
                if key in oyuncu.envanter:
                    self._mesaj_goster("Zaten sahipsin! (Mermiler Doldu)")
                elif puan_sis.harca(SILAHLAR[key]["fiyat"]):
                    oyuncu.silah_al(key)
                    self._mesaj_goster(f"✓ {SILAHLAR[key]['isim']} alındı!")
                else:
                    self._mesaj_goster("❌ Yeterli kredi yok!")

        bx, by, kart_gen, kart_yuk, bosluk = GENISLIK - 600, 180, 260, 110, 15
        for i, key in enumerate(YUKSELTMELER.keys()):
            kx, ky = bx + (i % 2) * (kart_gen + bosluk), by + (i // 2) * (kart_yuk + bosluk)
            if pygame.Rect(kx, ky, kart_gen, kart_yuk).collidepoint(fare_x, fare_y):
                veri = YUKSELTMELER[key]
                if oyuncu.yukseltmeler.get(key, 0) >= veri["max_seviye"]:
                    self._mesaj_goster("Maksimum seviyeye ulaşıldı!")
                elif puan_sis.harca(veri["fiyat"]):
                    oyuncu.yukseltmeler[key] = oyuncu.yukseltmeler.get(key, 0) + 1
                    if key == "can":
                        oyuncu.max_can += 40
                        oyuncu.can = min(oyuncu.can + 40, oyuncu.max_can)
                    elif key == "kalkan":
                        oyuncu.max_kalkan += 40
                        oyuncu.kalkan = min(oyuncu.kalkan + 40, oyuncu.max_kalkan)
                    elif key == "stamina":
                        oyuncu.max_stamina += 30
                        oyuncu.stamina = min(oyuncu.stamina + 30, oyuncu.max_stamina)
                    self._mesaj_goster(f"✓ {veri['isim']} Sev.{oyuncu.yukseltmeler[key]} oldu!")
                else:
                    self._mesaj_goster("❌ Yeterli kredi yok!")

        # Dürbün Tıklama Kontrolü
        bx, by, kart_gen, kart_yuk, bosluk = GENISLIK - 600, 740, 260, 80, 15
        for i, key in enumerate(DURBUNLER.keys()):
            kx, ky = bx + (i % 2) * (kart_gen + bosluk), by + (i // 2) * (kart_yuk + bosluk)
            if pygame.Rect(kx, ky, kart_gen, kart_yuk).collidepoint(fare_x, fare_y):
                veri = DURBUNLER[key]
                if key in oyuncu.durbunler:
                    oyuncu.aktif_durbun = key
                    self._mesaj_goster(f"✓ {veri['isim']} takıldı!")
                elif puan_sis.harca(veri["fiyat"]):
                    oyuncu.durbunler.append(key)
                    oyuncu.aktif_durbun = key
                    self._mesaj_goster(f"✓ {veri['isim']} satın alındı ve takıldı!")
                else:
                    self._mesaj_goster("❌ Yeterli kredi yok!")
        return None

    def _mesaj_goster(self, metin):
        self.mesaj = metin
        self.mesaj_sayac = 2.0
