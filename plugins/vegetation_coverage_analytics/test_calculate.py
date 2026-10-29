import unittest
import numpy as np
from calculate import generate_coverage_zonation, classify_coverage

class TestCalculateModule(unittest.TestCase):
    
    def setUp(self):
        """Fungsi ini otomatis jalan sebelum setiap test dimulai."""
        # Bikin dummy mask 10x10 (0 dan 1 acak)
        self.dummy_mask = np.random.randint(0, 2, (10, 10), dtype=np.uint8)
        self.dummy_bounds = [110.0, -7.0, 111.0, -6.0]
        self.dummy_threshold = {"low": 20, "medium_max": 50}

    def test_classify_coverage(self):
        """Test apakah klasifikasi low/medium/high berjalan benar."""
        self.assertEqual(classify_coverage(10, self.dummy_threshold), "low")
        self.assertEqual(classify_coverage(30, self.dummy_threshold), "medium")
        self.assertEqual(classify_coverage(80, self.dummy_threshold), "high")

    def test_generate_coverage_zonation_structure(self):
        """Test apakah struktur output zonasi sesuai format GeoJSON."""
        grid_size = 2
        hasil = generate_coverage_zonation(
            binary_mask=self.dummy_mask, 
            image_bounds=self.dummy_bounds, 
            grid_size=grid_size,
            threshold_dict=self.dummy_threshold
        )
        
        # 1. Pastikan outputnya dictionary dan formatnya FeatureCollection
        self.assertIsInstance(hasil, dict)
        self.assertEqual(hasil["type"], "FeatureCollection")
        
        # 2. Pastikan jumlah kotak (features) sesuai. 2x2 grid = 4 kotak
        self.assertEqual(len(hasil["features"]), 4)
        
        # 3. Cek isi salah satu kotak
        feature_pertama = hasil["features"][0]
        self.assertEqual(feature_pertama["type"], "Feature")
        self.assertEqual(feature_pertama["geometry"]["type"], "Polygon")
        
        # 4. Pastikan atribut perhitungan masuk
        properties = feature_pertama["properties"]
        self.assertIn("coverage_percentage", properties)
        self.assertIn("classification", properties)

if __name__ == '__main__':
    # 1. Jalankan unit test dulu
    unittest.main(exit=False)

    # 2. Cetak output asli untuk dilihat mata manusia
    print("\n=== LIHAT OUTPUT ASLINYA ===")
    import json
    dummy_mask = np.random.randint(0, 2, (10, 10), dtype=np.uint8)
    dummy_bounds = [110.0, -7.0, 111.0, -6.0]
    
    # Panggil fungsinya (Grid 2x2)
    hasil = generate_coverage_zonation(dummy_mask, dummy_bounds, grid_size=2)
    
    # Print hasilnya dengan format JSON yang cantik
    print(json.dumps(hasil, indent=2))