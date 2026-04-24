# ============================================================
#  varliklar/drop.py — Düşen Eşyalar (Can Paketi, Mermi Kutusu)
# ============================================================
import pygame
import math
import random


class Drop(pygame.sprite.Sprite):
    def __init__(self, x, y, tip):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.tip = tip          # "can" | "mermi"
        self.yari_cap = 12
        self.omur = 8.0         # 8 sn sonra kaybolur
        self.titreme = 0.0

        boyut = self.yari_cap * 2 + 4
        self.image = self._olustur(boyut)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _olustur(self, boyut):
        img = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        cx = cy = boyut // 2
        if self.tip == "can":
            pygame.draw.circle(img, (180, 30, 30), (cx, cy), self.yari_cap)
            pygame.draw.circle(img, (255, 80, 80), (cx, cy), self.yari_cap - 4)
            font = pygame.font.SysFont("Consolas", 12, bold=True)
            t = font.render("+", True, (255, 255, 255))
            img.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))
        else:
            pygame.draw.circle(img, (180, 140, 30), (cx, cy), self.yari_cap)
            pygame.draw.circle(img, (255, 200, 50), (cx, cy), self.yari_cap - 4)
            font = pygame.font.SysFont("Consolas", 9, bold=True)
            t = font.render("AM", True, (0, 0, 0))
            img.blit(t, (cx - t.get_width() // 2, cy - t.get_height() // 2))
        return img

    def update(self, dt):
        self.omur -= dt
        self.titreme += dt * 4
        # Hafif yukarı-aşağı salınım
        offset_y = int(math.sin(self.titreme) * 3)
        self.rect.center = (int(self.x), int(self.y) + offset_y)
        if self.omur <= 0:
            self.kill()

    def oyuncuya_dokunan(self, oyuncu_x, oyuncu_y, oyuncu_r):
        dx = oyuncu_x - self.x
        dy = oyuncu_y - self.y
        return math.hypot(dx, dy) < (self.yari_cap + oyuncu_r)

    @staticmethod
    def rastgele_olustur(x, y):
        """Zombi öldüğünde rastgele drop oluştur. %30 can, %25 mermi, %45 hiç."""
        sayi = random.random()
        if sayi < 0.30:
            return Drop(x, y, "can")
        elif sayi < 0.55:
            return Drop(x, y, "mermi")
        return None
