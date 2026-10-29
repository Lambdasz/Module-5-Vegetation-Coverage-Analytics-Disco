"""
calculate.py is a file where are the calculations inside module 5 is performed
all the code inside this file are expected to be a pure function code, becuase it will 
only take inputs and letting out outputs.....wellll for now it's not a pure function because it still writes to the terminal 
"""

import numpy as np # Tambahan library untuk kalkulasi matriks

# classify_coverage experimentation 
# Coverage Classification: Categorize areas into low, medium, or high vegetation coverage.
def classify_coverage(coverage_percentage, threshold_dict) : 
    
    if coverage_percentage <= threshold_dict["low"] :
        return "low"
    elif  coverage_percentage <= threshold_dict["medium_max"]: 
        return "medium"
    else :
        return "high"


# =====================================================================
# FITUR 4: generate_coverage_zonation
# =====================================================================

def _calculate_cell_polygon(row: int, col: int, grid_size: int, bounds: list) -> list:
    """
    Helper function (Pure): Menghitung koordinat [lon, lat] untuk 1 kotak grid.
    """
    min_lon, min_lat, max_lon, max_lat = bounds
    
    lon_step = (max_lon - min_lon) / grid_size
    lat_step = (max_lat - min_lat) / grid_size
    
    cell_min_lon = min_lon + (col * lon_step)
    cell_max_lon = min_lon + ((col + 1) * lon_step)
    
    cell_max_lat = max_lat - (row * lat_step)
    cell_min_lat = max_lat - ((row + 1) * lat_step)
    
    return [
        [cell_min_lon, cell_min_lat],
        [cell_max_lon, cell_min_lat],
        [cell_max_lon, cell_max_lat],
        [cell_min_lon, cell_max_lat],
        [cell_min_lon, cell_min_lat]
    ]


def generate_coverage_zonation(
    binary_mask: np.ndarray, 
    image_bounds: list, 
    grid_size: int = 4, 
    gsd: float = None, 
    threshold_dict: dict = None
) -> dict:
    """
    Fitur 4: Membagi mask menjadi grid NxN, menghitung coverage per sel, 
    dan menghasilkan layer vektor (GeoJSON FeatureCollection).
    """
    if binary_mask.ndim != 2:
        raise ValueError("binary_mask harus berupa 2D array")
    if len(image_bounds) != 4:
        raise ValueError("image_bounds harus berisi 4 float")

    # Bagi array menjadi grid NxN menggunakan numpy
    row_splits = np.array_split(binary_mask, grid_size, axis=0)
    features = []
    
    for r_idx, row_chunk in enumerate(row_splits):
        col_splits = np.array_split(row_chunk, grid_size, axis=1)
        
        for c_idx, cell in enumerate(col_splits):
            # Hitung coverage (persentase)
            coverage_pct = float(np.mean(cell) * 100) if cell.size > 0 else 0.0
            
            # Hitung polygon
            polygon_coords = _calculate_cell_polygon(r_idx, c_idx, grid_size, image_bounds)
            
            properties = {
                "cell_id": f"r{r_idx}_c{c_idx}",
                "row": r_idx,
                "col": c_idx,
                "coverage_percentage": round(coverage_pct, 2),
                "vegetation_pixels": int(np.sum(cell)),
                "total_pixels": int(cell.size)
            }
            
            # Gunakan fungsi classify_coverage yang sudah ada (jika threshold diberikan)
            if threshold_dict:
                properties["classification"] = classify_coverage(coverage_pct, threshold_dict)

            features.append({
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [polygon_coords]
                },
                "properties": properties
            })
            
    return {
        "type": "FeatureCollection",
        "features": features
    }

# =====================================================================
# BLOK UNTUK TESTING (Opsional, bisa dihapus nanti)
# =====================================================================
# mock_data = {"low": 20, "medium_max": 50}
# coverage_value = 20.1
# result = classify_coverage(coverage_percentage=coverage_value, threshold_dict=mock_data)
# print(result)