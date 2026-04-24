# ============================================================
#  varliklar/oyuncu.py — Nişangah Konisi (Aim Cone) ve Şarjör
# ============================================================
import pygame
import math
import random
from ayarlar import (
    OYUNCU_HIZ, OYUNCU_SPRINT_CARPAN, OYUNCU_STAMINA, OYUNCU_STAMINA_HARCAMA,
    OYUNCU_STAMINA_REGEN, OYUNCU_BASLANGIC_CAN, OYUNCU_YARI_CAP,
    OYUNCU_HASAR_GECIKME, OYUNCU_HASAR_FLASH, OYUNCU_BASLANGIC_KALKAN,
    OYUNCU_KALKAN_REGEN, OYUNCU_KALKAN_GECIKME, ULTIMATE_COOLDOWN,
    MAVI, BEYAZ, SILAHLAR, ZIRH_MAVI, SARI
)
from varliklar.mermi import Mermi
from sistemler.ses_sistemi import ses_sis

ZORLUK_CARPANI = 1.0

class Oyuncu(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = float(x)
        self.y = float(y)
        self.yari_cap = OYUNCU_YARI_CAP
        
        self.stamina = float(OYUNCU_STAMINA)
        self.max_stamina = float(OYUNCU_STAMINA)
        self.yoruldu_mu = False
        
        self.can = float(OYUNCU_BASLANGIC_CAN)
        self.max_can = float(OYUNCU_BASLANGIC_CAN)
        
        self.kalkan = float(OYUNCU_BASLANGIC_KALKAN)
        self.max_kalkan = float(OYUNCU_BASLANGIC_KALKAN)
        self.kalkan_yenilenme_sayaci = 0.0
        
        self.aci = 0.0
        self.ates_sayac = 0.0
        self.hasar_sayac = 0.0
        self.hasarli_sayac = 0.0
        self.oldu = False

        self.envanter = ["tabanca"]
        self.aktif_silah = "tabanca"
        self.mermiler = {"tabanca": -1}

        self.yukseltmeler = {
            "can": 0, "stamina": 0, "hiz": 0, "hasar": 0, 
            "kalkan": 0, "zirh": 0, "ult_cd": 0, "combo": 0, "mermi": 0
        }
        self.ult_bekleme = 0.0
        
        self.durbunler = ["red_dot"] # Varsayılan olarak Red Dot olsun
        self.aktif_durbun = "red_dot"
        self.guncel_zoom = 1.0

        self._image_olustur()
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def _image_olustur(self):
        boyut = self.yari_cap * 2 + 10
        self.image = pygame.Surface((boyut, boyut), pygame.SRCALPHA)
        cx = cy = boyut // 2
        pygame.draw.circle(self.image, (0, 0, 0, 80), (cx + 3, cy + 3), self.yari_cap)
        pygame.draw.circle(self.image, MAVI, (cx, cy), self.yari_cap)
        pygame.draw.circle(self.image, (120, 180, 255), (cx, cy), self.yari_cap - 6)
        pygame.draw.rect(self.image, BEYAZ, (cx, cy - 3, self.yari_cap + 12, 6))
        self._base_image = self.image.copy()

    @property
    def gercek_hiz(self): return OYUNCU_HIZ + self.yukseltmeler["hiz"] * 30
    @property
    def hasar_carpani(self): return 1.0 + self.yukseltmeler["hasar"] * 0.30
    @property
    def zirh_carpani(self): return max(0.2, 1.0 - self.yukseltmeler["zirh"] * 0.12) * ZORLUK_CARPANI
    @property
    def max_kalkan_degeri(self): return self.max_kalkan + self.yukseltmeler["kalkan"] * 40
    @property
    def max_stamina_degeri(self): return self.max_stamina + self.yukseltmeler["stamina"] * 30
    @property
    def ult_max_cd(self): return max(5.0, ULTIMATE_COOLDOWN - self.yukseltmeler["ult_cd"] * 2.0)
    @property
    def silah_verisi(self): return SILAHLAR[self.aktif_silah]
    @property
    def hareket_ediyor_mu(self): return getattr(self, "_son_hareket", False)

    def _silah_max_mermi(self, s_key):
        b = SILAHLAR[s_key]["kapasite"]
        if b == -1: return -1
        return int(b * (1.0 + self.yukseltmeler["mermi"] * 0.2))

    def silah_al(self, silah_key):
        if silah_key not in self.envanter:
            self.envanter.append(silah_key)
            self.mermiler[silah_key] = self._silah_max_mermi(silah_key)
        self.aktif_silah = silah_key

    def silah_degistir(self, silah_key):
        if silah_key in self.envanter:
            self.aktif_silah = silah_key

    def mermileri_fulle(self):
        for s in self.envanter:
            if s != "tabanca":
                self.mermiler[s] = self._silah_max_mermi(s)

    def aktif_mermi_doldur(self):
        ak = self.aktif_silah
        if ak != "tabanca":
            max_m = self._silah_max_mermi(ak)
            self.mermiler[ak] = min(max_m, self.mermiler[ak] + max_m // 2)

    def siradaki_silah(self, yon=1):
        if not self.envanter: return
        idx = self.envanter.index(self.aktif_silah) if self.aktif_silah in self.envanter else 0
        self.aktif_silah = self.envanter[(idx + yon) % len(self.envanter)]

    def update(self, dt, tuslar, fare_pos, mermiler, ekran_w, ekran_h, serbest_bakis=False):
        sprint = tuslar.get("sprint", False)
        nisan = tuslar.get("nisan", False)
        
        # Sağ tık (Nişan Alma) mekaniği
        from ayarlar import DURBUNLER
        if nisan:
            hiz_carpani = 0.4
            # Dürbün zoomunu uygula
            d_veri = DURBUNLER.get(self.aktif_durbun, {"zoom": 1.0})
            self.guncel_zoom = d_veri["zoom"]
            self.guncel_yayilma = self.silah_verisi["yayilma"] * (0.1 / self.guncel_zoom)
        elif sprint and self.stamina > 0 and not self.yoruldu_mu:
            self.stamina -= OYUNCU_STAMINA_HARCAMA * dt
            if self.stamina <= 0:
                self.stamina = 0
                self.yoruldu_mu = True
            hiz_carpani = OYUNCU_SPRINT_CARPAN
            self.guncel_yayilma = self.silah_verisi["yayilma"] * 1.5 
            self.guncel_zoom = 1.0
        else:
            hiz_carpani = 1.0
            self.stamina = min(self.max_stamina_degeri, self.stamina + OYUNCU_STAMINA_REGEN * dt)
            if self.stamina > 25:
                self.yoruldu_mu = False
            self.guncel_yayilma = self.silah_verisi["yayilma"]
            self.guncel_zoom = 1.0
        
        # 3D modunda hareket oyuncunun baktığı yöne göre olmalı!
        if serbest_bakis:
            self._hareket_3d(dt, tuslar, ekran_w, ekran_h, hiz_carpani)
        else:
            self._hareket(dt, tuslar, ekran_w, ekran_h, hiz_carpani)
            
        self._don(fare_pos, serbest_bakis)
        
        if self.ates_sayac > 0: self.ates_sayac -= dt
        if self.hasar_sayac > 0: self.hasar_sayac -= dt
        if self.hasarli_sayac > 0: self.hasarli_sayac -= dt
        if self.ult_bekleme > 0: self.ult_bekleme -= dt
        
        if self.kalkan_yenilenme_sayaci > 0:
            self.kalkan_yenilenme_sayaci -= dt
        elif self.kalkan < self.max_kalkan_degeri:
            self.kalkan = min(self.max_kalkan_degeri, self.kalkan + OYUNCU_KALKAN_REGEN * dt)

        if tuslar.get("ates") and self.ates_sayac <= 0:
            mevcut_mermi = self.mermiler.get(self.aktif_silah, -1)
            if mevcut_mermi > 0 or mevcut_mermi == -1:
                self._ates(mermiler)
            else:
                self.siradaki_silah()
            
        if tuslar.get("ult") and self.ult_bekleme <= 0:
            self._ultimate_kullan(mermiler)

    def _hareket(self, dt, tuslar, ekran_w, ekran_h, hiz_carpani):
        dx = dy = 0
        if tuslar.get("yukari"):  dy -= 1
        if tuslar.get("asagi"):   dy += 1
        if tuslar.get("sol"):     dx -= 1
        if tuslar.get("sag"):     dx += 1
        if dx != 0 and dy != 0:
            dx *= 0.7071; dy *= 0.7071
        v = self.gercek_hiz * hiz_carpani
        self.x += dx * v * dt
        self.y += dy * v * dt
        self._son_hareket = (dx != 0 or dy != 0)
        self.x = max(self.yari_cap, min(ekran_w - self.yari_cap, self.x))
        self.y = max(self.yari_cap, min(ekran_h - self.yari_cap, self.y))

    def _hareket_3d(self, dt, tuslar, ekran_w, ekran_h, hiz_carpani):
        # 3D Hareket: Baktığı yöne göre ileri/geri ve sağa/sola strafe
        aci_rad = math.radians(self.aci)
        v = self.gercek_hiz * hiz_carpani
        
        dx = dy = 0
        if tuslar.get("yukari"):
            dx += math.cos(aci_rad)
            dy += math.sin(aci_rad)
        if tuslar.get("asagi"):
            dx -= math.cos(aci_rad)
            dy -= math.sin(aci_rad)
        if tuslar.get("sol"):
            dx += math.sin(aci_rad)
            dy -= math.cos(aci_rad)
        if tuslar.get("sag"):
            dx -= math.sin(aci_rad)
            dy += math.cos(aci_rad)
            
        if dx != 0 or dy != 0:
            # Normalize movement vector
            mag = math.hypot(dx, dy)
            dx /= mag
            dy /= mag
            
        self.x += dx * v * dt
        self.y += dy * v * dt
        self._son_hareket = (dx != 0 or dy != 0)
        self.x = max(self.yari_cap, min(ekran_w - self.yari_cap, self.x))
        self.y = max(self.yari_cap, min(ekran_h - self.yari_cap, self.y))

    def _don(self, fare_pos, serbest_bakis=False):
        if not serbest_bakis:
            dx = fare_pos[0] - self.x
            dy = fare_pos[1] - self.y
            self.aci = math.degrees(math.atan2(dy, dx))
        
        img = self._base_image.copy()
        if self.kalkan > 0:
            alpha = int(100 * (self.kalkan / self.max_kalkan_degeri))
            hale = pygame.Surface((img.get_width(), img.get_height()), pygame.SRCALPHA)
            pygame.draw.circle(hale, (*ZIRH_MAVI, alpha), (img.get_width()//2, img.get_height()//2), self.yari_cap + 4, 4)
            img.blit(hale, (0, 0))
        self.image = pygame.transform.rotate(img, -self.aci)
        self.rect = self.image.get_rect(center=(int(self.x), int(self.y)))

    def ciz_nisangah(self, ekran, fare_pos, ox=0, oy=0):
        # Koni çizimi
        veri = self.silah_verisi
        yayilma = getattr(self, "guncel_yayilma", veri["yayilma"])
        uzunluk = min(1200, veri["mermi_hizi"])
        
        merkez_x = self.x + ox
        merkez_y = self.y + oy
        
        # Eğer yayılma yoksa veya nişan alınıyorsa tek bir ince lazer çizgisi çiz
        if yayilma < 1.0:
            dx = math.cos(math.radians(self.aci)) * uzunluk
            dy = math.sin(math.radians(self.aci)) * uzunluk
            pygame.draw.line(ekran, (*veri["renk"], 150), (merkez_x, merkez_y), (merkez_x + dx, merkez_y + dy), 2)
        else:
            # Yayılma açısına göre yarı saydam bir üçgen/koni oluştur
            # Performans için özel bir Surface
            koni_s = pygame.Surface((uzunluk*2, uzunluk*2), pygame.SRCALPHA)
            cx, cy = uzunluk, uzunluk
            
            aci1 = math.radians(self.aci - yayilma/2)
            aci2 = math.radians(self.aci + yayilma/2)
            
            p1 = (cx, cy)
            p2 = (cx + math.cos(aci1)*uzunluk, cy + math.sin(aci1)*uzunluk)
            p3 = (cx + math.cos(aci2)*uzunluk, cy + math.sin(aci2)*uzunluk)
            
            pygame.draw.polygon(koni_s, (*veri["renk"], 30), [p1, p2, p3])
            
            # Koni kenarları
            pygame.draw.line(koni_s, (*veri["renk"], 80), p1, p2, 1)
            pygame.draw.line(koni_s, (*veri["renk"], 80), p1, p3, 1)
            
            ekran.blit(koni_s, (int(merkez_x - cx), int(merkez_y - cy)))

    def _ates(self, mermiler):
        veri = self.silah_verisi
        adeti = veri["mermi_adeti"]
        yayilma = getattr(self, "guncel_yayilma", veri["yayilma"])
        if self.aktif_silah != "tabanca":
            self.mermiler[self.aktif_silah] -= 1
            
        for i in range(adeti):
            aci_offset = 0.0 if adeti == 1 else random.uniform(-yayilma / 2, yayilma / 2)
            m = Mermi(self.x, self.y, self.aci + aci_offset, veri, self.hasar_carpani)
            mermiler.add(m)
        self.ates_sayac = veri["ates_hizi"]
        
        # Silah sesini tipine göre seç (Profesyonel Mapping)
        ses_anahtar = "ates"
        if "ak47" in self.aktif_silah:    ses_anahtar = "ates_ak"
        elif "smg" in self.aktif_silah or "minigun" in self.aktif_silah: ses_anahtar = "ates_smg"
        elif "shotgun" in self.aktif_silah: ses_anahtar = "ates_pom"
        elif "sniper" in self.aktif_silah:  ses_anahtar = "ates_sni"
        elif "lazer" in self.aktif_silah or "plazma" in self.aktif_silah: ses_anahtar = "ates_laz"
        elif "alev" in self.aktif_silah:   ses_anahtar = "ates_ale"
        elif "bomba" in self.aktif_silah or "roket" in self.aktif_silah: ses_anahtar = "ates_pat"
        
        ses_sis.oynat(ses_anahtar)

    def _ultimate_kullan(self, mermiler):
        self.ult_bekleme = self.ult_max_cd
        veri = SILAHLAR["roket_ateş"].copy() if "roket_ateş" in SILAHLAR else SILAHLAR["tabanca"].copy()
        veri["mermi_hizi"] = 700
        veri["tip"] = "delici_patlayan"
        veri["hasar"] = 200
        veri["renk"] = SARI
        veri["patlama_r"] = 120
        veri["efekt"] = "yanma"
        for i in range(16):
            aci = i * 22.5
            m = Mermi(self.x, self.y, aci, veri, self.hasar_carpani * 2.0)
            mermiler.add(m)

    def hasar_al(self, miktar):
        gercek = miktar * self.zirh_carpani
        if self.kalkan > 0:
            if self.kalkan >= gercek:
                self.kalkan -= gercek
                gercek = 0
            else:
                gercek -= self.kalkan
                self.kalkan = 0
        if gercek > 0:
            self.can -= gercek
            ses_sis.oynat("hasar")
            
        self.hasarli_sayac = OYUNCU_HASAR_FLASH
        self.kalkan_yenilenme_sayaci = OYUNCU_KALKAN_GECIKME
        if self.can <= 0:
            self.can = 0
            self.oldu = True

    def zombi_temas(self, dt, miktar):
        if self.hasar_sayac <= 0:
            self.hasar_al(miktar)
            self.hasar_sayac = 0.15

    def can_doldur(self, miktar=40):
        self.can = min(self.max_can + self.yukseltmeler["can"]*40, self.can + miktar)

    def kalkan_doldur(self, miktar=50):
        self.kalkan = min(self.max_kalkan_degeri, self.kalkan + miktar)

    def flash_ciz(self, ekran):
        if self.hasarli_sayac > 0:
            alpha = int(180 * (self.hasarli_sayac / OYUNCU_HASAR_FLASH))
            flash = pygame.Surface(ekran.get_size(), pygame.SRCALPHA)
            flash.fill((255, 0, 0, alpha) if self.kalkan <= 0 else (100, 150, 255, alpha))
            ekran.blit(flash, (0, 0))
            
        oran = self.can / (self.max_can + self.yukseltmeler["can"]*40)
        if oran < 0.35:
            alpha = int(255 * (1.0 - oran/0.35)) * abs(math.sin(pygame.time.get_ticks() / 150))
            vignette = pygame.Surface(ekran.get_size(), pygame.SRCALPHA)
            pygame.draw.rect(vignette, (255, 0, 0, int(alpha*0.4)), vignette.get_rect(), 40)
            ekran.blit(vignette, (0, 0))
