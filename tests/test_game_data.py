import unittest
from roughset import (
    dependency_degree,
    is_dispensable,
    is_indispensable,
    find_reducts,
    find_core,
    evaluate_candidate_reduct
)
from game_data import LEVEL_1_DATA, LEVEL_2_DATA, LEVEL_3_DATA, LEVEL_4_DATA, QUIZ_QUESTIONS

class TestGameDataVerification(unittest.TestCase):
    def test_level_1_has_dispensable_and_indispensable(self):
        data = LEVEL_1_DATA["objects"]
        attrs = LEVEL_1_DATA["condition_attributes"]
        dec = LEVEL_1_DATA["decision_attribute"]
        
        # Initial dependency must be 1.0 (100%)
        gamma_full = dependency_degree(data, attrs, dec)
        self.assertEqual(gamma_full, 1.0)
        
        dispensables = [a for a in attrs if is_dispensable(data, attrs, a, dec)]
        indispensables = [a for a in attrs if is_indispensable(data, attrs, a, dec)]
        
        # Level 1 must have at least one dispensable and one indispensable attribute
        self.assertTrue(len(dispensables) >= 1, f"Found dispensables: {dispensables}")
        self.assertTrue(len(indispensables) >= 1, f"Found indispensables: {indispensables}")

    def test_level_2_core_unlocked(self):
        data = LEVEL_2_DATA["objects"]
        attrs = LEVEL_2_DATA["condition_attributes"]
        dec = LEVEL_2_DATA["decision_attribute"]
        
        gamma_full = dependency_degree(data, attrs, dec)
        self.assertEqual(gamma_full, 1.0)
        
        reducts = find_reducts(data, attrs, dec)
        self.assertTrue(len(reducts) >= 1)
        
        core = find_core(data, attrs, dec)
        # CORE must be non-empty and non-trivial
        self.assertTrue(len(core) >= 1, f"Core is {core}")
        self.assertTrue(len(core) < len(attrs), f"Core should be a proper subset: {core}")

    def test_level_3_reduct_challenge(self):
        data = LEVEL_3_DATA["objects"]
        attrs = LEVEL_3_DATA["condition_attributes"]
        dec = LEVEL_3_DATA["decision_attribute"]
        
        self.assertEqual(len(attrs), 8, "Level 3 should have 8 attributes")
        gamma_full = dependency_degree(data, attrs, dec)
        self.assertEqual(gamma_full, 1.0)
        
        reducts = find_reducts(data, attrs, dec)
        self.assertTrue(len(reducts) >= 1, "Level 3 must have valid minimal reducts")
        # Reduction rate should be significant (e.g. <= 5 attributes from 8)
        min_reduct_len = min(len(r) for r in reducts)
        self.assertTrue(min_reduct_len <= 5, f"Min reduct length is {min_reduct_len}")

    def test_level_4_face_lab_reduct(self):
        data = LEVEL_4_DATA["objects"]
        attrs = LEVEL_4_DATA["condition_attributes"]
        dec = LEVEL_4_DATA["decision_attribute"]
        
        gamma_full = dependency_degree(data, attrs, dec)
        self.assertEqual(gamma_full, 1.0)
        
        reducts = find_reducts(data, attrs, dec)
        self.assertTrue(len(reducts) >= 1)

    def test_quiz_questions_consistency(self):
        self.assertEqual(len(QUIZ_QUESTIONS), 5)
        for q in QUIZ_QUESTIONS:
            self.assertIn("id", q)
            self.assertIn("question", q)
            self.assertIn("options", q)
            self.assertIn("correct_key", q)
            self.assertIn("explanation", q)
            valid_keys = [opt["key"] for opt in q["options"]]
            self.assertIn(q["correct_key"], valid_keys)

if __name__ == "__main__":
    unittest.main()
