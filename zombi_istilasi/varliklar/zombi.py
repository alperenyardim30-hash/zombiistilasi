# ============================================================
#  varliklar/zombi.py — Element Efektleri (Yanma, Donma, Şok) ve Gölgeler
# ============================================================
import math
import random
import pygame
import ayarlar
from ayarlar import ZOMBI_TIPLER, SIYAH, ZAFIYET_TABLOSU
from varliklar.drop import Drop

class Zombi(pygame.sprite.Sprite):
    def __init__(self, x, y, tip="normal", zorluk_carpani=1.0):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.tip = tip
        v = ZOMBI_TIPLER[tip]
        self.baz_hiz = float(v["hiz"])
        self.hiz = self.baz_hiz
        self.can = float(v["can"]) * zorluk_carpani
        self.max_can = float(v["can"]) * zorluk_carpani
        self.hasar = v["hasar"] * zorluk_carpani
        self.skor = v["skor"]
        self.para = v["para"]
        self.yari_cap = v["r"]
        self.renk = v["renk"]
        self.ic_renk = v["ic"]
        
        self.hit_sayac = 0.0
        self.vx = self.vy = 0.0
        self.zehir_sayac = 0.0
        
        # Element Durumları
        self.yanma_sayac = 0.0
        self.donma_sayac = 0.0
        self.zehir_hasar_sayac = 0.0
        self.sok_sayac = 0.0
        
        # Boss giriş animasyonu
        self.spawn_sayac = 0.8 if tip == "boss" else 0.0  # saniye
        self.spawn_max   = 0.8

        self._image_olustur()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _image_olustur(self):
        r = self.yari_cap
        boyut = r * 2 + 10
        img = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        cx = cy = boyut // 2
        
        # Zombi Gölgesi
        pygame.draw.circle(img, (0, 0, 0, 80), (cx + 4, cy + 4), r)
        
        # Gövde
        pygame.draw.circle(img, self.renk, (cx, cy), r)
        pygame.draw.circle(img, self.ic_renk, (cx, cy), max(1, r - 6))
        
        # Yüz
        off = max(3, r // 3)
        pygame.draw.line(img, SIYAH, (cx-off, cy-off), (cx+off, cy+off), 2)
        pygame.draw.line(img, SIYAH, (cx+off, cy-off), (cx-off, cy+off), 2)
        
        if self.tip == "boss":
            pygame.draw.polygon(img, (255, 215, 0), [(cx, cy-r-5), (cx-7, cy-r+5), (cx+7, cy-r+5)])
        elif self.tip == "patlayan":
            for i in range(4):
                a = i * 90
                ar = math.radians(a)
                pygame.draw.line(img, (255, 200, 0),
                    (cx + int(math.cos(ar)*r*0.6), cy + int(math.sin(ar)*r*0.6)),
                    (cx + int(math.cos(ar+0.3)*r), cy + int(math.sin(ar+0.3)*r)), 2)
        elif self.tip == "zehirli":
            pygame.draw.circle(img, (0, 255, 100, 80), (cx, cy), r + 3)
            
        self._base_image = img.copy()
        
        hit = img.copy()
        hl = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        pygame.draw.circle(hl, (255, 60, 60, 150), (cx, cy), r)
        hit.blit(hl, (0, 0))
        self._hit_image = hit
        
        # PERFORMANS: Donma/yanma overlay'lerini bir kez olustur (her frame SRCALPHA olusturmaya son)
        donma_overlay = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        pygame.draw.circle(donma_overlay, (0, 200, 255, 100), (cx, cy), r)
        self._donma_image = self._base_image.copy()
        self._donma_image.blit(donma_overlay, (0, 0))
        
        yanma_overlay = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        pygame.draw.circle(yanma_overlay, (255, 100, 0, 100), (cx, cy), r)
        self._yanma_image = self._base_image.copy()
        self._yanma_image.blit(yanma_overlay, (0, 0))
        
        self.image = self._base_image

    def durum_guncelle(self, dt):
        """Element efektlerini işler."""
        if self.yanma_sayac > 0:
            self.yanma_sayac -= dt
            self.can -= 15 * dt  # Saniyede 15 yanma hasarı
            
        if self.zehir_hasar_sayac > 0:
            self.zehir_hasar_sayac -= dt
            self.can -= 25 * dt  # Saniyede 25 zehir hasarı
            
        if self.sok_sayac > 0:
            self.sok_sayac -= dt
            self.hiz = 0.0
        elif self.donma_sayac > 0:
            self.donma_sayac -= dt
            self.hiz = self.baz_hiz * 0.4
        elif self.zehir_hasar_sayac > 0:
            # Zehirli zombi yavaşlar ama hareket eder
            self.hiz = self.baz_hiz * 0.8
        else:
            self.hiz = self.baz_hiz
        
        # Element hasarından öldüyse işaretle (oyun_ekrani update'de yakalanır)
        if self.can <= 0 and self.alive():
            self._olum_efektten = True

    def update(self, dt, ox, oy):
        self.durum_guncelle(dt)
        
        # Boss giriş animasyonu — hareket etme, sadece büyü
        if self.spawn_sayac > 0:
            self.spawn_sayac -= dt
            ilerleme = 1.0 - (self.spawn_sayac / self.spawn_max)  # 0.0 → 1.0
            r_guncel = max(4, int(self.yari_cap * ilerleme))
            boyut = r_guncel * 2 + 10
            scaled = pygame.transform.scale(self._base_image, (boyut, boyut))
            self.image = scaled
            self.rect = scaled.get_rect(center=(int(self.x), int(self.y)))
            return  # Henüz hareket etme
        
        if self.hiz > 0:
            if self.tip == "kosucu":
                self._zigzag_sayac = getattr(self, '_zigzag_sayac', 0) + dt
                sapma = math.sin(self._zigzag_sayac * 8) * 80
                aci = math.atan2(oy - self.y, ox - self.x)
                self.x += math.cos(aci + sapma * 0.02) * self.hiz * dt
                self.y += math.sin(aci + sapma * 0.02) * self.hiz * dt
            else:
                dx = ox - self.x
                dy = oy - self.y
                uzak = math.hypot(dx, dy)
                if uzak > 0:
                    self.vx = (dx / uzak) * self.hiz
                    self.vy = (dy / uzak) * self.hiz
                self.x += self.vx * dt
                self.y += self.vy * dt
            
        self.rect.center = (int(self.x), int(self.y))
        
        if self.hit_sayac > 0:
            self.hit_sayac -= dt
            self.image = self._hit_image
        else:
            self.image = self._base_image
            
        # Görsel Efekt Katmanları — CACHED overlay kullan (her frame Surface olusturmaya son)
        if self.donma_sayac > 0:
            self.image = self._donma_image
        elif self.yanma_sayac > 0:
            self.image = self._yanma_image
        elif self.sok_sayac > 0:
            # Şok için sarsıntı efekti
            self.rect.x += random.randint(-2, 2)
            self.rect.y += random.randint(-2, 2)

        if self.tip == "zehirli":
            self.zehir_sayac += dt

    def mermi_carpisma(self, mermi):
        """Merminin isabet edip etmediğini kontrol eder. 
        Döndürür: (oldu, zafiyet_mesaji, gercek_hasar)
          gercek_hasar == 0  →  isabet YOK
        """
        mc, mr = mermi.get_circle()
        dist = math.hypot(mc[0] - self.x, mc[1] - self.y)
        # İsabet kontrolü — çarpışma olmadıysa (0, None, 0) döndür
        if dist >= (self.yari_cap + mr):
            return False, None, 0
        
        # Zafiyet çarpanı hesapla
        zafiyet = ZAFIYET_TABLOSU.get(self.tip, {})
        carpan = zafiyet.get(mermi.efekt, 1.0) if mermi.efekt != "yok" else 1.0
        
        gercek_hasar = mermi.hasar * carpan
        self.can -= gercek_hasar
        self.hit_sayac = 0.10
        
        # Zafiyet mesajı
        zafiyet_msg = None
        if carpan >= 1.5:
            zafiyet_msg = "ZAYIF NOKTA!"
        elif carpan <= 0.5:
            zafiyet_msg = "DİRENÇLİ"
        
        # Efekt Uygulama
        self._son_isabetefekti = mermi.efekt
        if mermi.efekt == "yanma":  self.yanma_sayac = 3.0
        elif mermi.efekt == "donma":  self.donma_sayac = 2.0
        elif mermi.efekt == "zehir":  self.zehir_hasar_sayac = 4.0
        elif mermi.efekt == "sok":    self.sok_sayac = 1.0
        
        # Mermiyi sonlandır (delici tipler hayatta kalır)
        if mermi.tip != "delici":
            if mermi.tip in ("roket", "delici_patlayan", "seken_bomba"):
                mermi.patlama_hazir = True
            mermi.kill()
        
        return self.can <= 0, zafiyet_msg, int(gercek_hasar)

    def oyuncuya_yakin_mi(self, ox, oy):
        return math.hypot(ox-self.x, oy-self.y) < (self.yari_cap + 18)

    def patlama_hasar_mesafe(self, ox, oy):
        return math.hypot(ox-self.x, oy-self.y)

    def drop_olustur(self):
        return Drop.rastgele_olustur(self.x, self.y)

    def can_bar_ciz(self, ekran):
        if self.can >= self.max_can: return
        bar_gen = 50 if self.tip != "boss" else 90
        bar_yuk = 6
        dolu = int(bar_gen * max(0, self.can) / self.max_can)
        cx, cy = int(self.x), int(self.y)
        pygame.draw.rect(ekran, (0, 0, 0), (cx-bar_gen//2 - 1, cy-self.yari_cap-12, bar_gen + 2, bar_yuk + 2), border_radius=3)
        pygame.draw.rect(ekran, (80, 0, 0), (cx-bar_gen//2, cy-self.yari_cap-11, bar_gen, bar_yuk), border_radius=2)
        if dolu > 0:
            renk = (210, 50, 50)
            if self.donma_sayac > 0: renk = (50, 150, 255)
            elif self.zehir_hasar_sayac > 0: renk = (150, 255, 50)
            pygame.draw.rect(ekran, renk, (cx-bar_gen//2, cy-self.yari_cap-11, dolu, bar_yuk), border_radius=2)

    @staticmethod
    def rastgele_dogur(ekran_w, ekran_h, tip="normal", zorluk_carpani=1.0):
        kenar = random.randint(0, 3)
        off = 90
        if kenar == 0:   x, y = random.randint(0, ekran_w), -off
        elif kenar == 1: x, y = ekran_w+off, random.randint(0, ekran_h)
        elif kenar == 2: x, y = random.randint(0, ekran_w), ekran_h+off
        else:            x, y = -off, random.randint(0, ekran_h)
        return Zombi(x, y, tip, zorluk_carpani=zorluk_carpani)
