"""
calculate.py is a file where are the calculations inside module 5 is performed
all the code inside this file are expected to be a pure function code, becuase it will 
only take inputs and letting out outputs.....wellll for now it's not a pure function because it still writes to the terminal 

"""
from typing import Final

DEFAULT_THRESHOLD_LOW: Final[float] = 30.0
DEFAULT_THRESHOLD_MEDIUM: Final[float] = 60.0


# classify_coverage experimentation 
# Coverage Classification: Categorize areas into low, medium, or high vegetation coverage.
def classify_coverage(coverage_percentage: float, 
                      low_limit : float = DEFAULT_THRESHOLD_LOW, 
                      medium_limit : float = DEFAULT_THRESHOLD_MEDIUM) -> str : 
    if not(0.0 <= coverage_percentage <=100.0) :
        raise ValueError(
            f"coverage_percentage harus berada pada rentang 0-100, anda memasukan: {coverage_percentage}"
        )
    
    if low_limit > medium_limit :
        raise ValueError("Batas low tidak boleh lebih tinggi dari medium")
    
    elif  coverage_percentage <= low_limit: 
        return "low"
    elif coverage_percentage <= medium_limit :
        return "medium"
    else : 
        return "high"
        



# mock_data = {"low": 20, "medium_max": 50}
# coverage_value = 20.1

# result = classify_coverage(
#     coverage_percentage=coverage_value, 
#     threshold_dict=mock_data, 
# )
# print(result)