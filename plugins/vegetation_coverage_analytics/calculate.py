"""
calculate.py is a file where calculations inside module 5 are performed.
All functions in this file adhere to Functional Programming principles:
- Pure Functions: Deterministic output solely based on input arguments without side-effects.
- Immutability: Inputs are never mutated in-place; new arrays/structures are returned.
- Separation of Concerns: I/O operations are strictly isolated at the boundary (e.g. load_mask),
  while data transformations (binarize, calculate, classify) remain purely mathematical.
- Function Composition: High-level operations are composed from small, focused functions.
"""

import os
from typing import Any, Dict, Optional, Union
import numpy as np
from PIL import Image


# ============================================================================
# 1. PURE TRANSFORMATION FUNCTIONS (No I/O, Deterministic, Immutable)
# ============================================================================

def parse_image_to_grayscale(img: Image.Image) -> np.ndarray:
    """
    Fungsi Murni: Mengonversi objek citra Pillow ke array 2D grayscale (uint8).
    Mendukung format RGB, RGBA, L (grayscale), dan 1 (1-bit biner).

    Parameters
    ----------
    img : PIL.Image.Image
        Objek citra Pillow.

    Returns
    -------
    np.ndarray
        Array 2D berdimensi (tinggi, lebar) dengan tipe data uint8.
    """
    if not isinstance(img, Image.Image):
        raise TypeError(f"Diharapkan PIL.Image.Image, diterima: {type(img)}")

    # Jika citra memiliki mode selain 'L', konversi secara murni tanpa mutasi citra asal
    gray_img = img.convert("L") if img.mode != "L" else img
    return np.array(gray_img, dtype=np.uint8)


def binarize_array(
    arr: np.ndarray,
    threshold: Optional[int] = None,
) -> np.ndarray:
    """
    Fungsi Murni: Memetakan array 2D menjadi array biner bernilai {0, 1} (uint8).
    
    Kaidah fungsional:
    - Tidak memutasi 'arr' asal.
    - Adaptif: jika array sudah biner {0, 1}, langsung dinormalisasi.
    - Jika array berskala 0-255 (standar mask PNG), nilai > threshold diubah menjadi 1.

    Parameters
    ----------
    arr : np.ndarray
        Array 2D numerik.
    threshold : int, optional
        Ambang batas binerisasi. Jika None, sistem otomatis memilih:
        - threshold = 0 jika nilai maksimum array <= 1 (format 0 dan 1).
        - threshold = 127 jika nilai maksimum array > 1 (format grayscale 0-255).

    Returns
    -------
    np.ndarray
        Array 2D biner berisikan nilai 0 dan 1 (dtype uint8).
    """
    if not isinstance(arr, np.ndarray):
        arr = np.array(arr)

    if arr.ndim != 2:
        raise ValueError(f"Array harus 2 dimensi, diterima dimensi: {arr.ndim}")

    if arr.size == 0:
        return np.zeros((0, 0), dtype=np.uint8)

    # Deteksi threshold otomatis bila tidak diberikan secara eksplisit
    if threshold is None:
        th = 0 if int(np.max(arr, initial=0)) <= 1 else 127
    else:
        th = threshold

    # Transformasi murni: hasil perbandingan boolean dikonversi ke uint8 (0 atau 1)
    return (arr > th).astype(np.uint8)


# ============================================================================
# 2. I/O BOUNDARY FUNCTION (Isolasi Efek Samping Berkas)
# ============================================================================

def load_mask(
    mask_path: str,
    threshold: Optional[int] = None,
) -> np.ndarray:
    """
    Membaca berkas citra vegetation mask hasil dari Modul 4, lalu
    mengonversinya menjadi array 2D biner {0, 1} (uint8) siap proses.

    Pipa komposisi fungsional:
    `mask_path -> open_image (I/O) -> parse_image_to_grayscale -> binarize_array`

    Parameters
    ----------
    mask_path : str
        Jalur berkas citra mask (format PNG, JPEG, TIFF dari Modul 4).
    threshold : int, optional
        Nilai ambang batas binerisasi. Jika None, otomatis menyesuaikan format masker.

    Returns
    -------
    np.ndarray
        Array 2D biner {0, 1} berdimensi (tinggi, lebar) dengan tipe data uint8.

    Raises
    ------
    FileNotFoundError
        Jika berkas mask_path tidak ditemukan pada sistem berkas.
    ValueError
        Jika berkas tidak dapat diurai sebagai gambar atau dimensinya tidak valid.
    """
    if not isinstance(mask_path, str) or not mask_path.strip():
        raise ValueError(f"mask_path tidak boleh kosong: {mask_path!r}")

    if not os.path.exists(mask_path):
        raise FileNotFoundError(f"Berkas vegetation mask tidak ditemukan di: {mask_path}")

    try:
        with Image.open(mask_path) as raw_img:
            # Komposisi fungsi: ubah ke grayscale -> binarisasi ke {0, 1}
            grayscale_arr = parse_image_to_grayscale(raw_img)
            binary_mask = binarize_array(grayscale_arr, threshold=threshold)
            return binary_mask
    except Exception as exc:
        if isinstance(exc, FileNotFoundError):
            raise
        raise ValueError(f"Gagal memproses berkas mask '{mask_path}': {exc}") from exc


# ============================================================================
# 3. PURE ANALYTICAL & CLASSIFICATION FUNCTIONS
# ============================================================================

def calculate_vegetation_coverage(
    binary_mask: Union[np.ndarray, list],
    gsd: Optional[float] = None,
) -> Dict[str, Any]:
    """
    Menghitung persentase tutupan vegetasi dan mengestimasi luas area
    yang tertutup vegetasi dalam satuan meter persegi (m²).

    Parameters
    ----------
    binary_mask : np.ndarray or list
        Array 2D biner yang mewakili vegetasi (nilai > 0 untuk vegetasi, 0 non-vegetasi).
    gsd : float, optional
        Ground Sampling Distance dalam meter per piksel (dari Modul 1).
        Jika None atau <= 0, estimasi luas area bernilai None (fallback mitigation).

    Returns
    -------
    dict
        - total_pixels (int): Total piksel dalam masker.
        - vegetation_pixels (int): Jumlah piksel vegetasi.
        - coverage_percentage (float): Persentase tutupan vegetasi (0.0 - 100.0).
        - vegetation_area_sqm (float or None): Luas vegetasi dalam m² (bila GSD tersedia).
        - total_area_sqm (float or None): Luas total area dalam m² (bila GSD tersedia).
    """
    if not isinstance(binary_mask, np.ndarray):
        binary_mask = np.array(binary_mask)

    if binary_mask.ndim != 2:
        raise ValueError(f"binary_mask harus berupa array 2D, diterima dimensi {binary_mask.ndim}")

    total_pixels = int(binary_mask.size)

    if total_pixels == 0:
        return {
            "total_pixels": 0,
            "vegetation_pixels": 0,
            "coverage_percentage": 0.0,
            "vegetation_area_sqm": 0.0 if (isinstance(gsd, (int, float)) and gsd > 0) else None,
            "total_area_sqm": 0.0 if (isinstance(gsd, (int, float)) and gsd > 0) else None,
        }

    # Menghitung piksel vegetasi (> 0 mendukung representasi biner 1 maupun 255)
    vegetation_pixels = int(np.count_nonzero(binary_mask > 0))
    coverage_percentage = round((vegetation_pixels / total_pixels) * 100.0, 4)

    # Mitigasi risiko: jika GSD valid (> 0), hitung luas fisik (m²)
    if isinstance(gsd, (int, float)) and gsd > 0:
        pixel_area_sqm = float(gsd) ** 2
        vegetation_area_sqm = round(vegetation_pixels * pixel_area_sqm, 4)
        total_area_sqm = round(total_pixels * pixel_area_sqm, 4)
    else:
        vegetation_area_sqm = None
        total_area_sqm = None

    return {
        "total_pixels": total_pixels,
        "vegetation_pixels": vegetation_pixels,
        "coverage_percentage": coverage_percentage,
        "vegetation_area_sqm": vegetation_area_sqm,
        "total_area_sqm": total_area_sqm,
    }


def classify_coverage(
    coverage_percentage: float,
    threshold_dict: Optional[Dict[str, float]] = None,
) -> str:
    """
    Mengklasifikasikan tingkat tutupan vegetasi (low/medium/high)
    berdasarkan nilai persentase coverage terhadap ambang batas (threshold).

    Parameters
    ----------
    coverage_percentage : float
        Nilai persentase tutupan vegetasi (0.0 - 100.0).
    threshold_dict : dict, optional
        Kamus batas ambang. Mendukung format:
        - {"low": 30.0, "high": 70.0} (standar platform)
        - {"low": 20.0, "medium_max": 50.0} (format eksperimen awal)
        - default fallback: low <= 30.0, medium <= 70.0, high > 70.0

    Returns
    -------
    str
        "low", "medium", atau "high"
    """
    if threshold_dict is None:
        threshold_dict = {"low": 30.0, "high": 70.0}

    low_threshold = float(threshold_dict.get("low", 30.0))
    # Fleksibel mendukung key 'high', 'medium', atau 'medium_max'
    high_threshold = float(
        threshold_dict.get(
            "high",
            threshold_dict.get("medium_max", threshold_dict.get("medium", 70.0)),
        )
    )

    if coverage_percentage <= low_threshold:
        return "low"
    elif coverage_percentage <= high_threshold:
        return "medium"
    else:
        return "high"


if __name__ == "__main__":
    print("=== Demo Fungsional: load_mask, calculate, classify ===")

    # Contoh komposisi fungsional langsung dari array
    sample_mask = np.zeros((10, 10), dtype=np.uint8)
    sample_mask[:4, :] = 1  # 40% vegetasi

    calc = calculate_vegetation_coverage(sample_mask, gsd=0.05)
    category = classify_coverage(calc["coverage_percentage"])

    print("Hasil Kalkulasi:", calc)
    print("Kategori Tutupan:", category)
