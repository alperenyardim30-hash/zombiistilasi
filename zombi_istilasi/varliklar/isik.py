# ============================================================
#  varliklar/isik.py — Anlik Isin (Raycast Beam) Gorunum Sinifi
# ============================================================
import pygame
import math


class AnlikIsin:
    """Lazer/Rail/Phaser silahlar icin anlik cizgi flash gorunum."""

    def __init__(self, x1, y1, aci, renk, uzunluk, genislik=3, sure=0.15):
        self.x1 = float(x1)
        self.y1 = float(y1)
        aci_rad = math.radians(aci)
        self.x2 = x1 + math.cos(aci_rad) * uzunluk
        self.y2 = y1 + math.sin(aci_rad) * uzunluk
        self.renk = renk[:3]
        self.genislik = genislik
        self.sure = sure
        self.kalan = sure

    def update(self, dt):
        self.kalan -= dt
        return self.kalan > 0

    def ciz(self, ekran):
        if self.kalan <= 0:
            return
        oran = self.kalan / self.sure          # 1.0 -> 0.0
        alpha = int(255 * oran)
        r, g, b = self.renk

        p1 = (int(self.x1), int(self.y1))
        p2 = (int(self.x2), int(self.y2))

        # Dis parlama katmani (kalin, seffaf)
        gw = self.genislik * 5
        glow_surf = pygame.Surface(ekran.get_size(), pygame.SRCALPHA)
        pygame.draw.line(glow_surf, (r, g, b, int(alpha * 0.25)), p1, p2, gw)
        ekran.blit(glow_surf, (0, 0))

        # Orta katman
        mid_surf = pygame.Surface(ekran.get_size(), pygame.SRCALPHA)
        pygame.draw.line(mid_surf, (r, g, b, int(alpha * 0.7)), p1, p2, self.genislik * 2)
        ekran.blit(mid_surf, (0, 0))

        # Beyaz cekirdek
        core_surf = pygame.Surface(ekran.get_size(), pygame.SRCALPHA)
        pygame.draw.line(core_surf, (255, 255, 255, alpha), p1, p2, max(1, self.genislik - 1))
        ekran.blit(core_surf, (0, 0))
