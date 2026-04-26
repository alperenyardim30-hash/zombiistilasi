import unittest
from ayarlar import SILAHLAR, ZORLUK_CARPANI, TEMEL_SILAHLAR, ELEMENTLER
from sistemler.dalga_sistemi import DalgaSistemi
import pygame

class TestZombiIstilasi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Pygame init for sprite groups
        pygame.init()
        
    def test_silah_olusturma(self):
        # Tabanca hariç, temel silah * element sayısı kadar kombinasyon
        kombinasyon_sayisi = (len(TEMEL_SILAHLAR) - 1) * len(ELEMENTLER) + 1
        self.assertEqual(len(SILAHLAR), kombinasyon_sayisi, f"Beklenen {kombinasyon_sayisi} silah oluşturulmamış.")
        
        # Test: Ak47 Zehirli
        ak_zehir = SILAHLAR.get("ak47_zehir")
        self.assertIsNotNone(ak_zehir, "ak47_zehir silahı bulunamadı.")
        self.assertEqual(ak_zehir["efekt"], "zehir")
        self.assertEqual(ak_zehir["tip"], "normal")
        
    def test_dalga_hesaplama(self):
        zombiler = pygame.sprite.Group()
        dalga_sis = DalgaSistemi(zombiler)
        
        # İlk dalga
        liste_1 = dalga_sis._dalga_olustur(1)
        self.assertTrue(len(liste_1) > 0, "1. dalga boş!")
        
        # Zorluk kontrolü
        eski_zorluk = ZORLUK_CARPANI
        dalga_sis._yeni_dalga_baslat(1920, 1080)
        import ayarlar
        self.assertGreater(ayarlar.ZORLUK_CARPANI, eski_zorluk, "Dalga arttıkça zorluk çarpanı artmıyor.")
        
        # İleri dalga
        liste_10 = dalga_sis._dalga_olustur(10)
        self.assertGreater(len(liste_10), len(liste_1), "10. dalga 1. dalgadan daha kalabalık değil.")

if __name__ == '__main__':
    unittest.main()
