# ============================================================
#  sistemler/basarim_sistemi.py — Başarım (Achievement) Sistemi
# ============================================================

BASARIMLAR = [
    {"id": "ilk_kan",       "isim": "İlk Kan",          "kosul": lambda d: d.get("zombi_oldu_sayisi", 0) >= 1,    "skor_bonusu": 100},
    {"id": "zombi_avcisi",  "isim": "Zombi Avcısı",     "kosul": lambda d: d.get("zombi_oldu_sayisi", 0) >= 50,   "skor_bonusu": 500},
    {"id": "katliam",       "isim": "Katliam!",          "kosul": lambda d: d.get("zombi_oldu_sayisi", 0) >= 200,  "skor_bonusu": 1500},
    {"id": "combo_5",       "isim": "Combo x5",          "kosul": lambda d: d.get("combo_max", 0) >= 5,           "skor_bonusu": 200},
    {"id": "combo_10",      "isim": "Combo x10",         "kosul": lambda d: d.get("combo_max", 0) >= 10,          "skor_bonusu": 600},
    {"id": "combo_15",      "isim": "Combo x15",         "kosul": lambda d: d.get("combo_max", 0) >= 15,          "skor_bonusu": 1200},
    {"id": "boss_olen",     "isim": "Boss Avcısı",       "kosul": lambda d: d.get("boss_olduruldu", False),        "skor_bonusu": 800},
    {"id": "dalga_5",       "isim": "5. Dalga",          "kosul": lambda d: d.get("dalga_no", 0) >= 5,            "skor_bonusu": 300},
    {"id": "dalga_10",      "isim": "10. Dalga",         "kosul": lambda d: d.get("dalga_no", 0) >= 10,           "skor_bonusu": 1000},
    {"id": "dalga_20",      "isim": "Hayatta Kalan",     "kosul": lambda d: d.get("dalga_no", 0) >= 20,           "skor_bonusu": 3000},
    {"id": "zengin",        "isim": "Zengin!",           "kosul": lambda d: d.get("para", 0) >= 10000,            "skor_bonusu": 400},
    {"id": "cephanelik",    "isim": "Cephanelik",        "kosul": lambda d: d.get("silah_sayisi", 0) >= 10,       "skor_bonusu": 500},
]


class BasarimSistemi:
    def __init__(self):
        self.kazanilan = set()      # Kazanılan başarım id'leri
        self._yeni_kuyruk = []      # Bu frame'de yeni kazanılanlar

    def kontrol_et(self, veri: dict):
        """Her frame çağrılır. veri dict'i oyun durumunu içerir.
        Yeni kazanılan başarımlar varsa True döner.
        """
        yeni_var = False
        for b in BASARIMLAR:
            if b["id"] in self.kazanilan:
                continue
            try:
                if b["kosul"](veri):
                    self.kazanilan.add(b["id"])
                    self._yeni_kuyruk.append(b)
                    yeni_var = True
            except Exception:
                pass
        return yeni_var

    def yeni_al(self):
        """Yeni kazanılan başarımları döndürür ve kuyruğu temizler."""
        sonuc = list(self._yeni_kuyruk)
        self._yeni_kuyruk.clear()
        return sonuc

    def toplam_bonus(self):
        return sum(b["skor_bonusu"] for b in BASARIMLAR if b["id"] in self.kazanilan)
