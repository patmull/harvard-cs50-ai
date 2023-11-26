import unittest

from shopping import load_data

TESTING_EVIDENCE = [0, 0.0, 0, 0.0, 1, 0.0, 0.2, 0.2, 0.0, 0.0, 1, 1, 1, 1, 1, 1, 0]
TESTING_LABEL = 0


class MyTestCase(unittest.TestCase):
    def test_load_data(self):
        evidence, labels = load_data("shopping.csv")
        self.assertEqual(TESTING_EVIDENCE, evidence[0])
        self.assertEqual(TESTING_LABEL, labels[0])


if __name__ == '__main__':
    unittest.main()
