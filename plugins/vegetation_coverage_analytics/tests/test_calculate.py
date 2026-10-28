import os
import sys
import tempfile
import unittest
import numpy as np
from PIL import Image

# Tambahkan direktori plugin ke path agar modul calculate dapat diimpor
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from calculate import (
    binarize_array,
    calculate_vegetation_coverage,
    classify_coverage,
    load_mask,
    parse_image_to_grayscale,
)


class TestPureTransformations(unittest.TestCase):
    """Pengujian fungsi-fungsi murni (pure functions) transformasi citra."""

    def test_parse_image_to_grayscale_rgb(self):
        """Memastikan konversi citra RGB menjadi grayscale 2D array uint8."""
        img = Image.new("RGB", (8, 8), color=(255, 0, 0))
        gray = parse_image_to_grayscale(img)
        self.assertEqual(gray.shape, (8, 8))
        self.assertEqual(gray.dtype, np.uint8)

    def test_parse_image_to_grayscale_rgba(self):
        """Memastikan konversi citra RGBA menjadi grayscale 2D array uint8."""
        img = Image.new("RGBA", (10, 5), color=(0, 255, 0, 128))
        gray = parse_image_to_grayscale(img)
        self.assertEqual(gray.shape, (5, 10))
        self.assertEqual(gray.dtype, np.uint8)

    def test_binarize_array_adaptive_0_1(self):
        """Memastikan array yang sudah berformat {0, 1} dipertahankan."""
        raw = np.array([[0, 1], [1, 0]], dtype=np.uint8)
        bin_arr = binarize_array(raw)
        self.assertTrue(np.array_equal(raw, bin_arr))
        self.assertEqual(bin_arr.dtype, np.uint8)

    def test_binarize_array_adaptive_0_255(self):
        """Memastikan array format standar mask PNG (0 dan 255) dipetakan ke {0, 1}."""
        raw = np.array([[0, 255], [255, 0]], dtype=np.uint8)
        expected = np.array([[0, 1], [1, 0]], dtype=np.uint8)
        bin_arr = binarize_array(raw)
        self.assertTrue(np.array_equal(expected, bin_arr))

    def test_binarize_array_custom_threshold(self):
        """Memastikan ambang batas kustom bekerja sesuai kaidah fungsional."""
        raw = np.array([[50, 100], [150, 200]], dtype=np.uint8)
        # Threshold 120: <= 120 jadi 0, > 120 jadi 1
        expected = np.array([[0, 0], [1, 1]], dtype=np.uint8)
        bin_arr = binarize_array(raw, threshold=120)
        self.assertTrue(np.array_equal(expected, bin_arr))


class TestLoadMask(unittest.TestCase):
    """Pengujian boundary I/O pembacaan berkas citra mask."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_mask_valid_png(self):
        """Memastikan citra mask PNG nyata dapat dibaca dan dikonversi ke array {0, 1}."""
        test_path = os.path.join(self.temp_dir.name, "mask_test.png")
        # Buat citra 10x10: separuh hitam (0), separuh putih (255)
        raw_arr = np.zeros((10, 10), dtype=np.uint8)
        raw_arr[:5, :] = 255
        Image.fromarray(raw_arr).save(test_path)

        loaded = load_mask(test_path)
        self.assertEqual(loaded.shape, (10, 10))
        self.assertEqual(loaded.dtype, np.uint8)
        # Separuh harus bernilai 1 (vegetasi), separuh 0 (non-vegetasi)
        self.assertEqual(np.count_nonzero(loaded == 1), 50)
        self.assertEqual(np.count_nonzero(loaded == 0), 50)

    def test_load_mask_file_not_found(self):
        """Memastikan melempar FileNotFoundError jika file tidak ada di disk."""
        non_existent = os.path.join(self.temp_dir.name, "ghost_mask.png")
        with self.assertRaises(FileNotFoundError):
            load_mask(non_existent)

    def test_load_mask_empty_path(self):
        """Memastikan melempar ValueError jika path string kosong."""
        with self.assertRaises(ValueError):
            load_mask("   ")


class TestVegetationCoverage(unittest.TestCase):
    """Pengujian perhitungan persentase tutupan dan luas m²."""

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
        self.assertAlmostEqual(result["total_area_sqm"], 4.0)

    def test_partial_vegetation_and_255_format(self):
        """Uji masker sebagian dengan format nilai 255."""
        mask = np.zeros((20, 20), dtype=np.uint8)
        mask[:10, :] = 255  # 50% vegetasi
        result = calculate_vegetation_coverage(mask, gsd=0.5)

        self.assertEqual(result["total_pixels"], 400)
        self.assertEqual(result["vegetation_pixels"], 200)
        self.assertEqual(result["coverage_percentage"], 50.0)
        self.assertAlmostEqual(result["vegetation_area_sqm"], 50.0)

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
    """Pengujian klasifikasi tutupan vegetasi."""

    def test_default_thresholds(self):
        """Uji klasifikasi dengan threshold default."""
        self.assertEqual(classify_coverage(15.0), "low")
        self.assertEqual(classify_coverage(30.0), "low")
        self.assertEqual(classify_coverage(50.0), "medium")
        self.assertEqual(classify_coverage(70.0), "medium")
        self.assertEqual(classify_coverage(85.0), "high")

    def test_custom_thresholds_with_medium_max_key(self):
        """Uji kompatibilitas dengan format threshold eksperimen (medium_max)."""
        custom_th = {"low": 20.0, "medium_max": 50.0}
        self.assertEqual(classify_coverage(10.0, custom_th), "low")
        self.assertEqual(classify_coverage(20.0, custom_th), "low")
        self.assertEqual(classify_coverage(35.0, custom_th), "medium")
        self.assertEqual(classify_coverage(50.0, custom_th), "medium")
        self.assertEqual(classify_coverage(60.0, custom_th), "high")


if __name__ == "__main__":
    unittest.main()
