# ============================================================
#  varliklar/mermi.py — 12 Gorsel Tip (Normal/Serit/Pellet/Plazma/Void/Roket...)
# ============================================================
import pygame
import math
import random
from varliklar.parcacik import Parcacik


class Mermi(pygame.sprite.Sprite):
    def __init__(self, x, y, aci, veri, hasar_carpani=1.0):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.aci = float(aci)
        self.vx = math.cos(math.radians(aci)) * veri["mermi_hizi"]
        self.vy = math.sin(math.radians(aci)) * veri["mermi_hizi"]
        self.tip = veri["tip"]
        self.gorsel_tip = veri.get("gorsel_tip", "normal")
        self.efekt = veri.get("efekt", "yok")
        self.hasar = veri["hasar"] * hasar_carpani
        self.renk = veri["renk"]
        self.patlama_r = veri.get("patlama_r", 0)
        self.patlama_hazir = False
        self.omur = 2.0
        self.vurulan_zombiler = set()

        # Roket/delici_serit icin iz parcaciklari
        self._iz_sayac = 0.0
        self._iz_araligi = 0.03  # saniye

        self._image_olustur()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    # ----------------------------------------------------------
    def _image_olustur(self):
        gt = self.gorsel_tip
        r, g, b = self.renk[:3]

        if gt == "normal":
            self.yari_cap = 4
            self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (r, g, b, 60), (8, 8), 8)
            pygame.draw.circle(self.image, (r, g, b, 140), (8, 8), 5)
            pygame.draw.circle(self.image, (255, 255, 255), (8, 8), 3)
            self._base_image = self.image.copy()

        elif gt == "pellet":
            self.yari_cap = 3
            self.image = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.rect(self.image, (r, g, b), (1, 1, 6, 6))
            pygame.draw.rect(self.image, (255, 255, 255, 120), (2, 2, 3, 3))
            self._base_image = self.image.copy()

        elif gt == "delici_serit":
            # Uzun ince serit — aci'ya gore dondurulacak
            self.yari_cap = 3
            uzunluk = 28
            genislik = 4
            base = pygame.Surface((uzunluk, genislik + 4), pygame.SRCALPHA)
            pygame.draw.rect(base, (r, g, b, 200), (0, 2, uzunluk, genislik))
            pygame.draw.rect(base, (255, 255, 255, 180), (uzunluk - 8, 2, 8, genislik))
            self._base_image = base
            self.image = pygame.transform.rotate(base, -self.aci)
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            return

        elif gt == "alev_koni":
            self.omur = 0.5
            self.yari_cap = 10
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 30, 0, 50), (16, 16), 16)
            pygame.draw.circle(self.image, (255, 100, 0, 130), (16, 16), 11)
            pygame.draw.circle(self.image, (255, 220, 0, 200), (16, 16), 5)
            # Buyurken buyuyor
            self._base_image = self.image.copy()

        elif gt == "roket_fuze":
            # Fuzeli roket — dondurulacak
            self.yari_cap = 7
            uzunluk = 24
            base = pygame.Surface((uzunluk + 6, 14), pygame.SRCALPHA)
            # Govde
            pygame.draw.ellipse(base, (r, g, b), (2, 3, uzunluk, 8))
            # Parlak burun
            pygame.draw.circle(base, (255, 255, 255, 200), (uzunluk + 2, 7), 3)
            # Kuyruk alevi
            pygame.draw.circle(base, (255, 150, 0, 180), (2, 7), 5)
            self._base_image = base
            self.image = pygame.transform.rotate(base, -self.aci)
            self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))
            return

        elif gt == "plazma_top":
            self.yari_cap = 14
            self.image = pygame.Surface((48, 48), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (r, g, b, 35), (24, 24), 24)
            pygame.draw.circle(self.image, (r, g, b, 110), (24, 24), 16)
            pygame.draw.circle(self.image, (r, g, b, 200), (24, 24), 22, 2)  # Halka
            pygame.draw.circle(self.image, (255, 255, 255, 220), (24, 24), 6)
            self._base_image = self.image.copy()

        elif gt == "void_dalgasi":
            self.yari_cap = 16
            self.image = pygame.Surface((56, 56), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (20, 0, 40, 230), (28, 28), 14)
            pygame.draw.circle(self.image, (100, 0, 200, 160), (28, 28), 22, 4)
            pygame.draw.circle(self.image, (180, 0, 255, 70), (28, 28), 28)
            self._base_image = self.image.copy()

        elif gt == "efsane_isin":
            self.yari_cap = 18
            self.image = pygame.Surface((60, 60), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 0, 255, 50), (30, 30), 30)
            pygame.draw.circle(self.image, (200, 0, 255, 130), (30, 30), 20)
            pygame.draw.circle(self.image, (255, 100, 255, 210), (30, 30), 10)
            pygame.draw.circle(self.image, (255, 255, 255, 240), (30, 30), 4)
            self._base_image = self.image.copy()

        elif gt == "elektrik_ark":
            self.yari_cap = 10
            self.image = pygame.Surface((32, 32), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (100, 150, 255, 70), (16, 16), 16)
            pygame.draw.circle(self.image, (200, 220, 255, 180), (16, 16), 10)
            pygame.draw.circle(self.image, (255, 255, 255, 240), (16, 16), 5)
            self._base_image = self.image.copy()

        elif gt == "iyon_top":
            self.yari_cap = 12
            self.image = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (r, g, b, 55), (20, 20), 20)
            pygame.draw.circle(self.image, (r, g, b, 140), (20, 20), 13)
            # Halka efekti
            pygame.draw.circle(self.image, (r, g, b, 200), (20, 20), 17, 2)
            pygame.draw.circle(self.image, (255, 255, 255, 220), (20, 20), 5)
            self._base_image = self.image.copy()

        elif gt == "the_end_isin":
            self.yari_cap = 22
            self.image = pygame.Surface((68, 68), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (255, 255, 255, 40), (34, 34), 34)
            pygame.draw.circle(self.image, (255, 255, 255, 140), (34, 34), 22)
            pygame.draw.circle(self.image, (255, 240, 200, 230), (34, 34), 10)
            pygame.draw.circle(self.image, (255, 255, 255, 255), (34, 34), 4)
            self._base_image = self.image.copy()

        else:
            # Fallback — normal
            self.yari_cap = 4
            self.image = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (r, g, b, 120), (8, 8), 6)
            pygame.draw.circle(self.image, (255, 255, 255), (8, 8), 3)
            self._base_image = self.image.copy()

    # ----------------------------------------------------------
    def update(self, dt, ekran_w, ekran_h):
        self.omur -= dt
        gt = self.gorsel_tip

        if gt == "alev_koni":
            self.vx *= 0.88
            self.vy *= 0.88
            self.yari_cap += dt * 45

        self.x += self.vx * dt
        self.y += self.vy * dt

        # Dondurme gerektiren tipler
        if gt in ("delici_serit", "roket_fuze"):
            donmus = pygame.transform.rotate(self._base_image, -self.aci)
            self.image = donmus
            self.rect = donmus.get_rect(center=(int(self.x), int(self.y)))
        else:
            self.rect.center = (int(self.x), int(self.y))

        # Plazma / void / iyon titreme efekti
        if gt in ("plazma_top", "void_dalgasi", "iyon_top", "efsane_isin"):
            jitter = random.randint(-1, 1)
            self.rect.x += jitter
            self.rect.y += jitter

        # Seken bomba sekme
        if gt == "seken_bomba" or self.tip == "seken_bomba":
            if self.x <= 0 or self.x >= ekran_w:
                self.vx *= -0.8
                self.x = max(0, min(ekran_w, self.x))
            if self.y <= 0 or self.y >= ekran_h:
                self.vy *= -0.8
                self.y = max(0, min(ekran_h, self.y))
            if self.omur <= 0:
                self.patlama_hazir = True
                self.kill()
            return

        # Sinir kontrolu
        if (self.x < -100 or self.x > ekran_w + 100 or
                self.y < -100 or self.y > ekran_h + 100 or
                self.omur <= 0):
            if self.tip in ("roket", "delici_patlayan"):
                self.patlama_hazir = True
            self.kill()

    # ----------------------------------------------------------
    def get_circle(self):
        return (self.x, self.y), self.yari_cap
