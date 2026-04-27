# ============================================================
#  varliklar/patlama.py — Roket Patlama Efekti
# ============================================================
import pygame
import math


class Patlama:
    def __init__(self, x, y, max_r, hasar=0):
        self.x = x
        self.y = y
        self.max_r = max_r
        self.hasar = hasar          # Silahın gerçek patlama hasarı
        self.r = 10.0
        self.sure = 0.45        # toplam süre
        self.gecen = 0.0
        self.hasar_verildi = False   # AoE hasarı yalnızca 1 kez verilir

    @property
    def bitti_mi(self):
        return self.gecen >= self.sure

    @property
    def ilerleme(self):
        return self.gecen / self.sure

    def update(self, dt):
        self.gecen += dt
        self.r = self.max_r * self.ilerleme

    def ciz(self, ekran):
        if self.bitti_mi:
            return
        alpha = int(255 * (1 - self.ilerleme))
        # Dış halka - turuncu
        surf = pygame.Surface((self.max_r * 2 + 20, self.max_r * 2 + 20), pygame.SRCALPHA)
        cx = cy = self.max_r + 10
        pygame.draw.circle(surf, (255, 120, 30, min(255, alpha + 60)),
                           (cx, cy), int(self.r), max(1, int(8 * (1 - self.ilerleme))))
        # İç dolgu - sarı
        pygame.draw.circle(surf, (255, 220, 50, alpha // 2), (cx, cy), max(1, int(self.r * 0.6)))
        ekran.blit(surf, (int(self.x) - self.max_r - 10, int(self.y) - self.max_r - 10))

    def zombi_hasari_ver(self, zombiler, hasar_carpani=1.0):
        """Patlama alanındaki tüm zombilere hasar ver. Yalnızca 1 kez çalışır.
        Merkezde tam hasar, kenarda %30 hasar (mesafe bazlı düşüş).
        """
        if self.hasar_verildi:
            return []
        self.hasar_verildi = True
        
        # Silahın kendi hasarı varsa onu kullan, yoksa eski formül (geriye uyum)
        baz_hasar = self.hasar if self.hasar > 0 else self.max_r * 1.5
        
        oldukler = []
        for z in list(zombiler):
            dx = z.x - self.x
            dy = z.y - self.y
            mesafe = math.hypot(dx, dy)
            etki_alani = self.max_r + z.yari_cap
            if mesafe < etki_alani:
                # Mesafe bazlı hasar düşüşü: merkezde %100, kenarda %30
                mesafe_orani = mesafe / etki_alani if etki_alani > 0 else 0
                hasar_carpan = 1.0 - (mesafe_orani * 0.7)  # 1.0 → 0.3
                gercek_hasar = baz_hasar * hasar_carpani * hasar_carpan
                z.can -= gercek_hasar
                z.hit_sayac = 0.2
                if z.can <= 0:
                    oldukler.append(z)
        return oldukler
