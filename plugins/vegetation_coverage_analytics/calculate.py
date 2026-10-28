"""
calculate.py is a file where are the calculations inside module 5 is performed
all the code inside this file are expected to be a pure function code, becuase it will 
only take inputs and letting out outputs.....wellll for now it's not a pure function because it still writes to the terminal 

"""

# classify_coverage experimentation 
# Coverage Classification: Categorize areas into low, medium, or high vegetation coverage.
def classify_coverage(coverage_percentage, threshold_dict) : 
    
    if coverage_percentage <= threshold_dict["low"] :
        return "low"
    elif  coverage_percentage <= threshold_dict["medium_max"]: 
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