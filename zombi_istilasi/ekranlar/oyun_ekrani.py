# ============================================================
#  ekranlar/oyun_ekrani.py
# ============================================================
import pygame
import math
import random
from ayarlar import (
    GENISLIK, YUKSEKLIK, BEYAZ, SIYAH, KIRMIZI, YESIL, SARI, ALTIN,
    SILAHLAR, SILAH_SIRASI, ZIRH_MAVI, MOR, ZAFIYET_TABLOSU,
)
from varliklar.oyuncu   import Oyuncu
from varliklar.patlama  import Patlama
from varliklar.parcacik import kan_parcaciklari, HarasarSayisi, BasarimBildirimi
from varliklar.isik     import AnlikIsin
from sistemler.dalga_sistemi   import DalgaSistemi
from sistemler.puan_sistemi    import PuanSistemi
from sistemler.perk_sistemi    import PerkSistemi, PERKLER
from sistemler.gorev_sistemi   import GorevSistemi
from sistemler.basarim_sistemi import BasarimSistemi
from sistemler.ses_sistemi     import ses_sis
from ekranlar.hud              import HudYoneticisi

class OyunEkrani:
    def __init__(self):
        self.font_hud    = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_buyuk  = pygame.font.SysFont("Consolas", 46, bold=True)
        self.font_kucuk  = pygame.font.SysFont("Consolas", 15, bold=True)
        self.font_sayi   = pygame.font.SysFont("Impact", 18)
        self.font_sayi_b = pygame.font.SysFont("Impact", 32)
        self.font_mermi  = pygame.font.SysFont("Impact", 56)
        
        self._combo_fontlar = {
            i: pygame.font.SysFont("Impact", i, bold=True)
            for i in range(46, 90, 4)
        }

        self.hud = HudYoneticisi({
            "hud":   self.font_hud,
            "buyuk": self.font_buyuk,
            "kucuk": self.font_kucuk,
            "mermi": self.font_mermi,
            "combo": self._combo_fontlar,
        })

        # Grafik iyileştirme: Zemin Detayları — PRE-RENDER edilmiş Surface
        self._zemin_verileri = []
        for _ in range(300):
            r = random.choice([2, 3, 5])
            c = random.choice([(30, 35, 40), (20, 25, 30), (45, 25, 25)])
            self._zemin_verileri.append((random.randint(-200, GENISLIK + 200), random.randint(-200, YUKSEKLIK + 200), r, c))
        # Zemin surface'i bir kez olustur (her frame 300 circle cizimine son)
        self._zemin_surface = pygame.Surface((GENISLIK + 400, YUKSEKLIK + 400), pygame.SRCALPHA)
        for (px, py, pr, pcolor) in self._zemin_verileri:
            pygame.draw.circle(self._zemin_surface, pcolor, (px + 200, py + 200), pr)

        # Karanlık dalga torch efekti — bir kez olustur
        torch_r = 200
        self._torch_surface = pygame.Surface((torch_r*2, torch_r*2), pygame.SRCALPHA)
        for dr in range(torch_r, 0, -4):
            a = int(155 * (1 - dr/torch_r) ** 2)
            pygame.draw.circle(self._torch_surface, (0, 0, 0, 155 - a), (torch_r, torch_r), dr)
        self._torch_r = torch_r
        
        self._karanlik_overlay = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
        self._karanlik_overlay.fill((0, 0, 0, 155))
        self._isin_surface = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)

        self.haritalar = [
            {"isim": "Sehir Asfalti", "zemin": (10, 12, 16), "cizgi": (22, 28, 36), "karo": 80},
            {"isim": "Laboratuvar", "zemin": (14, 22, 20), "cizgi": (45, 70, 65), "karo": 70},
        ]
        self.aktif_harita = 0
        self._sifirla()


    def _sifirla(self):
        self.mermiler    = pygame.sprite.Group()
        self.zombiler    = pygame.sprite.Group()
        self.droplar     = pygame.sprite.Group()
        self.patlamalar  = []
        self.parcaciklar = []
        self.sayilar     = []
        self.basarimlar  = []
        self.zehir_havuzlari = []
        self.anlik_isinlar   = []  # Raycast beam gorunum listesi
        
        self.oyuncu      = Oyuncu(GENISLIK // 2, YUKSEKLIK // 2)
        self.dalga_sis   = DalgaSistemi(self.zombiler)
        self.puan_sis    = PuanSistemi()
        self.perk_sis    = PerkSistemi()
        self.gorev_sis   = GorevSistemi()
        self.basarim_sis = BasarimSistemi()
        
        self.istatistikler = {
            "toplam_zombi": 0,
            "toplam_atis": 0,
            "toplam_hasar": 0,
            "boss_olduruldu": 0,
            "max_combo": 0,
        }
        self._harita_gecis = 0.0
        self.gorev_sis.yeni_gorev_sec()
        # Perk sistemi referansini oyuncuya bagla (ikiz_namlu, hasar_alindi vs)
        self.oyuncu._perk_sis_ref = self.perk_sis
        
        self.sarsinti    = 0.0
        self.bitti       = False
        self.son_fare_pos = (0, 0)
        self._dalga_bitti_setter = False  # Cheat ile dalga atlama icin
        
        self.hile_bekleme = 0.0  # Hile tuslari icin cooldown

    def baslat(self):
        self._sifirla()

    def harita_degistir(self):
        self.aktif_harita = (self.aktif_harita + 1) % len(self.haritalar)
        self._harita_gecis = 0.4  # saniye



    def guncelle(self, dt, tuslar, fare_pos):
        if self.bitti: return
        
        # Soğuk Kan perki — nişanda zaman yavaşlar
        if 'soguk_kan' in self.perk_sis.aktif_perkler:
            if pygame.mouse.get_pressed()[2]:  # sağ tık nişan
                dt = dt * 0.45
        
        self.son_fare_pos = fare_pos
        onceki_ates = self.oyuncu.ates_sayac
        self.oyuncu.update(dt, tuslar, fare_pos, self.mermiler, GENISLIK, YUKSEKLIK, False)
        if onceki_ates <= 0 and self.oyuncu.ates_sayac > 0:
            self.istatistikler["toplam_atis"] += 1
            
        if self.puan_sis.combo > self.istatistikler["max_combo"]:
            self.istatistikler["max_combo"] = self.puan_sis.combo
            
        if getattr(self.oyuncu, '_kalkan_patlama_flag', False):
            self.oyuncu._kalkan_patlama_flag = False
            self.patlamalar.append(Patlama(self.oyuncu.x, self.oyuncu.y, 150, hasar=80))
            self.basarimlar.append(BasarimBildirimi("KALKAN PATLAMASI!", ""))
        self.mermiler.update(dt, GENISLIK, YUKSEKLIK)
        self.puan_sis.update(dt)

        # Hile / Test Komutlari
        self.hile_bekleme -= dt
        if self.hile_bekleme < 0: self.hile_bekleme = 0
        
        if self.hile_bekleme == 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_F1]:
                self.puan_sis.para += 50000
                self.basarimlar.append(BasarimBildirimi("HİLE AKTİF", "50.000 Para Eklendi!"))
                self.hile_bekleme = 0.5
            elif keys[pygame.K_F2]:
                self.puan_sis._xp_ekle(5000)
                self.basarimlar.append(BasarimBildirimi("HİLE AKTİF", "5000 XP Eklendi!"))
                self.hile_bekleme = 0.5
            elif keys[pygame.K_F3]:
                self.oyuncu.can = getattr(self.oyuncu, "max_can_degeri", 100)
                self.oyuncu.kalkan = getattr(self.oyuncu, "max_kalkan_degeri", 100)
                self.oyuncu.ult_bekleme = 0
                self.basarimlar.append(BasarimBildirimi("HİLE AKTİF", "Can, Kalkan ve Ulti Fullendi!"))
                self.hile_bekleme = 0.5
            elif keys[pygame.K_F4]:
                for s in SILAH_SIRASI:
                    if s not in self.oyuncu.envanter:
                        self.oyuncu.envanter.append(s)
                    self.oyuncu.mermiler[s] = 9999
                self.basarimlar.append(BasarimBildirimi("HİLE AKTİF", "Tüm Silahlar Açıldı ve Mermi: 9999!"))
                self.hile_bekleme = 0.5
            elif keys[pygame.K_F5]:
                for z in list(self.zombiler):
                    z.can = 0
                    self._zombi_oldu(z)
                self.basarimlar.append(BasarimBildirimi("HİLE AKTİF", "Ekrandaki Tüm Zombiler Öldürüldü!"))
                self.hile_bekleme = 0.5
            elif keys[pygame.K_F6]:
                self.oyuncu.god_mode = not getattr(self.oyuncu, "god_mode", False)
                durum = "AÇIK" if self.oyuncu.god_mode else "KAPALI"
                self.basarimlar.append(BasarimBildirimi("HİLE AKTİF", f"Ölümsüzlük (God Mode) {durum}"))
                self.hile_bekleme = 0.5

        # Raycast silah kuyrugunu isle
        for rc in self.oyuncu.raycast_kuyrugu:
            self._isle_raycast(rc)
        self.oyuncu.raycast_kuyrugu.clear()

        # Anlik isinlari guncelle
        self.anlik_isinlar = [i for i in self.anlik_isinlar if i.update(dt)]


        for zh in self.zehir_havuzlari:
            zh[3] -= dt
            if zh[3] > 0 and math.hypot(zh[0] - self.oyuncu.x, zh[1] - self.oyuncu.y) < (zh[2] + self.oyuncu.yari_cap):
                self.oyuncu.zombi_temas(dt, 5)
        # Suresi dolan havuzlari filtrele (list.remove O(N) yerine list comprehension O(1))
        self.zehir_havuzlari = [zh for zh in self.zehir_havuzlari if zh[3] > 0]

        for z in list(self.zombiler):
            z.update(dt, self.oyuncu.x, self.oyuncu.y)
            if z.tip == "zehirli" and z.zehir_sayac >= 0.3:
                z.zehir_sayac = 0.0
                self.zehir_havuzlari.append([z.x, z.y, 16, 2.5, 2.5])
            
            # Element hasarından (yanma/zehir) ölen zombileri yakala
            if getattr(z, "_olum_efektten", False) and z.alive():
                z._olum_efektten = False
                self._zombi_oldu(z, patlama_mi=False)
                continue
                
            if z.oyuncuya_yakin_mi(self.oyuncu.x, self.oyuncu.y):
                if z.tip == "patlayan" and z.alive():
                    # Patlayan zombi: direkt oldur, _zombi_oldu iceride patlama yapar
                    self._zombi_oldu(z, patlama_mi=True)
                elif z.tip != "patlayan":
                    self.oyuncu.zombi_temas(dt, z.hasar)
                    
                if self.oyuncu.oldu:
                    self._bitis()
                    return

        zombi_listesi = [z for z in self.zombiler if z.alive()]
        huc_boyutu = 120
        zombi_grid = {}
        for z in zombi_listesi:
            gx, gy = int(z.x // huc_boyutu), int(z.y // huc_boyutu)
            zombi_grid.setdefault((gx, gy), []).append(z)
            
        # Zombi İtme (Separation Steering)
        for z in zombi_listesi:
            if z.tip == "boss": continue
            gx, gy = int(z.x // huc_boyutu), int(z.y // huc_boyutu)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for diger in zombi_grid.get((gx+dx, gy+dy), []):
                        if diger is z: continue
                        dx_sep = z.x - diger.x
                        dy_sep = z.y - diger.y
                        dist = math.hypot(dx_sep, dy_sep)
                        min_dist = z.yari_cap + diger.yari_cap
                        if 0 < dist < min_dist:
                            guc = (min_dist - dist) / dist
                            z.x += dx_sep * guc * 0.5
                            z.y += dy_sep * guc * 0.5
                            z.rect.center = (int(z.x), int(z.y))

        # O(N) Spatial Hash Mermi Çarpışması
        for m in list(self.mermiler):
            if not m.alive(): continue
            gx, gy = int(m.x // huc_boyutu), int(m.y // huc_boyutu)
            yakindaki_zombiler = []
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    yakindaki_zombiler.extend(zombi_grid.get((gx+dx, gy+dy), []))
                    
            if m.tip in ("roket", "seken_bomba", "delici_patlayan"):
                for z in yakindaki_zombiler:
                    if math.hypot(z.x - m.x, z.y - m.y) < (z.yari_cap + m.yari_cap):
                        # Patlama olustur — silah hasarini aktar
                        self.patlamalar.append(Patlama(m.x, m.y, m.patlama_r, hasar=m.hasar))
                        m.kill()
                        break
            else:
                for z in yakindaki_zombiler:
                    if m.tip == "delici" and z in getattr(m, "vurulan_zombiler", set()):
                        continue
                        
                    oldu, zafiyet_msg, gercek_hasar = z.mermi_carpisma(m)
                    
                    # Mermi isabet ETTİ mi? (gercek_hasar > 0 = gerçek çarpışma)
                    if gercek_hasar <= 0:
                        continue
                    
                    self.gorev_sis.isabet_bildir()
                    
                    if m.tip == "delici":
                        # Sadece isabet eden zombiyi kaydet
                        if not hasattr(m, "vurulan_zombiler"): m.vurulan_zombiler = set()
                        m.vurulan_zombiler.add(z)
                        
                    if not m.alive() or m.tip == "delici":
                        renk = m.renk if m.efekt != "yok" else (180, 20, 20)
                        self.parcaciklar.extend(kan_parcaciklari(z.x, z.y, 4, renk))
                        # Zafiyet mesajı
                        if zafiyet_msg == "ZAYIF NOKTA!":
                            self.sayilar.append(HarasarSayisi(z.x, z.y - 20, zafiyet_msg, SARI, True))
                            self.sayilar.append(HarasarSayisi(z.x, z.y, gercek_hasar, (255, 255, 80)))
                        elif zafiyet_msg == "DİRENÇLİ":
                            self.sayilar.append(HarasarSayisi(z.x, z.y - 20, zafiyet_msg, (160, 160, 160)))
                            self.sayilar.append(HarasarSayisi(z.x, z.y, gercek_hasar, (140, 140, 140)))
                        else:
                            self.sayilar.append(HarasarSayisi(z.x, z.y, gercek_hasar, m.renk))
                        if oldu:
                            self._zombi_oldu(z)
                        if not m.alive():
                            break

        for m in list(self.mermiler):
            if not m.alive() and m.tip in ("roket", "seken_bomba", "delici_patlayan") and m.patlama_hazir:
                self.patlamalar.append(Patlama(m.x, m.y, m.patlama_r, hasar=m.hasar))

        for p in self.patlamalar[:]:
            p.update(dt)
            if not p.hasar_verildi:
                oldukler = p.zombi_hasari_ver(self.zombiler, hasar_carpani=self.oyuncu.hasar_carpani)
                for z in oldukler:
                    # Gercek patlama hasarini goster
                    gosterilen = int(p.hasar * self.oyuncu.hasar_carpani) if p.hasar > 0 else int(p.max_r * 1.5)
                    self.sayilar.append(HarasarSayisi(z.x, z.y, gosterilen, SARI, True))
                    self._zombi_oldu(z)
        self.patlamalar = [p for p in self.patlamalar if not p.bitti_mi]

        manyetik = self.perk_sis.drop_manyetik_mi()
        for d in list(self.droplar):
            d.update(dt, manyetik=manyetik, oyuncu_x=self.oyuncu.x, oyuncu_y=self.oyuncu.y)
            if d.alive() and d.oyuncuya_dokunan(self.oyuncu.x, self.oyuncu.y, self.oyuncu.yari_cap):
                if d.tip == "can":
                    self.oyuncu.can_doldur(40)
                    self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, 40, YESIL, True))
                elif d.tip == "mermi":
                    self.oyuncu.aktif_mermi_doldur()
                    self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, "+Mermi!", SARI, True))
                ses_sis.oynat("drop_al")
                d.kill()

        self.parcaciklar = [p for p in self.parcaciklar if p.update(dt)]
        self.sayilar = [s for s in self.sayilar if s.update(dt)]
        self.basarimlar = [b for b in self.basarimlar if b.update(dt)]
        
        if self.puan_sis.yeni_seviye_flag:
            self.puan_sis.yeni_seviye_flag = False
            self.basarimlar.append(BasarimBildirimi(f"SEVİYE {self.puan_sis.seviye}!", "Tüm istatistiklerin artıyor!"))
            ses_sis.oynat("ui_level_up")

        if self.oyuncu.yoruldu_mu and not getattr(self, "_yoruldu_bildirildi", False):
            self._yoruldu_bildirildi = True
            self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, "Yoruldum!", KIRMIZI))
        elif not self.oyuncu.yoruldu_mu:
            self._yoruldu_bildirildi = False

        if self.sarsinti > 0: self.sarsinti -= dt
        self.dalga_sis.guncelle(dt, GENISLIK, YUKSEKLIK)
        self.gorev_sis.guncelle(dt, self.puan_sis)
        
        bonus = self.basarim_sis.kontrol_et({
            "dalga_no": self.dalga_sis.dalga_no,
            "zombi_oldu_sayisi": self.istatistikler.get("toplam_zombi", 0),
            "combo_max": self.istatistikler.get("max_combo", 0),
            "boss_olduruldu": self.istatistikler.get("boss_olduruldu", 0) > 0,
            "perk_sayisi": len(self.perk_sis.aktif_perkler),
            "para": self.puan_sis.para,
            "silah_sayisi": len(self.oyuncu.envanter)
        })
        for b in self.basarim_sis.yeni_al():
            self.basarimlar.append(
                BasarimBildirimi(f"🏆 {b['isim']}", f"+{b['skor_bonusu']} puan!")
            )
            ses_sis.oynat("ui_level_up")
            self.puan_sis.puan += b['skor_bonusu']

    def _zombi_oldu(self, z, patlama_mi=False):
        if not z.alive(): return  # Cift olum guardi
        if z.tip == "patlayan":
            # Patlayan zombi kendi patlaması: 40 hasar, 120 yarıçap
            self.patlamalar.append(Patlama(z.x, z.y, 120, hasar=40))
            if z.patlama_hasar_mesafe(self.oyuncu.x, self.oyuncu.y) < 120 + self.oyuncu.yari_cap:
                self.oyuncu.hasar_al(40)
        
        # ONCE kill() — tekrar _zombi_oldu'ya girmesini engeller
        z.kill()
        
        self.istatistikler["toplam_zombi"] += 1
        if z.tip == "boss":
            self.istatistikler["boss_olduruldu"] += 1
            
        if 'patlama' in self.perk_sis.aktif_perkler:
            for komsu in list(self.zombiler):
                if komsu is not z and math.hypot(komsu.x - z.x, komsu.y - z.y) < 120:
                    komsu.can -= 60
                    self.sayilar.append(HarasarSayisi(komsu.x, komsu.y, 60, (255, 140, 0)))
                    if komsu.can <= 0:
                        self._zombi_oldu(komsu)
                        
        mesafe = math.hypot(z.x - self.oyuncu.x, z.y - self.oyuncu.y)
        self.gorev_sis.yakin_olum_bildir(mesafe)
                
        self.parcaciklar.extend(kan_parcaciklari(z.x, z.y, 18))
        
        if z.tip == "boss":
            self.parcaciklar.extend(kan_parcaciklari(z.x, z.y, 8, (80, 80, 80), tip="parca"))
            ses_sis.oynat("ates_pat", volume=1.0)
            ses_sis.oynat("ui_level_up", volume=0.8)
            self.basarimlar.append(BasarimBildirimi("BOSS YENİLDİ! 💀", f"+{z.skor} SKOR"))
            
        if z.tip == "zehirli":
            self.zehir_havuzlari.append([z.x, z.y, 40, 6.0, 6.0])
            self.parcaciklar.extend(kan_parcaciklari(z.x, z.y, 12, (50, 255, 80)))
            
        # Perk: vampir ve para_avcisi
        self.perk_sis.uygula_olum(self.oyuncu, z)
        # Görev: element ve patlama
        efekt = getattr(z, "_son_isabetefekti", "yok")
        self.gorev_sis.zombi_oldu_bildir(efekt, patlama_mi)
        
        elde_puan, elde_para = self.puan_sis.zombi_oldu(z.skor, z.para, baz_xp=25, combo_suresi_ek=self.oyuncu.yukseltmeler["combo"]*0.5)
        # Görev: combo takibi
        self.gorev_sis.combo_bildir(self.puan_sis.combo)
        self.sayilar.append(HarasarSayisi(z.x, z.y - 25, f"+{elde_para}$", ALTIN))
        
        self.sarsinti = 0.12 if z.tip != "boss" else 0.35
        ses_sis.zombi_olum_sesi_oynat()
        drop = z.drop_olustur()
        if drop: self.droplar.add(drop)

    def _bitis(self):
        self.bitti = True
        self.gorev_sis.dalga_bitti_kontrol(self.puan_sis)
        self.puan_sis.kaydet()

    def _nokta_cizgiye_uzaklik(self, px, py, x1, y1, x2, y2):
        """Nokta'dan cizgi segmentine en kisa mesafe."""
        dx, dy = x2 - x1, y2 - y1
        uzunluk_kare = dx * dx + dy * dy
        if uzunluk_kare == 0:
            return math.hypot(px - x1, py - y1)
        t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / uzunluk_kare))
        return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))

    def _isle_raycast(self, rc):
        """Raycast silah atisi: aninda hasar + AnlikIsin gorseli olusturur."""
        x, y = rc["x"], rc["y"]
        aci = rc["aci"]
        veri = rc["veri"]
        hasar_baz = veri["hasar"] * rc["carpan"] * self.oyuncu.hasar_carpani
        renk = veri["renk"]
        efekt = veri.get("efekt", "yok")

        # Isin uzunlugu
        uzunluk = min(GENISLIK + YUKSEKLIK, veri.get("mermi_hizi", 1400))
        aci_rad = math.radians(aci)
        bx = x + math.cos(aci_rad) * uzunluk
        by = y + math.sin(aci_rad) * uzunluk

        for z in list(self.zombiler):
            if not z.alive():
                continue
            uzaklik = self._nokta_cizgiye_uzaklik(z.x, z.y, x, y, bx, by)
            if uzaklik < z.yari_cap + 3:
                # BUG FIX: Zafiyet tablosu artik raycast icin de uygulanıyor
                zafiyet = ZAFIYET_TABLOSU.get(z.tip, {})
                carpan = zafiyet.get(efekt, 1.0) if efekt != "yok" else 1.0
                hasar = hasar_baz * carpan
                z.can -= hasar
                z.hit_sayac = 0.12
                # Zafiyet mesaji
                if carpan >= 1.5:
                    self.sayilar.append(HarasarSayisi(z.x, z.y - 20, "ZAYIF NOKTA!", SARI, True))
                elif carpan <= 0.5:
                    self.sayilar.append(HarasarSayisi(z.x, z.y - 20, "DİRENÇLİ", (160, 160, 160)))
                self.sayilar.append(HarasarSayisi(z.x, z.y, int(hasar), renk))
                self.parcaciklar.extend(kan_parcaciklari(z.x, z.y, 4, renk))
                if z.can <= 0:
                    self._zombi_oldu(z)

        # Gorsel isin olustur
        genislik = 4 if veri.get("gorsel_tip") == "the_end_isin" else 2
        self.anlik_isinlar.append(AnlikIsin(x, y, aci, renk, uzunluk, genislik))

    def ciz(self, ekran):
        ox = random.randint(-4, 4) if self.sarsinti > 0 else 0
        oy = random.randint(-4, 4) if self.sarsinti > 0 else 0

        aktif_harita = self.haritalar[self.aktif_harita]
        ekran.fill(aktif_harita["zemin"])
        
        # Izgara çizgileri (Fayans Derzleri)
        kare = aktif_harita["karo"]
        for x in range(int(ox) % kare, GENISLIK, kare):
            pygame.draw.line(ekran, aktif_harita["cizgi"], (x, 0), (x, YUKSEKLIK), 2)
        for y in range(int(oy) % kare, YUKSEKLIK, kare):
            pygame.draw.line(ekran, aktif_harita["cizgi"], (0, y), (GENISLIK, y), 2)
            
        # Zemin pre-rendered surface (300 circle artik her frame cizilmiyor)
        ekran.blit(self._zemin_surface, (-200 + ox, -200 + oy))
            
        for zh in self.zehir_havuzlari:
            alpha = int(90 * (zh[3] / zh[4]))
            s = pygame.Surface((zh[2]*2, zh[2]*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (50, 255, 80, alpha), (zh[2], zh[2]), zh[2])
            ekran.blit(s, (zh[0] - zh[2] + ox, zh[1] - zh[2] + oy))

        for d in self.droplar: ekran.blit(d.image, (d.rect.x + ox, d.rect.y + oy))
        
        # Nişangah (Cone) Çizimi (Sadece oyuncu yaşıyorsa)
        if not self.bitti:
            self.oyuncu.ciz_nisangah(ekran, self.son_fare_pos, ox, oy)

        for m in self.mermiler: ekran.blit(m.image, (m.rect.x + ox, m.rect.y + oy))
        for p in self.patlamalar: p.ciz(ekran)
        for p in self.parcaciklar: p.ciz(ekran)

        # Anlik isinlari (raycast beams) ciz
        if self.anlik_isinlar:
            self._isin_surface.fill((0, 0, 0, 0))
            for isin in self.anlik_isinlar:
                isin.ciz(self._isin_surface)
            ekran.blit(self._isin_surface, (0, 0))

        # Görev 22 — Hızlı Zombi Trail Efekti
        for z in self.zombiler:
            if z.tip in ("hizli", "kosucu") and z.hiz > 0:
                iz_s = pygame.Surface((z.yari_cap*2, z.yari_cap*2), pygame.SRCALPHA)
                pygame.draw.circle(iz_s, (*z.renk, 40), (z.yari_cap, z.yari_cap), z.yari_cap)
                ekran.blit(iz_s, (z.rect.x + ox - 6, z.rect.y + oy + 6))
            ekran.blit(z.image, (z.rect.x + ox, z.rect.y + oy))
            
        for z in self.zombiler: z.can_bar_ciz(ekran)

        # Görev 19 — Sprint İz Efekti
        for (ix, iy, it) in getattr(self.oyuncu, '_iz_konumlar', []):
            yash = (pygame.time.get_ticks() - it) / 1000.0
            alpha = max(0, int(120 * (1 - yash / 0.5)))
            if alpha > 0:
                iz_s = pygame.Surface((36, 36), pygame.SRCALPHA)
                pygame.draw.circle(iz_s, (80, 160, 255, alpha), (18, 18), 18)
                ekran.blit(iz_s, (int(ix) - 18 + ox, int(iy) - 18 + oy))

        ekran.blit(self.oyuncu.image, (self.oyuncu.rect.x + ox, self.oyuncu.rect.y + oy))
        
        # Görev 20 — Manyetik Çekim Görsel Efekti
        if 'manyetik' in self.perk_sis.aktif_perkler:
            t = pygame.time.get_ticks() / 1000.0
            for i in range(6):
                aci = math.radians(t * 180 + i * 60)
                rx = self.oyuncu.x + math.cos(aci) * 35 + ox
                ry = self.oyuncu.y + math.sin(aci) * 35 + oy
                pygame.draw.circle(ekran, (100, 200, 255), (int(rx), int(ry)), 4)

        for s in self.sayilar: s.ciz(ekran, self.font_sayi, self.font_sayi_b)

        # Karanlık Dalga Overlay
        if getattr(self.dalga_sis, "aktif_mod", None) and \
                self.dalga_sis.aktif_mod.get("efekt") == "karanlik":
            ekran.blit(self._karanlik_overlay, (0, 0))
            r = self._torch_r
            ekran.blit(self._torch_surface, (self.oyuncu.x - r + ox, self.oyuncu.y - r + oy))
            
        # Görev 42 — Harita Değiştirme Animasyonu
        if getattr(self, '_harita_gecis', 0) > 0:
            self._harita_gecis -= 0.016
            alpha = int(255 * (self._harita_gecis / 0.4))
            gecis = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
            gecis.fill((0, 0, 0, alpha))
            ekran.blit(gecis, (0, 0))
            
        # Görev 23 — Ultimate Ekran Flash Efekti
        if getattr(self.oyuncu, '_ult_flash', 0) > 0:
            self.oyuncu._ult_flash -= 0.016
            alpha = max(0, min(255, int(180 * self.oyuncu._ult_flash / 0.3)))
            flash = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
            flash.fill((255, 220, 0, alpha))
            ekran.blit(flash, (0, 0))

        self.hud.ciz(ekran, self.oyuncu, self.puan_sis, self.dalga_sis, self.perk_sis, self.zombiler)
        self.oyuncu.flash_ciz(ekran)
        for b in self.basarimlar:
            b.ciz(ekran, self.font_kucuk, self.font_hud, GENISLIK, YUKSEKLIK)
        self.gorev_sis.ciz_hud(ekran, self.font_hud, self.font_kucuk, GENISLIK, YUKSEKLIK)
        if self.perk_sis.secim_bekliyor:
            self.perk_sis.ciz_secim_ekrani(ekran, self.font_buyuk, self.font_hud, self.font_kucuk, GENISLIK, YUKSEKLIK)

    @property
    def oyuncu_oldu_mu(self): return self.bitti
    @property
    def dalga_bitti_mi(self): return self.dalga_sis.dalga_bitti
    @dalga_bitti_mi.setter
    def dalga_bitti_mi(self, val): self.dalga_sis.dalga_bitti = val
    @property
    def son_puan(self): return self.puan_sis.puan
    @property
    def dalga_no(self): return self.dalga_sis.dalga_no
    @property
    def yuksek_skorlar(self): return self.puan_sis.yuksek_skorlar

