# ============================================================
#  sistemler/ses_sistemi.py — Ses Motoru v4.0
#  ElevenLabs SFX entegrasyonu + Prosedürel fallback
# ============================================================
import pygame
import os
import math
import wave
import io
import struct
import random

# VERSION: 4.0 (ElevenLabs SFX Engine)
print("Ses Sistemi v4.0 Yukleniyor... (ElevenLabs SFX Aktif)")

# ---------------------------------------------------------------------------
#  Ses dosya adı → MP3 adı eşleştirmesi
#  (dosya .mp3 olarak kaydedilmiş, pygame bunu da destekler)
# ---------------------------------------------------------------------------
_DOSYA_ESLESMESI = {
    # Silah ateşleme
    "ates":          "ates_tabanca.mp3",
    "ates_ak":       "ates_ak.mp3",
    "ates_smg":      "ates_smg.mp3",
    "ates_pom":      "ates_pom.mp3",
    "ates_sni":      "ates_sni.mp3",
    "ates_laz":      "ates_laz.mp3",
    "ates_ale":      "ates_ale.mp3",
    "ates_pat":      "ates_pat.mp3",
    # Oyuncu
    "ayak_sesi":     "ayak_sesi.mp3",
    "hasar":         "oyuncu_hasar.mp3",
    "oyuncu_hasar":  "oyuncu_hasar.mp3",
    "oyuncu_hasar1": "oyuncu_hasar1.mp3",
    "oyuncu_hasar2": "oyuncu_hasar2.mp3",
    "oyuncu_hasar3": "oyuncu_hasar3.mp3",
    "oyuncu_hasar4": "oyuncu_hasar4.mp3",
    "olum":          "oyuncu_olum.mp3",
    "oyuncu_olum":   "oyuncu_olum.mp3",
    "reload_hafif":  "reload_hafif.mp3",
    "reload_agir":   "reload_agir.mp3",
    "silah_bos":     "silah_bos.mp3",
    # UI
    "ui_click":      "ui_click.mp3",
    "ui_satin_al":   "ui_satin_al.mp3",
    "ui_level_up":   "ui_level_up.mp3",
    "drop_al":       "drop_al.mp3",
    # Ambiyans (Music kanalı için ayrı)
    "ambiyans":      "ambiyans.mp3",
    # Zombi sesleri — ElevenLabs'ta üretilmediyse prosedürel fallback
    "zombi_normal":  "zombi_normal.mp3",
    "zombi_hizli":   "zombi_hizli.mp3",
    "zombi_zehir":   "zombi_zehir.mp3",
    "zombi_patlayan":"zombi_patlayan.mp3",
    "zombi_boss":    "zombi_boss.mp3",
    "zombi_olum":    "zombi_olum.mp3",
}

# Silah kategorisi → ateş sesi eşlemesi (ayarlar.py'deki KATEGORİ değerleriyle uyumlu)
SILAH_ATES_SESi = {
    "tabanca":    "ates",
    "smg":        "ates_smg",
    "tufek":      "ates_ak",
    "pompalı":    "ates_pom",
    "keskin":     "ates_sni",
    "lazer":      "ates_laz",
    "alev":       "ates_ale",
    "patlayici":  "ates_pat",
    # Varsayılan
    "default":    "ates",
}

SILAH_RELOAD_SESi = {
    "tabanca":  "reload_hafif",
    "smg":      "reload_hafif",
    "tufek":    "reload_agir",
    "pompalı":  "reload_agir",
    "keskin":   "reload_agir",
    "lazer":    "reload_hafif",
    "alev":     "reload_agir",
    "patlayici":"reload_agir",
    "default":  "reload_hafif",
}


class SesSistemi:
    def __init__(self):
        self.aktif = False
        self.sesler = {}
        self._ambiyans_kanal = None
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            pygame.mixer.set_num_channels(32)
            # Proje koku zombiistilasi/ ya da zombi_istilasi/ altından çalışabilir
            _adaylar = [
                os.path.join("assets", "sounds"),
                os.path.join("..", "assets", "sounds"),
            ]
            self.dizin = next(
                (p for p in _adaylar if os.path.isdir(p) and any(
                    f.endswith(".mp3") or f.endswith(".wav")
                    for f in os.listdir(p)
                )),
                _adaylar[0]
            )
            if not os.path.exists(self.dizin):
                os.makedirs(self.dizin)
            self._yukle()
            self.aktif = True
            print(f"  [{len(self.sesler)}] ses dosyasi yuklendi. (Dizin: {os.path.abspath(self.dizin)})")
        except Exception as e:
            print(f"Ses sistemi hatasi: {e}")

    # ------------------------------------------------------------------
    #  YUKLE
    # ------------------------------------------------------------------
    def _yukle(self):
        for anahtar, dosya_adi in _DOSYA_ESLESMESI.items():
            yol = os.path.join(self.dizin, dosya_adi)
            if os.path.exists(yol):
                try:
                    self.sesler[anahtar] = pygame.mixer.Sound(yol)
                    # Varsayılan ses seviyeleri
                    if "ates" in anahtar:
                        self.sesler[anahtar].set_volume(0.75)
                    elif "ambiyans" in anahtar:
                        self.sesler[anahtar].set_volume(0.35)
                    elif "zombi" in anahtar:
                        self.sesler[anahtar].set_volume(0.65)
                    elif "ui" in anahtar:
                        self.sesler[anahtar].set_volume(0.55)
                except Exception as ex:
                    print(f"  UYARI: '{dosya_adi}' yuklenemedi: {ex}")
            else:
                # Eksik dosya → prosedürel fallback
                fb = self._prosedürel_uret(anahtar)
                if fb:
                    self.sesler[anahtar] = fb

    # ------------------------------------------------------------------
    #  PROSEDÜREL FALLBACK (dosya yoksa)
    # ------------------------------------------------------------------
    def _prosedürel_uret(self, tip):
        """Sadece kritik sesler için basit bir WAV üretir."""
        profiller = {
            "ates":       (0.12, 120, 0.6, 0.4, 2.0),
            "ates_ak":    (0.25,  55, 0.9, 0.1, 1.2),
            "ates_smg":   (0.08, 200, 0.5, 0.5, 2.5),
            "ates_pom":   (0.40,  40, 1.0, 0.2, 3.0),
            "ates_sni":   (0.80,  30, 1.0, 0.1, 0.8),
            "ates_laz":   (0.30, 800, 0.1, 0.9, 2.0),
            "ates_ale":   (0.10, 100, 1.0, 0.0, 5.0),
            "ates_pat":   (0.60,  35, 1.0, 0.3, 1.0),
            "hasar":      (0.10, 250, 0.0, 1.0, 2.0),
            "olum":       (0.30, 100, 0.5, 0.5, 1.5),
            "zombi_olum": (0.20, 150, 0.8, 0.2, 1.8),
            "ui_click":   (0.05, 600, 0.0, 1.0, 3.0),
            "silah_bos":  (0.06, 300, 0.1, 0.9, 4.0),
        }
        if tip not in profiller:
            return None
        try:
            sample_rate = 44100
            byte_io = io.BytesIO()
            sure, frek, noise_v, sine_v, decay = profiller[tip]
            num_samples = int(sample_rate * sure)

            with wave.open(byte_io, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(sample_rate)
                for i in range(num_samples):
                    t = float(i) / sample_rate
                    vol = (1.0 - float(i) / num_samples) ** decay
                    if "laz" in tip:
                        val = math.sin(t * frek * (1.0 - t * 0.5) * 2 * math.pi) * 32767
                    else:
                        noise = (random.random() * 2 - 1) * noise_v
                        sine = math.sin(t * frek * 2 * math.pi) * sine_v
                        val = (noise + sine) * 32767
                    fv = max(-32768, min(32767, int(val * vol)))
                    wf.writeframesraw(struct.pack('<h', fv))

            byte_io.seek(0)
            return pygame.mixer.Sound(byte_io)
        except Exception:
            return None

    # ------------------------------------------------------------------
    #  PUBLIC API
    # ------------------------------------------------------------------
    def oynat(self, isim, volume=None):
        """Bir efekti tek seferlik oynat."""
        if not self.aktif:
            return
            
        # Oyuncu hasar sesi ust uste binmesini onleme
        if isim.startswith("oyuncu_hasar"):
            su_an = pygame.time.get_ticks()
            if getattr(self, "_son_hasar_sesi", 0) + 400 > su_an:
                return
            self._son_hasar_sesi = su_an

        ses = self.sesler.get(isim)
        if ses:
            if volume is not None:
                ses.set_volume(max(0.0, min(1.0, volume)))
            ses.play()

    def oyuncu_hasar_sesi_oynat(self):
        """4 farkli bagirma sesinden rastgele birini oynatir."""
        idx = random.randint(1, 4)
        self.oynat(f"oyuncu_hasar{idx}")

    def ates_sesi_oynat(self, silah_kategori):
        """Silah kategorisine göre doğru ateş sesini çalar."""
        anahtar = SILAH_ATES_SESi.get(silah_kategori, SILAH_ATES_SESi["default"])
        self.oynat(anahtar)

    def reload_sesi_oynat(self, silah_kategori):
        """Silah kategorisine göre reload sesini çalar."""
        anahtar = SILAH_RELOAD_SESi.get(silah_kategori, SILAH_RELOAD_SESi["default"])
        self.oynat(anahtar)

    def zombi_sesi_oynat(self, zombi_tipi="normal"):
        """Zombi tipine göre ses çalar (rastgele aralıklarla)."""
        anahtar_map = {
            "normal":    "zombi_normal",
            "hizli":     "zombi_hizli",
            "zehir":     "zombi_zehir",
            "patlayan":  "zombi_patlayan",
            "boss":      "zombi_boss",
        }
        anahtar = anahtar_map.get(zombi_tipi, "zombi_normal")
        self.oynat(anahtar, volume=0.6)

    def zombi_olum_sesi_oynat(self):
        self.oynat("zombi_olum", volume=0.7)

    def ambiyans_baslat(self):
        """Ambiyans müziğini loop olarak çalar."""
        if not self.aktif:
            return
        ses = self.sesler.get("ambiyans")
        if ses:
            self._ambiyans_kanal = ses.play(loops=-1, fade_ms=2000)

    def ambiyans_durdur(self):
        if self._ambiyans_kanal:
            self._ambiyans_kanal.fadeout(1500)

    def ses_seviyesi_ayarla(self, kategori, seviye):
        """
        kategori: 'silah' | 'zombi' | 'ui' | 'ambiyans' | 'hepsi'
        seviye: 0.0 - 1.0
        """
        for isim, ses in self.sesler.items():
            if kategori == "hepsi":
                ses.set_volume(seviye)
            elif kategori == "silah" and isim.startswith("ates"):
                ses.set_volume(seviye)
            elif kategori == "zombi" and isim.startswith("zombi"):
                ses.set_volume(seviye)
            elif kategori == "ui" and isim.startswith("ui"):
                ses.set_volume(seviye)
            elif kategori == "ambiyans" and isim == "ambiyans":
                ses.set_volume(seviye)

    def duraksat(self):
        pygame.mixer.pause()

    def devam_et(self):
        pygame.mixer.unpause()

    def tamamen_durdur(self):
        pygame.mixer.stop()


# ---------------------------------------------------------------------------
#  Singleton — oyun boyunca tek örnek
# ---------------------------------------------------------------------------
ses_sis = SesSistemi()
