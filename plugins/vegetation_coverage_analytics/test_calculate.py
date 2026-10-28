# Used for later!! MAybe.....


import unittest
from calculate import classify_coverage

LOW, HIGH = 20, 60   # default di parameters.json

CASES = [
    # (input, hasil yang diharapkan)
    (0, "low"), (19.9, "low"), (20, "low"), (35, "medium"),
    (59.9, "medium"), (60, "high"), (100, "high"),
]

class TestClassifyCoverage(unittest.TestCase):
    def test_cases(self):
        for value, expected in CASES:
            with self.subTest(value=value):
               
                self.assertEqual(classify_coverage(value, ...), expected)

if __name__ == "__main__":
    unittest.main()