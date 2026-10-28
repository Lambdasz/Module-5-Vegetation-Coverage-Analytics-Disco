import unittest
import numpy as np
import sys
import os

# Tambahkan direktori plugin ke path agar bisa import calculate
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculate import calculate_vegetation_coverage, classify_coverage


class TestVegetationCoverage(unittest.TestCase):
    def test_all_vegetation(self):
        """Uji masker serba vegetasi (100%)."""
        mask = np.ones((10, 10), dtype=np.uint8)
        result = calculate_vegetation_coverage(mask, gsd=0.1)

        self.assertEqual(result["total_pixels"], 100)
        self.assertEqual(result["vegetation_pixels"], 100)
        self.assertEqual(result["coverage_percentage"], 100.0)
        self.assertAlmostEqual(result["vegetation_area_sqm"], 1.0)  # 100 * 0.01 = 1.0 m²
        self.assertAlmostEqual(result["total_area_sqm"], 1.0)

    def test_zero_vegetation(self):
        """Uji masker tanpa vegetasi (0%)."""
        mask = np.zeros((10, 10), dtype=np.uint8)
        result = calculate_vegetation_coverage(mask, gsd=0.2)

        self.assertEqual(result["total_pixels"], 100)
        self.assertEqual(result["vegetation_pixels"], 0)
        self.assertEqual(result["coverage_percentage"], 0.0)
        self.assertAlmostEqual(result["vegetation_area_sqm"], 0.0)
        self.assertAlmostEqual(result["total_area_sqm"], 4.0)  # 100 * 0.04 = 4.0 m²

    def test_partial_vegetation_and_255_format(self):
        """Uji masker sebagian dengan nilai 255 (format standar mask citra)."""
        mask = np.zeros((20, 20), dtype=np.uint8)
        mask[:10, :] = 255  # Separuh bernilai 255 (50%)
        result = calculate_vegetation_coverage(mask, gsd=0.5)

        self.assertEqual(result["total_pixels"], 400)
        self.assertEqual(result["vegetation_pixels"], 200)
        self.assertEqual(result["coverage_percentage"], 50.0)
        self.assertAlmostEqual(result["vegetation_area_sqm"], 50.0)  # 200 * 0.25 = 50.0 m²

    def test_gsd_none_fallback(self):
        """Uji mitigasi risiko: jika GSD None, area bernilai None tanpa error."""
        mask = np.ones((5, 5), dtype=np.uint8)
        result = calculate_vegetation_coverage(mask, gsd=None)

        self.assertEqual(result["coverage_percentage"], 100.0)
        self.assertIsNone(result["vegetation_area_sqm"])
        self.assertIsNone(result["total_area_sqm"])

    def test_invalid_mask_dimensions(self):
        """Uji validasi bahwa mask harus 2 dimensi."""
        with self.assertRaises(ValueError):
            calculate_vegetation_coverage(np.array([1, 0, 1]))


class TestClassifyCoverage(unittest.TestCase):
    def test_default_thresholds(self):
        """Uji klasifikasi dengan threshold default (low<=30, medium<=70, high>70)."""
        self.assertEqual(classify_coverage(15.0), "low")
        self.assertEqual(classify_coverage(30.0), "low")
        self.assertEqual(classify_coverage(50.0), "medium")
        self.assertEqual(classify_coverage(70.0), "medium")
        self.assertEqual(classify_coverage(85.0), "high")

    def test_custom_thresholds_with_medium_max_key(self):
        """Uji kompatibilitas dengan format threshold dari Radit (medium_max)."""
        custom_th = {"low": 20.0, "medium_max": 50.0}
        self.assertEqual(classify_coverage(10.0, custom_th), "low")
        self.assertEqual(classify_coverage(20.0, custom_th), "low")
        self.assertEqual(classify_coverage(35.0, custom_th), "medium")
        self.assertEqual(classify_coverage(50.0, custom_th), "medium")
        self.assertEqual(classify_coverage(60.0, custom_th), "high")


if __name__ == "__main__":
    unittest.main()
