import pygame
import math
from ayarlar import GENISLIK, YUKSEKLIK, YESIL

class Raycaster:
    def __init__(self, ekran):
        self.ekran = ekran
        self.fov = 75
        self.max_derinlik = 1500
        self.duvar_yuksekligi = 50000
        self.sway_x = 0
        self.sway_y = 0
        self.sway_time = 0
        
        # Zoom animasyonu
        self.zoom_hedef    = 1.0
        self.guncel_zoom   = 1.0  # Smooth lerp ile güncellenir
        self.zoom_hizi     = 8.0  # Lerp katsayısı
        self.overlay_alpha = 0    # Kapsam overlay alfa değeri (0→255 geçiş)
        
        # Harita Tanımı (T=200 boyutunda kareler)
        self.T = 200
        self.harita_data = {}
        
        # Basit bir arenamsı harita (Sınırlar ve sütunlar)
        for i in range(-20, 20):
            self.harita_data[(i, -20)] = 1
            self.harita_data[(i, 19)] = 1
            self.harita_data[(-20, i)] = 1
            self.harita_data[(19, i)] = 1
            
        # İçerideki Sütunlar
        self.harita_data[(5, 5)] = 2
        self.harita_data[(5, -5)] = 2
        self.harita_data[(-5, 5)] = 3
        self.harita_data[(-5, -5)] = 3
        
        self.z_buffer = [1e30] * GENISLIK

    def ciz(self, oyuncu, zombiler, mermiler, droplar):
        # Smooth Zoom Lerp (dt bağımsız yaklaşım — frame hızı farkı yok)
        self.zoom_hedef = oyuncu.guncel_zoom if hasattr(oyuncu, "guncel_zoom") else 1.0
        self.guncel_zoom += (self.zoom_hedef - self.guncel_zoom) * 0.18
        zoom_seviyesi = self.guncel_zoom
        guncel_fov = 75.0 / zoom_seviyesi
        
        # 1. Atmosfer (Gökyüzü ve Zemin)
        self.ekran.fill((5, 5, 10))
        for i in range(150):
            pygame.draw.circle(self.ekran, (200, 200, 255), (int(i*137)%GENISLIK, int(i*89)%(YUKSEKLIK//2)), 1)
        
        pygame.draw.circle(self.ekran, (240, 240, 255), (GENISLIK - 200, 150), 40)
        pygame.draw.circle(self.ekran, (5, 5, 10), (GENISLIK - 180, 150), 35)
        pygame.draw.rect(self.ekran, (2, 2, 5), (0, YUKSEKLIK//2 - 20, GENISLIK, 20))
        
        for i in range(0, YUKSEKLIK // 2, 4):
            v = int(10 + (i / (YUKSEKLIK/2)) * 30)
            pygame.draw.rect(self.ekran, (v, v, v + 5), (0, YUKSEKLIK // 2 + i, GENISLIK, 4))

        # 2. DDA Duvar Işın Atma (Raycasting)
        self._ciz_duvarlar(oyuncu, guncel_fov, zoom_seviyesi)

        # 3. Nesneleri Çiz (Billboard + Z-Buffer kontrolü)
        nesneler = []
        for z in zombiler:
            dist = math.hypot(z.x - oyuncu.x, z.y - oyuncu.y)
            if dist < self.max_derinlik: nesneler.append(("zombi", z, dist))
        for m in mermiler:
            dist = math.hypot(m.x - oyuncu.x, m.y - oyuncu.y)
            if dist < self.max_derinlik: nesneler.append(("mermi", m, dist))
        for d in droplar:
            dist = math.hypot(d.x - oyuncu.x, d.y - oyuncu.y)
            if dist < self.max_derinlik: nesneler.append(("drop", d, dist))

        nesneler.sort(key=lambda x: x[2], reverse=True)

        for tip, obj, dist in nesneler:
            rel_aci = math.atan2(obj.y - oyuncu.y, obj.x - oyuncu.x) - math.radians(oyuncu.aci)
            while rel_aci > math.pi: rel_aci -= 2 * math.pi
            while rel_aci < -math.pi: rel_aci += 2 * math.pi
            
            if abs(rel_aci) < math.radians(guncel_fov):
                ekran_x = int((0.5 * (rel_aci / math.radians(guncel_fov / 2)) + 0.5) * GENISLIK)
                
                # Z-Buffer kontrolü: Eğer obje duvarın arkasındaysa çizme
                if 0 <= ekran_x < GENISLIK and dist > self.z_buffer[ekran_x]:
                    continue
                
                proj_yuk = (self.duvar_yuksekligi / (max(5.0, dist))) * zoom_seviyesi
                
                if tip == "zombi":
                    img_w = min(GENISLIK * 4, int(obj.image.get_width() * (proj_yuk / 100)))
                    img_h = min(YUKSEKLIK * 4, int(obj.image.get_height() * (proj_yuk / 100)))
                    if img_w > 5 and img_h > 5:
                        scaled = pygame.transform.scale(obj.image, (img_w, img_h))
                        self.ekran.blit(scaled, (ekran_x - img_w // 2, YUKSEKLIK // 2 - img_h // 2))
                elif tip == "mermi":
                    size = max(2, int(2000 / (dist + 1)))
                    pygame.draw.circle(self.ekran, obj.renk, (ekran_x, YUKSEKLIK // 2), size)
                elif tip == "drop":
                    img_w = int(obj.image.get_width() * (proj_yuk / 80))
                    img_h = int(obj.image.get_height() * (proj_yuk / 80))
                    if img_w > 0 and img_h > 0:
                        scaled = pygame.transform.scale(obj.image, (img_w, img_h))
                        self.ekran.blit(scaled, (ekran_x - img_w // 2, YUKSEKLIK // 2 + 20))

        # 4. POV Silah ve Dürbün
        self._ciz_pov_silah(oyuncu, zoom_seviyesi)
        if zoom_seviyesi > 1.1:
            self._ciz_durbun_overlay(zoom_seviyesi)

    def _ciz_duvarlar(self, oyuncu, guncel_fov, zoom_seviyesi):
        sutun_gen = 4
        num_rays = GENISLIK // sutun_gen
        
        ray_angle = math.radians(oyuncu.aci - guncel_fov / 2)
        angle_step = math.radians(guncel_fov) / num_rays
        
        px, py = oyuncu.x / self.T, oyuncu.y / self.T
        
        for i in range(num_rays):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)
            
            mx, my = int(px), int(py)
            ray_dx, ray_dy = cos_a, sin_a
            
            delta_dist_x = abs(1 / ray_dx) if ray_dx != 0 else 1e30
            delta_dist_y = abs(1 / ray_dy) if ray_dy != 0 else 1e30
            
            if ray_dx < 0:
                step_x = -1
                side_dist_x = (px - mx) * delta_dist_x
            else:
                step_x = 1
                side_dist_x = (mx + 1.0 - px) * delta_dist_x
                
            if ray_dy < 0:
                step_y = -1
                side_dist_y = (py - my) * delta_dist_y
            else:
                step_y = 1
                side_dist_y = (my + 1.0 - py) * delta_dist_y
                
            hit = 0
            side = 0
            
            # Max iterasyon sınırlaması (derinlik)
            for _ in range(60):
                if side_dist_x < side_dist_y:
                    side_dist_x += delta_dist_x
                    mx += step_x
                    side = 0
                else:
                    side_dist_y += delta_dist_y
                    my += step_y
                    side = 1
                    
                if (mx, my) in self.harita_data:
                    hit = self.harita_data[(mx, my)]
                    break
                    
            if hit:
                if side == 0:
                    perp_wall_dist = (mx - px + (1 - step_x) / 2) / ray_dx
                else:
                    perp_wall_dist = (my - py + (1 - step_y) / 2) / ray_dy
                    
                # Balıkgözü düzeltmesi
                perp_wall_dist *= math.cos(math.radians(oyuncu.aci) - ray_angle)
                
                # Z-Buffer'a kaydet (Oyun dünyasındaki mesafeye çevirerek)
                gercek_mesafe = perp_wall_dist * self.T
                for w in range(sutun_gen):
                    if (i * sutun_gen + w) < GENISLIK:
                        self.z_buffer[i * sutun_gen + w] = gercek_mesafe
                
                if perp_wall_dist > 0.01:
                    line_height = int((YUKSEKLIK / perp_wall_dist) * zoom_seviyesi * 0.8)
                    
                    if hit == 1: color = (100, 100, 110)
                    elif hit == 2: color = (130, 60, 60)
                    else: color = (60, 130, 60)
                    
                    # Gölgeleme (Y/X yönüne göre)
                    if side == 1: color = (color[0]//2, color[1]//2, color[2]//2)
                    
                    rect_y = YUKSEKLIK // 2 - line_height // 2
                    pygame.draw.rect(self.ekran, color, (i * sutun_gen, rect_y, sutun_gen, line_height))
            else:
                for w in range(sutun_gen):
                    if (i * sutun_gen + w) < GENISLIK:
                        self.z_buffer[i * sutun_gen + w] = 1e30

            ray_angle += angle_step

    def _ciz_durbun_overlay(self, zoom):
        # Overlay geçiş alpha'sini animate et (zoom ne kadar büyükse o kadar opak)
        hedef_alpha = min(255, int((zoom - 1.0) / 5.0 * 255))
        self.overlay_alpha = int(self.overlay_alpha + (hedef_alpha - self.overlay_alpha) * 0.2)
        
        # Siyah kenarlar (Scope Mask)
        mask = pygame.Surface((GENISLIK, YUKSEKLIK), pygame.SRCALPHA)
        pygame.draw.rect(mask, (0, 0, 0, self.overlay_alpha), (0, 0, GENISLIK, YUKSEKLIK))
        
        # Ortadaki delik (Scope lens) — boyut zoom ile ters orantılı
        r = int(YUKSEKLIK * 0.42 - zoom * 8)
        r = max(80, r)
        pygame.draw.circle(mask, (0, 0, 0, 0), (GENISLIK // 2, YUKSEKLIK // 2), r)
        self.ekran.blit(mask, (0, 0))
        
        # Dürbün Kenarlık (metal halka)
        pygame.draw.circle(self.ekran, (80, 80, 90), (GENISLIK // 2, YUKSEKLIK // 2), r, 10)
        pygame.draw.circle(self.ekran, (140, 140, 150), (GENISLIK // 2, YUKSEKLIK // 2), r, 3)
        
        # Kıl Çizgileri (ince + kalın)
        c = GENISLIK // 2
        m = YUKSEKLIK // 2
        pygame.draw.line(self.ekran, (30, 30, 30), (c - r, m), (c + r, m), 4)
        pygame.draw.line(self.ekran, (30, 30, 30), (c, m - r), (c, m + r), 4)
        pygame.draw.line(self.ekran, (200, 200, 200), (c - r, m), (c + r, m), 1)
        pygame.draw.line(self.ekran, (200, 200, 200), (c, m - r), (c, m + r), 1)
        # Yatay mil çentikleri
        for i in range(1, 5):
            off = r * i // 5
            h = 12 if i % 2 == 0 else 6
            pygame.draw.line(self.ekran, (180, 180, 180), (c + off, m - h), (c + off, m + h), 2)
            pygame.draw.line(self.ekran, (180, 180, 180), (c - off, m - h), (c - off, m + h), 2)
        
        # Zoom Yazısı
        font = pygame.font.SysFont("Arial", 22, bold=True)
        txt = font.render(f"{zoom:.1f}x", True, (230, 230, 230))
        self.ekran.blit(txt, (c - txt.get_width() // 2, m + r + 14))

    def _ciz_pov_silah(self, oyuncu, zoom=1.0):
        zoom_offset = (zoom - 1.0) * 150
        silah_v = oyuncu.silah_verisi
        renk = silah_v["renk"]

        if oyuncu.hareket_ediyor_mu:
            self.sway_time += 0.15
            self.sway_x = math.sin(self.sway_time) * 20
            self.sway_y = abs(math.cos(self.sway_time)) * 15
        else:
            self.sway_x *= 0.9
            self.sway_y *= 0.9

        s_gen, s_yuk = 500, 500
        silah_surf = pygame.Surface((s_gen, s_yuk), pygame.SRCALPHA)
        
        pygame.draw.ellipse(silah_surf, (80, 60, 50), (-50, 350, 200, 300))
        pygame.draw.ellipse(silah_surf, (80, 60, 50), (350, 350, 200, 300))

        pygame.draw.rect(silah_surf, (20, 20, 25), (150, 250, 200, 250), border_radius=10)
        pygame.draw.rect(silah_surf, (10, 10, 12), (210, 50, 80, 250), border_radius=5)
        
        recoil = (oyuncu.ates_sayac / silah_v["ates_hizi"]) * 50 if oyuncu.ates_sayac > 0 else 0
        pygame.draw.circle(silah_surf, (*renk, 150 if recoil > 0 else 50), (250, 250), 60)
        
        pos_x = GENISLIK // 2 - s_gen // 2 + self.sway_x
        pos_y = YUKSEKLIK - s_yuk + 100 + self.sway_y + recoil + zoom_offset
        self.ekran.blit(silah_surf, (pos_x, pos_y))
        
        pygame.draw.circle(self.ekran, (255, 255, 255, 180), (GENISLIK // 2, YUKSEKLIK // 2), 4)
        pygame.draw.line(self.ekran, YESIL, (GENISLIK // 2 - 15, YUKSEKLIK // 2), (GENISLIK // 2 + 15, YUKSEKLIK // 2), 2)
        pygame.draw.line(self.ekran, YESIL, (GENISLIK // 2, YUKSEKLIK // 2 - 15), (GENISLIK // 2, YUKSEKLIK // 2 + 15), 2)
