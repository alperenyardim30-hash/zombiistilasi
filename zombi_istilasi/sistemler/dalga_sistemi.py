# ============================================================
#  sistemler/dalga_sistemi.py — 6 Zombi Tipi + Daha Zor Dalgalar
# ============================================================
import random
from ayarlar import DALGA_ARASI_SURE
from varliklar.zombi import Zombi


class DalgaSistemi:
    def __init__(self, zombiler_grubu):
        self.zombiler = zombiler_grubu
        self.dalga_no = 0
        self.spawn_listesi = []
        self.spawn_sayac = 0.0
        self.spawn_aralik = 0.8
        self.dalga_aktif = False
        self.dalga_bitti = False
        self.bildirim_sayac = 0.0
        self.bildirim_metni = ""

    def _dalga_olustur(self, dalga_no):
        liste = []
        # Baz sayılar
        normal = 4 + dalga_no * 2
        hizli = max(0, dalga_no * 2 - 2)
        kosucu = max(0, dalga_no - 3) * 2
        patlayan = max(0, dalga_no - 4)
        zehirli = max(0, dalga_no - 6)
        
        liste += ["normal"] * normal
        liste += ["hizli"] * hizli
        liste += ["kosucu"] * kosucu
        liste += ["patlayan"] * patlayan
        liste += ["zehirli"] * zehirli
        
        # Her 5 dalgada boss (+ yanında korumalar)
        if dalga_no % 5 == 0:
            boss_sayisi = dalga_no // 5
            liste += ["boss"] * boss_sayisi
            liste += ["patlayan"] * boss_sayisi * 2
            
        random.shuffle(liste)
        return liste

    def guncelle(self, dt, ekran_w, ekran_h):
        if self.dalga_bitti:
            return

        if not self.dalga_aktif:
            self._yeni_dalga_baslat(ekran_w, ekran_h)
            return

        if self.spawn_listesi:
            self.spawn_sayac -= dt
            if self.spawn_sayac <= 0:
                tip = self.spawn_listesi.pop(0)
                self.zombiler.add(Zombi.rastgele_dogur(ekran_w, ekran_h, tip))
                self.spawn_sayac = self.spawn_aralik
        elif len(self.zombiler) == 0:
            self.dalga_aktif = False
            self.dalga_bitti = True
            self.bildirim_metni = "✓ Dalga Temizlendi!"
            self.bildirim_sayac = 2.0

        if self.bildirim_sayac > 0:
            self.bildirim_sayac -= dt

    def _yeni_dalga_baslat(self, ekran_w, ekran_h):
        self.dalga_no += 1
        self.dalga_aktif = True
        self.dalga_bitti = False
        self.spawn_listesi = self._dalga_olustur(self.dalga_no)
        self.spawn_sayac = 0.5
        # Spawn aralığını düşür (daha hızlı gelsinler)
        self.spawn_aralik = max(0.15, 0.7 - self.dalga_no * 0.05)
        
        if self.dalga_no % 5 == 0:
            self.bildirim_metni = f"DALGA {self.dalga_no} — BOSS DALGASI! 💀"
        else:
            self.bildirim_metni = f"DALGA {self.dalga_no}"
        self.bildirim_sayac = 2.5

    def yeni_dalga_hazirla(self):
        self.dalga_bitti = False
        self.dalga_aktif = False

    def bildirim_goster(self):
        if self.bildirim_sayac > 0:
            return self.bildirim_metni, self.bildirim_sayac
        return None, 0
