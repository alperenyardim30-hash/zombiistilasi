import unittest
from ayarlar import SILAHLAR, TEMEL_SILAHLAR, SILAH_SIRASI
from sistemler.dalga_sistemi import DalgaSistemi
import pygame


class TestZombiIstilasi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Pygame init for sprite groups
        pygame.init()

    def test_silah_olusturma(self):
        """60 silahın tamamı SILAHLAR sözlüğüne eklenmiş olmalı."""
        # Tabanca dahil TEMEL_SILAHLAR kadar silah olmalı
        beklenen = len(TEMEL_SILAHLAR)
        self.assertEqual(
            len(SILAHLAR), beklenen,
            f"Beklenen {beklenen} silah var, ama {len(SILAHLAR)} silah oluşturulmuş."
        )

        # Tabanca her zaman var ve ücretsiz olmalı
        self.assertIn("tabanca", SILAHLAR, "Tabanca silah listesinde bulunamadı.")
        self.assertEqual(SILAHLAR["tabanca"]["fiyat"], 0, "Tabanca ücretsiz olmalı.")

        # Kapasite -1 olan silahın mermisi sonsuz olmalı
        self.assertEqual(SILAHLAR["tabanca"]["kapasite"], -1, "Tabanca sonsuz mermili olmalı.")

        # AK-47 temel kontrol
        ak = SILAHLAR.get("ak47")
        self.assertIsNotNone(ak, "ak47 silahı bulunamadı.")
        self.assertGreater(ak["hasar"], 0, "ak47 hasarı sıfırdan büyük olmalı.")
        self.assertIn("renk", ak, "ak47 renk bilgisi eksik.")

        # Efsanevi silahların hasar sıralaması
        the_end = SILAHLAR.get("the_end")
        tabanca = SILAHLAR.get("tabanca")
        self.assertIsNotNone(the_end, "the_end silahı bulunamadı.")
        self.assertGreater(the_end["hasar"], tabanca["hasar"], "The End tabancadan güçlü olmalı.")

        # Tüm silahların zorunlu alanları mevcut
        zorunlu_alanlar = {"isim", "hasar", "ates_hizi", "mermi_hizi", "renk", "tip", "kapasite"}
        for s_key, s_veri in SILAHLAR.items():
            eksik = zorunlu_alanlar - set(s_veri.keys())
            self.assertEqual(
                len(eksik), 0,
                f"'{s_key}' silahında eksik alan(lar): {eksik}"
            )

    def test_silah_sirasi(self):
        """SILAH_SIRASI listesi SILAHLAR sözlüğüyle tutarlı olmalı."""
        self.assertIn("tabanca", SILAH_SIRASI, "Tabanca sıralamasında yok.")
        self.assertEqual(
            SILAH_SIRASI[0], "tabanca",
            "İlk silah tabanca olmalı."
        )
        for s_key in SILAH_SIRASI:
            self.assertIn(
                s_key, SILAHLAR,
                f"'{s_key}' SILAH_SIRASI'nda var ama SILAHLAR'da yok."
            )

    def test_dalga_hesaplama(self):
        """Dalga sistemi doğru zombi sayısı ve zorluk artışı üretmeli."""
        zombiler = pygame.sprite.Group()
        dalga_sis = DalgaSistemi(zombiler)

        # İlk dalga boş olmamalı
        liste_1 = dalga_sis._dalga_olustur(1)
        self.assertTrue(len(liste_1) > 0, "1. dalga boş!")

        # Zorluk arttıkça çarpan artmalı
        eski_zorluk = dalga_sis.zorluk_carpani
        dalga_sis._yeni_dalga_baslat(1920, 1080)
        self.assertGreater(
            dalga_sis.zorluk_carpani, eski_zorluk,
            "Dalga arttıkça zorluk çarpanı artmıyor."
        )

        # 10. dalga 1. dalgadan kalabalık olmalı
        liste_10 = dalga_sis._dalga_olustur(10)
        self.assertGreater(
            len(liste_10), len(liste_1),
            "10. dalga 1. dalgadan daha kalabalık değil."
        )

    def test_boss_dalgasi(self):
        """Her 5. dalga boss içermeli."""
        zombiler = pygame.sprite.Group()
        dalga_sis = DalgaSistemi(zombiler)
        liste_5 = dalga_sis._dalga_olustur(5)
        self.assertIn("boss", liste_5, "5. dalga boss içermiyor.")

    def test_zombie_tipleri(self):
        """Tüm zombi tipleri geçerli alanlara sahip olmalı."""
        from ayarlar import ZOMBI_TIPLER
        zorunlu = {"hiz", "can", "hasar", "skor", "para", "r", "renk", "ic"}
        for tip, veri in ZOMBI_TIPLER.items():
            eksik = zorunlu - set(veri.keys())
            self.assertEqual(len(eksik), 0, f"'{tip}' zombisinde eksik alan: {eksik}")


if __name__ == '__main__':
    unittest.main()
