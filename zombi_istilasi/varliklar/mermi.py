# ============================================================
#  varliklar/mermi.py — Element Efektleri ve Parlama (Glow)
# ============================================================
import pygame
import math
from varliklar.parcacik import Parcacik

class Mermi(pygame.sprite.Sprite):
    def __init__(self, x, y, aci, veri, hasar_carpani=1.0):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.vx = math.cos(math.radians(aci)) * veri["mermi_hizi"]
        self.vy = math.sin(math.radians(aci)) * veri["mermi_hizi"]
        self.tip = veri["tip"]
        self.efekt = veri.get("efekt", "yok")
        self.hasar = veri["hasar"] * hasar_carpani
        self.renk = veri["renk"]
        self.patlama_r = veri.get("patlama_r", 0)
        self.patlama_hazir = False
        self.omur = 2.0
        
        self._image_olustur()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
        self.vurulan_zombiler = set()

    def _image_olustur(self):
        # Alev
        if self.tip == "alev":
            self.omur = 0.5
            self.yari_cap = 10
            self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 60, 0, 100), (15, 15), 15)
            pygame.draw.circle(self.image, (255, 150, 0, 180), (15, 15), 8)
        # Seken Bomba
        elif self.tip == "seken_bomba":
            self.omur = 1.2
            self.yari_cap = 6
            self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(self.image, self.renk, (8, 8), 6)
            pygame.draw.circle(self.image, (0,0,0), (8, 8), 3)
            # Glow
            pygame.draw.circle(self.image, (*self.renk, 50), (8, 8), 8)
        # Roket
        elif self.tip in ("roket", "delici_patlayan"):
            self.yari_cap = 8
            self.image = pygame.Surface((24, 24), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (*self.renk, 80), (12, 12), 12)
            pygame.draw.circle(self.image, self.renk, (12, 12), 8)
        # Standart & Lazer
        else:
            self.yari_cap = 4
            self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
            # Dış Parlama (Glow)
            pygame.draw.circle(self.image, (*self.renk, 60), (8, 8), 8)
            pygame.draw.circle(self.image, (*self.renk, 120), (8, 8), 6)
            # Merkez
            pygame.draw.circle(self.image, (255, 255, 255), (8, 8), 3)

    def update(self, dt, ekran_w, ekran_h):
        self.omur -= dt
        
        if self.tip == "alev":
            self.vx *= 0.88
            self.vy *= 0.88
            self.yari_cap += dt * 45
            
        self.x += self.vx * dt
        self.y += self.vy * dt
        
        if self.tip == "seken_bomba":
            if self.x <= 0 or self.x >= ekran_w:
                self.vx *= -0.8
                self.x = max(0, min(ekran_w, self.x))
            if self.y <= 0 or self.y >= ekran_h:
                self.vy *= -0.8
                self.y = max(0, min(ekran_h, self.y))
                
            if self.omur <= 0:
                self.patlama_hazir = True
                self.kill()
        else:
            if self.x < -100 or self.x > ekran_w + 100 or self.y < -100 or self.y > ekran_h + 100 or self.omur <= 0:
                if self.tip in ("roket", "delici_patlayan"):
                    self.patlama_hazir = True
                self.kill()
                
        self.rect.center = (int(self.x), int(self.y))

    def get_circle(self):
        return (self.x, self.y), self.yari_cap
