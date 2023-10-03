import unittest

from optimizer.utils.parser import search_field


class TestSearchField(unittest.TestCase):
    def test_case1(self):
        obj = {"a": 1, "b": 2, "c": 3}
        candidates = ["d", "b", "e", "a"]
        result = search_field(obj, candidates)
        self.assertEqual(result, 2)

    def test_case2(self):
        obj = {"a": 1, "b": 2, "c": 3}
        candidates = ["d", "e", "f"]
        result = search_field(obj, candidates)
        self.assertIsNone(result)

    def test_case3(self):
        obj = {"x": {"y": {"z": "foo"}}}
        candidates = ["p", "x", "y", "z"]
        result = search_field(obj, candidates)
        self.assertEqual(result, {"y": {"z": "foo"}})


if __name__ == "__main__":
    unittest.main()
