"""
calculate.py is a file where calculations inside module 5 are performed.
All functions in this file are pure functions: they accept inputs and return
deterministic outputs without causing side effects.
"""

from typing import Any, Dict, Optional, Union
import numpy as np


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

    # Piksel vegetasi diidentifikasi jika bernilai > 0 (mendukung mask format 0/1 maupun 0/255)
    vegetation_pixels = int(np.count_nonzero(binary_mask > 0))
    coverage_percentage = round((vegetation_pixels / total_pixels) * 100.0, 4)

    # Mitigasi risiko: jika GSD tersedia dan valid (> 0), hitung luas fisik (m²)
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
    # Demo pengujian mandiri
    print("=== Demo calculate_vegetation_coverage & classify_coverage ===")

    # Buat dummy mask 10x10 dengan 30% vegetasi
    sample_mask = np.zeros((10, 10), dtype=np.uint8)
    sample_mask[:3, :] = 1  # 30 piksel vegetasi dari 100 total

    # Kasus 1: GSD tersedia (misal 0.05 meter/pixel = 5 cm/pixel)
    gsd_val = 0.05
    cov_result = calculate_vegetation_coverage(sample_mask, gsd=gsd_val)
    classification = classify_coverage(cov_result["coverage_percentage"])

    print(f"Hasil kalkulasi dengan GSD={gsd_val} m/px:")
    print(cov_result)
    print(f"Klasifikasi: {classification}")

    # Kasus 2: GSD tidak tersedia (None fallback)
    cov_no_gsd = calculate_vegetation_coverage(sample_mask, gsd=None)
    print("\nHasil kalkulasi tanpa GSD (fallback):")
    print(cov_no_gsd)
