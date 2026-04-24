# ============================================================
#  sistemler/puan_sistemi.py — XP, Seviye, Combo, Para, Skor
# ============================================================
import json
import os
from ayarlar import KAYIT_DOSYASI, XP_BAZA, XP_CARPAN, COMBO_MAX

MAX_KAYIT = 5

class PuanSistemi:
    def __init__(self):
        self.puan = 0       
        self.para = 0       
        self.seviye = 1
        self.xp = 0
        self.xp_hedef = XP_BAZA
        
        self.combo = 0
        self.combo_sayac = 0.0
        
        self.yeni_seviye_flag = False  # Ekranda "Seviye Atladın!" göstermek için
        self.yuksek_skorlar = self._yukle()

    def update(self, dt):
        if self.combo_sayac > 0:
            self.combo_sayac -= dt
            if self.combo_sayac <= 0:
                self.combo = 0

    def zombi_oldu(self, skor, para, baz_xp=15, combo_suresi_ek=0.0):
        # Combo artışı
        self.combo = min(COMBO_MAX, self.combo + 1)
        self.combo_sayac = 3.0 + combo_suresi_ek
        
        # Çarpanlar
        carpan = 1.0 + (self.combo * 0.1)  # Maksimum %100 ekstra
        
        elde_puan = int(skor * carpan)
        elde_para = int(para * carpan)
        elde_xp = int(baz_xp * carpan)
        
        self.puan += elde_puan
        self.para += elde_para
        self._xp_ekle(elde_xp)
        
        return elde_puan, elde_para

    def _xp_ekle(self, miktar):
        self.xp += miktar
        if self.xp >= self.xp_hedef:
            self.seviye += 1
            self.xp -= self.xp_hedef
            self.xp_hedef = int(self.xp_hedef * XP_CARPAN)
            self.yeni_seviye_flag = True

    def harca(self, miktar):
        if self.para >= miktar:
            self.para -= miktar
            return True
        return False

    def sifirla(self):
        self.puan = 0
        self.para = 0
        self.seviye = 1
        self.xp = 0
        self.xp_hedef = XP_BAZA
        self.combo = 0

    def kaydet(self):
        self.yuksek_skorlar.append(self.puan)
        self.yuksek_skorlar.sort(reverse=True)
        self.yuksek_skorlar = self.yuksek_skorlar[:MAX_KAYIT]
        self._kaydet()

    def en_yuksek(self):
        return self.yuksek_skorlar[0] if self.yuksek_skorlar else 0

    def _yukle(self):
        try:
            with open(KAYIT_DOSYASI, "r", encoding="utf-8") as f:
                return json.load(f).get("skorlar", [])
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _kaydet(self):
        os.makedirs(os.path.dirname(KAYIT_DOSYASI), exist_ok=True)
        with open(KAYIT_DOSYASI, "w", encoding="utf-8") as f:
            json.dump({"skorlar": self.yuksek_skorlar}, f, indent=2)
