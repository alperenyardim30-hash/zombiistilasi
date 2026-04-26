# ============================================================
#  ekranlar/oyun_ekrani.py — Nişangah Konisi (Aim Cone) ve Devasa Grafikler
# ============================================================
import pygame
import math
import random
from ayarlar import (
    GENISLIK, YUKSEKLIK, ARKAPLAN, BEYAZ, SIYAH, KIRMIZI, YESIL, SARI, ALTIN, 
    SILAHLAR, SILAH_SIRASI, ZIRH_MAVI, CAMGOBEGI, PEMBE, MOR, TURUNCU
)
from varliklar.oyuncu  import Oyuncu
from varliklar.zombi   import Zombi
from varliklar.drop    import Drop
from varliklar.patlama import Patlama
from varliklar.parcacik import kan_parcaciklari, HarasarSayisi, BasarimBildirimi
from varliklar.isik import AnlikIsin
from sistemler.dalga_sistemi import DalgaSistemi
from sistemler.puan_sistemi  import PuanSistemi
from sistemler.perk_sistemi  import PerkSistemi
from sistemler.gorev_sistemi import GorevSistemi

class OyunEkrani:
    def __init__(self):
        self.font_hud    = pygame.font.SysFont("Consolas", 18, bold=True)
        self.font_buyuk  = pygame.font.SysFont("Consolas", 46, bold=True)
        self.font_kucuk  = pygame.font.SysFont("Consolas", 15, bold=True)
        self.font_sayi   = pygame.font.SysFont("Impact", 18)
        self.font_sayi_b = pygame.font.SysFont("Impact", 32)
        self.font_mermi  = pygame.font.SysFont("Impact", 56)
        
        # Grafik iyileştirme: Zemin Detayları (Kan ve Enkaz)
        self._zemin = []
        for _ in range(300):
            r = random.choice([2, 3, 5])
            c = random.choice([(30, 35, 40), (20, 25, 30), (45, 25, 25)]) # Kırmızımsı lekeler ve gri taşlar
            self._zemin.append((random.randint(-200, GENISLIK + 200), random.randint(-200, YUKSEKLIK + 200), r, c))

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
        self.gorev_sis.yeni_gorev_sec()
        
        self.sarsinti    = 0.0
        self.bitti       = False
        self.son_fare_pos = (0, 0)

    def baslat(self):
        self._sifirla()

    def harita_degistir(self):
        self.aktif_harita = (self.aktif_harita + 1) % len(self.haritalar)



    def guncelle(self, dt, tuslar, fare_pos):
        if self.bitti: return
        
        self.son_fare_pos = fare_pos
        self.oyuncu.update(dt, tuslar, fare_pos, self.mermiler, GENISLIK, YUKSEKLIK, False)
        self.mermiler.update(dt, GENISLIK, YUKSEKLIK)
        self.puan_sis.update(dt)

        # Raycast silah kuyrugunu isle
        for rc in self.oyuncu.raycast_kuyrugu:
            self._isle_raycast(rc)
        self.oyuncu.raycast_kuyrugu.clear()

        # Anlik isinlari guncelle
        self.anlik_isinlar = [i for i in self.anlik_isinlar if i.update(dt)]


        for zh in self.zehir_havuzlari[:]:
            zh[3] -= dt
            if zh[3] <= 0:
                self.zehir_havuzlari.remove(zh)
            elif math.hypot(zh[0] - self.oyuncu.x, zh[1] - self.oyuncu.y) < (zh[2] + self.oyuncu.yari_cap):
                self.oyuncu.zombi_temas(dt, 5)

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
                if z.tip == "patlayan":
                    self.patlamalar.append(Patlama(z.x, z.y, 120))
                    self.oyuncu.hasar_al(40)
                    z.kill()
                    self.sarsinti = 0.3
                else:
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
                        self.patlamalar.append(Patlama(m.x, m.y, m.patlama_r))
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
                self.patlamalar.append(Patlama(m.x, m.y, m.patlama_r))

        for p in self.patlamalar[:]:
            p.update(dt)
            if not p.hasar_verildi:
                oldukler = p.zombi_hasari_ver(self.zombiler, self.oyuncu.hasar_carpani * p.r * 1.5)
                for z in oldukler:
                    self.sayilar.append(HarasarSayisi(z.x, z.y, self.oyuncu.hasar_carpani * p.r * 1.5, SARI, True))
                    self._zombi_oldu(z)
            if p.bitti_mi:
                self.patlamalar.remove(p)

        for d in list(self.droplar):
            d.update(dt)
            if d.alive() and d.oyuncuya_dokunan(self.oyuncu.x, self.oyuncu.y, self.oyuncu.yari_cap):
                if d.tip == "can":
                    self.oyuncu.can_doldur(40)
                    self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, 40, YESIL, True))
                elif d.tip == "mermi":
                    self.oyuncu.aktif_mermi_doldur()
                    self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, "+Mermi!", SARI, True))
                d.kill()

        self.parcaciklar = [p for p in self.parcaciklar if p.update(dt)]
        self.sayilar = [s for s in self.sayilar if s.update(dt)]
        self.basarimlar = [b for b in self.basarimlar if b.update(dt)]
        
        if self.puan_sis.yeni_seviye_flag:
            self.puan_sis.yeni_seviye_flag = False
            self.basarimlar.append(BasarimBildirimi(f"SEVİYE {self.puan_sis.seviye}!", "Tüm istatistiklerin artıyor!"))

        if self.oyuncu.yoruldu_mu and not getattr(self, "_yoruldu_bildirildi", False):
            self._yoruldu_bildirildi = True
            self.sayilar.append(HarasarSayisi(self.oyuncu.x, self.oyuncu.y, "Yoruldum!", KIRMIZI))
        elif not self.oyuncu.yoruldu_mu:
            self._yoruldu_bildirildi = False

        if self.sarsinti > 0: self.sarsinti -= dt
        self.dalga_sis.guncelle(dt, GENISLIK, YUKSEKLIK)
        self.gorev_sis.guncelle(dt, self.puan_sis)

    def _zombi_oldu(self, z, patlama_mi=False):
        if not z.alive(): return
        if z.tip == "patlayan":
            self.patlamalar.append(Patlama(z.x, z.y, 120))
            if z.patlama_hasar_mesafe(self.oyuncu.x, self.oyuncu.y) < 120 + self.oyuncu.yari_cap:
                self.oyuncu.hasar_al(40)
                
        self.parcaciklar.extend(kan_parcaciklari(z.x, z.y, 18))
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
        drop = z.drop_olustur()
        if drop: self.droplar.add(drop)
        z.kill()

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
        hasar = veri["hasar"] * rc["carpan"] * self.oyuncu.hasar_carpani
        renk = veri["renk"]

        # Isin uzunlugu
        uzunluk = min(GENISLIK + YUKSEKLIK, veri.get("mermi_hizi", 1400))
        aci_rad = math.radians(aci)
        bx = x + math.cos(aci_rad) * uzunluk
        by = y + math.sin(aci_rad) * uzunluk

        # Tum zombileri kontrol et — isabededenler hasar alir
        for z in list(self.zombiler):
            if not z.alive():
                continue
            uzaklik = self._nokta_cizgiye_uzaklik(z.x, z.y, x, y, bx, by)
            if uzaklik < z.yari_cap + 3:
                z.can -= hasar
                z.hit_sayac = 0.12
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
            
        for (px, py, pr, pcolor) in self._zemin:
            pygame.draw.circle(ekran, pcolor, (px + ox, py + oy), pr)
            
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
        for isin in self.anlik_isinlar:
            isin.ciz(ekran)

        for z in self.zombiler: ekran.blit(z.image, (z.rect.x + ox, z.rect.y + oy))
        for z in self.zombiler: z.can_bar_ciz(ekran)

        ekran.blit(self.oyuncu.image, (self.oyuncu.rect.x + ox, self.oyuncu.rect.y + oy))
        
        for s in self.sayilar: s.ciz(ekran, self.font_sayi, self.font_sayi_b)

        # Karanlık Dalga Overlay
        if getattr(self.dalga_sis, "aktif_mod", None) and \
                self.dalga_sis.aktif_mod.get("efekt") == "karanlik":
            karanlik = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
            karanlik.fill((0, 0, 0, 155))
            ekran.blit(karanlik, (0, 0))
            # Oyuncu etrafında bir projektif ışık dairesi bırak
            r = 200
            torch = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            for dr in range(r, 0, -4):
                a = int(155 * (1 - dr/r) ** 2)
                pygame.draw.circle(torch, (0, 0, 0, 155 - a), (r, r), dr)
            ekran.blit(torch, (self.oyuncu.x - r + ox, self.oyuncu.y - r + oy))

        # 2D/3D ve Harita ipucu metni
        ipucu = self.font_kucuk.render(
            f"3: 2D/3D  |  M: Harita ({aktif_harita['isim']})",
            True,
            (200, 200, 200),
        )
        ekran.blit(ipucu, (GENISLIK - ipucu.get_width() - 20, YUKSEKLIK - ipucu.get_height() - 20))

        self._ciz_hud(ekran)
        self._ciz_bildirim(ekran)
        self._ciz_silah_bar(ekran)
        self.oyuncu.flash_ciz(ekran)
        
        for b in self.basarimlar: b.ciz(ekran, self.font_kucuk, self.font_hud, GENISLIK, YUKSEKLIK)
        
        # Görev HUD (sağ üst)
        self.gorev_sis.ciz_hud(ekran, self.font_hud, self.font_kucuk, GENISLIK, YUKSEKLIK)
        
        # Perk seçim ekranı (varsa üstte çiz)
        if self.perk_sis.secim_bekliyor:
            self.perk_sis.ciz_secim_ekrani(ekran, self.font_buyuk, self.font_hud, self.font_kucuk, GENISLIK, YUKSEKLIK)

    def _ciz_hud(self, ekran):
        pygame.draw.rect(ekran, (10, 10, 15, 200), (20, 20, 300, 140), border_radius=12)
        pygame.draw.rect(ekran, (50, 50, 60), (20, 20, 300, 140), 2, border_radius=12)
        
        bx, by, bg, byk = 30, 30, 280, 16
        
        # 1. Can
        c_oran = self.oyuncu.can / self.oyuncu.max_can_degeri
        pygame.draw.rect(ekran, (60, 0, 0), (bx, by, bg, byk), border_radius=6)
        if c_oran > 0: pygame.draw.rect(ekran, (220, 50, 50), (bx, by, int(bg * c_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"HP: {int(self.oyuncu.can)}", True, BEYAZ), (bx + 8, by))
        
        # 2. Kalkan
        by += 22
        k_oran = self.oyuncu.kalkan / self.oyuncu.max_kalkan_degeri
        pygame.draw.rect(ekran, (0, 30, 80), (bx, by, bg, byk), border_radius=6)
        if k_oran > 0: pygame.draw.rect(ekran, ZIRH_MAVI, (bx, by, int(bg * k_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"SH: {int(self.oyuncu.kalkan)}", True, BEYAZ), (bx + 8, by))

        # 3. Stamina
        by += 22
        s_oran = self.oyuncu.stamina / self.oyuncu.max_stamina_degeri
        pygame.draw.rect(ekran, (60, 60, 60), (bx, by, bg, byk), border_radius=6)
        if s_oran > 0: pygame.draw.rect(ekran, (255, 255, 100), (bx, by, int(bg * s_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"STM: {int(self.oyuncu.stamina)}", True, SIYAH if s_oran > 0.5 else BEYAZ), (bx + 8, by))

        # 4. XP
        by += 22
        xp_oran = self.puan_sis.xp / self.puan_sis.xp_hedef
        pygame.draw.rect(ekran, (40, 40, 40), (bx, by, bg, byk), border_radius=6)
        if xp_oran > 0: pygame.draw.rect(ekran, MOR, (bx, by, int(bg * xp_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render(f"SV: {self.puan_sis.seviye}", True, BEYAZ), (bx + 8, by))
        
        # 5. Ultimate
        by += 22
        u_oran = 1.0 - (self.oyuncu.ult_bekleme / self.oyuncu.ult_max_cd)
        pygame.draw.rect(ekran, (40, 40, 0), (bx, by, bg, byk), border_radius=6)
        if u_oran > 0: pygame.draw.rect(ekran, SARI, (bx, by, int(bg * u_oran), byk), border_radius=6)
        ekran.blit(self.font_kucuk.render("ULT [BOŞLUK]" if u_oran >= 1.0 else f"ULT: {self.oyuncu.ult_bekleme:.1f}s", True, SIYAH if u_oran >= 1.0 else BEYAZ), (bx + bg//2 - 45, by))

        # Sağ üst panel
        pygame.draw.rect(ekran, (10, 10, 15, 200), (GENISLIK - 240, 20, 220, 110), border_radius=12)
        pygame.draw.rect(ekran, (50, 50, 60), (GENISLIK - 240, 20, 220, 110), 2, border_radius=12)
        
        st = self.font_hud.render(f"PUAN: {self.puan_sis.puan}", True, BEYAZ)
        ekran.blit(st, (GENISLIK - st.get_width() - 35, 30))
        pt = self.font_hud.render(f"PARA: {self.puan_sis.para}$", True, ALTIN)
        ekran.blit(pt, (GENISLIK - pt.get_width() - 35, 60))
        dt2 = self.font_hud.render(f"DALGA: {self.dalga_sis.dalga_no}", True, (180, 255, 180))
        ekran.blit(dt2, (GENISLIK - dt2.get_width() - 35, 90))

        # Sağ alt panel - MERMİ GÖSTERGESİ (Büyütüldü)
        ak = self.oyuncu.aktif_silah
        mermi = self.oyuncu.mermiler.get(ak, -1)
        kapasite = self.oyuncu._silah_max_mermi(ak)
        
        m_metin = "∞" if kapasite == -1 else f"{mermi}/{kapasite}"
        renk = KIRMIZI if mermi == 0 else (SARI if mermi < kapasite * 0.3 else BEYAZ)
        
        pygame.draw.rect(ekran, (10, 10, 15, 200), (GENISLIK - 260, YUKSEKLIK - 120, 240, 100), border_radius=15)
        pygame.draw.rect(ekran, (50, 50, 60), (GENISLIK - 260, YUKSEKLIK - 120, 240, 100), 2, border_radius=15)
        
        t = self.font_mermi.render(m_metin, True, renk)
        ekran.blit(t, (GENISLIK - 140 - t.get_width()//2, YUKSEKLIK - 105))
        
        silah_isim = SILAHLAR[ak]["isim"]
        sit = self.font_kucuk.render(silah_isim, True, SILAHLAR[ak]["renk"])
        ekran.blit(sit, (GENISLIK - 140 - sit.get_width()//2, YUKSEKLIK - 45))

        # Combo
        if self.puan_sis.combo > 1:
            cx = GENISLIK // 2
            cy = 80
            ct = self.font_buyuk.render(f"{self.puan_sis.combo}x COMBO!", True, TURUNCU)
            ekran.blit(ct, (cx - ct.get_width() // 2, cy))

    def _ciz_silah_bar(self, ekran):
        bar_yuk = 80
        bar_y = YUKSEKLIK - bar_yuk - 20
        
        kart_gen, bosluk = 80, 10
        sahip = [k for k in SILAH_SIRASI if k in self.oyuncu.envanter]
        
        # Çok fazla silah varsa ekranın altına sığmayabilir, sadece seçili silaha en yakın olanları çizebiliriz.
        # Ya da basitçe hepsini çizelim (1920 ekranda 20-25 silah sığar).
        gosterilecek = sahip[-15:] # Ekrana sığması için son 15 silah
        
        toplam_gen = len(gosterilecek) * (kart_gen + bosluk) - bosluk
        start_x = GENISLIK // 2 - toplam_gen // 2
        
        # Arkaplan
        pygame.draw.rect(ekran, (10, 10, 15, 200), (start_x - 10, bar_y - 10, toplam_gen + 20, bar_yuk + 20), border_radius=15)

        for i, key in enumerate(gosterilecek):
            veri = SILAHLAR[key]
            aktif = self.oyuncu.aktif_silah == key
            kx, ky, kh = start_x + i * (kart_gen + bosluk), bar_y, bar_yuk

            bg = (50, 80, 50) if aktif else (30, 30, 40)
            border = veri["renk"] if aktif else (80, 80, 80)
            
            if aktif:
                hale = pygame.Surface((kart_gen+10, kh+10), pygame.SRCALPHA)
                pygame.draw.rect(hale, (*veri["renk"], 80), (0, 0, kart_gen+10, kh+10), border_radius=12)
                ekran.blit(hale, (kx-5, ky-5))

            pygame.draw.rect(ekran, bg, (kx, ky, kart_gen, kh), border_radius=10)
            pygame.draw.rect(ekran, border, (kx, ky, kart_gen, kh), 2, border_radius=10)

            pygame.draw.circle(ekran, veri["renk"], (kx + kart_gen//2, ky + 25), 12)
            isim_t = self.font_kucuk.render(veri["isim"][:9], True, BEYAZ if aktif else (160, 160, 160))
            ekran.blit(isim_t, (kx + kart_gen//2 - isim_t.get_width()//2, ky + 45))

    def _ciz_bildirim(self, ekran):
        metin, kalan = self.dalga_sis.bildirim_goster()
        if not metin: return
        alpha = min(255, int(255 * (kalan / 2.5)))
        surf = self.font_buyuk.render(metin, True, (255, 100, 100) if "BOSS" in metin else SARI)
        surf.set_alpha(alpha)
        ekran.blit(surf, (GENISLIK // 2 - surf.get_width() // 2, YUKSEKLIK // 2 - 120))

    @property
    def oyuncu_oldu_mu(self): return self.bitti
    @property
    def dalga_bitti_mi(self): return self.dalga_sis.dalga_bitti
    @property
    def son_puan(self): return self.puan_sis.puan
    @property
    def dalga_no(self): return self.dalga_sis.dalga_no
    @property
    def yuksek_skorlar(self): return self.puan_sis.yuksek_skorlar
