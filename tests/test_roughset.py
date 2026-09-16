import unittest
from roughset import (
    indiscernibility_classes,
    positive_region,
    dependency_degree,
    is_dispensable,
    is_indispensable,
    find_reducts,
    find_core,
    evaluate_candidate_reduct
)

class TestRoughSetEngine(unittest.TestCase):
    def setUp(self):
        # Classic textbook example
        self.attributes = ["a1", "a2", "a3", "a4"]
        self.decision = "d"
        self.data = [
            {"a1": 1, "a2": 1, "a3": 1, "a4": 1, "d": 1},
            {"a1": 1, "a2": 0, "a3": 1, "a4": 0, "d": 1},
            {"a1": 0, "a2": 1, "a3": 0, "a4": 1, "d": 2},
            {"a1": 0, "a2": 0, "a3": 0, "a4": 0, "d": 2},
            {"a1": 1, "a2": 1, "a3": 0, "a4": 0, "d": 1},
            {"a1": 0, "a2": 1, "a3": 1, "a4": 0, "d": 2},
        ]

    def test_indiscernibility(self):
        # Empty attributes -> all objects together
        classes = indiscernibility_classes(self.data, [])
        self.assertEqual(len(classes), 1)
        self.assertEqual(len(classes[0]), 6)
        
        # Attribute a1: objects with a1=1 (0,1,4) and a1=0 (2,3,5)
        classes_a1 = indiscernibility_classes(self.data, ["a1"])
        self.assertEqual(len(classes_a1), 2)

    def test_dependency_and_positive_region(self):
        # Full attributes should have perfect dependency (1.0)
        gamma_full = dependency_degree(self.data, self.attributes, self.decision)
        self.assertEqual(gamma_full, 1.0)
        
        pos_full = positive_region(self.data, self.attributes, self.decision)
        self.assertEqual(len(pos_full), 6)

    def test_reducts_and_core(self):
        reducts = find_reducts(self.data, self.attributes, self.decision)
        self.assertTrue(len(reducts) > 0)
        
        # Verify every reduct has 100% dependency and is minimal
        for r in reducts:
            self.assertEqual(dependency_degree(self.data, r, self.decision), 1.0)
            valid, status, cand_g, tgt_g = evaluate_candidate_reduct(
                self.data, r, self.attributes, self.decision
            )
            self.assertTrue(valid)
            self.assertEqual(status, "valid_reduct")
            
        core = find_core(self.data, self.attributes, self.decision)
        # CORE must equal intersection of all reducts
        intersection = set(reducts[0])
        for r in reducts[1:]:
            intersection.intersection_update(r)
        self.assertEqual(set(core), intersection)


if __name__ == "__main__":
    unittest.main()
