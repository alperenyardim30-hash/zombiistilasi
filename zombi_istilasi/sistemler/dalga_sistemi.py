# ============================================================
#  sistemler/dalga_sistemi.py — 6 Zombi Tipi + Daha Zor Dalgalar + Dalga Modları
# ============================================================
import random
from varliklar.zombi import Zombi
import ayarlar
from ayarlar import DALGA_MODLARI


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
        self.aktif_mod = None  # Görev 3: Mevcut dalga modu
        # ZORLUK_CARPANI artik instance degiskeni.
        self.zorluk_carpani = 1.0

    def _dalga_olustur(self, dalga_no):
        liste = []
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
            
        # BOSS KORUMALARI modu — mini bosslar ekle
        if self.aktif_mod and self.aktif_mod.get("efekt") == "mini_boss":
            liste += ["boss"] * 2
            
        random.shuffle(liste)
        return liste

    def _mod_uygula(self, zombi):
        """Aktif mod efektini yeni spawn olan zombiye uygular."""
        if not self.aktif_mod:
            return
        efekt = self.aktif_mod.get("efekt")
        if efekt == "hiz":
            zombi.baz_hiz *= 1.5
            zombi.hiz = zombi.baz_hiz
        elif efekt == "zirh":
            zombi.can *= 1.75
            zombi.max_can *= 1.75
        elif efekt == "para":
            zombi.para *= 2

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
                yeni_z = Zombi.rastgele_dogur(ekran_w, ekran_h, tip, zorluk_carpani=self.zorluk_carpani)
                self._mod_uygula(yeni_z)
                self.zombiler.add(yeni_z)
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
        self.zorluk_carpani = 1.0 + (self.dalga_no * 0.1)
        
        # Boss dalgasında mod yok
        if self.dalga_no % 5 == 0:
            self.aktif_mod = None
            self.bildirim_metni = f"DALGA {self.dalga_no} — BOSS DALGASI! 💀"
        else:
            self.aktif_mod = random.choice(DALGA_MODLARI)
            mod_isim = self.aktif_mod["isim"]
            mod_acik = self.aktif_mod["aciklama"]
            self.bildirim_metni = f"DALGA {self.dalga_no}  ⚡ {mod_isim}" + (f"\n{mod_acik}" if mod_acik else "")
        
        self.dalga_aktif = True
        self.dalga_bitti = False
        self.spawn_listesi = self._dalga_olustur(self.dalga_no)
        self.spawn_sayac = 0.5
        self.spawn_aralik = max(0.15, 0.7 - self.dalga_no * 0.05)
        self.bildirim_sayac = 3.0

    def yeni_dalga_hazirla(self):
        self.dalga_bitti = False
        self.dalga_aktif = False

    def bildirim_goster(self):
        if self.bildirim_sayac > 0:
            return self.bildirim_metni, self.bildirim_sayac
        return None, 0

