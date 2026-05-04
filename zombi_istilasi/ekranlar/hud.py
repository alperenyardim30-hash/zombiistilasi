# ============================================================
#  ekranlar/hud.py — Tüm HUD (Heads-Up Display) çizim mantığı
# ============================================================
import pygame
import math
import random
from ayarlar import (
    GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI, SARI, ALTIN,
    MOR, ZIRH_MAVI, SILAHLAR, SILAH_SIRASI,
)
from sistemler.perk_sistemi import PERKLER


class HudYoneticisi:
    """
    OyunEkrani'ndan ayrıştırılmış arayüz çizim sınıfı.
    Sorumluluğu: Can/Kalkan/XP barları, silah barı, mermi göstergesi,
    boss barı, dalga bildirimi ve combo göstergesi.
    """

    def __init__(self, fontlar: dict):
        """
        fontlar: {
            "hud": pygame.font,  "buyuk": pygame.font,
            "kucuk": pygame.font, "mermi": pygame.font,
            "combo": dict[int, pygame.font]
        }
        """
        self.font_hud    = fontlar["hud"]
        self.font_buyuk  = fontlar["buyuk"]
        self.font_kucuk  = fontlar["kucuk"]
        self.font_mermi  = fontlar["mermi"]
        self._combo_fontlar = fontlar.get("combo", {})

    # ----------------------------------------------------------
    # Ana Çizim
    # ----------------------------------------------------------
    def ciz(self, ekran, oyuncu, puan_sis, dalga_sis, perk_sis, zombiler):
        """Tüm HUD katmanlarını tek çağrıyla çizer."""
        self._ciz_hud(ekran, oyuncu, puan_sis, dalga_sis, perk_sis, zombiler)
        self._ciz_silah_bar(ekran, oyuncu)
        self._ciz_bildirim(ekran, dalga_sis)
        self._ciz_boss_bar(ekran, zombiler)

    # ----------------------------------------------------------
    # Sol Üst Panel: Can, Kalkan, Stamina, XP, Ultimate + Perkler
    # Sağ Üst Panel: Puan, Para, Dalga, Zombi sayısı
    # Sağ Alt Panel: Mermi göstergesi
    # Orta: Combo
    # ----------------------------------------------------------
    def _ciz_hud(self, ekran, oyuncu, puan_sis, dalga_sis, perk_sis, zombiler):
        # Sol üst arka plan paneli
        pygame.draw.rect(ekran, (10, 10, 15, 200), (20, 20, 300, 140), border_radius=12)
        pygame.draw.rect(ekran, (50, 50, 60),       (20, 20, 300, 140), 2, border_radius=12)

        bx, by, bg, byk = 30, 30, 280, 16

        # 1. Can
        c_oran = oyuncu.can / oyuncu.max_can_degeri
        pygame.draw.rect(ekran, (60, 0, 0), (bx, by, bg, byk), border_radius=6)
        if c_oran > 0:
            pygame.draw.rect(ekran, (220, 50, 50), (bx, by, int(bg * c_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"HP: {int(oyuncu.can)}", True, BEYAZ), (bx + 8, by))

        # 2. Kalkan
        by += 22
        k_oran = oyuncu.kalkan / oyuncu.max_kalkan_degeri
        pygame.draw.rect(ekran, (0, 30, 80), (bx, by, bg, byk), border_radius=6)
        if k_oran > 0:
            pygame.draw.rect(ekran, ZIRH_MAVI, (bx, by, int(bg * k_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"SH: {int(oyuncu.kalkan)}", True, BEYAZ), (bx + 8, by))
        if oyuncu.kalkan_yenilenme_sayaci > 0:
            bt = self.font_kucuk.render(f"SH: {oyuncu.kalkan_yenilenme_sayaci:.1f}s", True, (100, 100, 200))
            ekran.blit(bt, (bx + bg + 8, by - 22))

        # 3. Stamina
        by += 22
        s_oran = oyuncu.stamina / oyuncu.max_stamina_degeri
        pygame.draw.rect(ekran, (60, 60, 60), (bx, by, bg, byk), border_radius=6)
        if s_oran > 0:
            pygame.draw.rect(ekran, (255, 255, 100), (bx, by, int(bg * s_oran), byk), border_radius=6)
        ekran.blit(
            self.font_kucuk.render(f"STM: {int(oyuncu.stamina)}", True, SIYAH if s_oran > 0.5 else BEYAZ),
            (bx + 8, by),
        )

        # 4. XP
        by += 22
        xp_oran = puan_sis.xp / puan_sis.xp_hedef
        pygame.draw.rect(ekran, (40, 40, 40), (bx, by, bg, byk), border_radius=6)
        if xp_oran > 0:
            pygame.draw.rect(ekran, MOR, (bx, by, int(bg * xp_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"SV: {puan_sis.seviye}", True, BEYAZ), (bx + 8, by))

        # 5. Ultimate
        by += 22
        u_oran = 1.0 - (oyuncu.ult_bekleme / oyuncu.ult_max_cd)
        pygame.draw.rect(ekran, (40, 40, 0), (bx, by, bg, byk), border_radius=6)
        if u_oran > 0:
            pygame.draw.rect(ekran, SARI, (bx, by, int(bg * u_oran), byk), border_radius=6)
        ult_metin = "ULT [BOŞLUK]" if u_oran >= 1.0 else f"ULT: {oyuncu.ult_bekleme:.1f}s"
        ekran.blit(
            self.font_kucuk.render(ult_metin, True, SIYAH if u_oran >= 1.0 else BEYAZ),
            (bx + bg // 2 - 45, by),
        )

        # Aktif Perk ikonları (sol panelin altı)
        if perk_sis.aktif_perkler:
            py_ikon = 175
            for p_key in perk_sis.aktif_perkler[:6]:
                p = PERKLER.get(p_key, {})
                pt = self.font_kucuk.render(p.get("isim", p_key)[:12], True, (180, 255, 180))
                ekran.blit(pt, (25, py_ikon))
                py_ikon += 18

        # Sağ üst panel
        pygame.draw.rect(ekran, (10, 10, 15, 200), (GENISLIK - 240, 20, 220, 110), border_radius=12)
        pygame.draw.rect(ekran, (50, 50, 60),       (GENISLIK - 240, 20, 220, 110), 2, border_radius=12)
        for metin, deger, renk, y in [
            (f"PUAN: {puan_sis.puan}",    None, BEYAZ,           30),
            (f"PARA: {puan_sis.para}$",   None, ALTIN,           60),
            (f"DALGA: {dalga_sis.dalga_no}", None, (180, 255, 180), 90),
        ]:
            t = self.font_hud.render(metin, True, renk)
            ekran.blit(t, (GENISLIK - t.get_width() - 35, y))

        spawn_kalan  = len(dalga_sis.spawn_listesi)
        zombi_kalan  = len(zombiler) + spawn_kalan
        zt = self.font_hud.render(f"ZOMBİ: {zombi_kalan}", True, (220, 80, 80))
        ekran.blit(zt, (GENISLIK - zt.get_width() - 35, 120))

        mod = getattr(dalga_sis, "aktif_mod", None)
        if mod and mod.get("efekt") == "para":
            pt2 = self.font_hud.render("💰 2x PARA", True, ALTIN)
            ekran.blit(pt2, (GENISLIK - pt2.get_width() - 35, 150))

        # Sağ alt: Mermi göstergesi
        ak       = oyuncu.aktif_silah
        mermi    = oyuncu.mermiler.get(ak, -1)
        kapasite = oyuncu._silah_max_mermi(ak)
        m_metin  = "∞" if kapasite == -1 else f"{mermi}/{kapasite}"
        renk     = KIRMIZI if mermi == 0 else (SARI if kapasite > 0 and mermi < kapasite * 0.3 else BEYAZ)
        pygame.draw.rect(ekran, (10, 10, 15, 200), (GENISLIK - 260, YUKSEKLIK - 120, 240, 100), border_radius=15)
        pygame.draw.rect(ekran, (50, 50, 60),       (GENISLIK - 260, YUKSEKLIK - 120, 240, 100), 2, border_radius=15)
        t = self.font_mermi.render(m_metin, True, renk)
        ekran.blit(t, (GENISLIK - 140 - t.get_width() // 2, YUKSEKLIK - 105))
        sit = self.font_kucuk.render(SILAHLAR[ak]["isim"], True, SILAHLAR[ak]["renk"])
        ekran.blit(sit, (GENISLIK - 140 - sit.get_width() // 2, YUKSEKLIK - 45))

        # Combo göstergesi
        if puan_sis.combo > 1:
            boyut = (min(66, 46 + puan_sis.combo * 2) // 4) * 4
            font_combo = self._combo_fontlar.get(boyut, self.font_buyuk)
            titreme    = random.randint(-2, 2) if puan_sis.combo >= 5 else 0
            renk_combo = (255, 100, 0) if puan_sis.combo < 10 else (255, 50, 50)
            ct = font_combo.render(f"{puan_sis.combo}x COMBO!", True, renk_combo)
            ekran.blit(ct, (GENISLIK // 2 - ct.get_width() // 2 + titreme, 80 + titreme))

    def _ciz_silah_bar(self, ekran, oyuncu):
        bar_yuk, bosluk = 80, 10
        kart_gen = 80
        bar_y = YUKSEKLIK - bar_yuk - 20

        sahip = [k for k in SILAH_SIRASI if k in oyuncu.envanter]
        aktif_idx = sahip.index(oyuncu.aktif_silah) if oyuncu.aktif_silah in sahip else 0
        pencere = 9
        baslangic = max(0, min(len(sahip) - pencere, aktif_idx - pencere // 2))
        gosterilecek = sahip[baslangic : baslangic + pencere]

        toplam_gen = len(gosterilecek) * (kart_gen + bosluk) - bosluk
        start_x = GENISLIK // 2 - toplam_gen // 2

        pygame.draw.rect(ekran, (10, 10, 15, 200), (start_x - 10, bar_y - 10, toplam_gen + 20, bar_yuk + 20), border_radius=15)

        for i, key in enumerate(gosterilecek):
            veri  = SILAHLAR[key]
            aktif = oyuncu.aktif_silah == key
            kx, ky = start_x + i * (kart_gen + bosluk), bar_y
            bg_renk = (50, 80, 50) if aktif else (30, 30, 40)
            border  = veri["renk"] if aktif else (80, 80, 80)

            if aktif:
                hale = pygame.Surface((kart_gen + 10, bar_yuk + 10), pygame.SRCALPHA)
                pygame.draw.rect(hale, (*veri["renk"], 80), (0, 0, kart_gen + 10, bar_yuk + 10), border_radius=12)
                ekran.blit(hale, (kx - 5, ky - 5))

            pygame.draw.rect(ekran, bg_renk, (kx, ky, kart_gen, bar_yuk), border_radius=10)
            pygame.draw.rect(ekran, border,  (kx, ky, kart_gen, bar_yuk), 2, border_radius=10)
            pygame.draw.circle(ekran, veri["renk"], (kx + kart_gen // 2, ky + 25), 12)
            isim_t = self.font_kucuk.render(veri["isim"][:9], True, BEYAZ if aktif else (160, 160, 160))
            ekran.blit(isim_t, (kx + kart_gen // 2 - isim_t.get_width() // 2, ky + 45))

    def _ciz_bildirim(self, ekran, dalga_sis):
        mod = getattr(dalga_sis, "aktif_mod", None)
        if mod and mod.get("efekt") not in (None, "karanlik"):
            renk  = mod.get("renk", (255, 255, 255))
            alpha = max(0, min(255, 60 + int(30 * math.sin(pygame.time.get_ticks() / 300))))
            cerceve = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
            pygame.draw.rect(cerceve, (*renk, alpha), (0, 0, GENISLIK, YUKSEKLIK), 8)
            ekran.blit(cerceve, (0, 0))

        metin, kalan = dalga_sis.bildirim_goster()
        if not metin:
            return
        alpha = min(255, int(255 * (kalan / 2.5)))
        surf  = self.font_buyuk.render(metin, True, (255, 100, 100) if "BOSS" in metin else SARI)
        surf.set_alpha(alpha)
        ekran.blit(surf, (GENISLIK // 2 - surf.get_width() // 2, YUKSEKLIK // 2 - 120))

    def _ciz_boss_bar(self, ekran, zombiler):
        for z in zombiler:
            if z.tip == "boss" and z.alive():
                bw, bh = 600, 22
                bx = GENISLIK // 2 - bw // 2
                by = 15
                oran = max(0.0, z.can / z.max_can)
                pygame.draw.rect(ekran, (60, 0, 0), (bx, by, bw, bh), border_radius=8)
                if oran > 0:
                    renk = (220, 30, 30) if oran > 0.3 else (255, 80, 0)
                    pygame.draw.rect(ekran, renk, (bx, by, int(bw * oran), bh), border_radius=8)
                pygame.draw.rect(ekran, (180, 0, 0), (bx, by, bw, bh), 2, border_radius=8)
                bt = self.font_kucuk.render(f"👹 BOSS  {int(z.can)}/{int(z.max_can)}", True, (255, 200, 200))
                ekran.blit(bt, (GENISLIK // 2 - bt.get_width() // 2, by + 2))
                break
