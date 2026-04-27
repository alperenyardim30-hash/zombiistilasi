# ============================================================
#  ayarlar.py — 60 Silah (Elementler) & Devasa Güncelleme
# ============================================================
import ctypes
import os


def _ekran_boyutu_al():
    """
    Mümkünse sistemin gerçek ekran çözünürlüğünü alır.
    Windows dışı ortamlarda güvenli varsayılan değere düşer.
    """
    try:
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        return user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
    except Exception:
        return 1920, 1080


GENISLIK, YUKSEKLIK = _ekran_boyutu_al()

FPS = 60  # 2D top-down oyun icin 60 FPS yeterli, CPU kullanimi 1/3'e duser
BASLIK = "🧟 Zombi İstilası — 100+ Dev Güncelleme!"

# Renkler
SIYAH      = (0, 0, 0)
BEYAZ      = (255, 255, 255)
KIRMIZI    = (220, 50, 47)
YESIL      = (80, 220, 100)
MAVI       = (70, 130, 200)
SARI       = (255, 220, 0)
TURUNCU    = (255, 140, 0)
GRI        = (60, 60, 60)
KOYU_GRI   = (25, 25, 35)
ACIK_GRI   = (120, 120, 120)
ALTIN      = (255, 200, 0)
MOR        = (160, 60, 220)
CAMGOBEGI  = (80, 200, 255)
PEMBE      = (255, 100, 180)
ZIRH_MAVI  = (60, 140, 255)
ARKAPLAN   = (14, 18, 22)
ZOMBI_YESIL= (90, 160, 70)

# Zorluk — NOT: Bu global artik dogrudan yazilmamali.
# DalgaSistemi instance uzerinden yonetilecek.
ZORLUK_CARPANI = 1.0

# Zombi Element Zafiyetleri (carpan >= 1.5 = ZAYIF NOKTA, <= 0.5 = DIRENCLI)
ZAFIYET_TABLOSU = {
    "normal":   {"yanma": 1.0, "donma": 1.0, "zehir": 1.0, "sok": 1.0},
    "hizli":    {"yanma": 0.5, "donma": 2.0, "zehir": 1.0, "sok": 1.5},
    "kosucu":   {"yanma": 1.0, "donma": 2.5, "zehir": 0.5, "sok": 1.0},
    "patlayan": {"yanma": 0.2, "donma": 1.5, "zehir": 1.0, "sok": 2.0},
    "zehirli":  {"yanma": 1.5, "donma": 1.0, "zehir": 0.1, "sok": 1.0},
    "boss":     {"yanma": 0.3, "donma": 2.0, "zehir": 1.2, "sok": 0.5},
}

# Dalga Modifikatörleri
DALGA_MODLARI = [
    {"isim": "HIZLI SÜRÜ",     "aciklama": "Tüm zombiler %50 daha hızlı!",      "renk": (255, 100, 0),  "efekt": "hiz"},
    {"isim": "ZİRHLI ORDU",   "aciklama": "Zombilerin canı %75 fazla!",        "renk": (100, 100, 255),"efekt": "zirh"},
    {"isim": "KARANLIK DALGA","aciklama": "Görüş alanı kısıtlı!",            "renk": (50, 50, 50),   "efekt": "karanlik"},
    {"isim": "BEREKET DALGASI","aciklama": "Zombiler 2x para bırakıyor!",      "renk": (255, 215, 0),  "efekt": "para"},
    {"isim": "BOSS KORUMALARI","aciklama": "Mini bosslar ile geliyor!",         "renk": (160, 0, 255),  "efekt": "mini_boss"},
    {"isim": "NORMAL DALGA",   "aciklama": "",                                  "renk": (180, 255, 180), "efekt": None},
]

# Oyuncu & Sistemler
OYUNCU_HIZ            = 210
OYUNCU_SPRINT_CARPAN  = 1.6
OYUNCU_STAMINA        = 100.0
OYUNCU_STAMINA_HARCAMA= 35.0
OYUNCU_STAMINA_REGEN  = 20.0
OYUNCU_BASLANGIC_CAN  = 150
OYUNCU_YARI_CAP       = 18
OYUNCU_HASAR_GECIKME  = 0.15
OYUNCU_HASAR_FLASH    = 0.3
OYUNCU_BASLANGIC_KALKAN= 80
OYUNCU_KALKAN_REGEN   = 10.0
OYUNCU_KALKAN_GECIKME = 3.0
ULTIMATE_COOLDOWN     = 18.0

MERMI_YARI_CAP = 5
ZOMBI_YARI_CAP = 18

_ZR = {
    "normal":   {"hiz": 80,  "can": 70,  "hasar": 10, "skor": 50,  "para": 50,  "r": 18, "renk": ZOMBI_YESIL,     "ic": (130, 190, 100)},
    "hizli":    {"hiz": 160, "can": 40,  "hasar": 8,  "skor": 80,  "para": 80,  "r": 16, "renk": (180, 220, 80),  "ic": (220, 255, 120)},
    "kosucu":   {"hiz": 240, "can": 25,  "hasar": 5,  "skor": 120, "para": 100, "r": 14, "renk": (255, 180, 50),  "ic": (255, 220, 120)},
    "patlayan": {"hiz": 70,  "can": 140, "hasar": 35, "skor": 150, "para": 130, "r": 22, "renk": (200, 80,  30),  "ic": (255, 130, 60)},
    "zehirli":  {"hiz": 75,  "can": 110, "hasar": 15, "skor": 140, "para": 120, "r": 20, "renk": (60,  200, 100), "ic": (120, 255, 150)},
    "boss":     {"hiz": 55,  "can": 1200,"hasar": 40, "skor": 800, "para": 600, "r": 38, "renk": (140, 50,  200), "ic": (180, 90,  240)},
}
ZOMBI_TIPLER = _ZR

XP_BAZA = 100
XP_CARPAN = 1.6
COMBO_MAX = 15
DALGA_ARASI_SURE = 3.0

# =======================================================
# 60 ESSIZ SILAH (element yoktur — her biri kendi turu)
# =======================================================
TEMEL_SILAHLAR = {
    # ── STARTER ───────────────────────────────────────────────
    "tabanca":    {"isim": "Tabanca",         "hasar": 35,  "hiz": 0.25, "mermi_hizi": 750,  "yayilma": 2,  "adet": 1, "kapasite": -1,  "tip": "normal",          "renk": (200,200,200)},
    # ── PİSTOL SINIFI ─────────────────────────────────────────
    "cift":       {"isim": "Cift Namlu",      "hasar": 45,  "hiz": 0.20, "mermi_hizi": 800,  "yayilma": 6,  "adet": 2, "kapasite": 140, "tip": "normal",          "renk": (200,180,120)},
    "revolver":   {"isim": "Revolver",        "hasar": 90,  "hiz": 0.50, "mermi_hizi": 850,  "yayilma": 1,  "adet": 1, "kapasite": 36,  "tip": "delici",          "renk": (180,140, 80)},
    "deagle":     {"isim": "Desert Eagle",    "hasar": 130, "hiz": 0.55, "mermi_hizi": 920,  "yayilma": 2,  "adet": 1, "kapasite": 42,  "tip": "delici",          "renk": (220,200, 60)},
    "glock18":    {"isim": "Glock 18 Full",   "hasar": 28,  "hiz": 0.06, "mermi_hizi": 870,  "yayilma": 5,  "adet": 1, "kapasite": 320, "tip": "normal",          "renk": ( 80,200,220)},
    "mateba":     {"isim": "Mateba Oto",      "hasar": 110, "hiz": 0.38, "mermi_hizi": 900,  "yayilma": 1,  "adet": 1, "kapasite": 48,  "tip": "delici",          "renk": (160,100,200)},
    # ── SMG SINIFI ────────────────────────────────────────────
    "smg":        {"isim": "SMG",             "hasar": 22,  "hiz": 0.08, "mermi_hizi": 820,  "yayilma": 8,  "adet": 1, "kapasite": 300, "tip": "normal",          "renk": ( 80,180,100)},
    "vector":     {"isim": "Vector K10",      "hasar": 32,  "hiz": 0.05, "mermi_hizi": 950,  "yayilma": 5,  "adet": 1, "kapasite": 400, "tip": "normal",          "renk": ( 50,220,150)},
    "pp90":       {"isim": "PP-90 Storm",     "hasar": 38,  "hiz": 0.07, "mermi_hizi": 880,  "yayilma": 7,  "adet": 1, "kapasite": 350, "tip": "normal",          "renk": (100,200,255)},
    "bizon":      {"isim": "Bizon-PP19",      "hasar": 26,  "hiz": 0.06, "mermi_hizi": 860,  "yayilma": 9,  "adet": 1, "kapasite": 640, "tip": "normal",          "renk": ( 60,160,220)},
    # ── TUFEK SINIFI ──────────────────────────────────────────
    "ak47":       {"isim": "AK-47",           "hasar": 55,  "hiz": 0.12, "mermi_hizi": 860,  "yayilma": 5,  "adet": 1, "kapasite": 180, "tip": "normal",          "renk": (200, 80, 40)},
    "m4a1":       {"isim": "M4A1-S",          "hasar": 62,  "hiz": 0.11, "mermi_hizi": 900,  "yayilma": 3,  "adet": 1, "kapasite": 200, "tip": "normal",          "renk": ( 80,160,255)},
    "aug":        {"isim": "AUG Taur",        "hasar": 70,  "hiz": 0.12, "mermi_hizi": 920,  "yayilma": 4,  "adet": 1, "kapasite": 180, "tip": "normal",          "renk": ( 60,200,120)},
    "scar":       {"isim": "SCAR-H",          "hasar": 88,  "hiz": 0.14, "mermi_hizi": 940,  "yayilma": 3,  "adet": 1, "kapasite": 160, "tip": "normal",          "renk": (200,150, 50)},
    "famas":      {"isim": "FAMAS Burst",     "hasar": 48,  "hiz": 0.09, "mermi_hizi": 890,  "yayilma": 6,  "adet": 3, "kapasite": 240, "tip": "normal",          "renk": (120,220,100)},
    "an94":       {"isim": "AN-94 Abakan",    "hasar": 72,  "hiz": 0.11, "mermi_hizi": 950,  "yayilma": 3,  "adet": 2, "kapasite": 160, "tip": "normal",          "renk": (180, 80,220)},
    "galil":      {"isim": "Galil ACE",       "hasar": 65,  "hiz": 0.12, "mermi_hizi": 870,  "yayilma": 5,  "adet": 1, "kapasite": 200, "tip": "normal",          "renk": (220,200, 60)},
    # ── SHOTGUN SINIFI ────────────────────────────────────────
    "shotgun":    {"isim": "Pompali",         "hasar": 28,  "hiz": 0.85, "mermi_hizi": 600,  "yayilma": 28, "adet": 8, "kapasite": 45,  "tip": "normal",          "renk": (180,120, 60)},
    "aa12":       {"isim": "AA-12 Oto",       "hasar": 22,  "hiz": 0.30, "mermi_hizi": 620,  "yayilma": 22, "adet": 8, "kapasite": 80,  "tip": "normal",          "renk": (220, 80, 80)},
    "ksg":        {"isim": "KSG Tactical",    "hasar": 45,  "hiz": 0.70, "mermi_hizi": 640,  "yayilma": 16, "adet": 6, "kapasite": 70,  "tip": "normal",          "renk": ( 80, 80,220)},
    "spas":       {"isim": "SPAS-12",         "hasar": 55,  "hiz": 0.80, "mermi_hizi": 580,  "yayilma": 30, "adet": 9, "kapasite": 36,  "tip": "normal",          "renk": (100,100,100)},
    "striker":    {"isim": "Striker Rev.",    "hasar": 35,  "hiz": 0.50, "mermi_hizi": 600,  "yayilma": 24, "adet": 8, "kapasite": 96,  "tip": "normal",          "renk": (255,140,  0)},
    "saiga":      {"isim": "Saiga-12 Ful",   "hasar": 30,  "hiz": 0.22, "mermi_hizi": 650,  "yayilma": 20, "adet": 7, "kapasite": 112, "tip": "normal",          "renk": ( 60,180,200)},
    # ── SNIPER SINIFI ─────────────────────────────────────────
    "sniper":     {"isim": "Keskin Nisanci",  "hasar": 400, "hiz": 1.50, "mermi_hizi": 2200, "yayilma": 0,  "adet": 1, "kapasite": 25,  "tip": "delici",          "renk": ( 80,200,120)},
    "awm":        {"isim": "AWM Magnum",      "hasar": 550, "hiz": 1.80, "mermi_hizi": 2600, "yayilma": 0,  "adet": 1, "kapasite": 15,  "tip": "delici",          "renk": (255,220,  0)},
    "barrett":    {"isim": "Barrett M82",     "hasar": 700, "hiz": 2.20, "mermi_hizi": 3000, "yayilma": 0,  "adet": 1, "kapasite": 10,  "tip": "delici",          "renk": (200, 60, 60)},
    "intervention":{"isim": "Intervention",  "hasar": 620, "hiz": 2.00, "mermi_hizi": 2800, "yayilma": 0,  "adet": 1, "kapasite": 12,  "tip": "delici",          "renk": (120,180,255)},
    "cheytac":    {"isim": "CheyTac M200",    "hasar": 850, "hiz": 2.50, "mermi_hizi": 3400, "yayilma": 0,  "adet": 1, "kapasite": 7,   "tip": "delici",          "renk": (200,100,255)},
    # ── LAZER / ENERJİ ────────────────────────────────────────
    "lazer":      {"isim": "Lazer Topu",      "hasar": 110, "hiz": 0.35, "mermi_hizi": 1400, "yayilma": 0,  "adet": 1, "kapasite": 60,  "tip": "delici",          "renk": ( 50,220,255)},
    "lazer_mk2":  {"isim": "Lazer MK-II",     "hasar": 160, "hiz": 0.28, "mermi_hizi": 1800, "yayilma": 0,  "adet": 1, "kapasite": 45,  "tip": "delici",          "renk": (  0,255,180)},
    "ion":        {"isim": "Ion Kanon",       "hasar": 220, "hiz": 0.50, "mermi_hizi": 2000, "yayilma": 2,  "adet": 1, "kapasite": 30,  "tip": "delici",          "renk": (180,  0,255)},
    "taser_xl":   {"isim": "Taser XL",        "hasar": 80,  "hiz": 0.20, "mermi_hizi": 1200, "yayilma": 10, "adet": 3, "kapasite": 90,  "tip": "delici",          "renk": (255,255, 50)},
    "phaser":     {"isim": "Phaser X9",       "hasar": 300, "hiz": 0.60, "mermi_hizi": 2200, "yayilma": 0,  "adet": 1, "kapasite": 20,  "tip": "delici",          "renk": (  0,200,255)},
    # ── PLAZMA / SCI-FI ───────────────────────────────────────
    "plazma":     {"isim": "Plazma Tabancasi","hasar": 150, "hiz": 0.60, "mermi_hizi": 1000, "yayilma": 4,  "adet": 1, "kapasite": 40,  "tip": "delici_patlayan", "renk": (100, 80,255), "r": 80},
    "plazma_mk2": {"isim": "Plazma MK-II",    "hasar": 220, "hiz": 0.65, "mermi_hizi": 1100, "yayilma": 3,  "adet": 1, "kapasite": 30,  "tip": "delici_patlayan", "renk": (140,  0,255), "r": 100},
    "void":       {"isim": "Void Striker",    "hasar": 350, "hiz": 0.90, "mermi_hizi": 1500, "yayilma": 0,  "adet": 1, "kapasite": 20,  "tip": "delici_patlayan", "renk": ( 80,  0,200), "r": 120},
    "antimatter": {"isim": "Antimatter Gun",  "hasar": 500, "hiz": 1.20, "mermi_hizi": 1800, "yayilma": 0,  "adet": 1, "kapasite": 12,  "tip": "delici_patlayan", "renk": (255,  0,200), "r": 160},
    # ── MINIGUN / AGIR ────────────────────────────────────────
    "minigun":    {"isim": "Minigun",         "hasar": 24,  "hiz": 0.04, "mermi_hizi": 900,  "yayilma": 15, "adet": 1, "kapasite": 600, "tip": "normal",          "renk": (255,100, 40)},
    "vulcan":     {"isim": "M134 Vulcan",     "hasar": 35,  "hiz": 0.03, "mermi_hizi": 1000, "yayilma": 12, "adet": 1, "kapasite": 900, "tip": "normal",          "renk": (255,160,  0)},
    "chaingun":   {"isim": "Chaingun X",      "hasar": 42,  "hiz": 0.035,"mermi_hizi": 950,  "yayilma": 10, "adet": 1, "kapasite": 1200,"tip": "normal",          "renk": (200,200,  0)},
    # ── ALEV / YANMA ──────────────────────────────────────────
    "alev":       {"isim": "Alev Makinesi",   "hasar": 12,  "hiz": 0.03, "mermi_hizi": 400,  "yayilma": 25, "adet": 2, "kapasite": 800, "tip": "alev",            "renk": (255, 80,  0)},
    "napalm":     {"isim": "Napalm Launcher", "hasar": 18,  "hiz": 0.04, "mermi_hizi": 380,  "yayilma": 30, "adet": 2, "kapasite": 600, "tip": "alev",            "renk": (255,140,  0)},
    "drakon":     {"isim": "Drakon MKIII",    "hasar": 28,  "hiz": 0.035,"mermi_hizi": 450,  "yayilma": 22, "adet": 3, "kapasite": 900, "tip": "alev",            "renk": (255, 50, 50)},
    # ── PATLAYICI / ROKET ─────────────────────────────────────
    "bomba":      {"isim": "Bomba Atar",      "hasar": 180, "hiz": 1.20, "mermi_hizi": 500,  "yayilma": 0,  "adet": 1, "kapasite": 15,  "tip": "seken_bomba",     "renk": (200,180,  0), "r": 120},
    "roket":      {"isim": "Roket Atari",     "hasar": 280, "hiz": 2.00, "mermi_hizi": 550,  "yayilma": 0,  "adet": 1, "kapasite": 12,  "tip": "roket",           "renk": (255, 80,  0), "r": 160},
    "thermobarik":{"isim": "Termobarik",      "hasar": 400, "hiz": 2.20, "mermi_hizi": 480,  "yayilma": 0,  "adet": 1, "kapasite": 8,   "tip": "roket",           "renk": (255, 40, 40), "r": 200},
    "rail":       {"isim": "Rail Gun Mk1",    "hasar": 600, "hiz": 2.50, "mermi_hizi": 4000, "yayilma": 0,  "adet": 1, "kapasite": 6,   "tip": "delici",          "renk": (  0,255,255)},
    "thor":       {"isim": "Thor Hammer",     "hasar": 450, "hiz": 2.00, "mermi_hizi": 600,  "yayilma": 5,  "adet": 1, "kapasite": 6,   "tip": "roket",           "renk": (100,100,255), "r": 220},
    "orbital":    {"isim": "Orbital Strike",  "hasar": 800, "hiz": 3.00, "mermi_hizi": 500,  "yayilma": 0,  "adet": 1, "kapasite": 3,   "tip": "roket",           "renk": (255,255,  0), "r": 280},
    # ── EFSANEVİ SINIF ────────────────────────────────────────
    "widowmaker": {"isim": "Widowmaker",      "hasar": 900, "hiz": 2.80, "mermi_hizi": 3500, "yayilma": 0,  "adet": 1, "kapasite": 5,   "tip": "delici_patlayan", "renk": (150,  0,255), "r": 140},
    "apocalypse": {"isim": "Apocalypse",      "hasar": 1200,"hiz": 3.50, "mermi_hizi": 2500, "yayilma": 2,  "adet": 1, "kapasite": 4,   "tip": "roket",           "renk": (255,  0,  0), "r": 320},
    "zeus":       {"isim": "Zeus Kanon",      "hasar": 750, "hiz": 1.00, "mermi_hizi": 3000, "yayilma": 3,  "adet": 5, "kapasite": 10,  "tip": "delici_patlayan", "renk": (255,220,  0), "r": 180},
    "mjolnir":    {"isim": "Mjolnir",         "hasar": 1500,"hiz": 4.00, "mermi_hizi": 1500, "yayilma": 0,  "adet": 1, "kapasite": 2,   "tip": "roket",           "renk": (200,200,255), "r": 380},
    "nemesis":    {"isim": "Nemesis X0",      "hasar": 650, "hiz": 0.08, "mermi_hizi": 2000, "yayilma": 3,  "adet": 1, "kapasite": 25,  "tip": "delici",          "renk": (255,  0,128)},
    "the_end":    {"isim": "The End",         "hasar": 2000,"hiz": 5.00, "mermi_hizi": 5000, "yayilma": 0,  "adet": 1, "kapasite": 1,   "tip": "delici_patlayan", "renk": (255,255,255), "r": 500},
}

SILAHLAR = {}
SILAH_SIRASI = []

# Tabancayi ucretsiz ekle
SILAHLAR["tabanca"] = {
    "isim": "Standart Tabanca", "fiyat": 0, "hasar": 35, "ates_hizi": 0.25,
    "mermi_hizi": 750, "yayilma": 2, "mermi_adeti": 1, "kapasite": -1,
    "renk": (200,200,200), "tip": "normal", "patlama_r": 0, "efekt": "yok",
    "gorsel_tip": "normal",
    "aciklama": ["Sonsuz mermi", "Baslatici silah"]
}
SILAH_SIRASI.append("tabanca")

baz_fiyatlar = {
    # Pistol
    "cift": 1200, "revolver": 2000, "deagle": 3500, "glock18": 2800, "mateba": 4500,
    # SMG
    "smg": 1800, "vector": 3000, "pp90": 3500, "bizon": 2500,
    # Tufek
    "ak47": 2500, "m4a1": 3200, "aug": 4000, "scar": 5000, "famas": 3800,
    "an94": 6000, "galil": 4500,
    # Shotgun
    "shotgun": 2200, "aa12": 4000, "ksg": 5000, "spas": 4500, "striker": 5500, "saiga": 6000,
    # Sniper
    "sniper": 4500, "awm": 8000, "barrett": 12000, "intervention": 10000, "cheytac": 18000,
    # Lazer/Enerji
    "lazer": 6000, "lazer_mk2": 9000, "ion": 13000, "taser_xl": 7000, "phaser": 15000,
    # Plazma
    "plazma": 8000, "plazma_mk2": 12000, "void": 18000, "antimatter": 25000,
    # Minigun/Agir
    "minigun": 7000, "vulcan": 11000, "chaingun": 16000,
    # Alev
    "alev": 6500, "napalm": 10000, "drakon": 14000,
    # Patlayici/Roket
    "bomba": 8000, "roket": 11000, "thermobarik": 17000, "rail": 22000,
    "thor": 20000, "orbital": 30000,
    # Efsanevi
    "widowmaker": 35000, "apocalypse": 50000, "zeus": 45000,
    "mjolnir": 75000, "nemesis": 40000, "the_end": 99999,
}

# Gorsel tip haritasi — her silaha hangi render stili uygulanacak
GORSEL_TIP_MAP = {
    # Anlik isin (raycast — Mermi olusturmaz)
    "lazer": "raycast", "lazer_mk2": "raycast", "phaser": "raycast",
    # Iyon/enerji topu
    "ion": "iyon_top", "taser_xl": "iyon_top",
    # Delici serit (hizli mermi + ince serit gorunum)
    "revolver": "delici_serit", "deagle": "delici_serit", "mateba": "delici_serit",
    "sniper": "delici_serit", "awm": "delici_serit", "barrett": "delici_serit",
    "intervention": "delici_serit", "cheytac": "delici_serit",
    "rail": "delici_serit", "nemesis": "delici_serit",
    # Sacma pellet
    "shotgun": "pellet", "aa12": "pellet", "ksg": "pellet",
    "spas": "pellet", "striker": "pellet", "saiga": "pellet",
    # Alev koni
    "alev": "alev_koni", "napalm": "alev_koni", "drakon": "alev_koni",
    # Roket fuze
    "roket": "roket_fuze", "thermobarik": "roket_fuze",
    "thor": "roket_fuze", "orbital": "roket_fuze",
    "apocalypse": "roket_fuze", "mjolnir": "roket_fuze",
    # Plazma topu
    "plazma": "plazma_top", "plazma_mk2": "plazma_top",
    # Void dalgasi
    "void": "void_dalgasi", "antimatter": "void_dalgasi",
    # Efsanevi
    "widowmaker": "efsane_isin",
    # Elektrik ark
    "zeus": "elektrik_ark",
    # The End ozel
    "the_end": "the_end_isin",
}

# Her silahi SILAHLAR'a dogrudan ekle
for s_key, s_veri in TEMEL_SILAHLAR.items():
    if s_key == "tabanca": continue
    fiyat = baz_fiyatlar.get(s_key, 5000)
    SILAHLAR[s_key] = {
        "isim": s_veri["isim"], "fiyat": fiyat,
        "hasar": s_veri["hasar"], "ates_hizi": s_veri["hiz"],
        "mermi_hizi": s_veri["mermi_hizi"], "yayilma": s_veri["yayilma"],
        "mermi_adeti": s_veri["adet"], "kapasite": s_veri["kapasite"],
        "renk": s_veri.get("renk", (200,200,200)), "tip": s_veri["tip"],
        "patlama_r": s_veri.get("r", 0), "efekt": "yok",
        "gorsel_tip": GORSEL_TIP_MAP.get(s_key, "normal"),  # BUG FIX: gorsel_tip artik SILAHLAR'a ekleniyor
        "aciklama": [f"Hasar: {s_veri['hasar']}", f"Kapasite: {s_veri['kapasite']}", f"Fiyat: {fiyat}$"]
    }
    SILAH_SIRASI.append(s_key)


YUKSELTMELER = {
    "can":    {"isim": "Max Can",       "aciklama": "+40 Max Can",        "fiyat": 400,  "max_seviye": 10},
    "stamina":{"isim": "Dayaniklilik",  "aciklama": "+30 Stamina",        "fiyat": 300,  "max_seviye": 10},
    "hiz":    {"isim": "Hiz",           "aciklama": "+25 Hareket Hizi",   "fiyat": 450,  "max_seviye": 6},
    "hasar":  {"isim": "Hasar",         "aciklama": "+30% Tum Hasar",     "fiyat": 600,  "max_seviye": 10},
    "kalkan": {"isim": "Kalkan",        "aciklama": "+40 Max Kalkan",     "fiyat": 500,  "max_seviye": 10},
    "zirh":   {"isim": "Zirh",          "aciklama": "-%12 Alinan Hasar",  "fiyat": 700,  "max_seviye": 5},
    "mermi":  {"isim": "Genis Sarjor",  "aciklama": "+20% Cephane",       "fiyat": 650,  "max_seviye": 5},
    "ult_cd": {"isim": "Hizli Ulti",    "aciklama": "-2s Ulti Bekleme",   "fiyat": 800,  "max_seviye": 5},
    "combo":  {"isim": "Uzun Combo",    "aciklama": "+0.5s Combo Suresi", "fiyat": 550,  "max_seviye": 5},
}

DURBUNLER = {
    "red_dot": {"isim": "Red Dot (1x)", "zoom": 1.0, "fiyat": 200},
    "holo":    {"isim": "Holo (2x)",    "zoom": 2.0, "fiyat": 250},
    "4x":      {"isim": "Scope (4x)",   "zoom": 4.0, "fiyat": 350},
    "6x":      {"isim": "Sniper (6x)",  "zoom": 6.0, "fiyat": 400},
}


DURUM_MENU  = "menu"
DURUM_OYUN  = "oyun"
DURUM_PAUSE = "pause"
DURUM_SHOP  = "shop"
DURUM_BITTI = "bitti"
PROJE_DIZIN   = os.path.dirname(os.path.abspath(__file__))
KAYIT_DOSYASI = os.path.join(PROJE_DIZIN, "kayitlar", "highscore.json")
os.makedirs(os.path.dirname(KAYIT_DOSYASI), exist_ok=True)
