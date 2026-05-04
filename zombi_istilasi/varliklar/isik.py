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
        if self.kalan <= 0: return
        oran = self.kalan / self.sure
        alpha = int(255 * oran)
        r, g, b = self.renk
        p1 = (int(self.x1), int(self.y1))
        p2 = (int(self.x2), int(self.y2))
        # Glow — tek surface, her ışın için değil, oyun_ekrani'nde toplu blit
        pygame.draw.line(ekran, (r, g, b, int(alpha * 0.3)), p1, p2, self.genislik * 4)
        pygame.draw.line(ekran, (r, g, b, int(alpha * 0.7)), p1, p2, self.genislik * 2)
        pygame.draw.line(ekran, (255, 255, 255, alpha), p1, p2, max(1, self.genislik - 1))
