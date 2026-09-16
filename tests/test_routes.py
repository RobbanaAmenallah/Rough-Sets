import unittest
import uuid
from app import app
import database as db

class TestFlaskRoutesAndAPIs(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.app.config["SECRET_KEY"] = "test-secret"
        self.client = self.app.test_client()

        # Create a test classroom with unique code
        code_suffix = uuid.uuid4().hex[:4].upper()
        self.code = f"T{code_suffix}"
        self.classroom = db.create_classroom(self.code)
        self.player = db.create_player(self.classroom["id"], "TestStudent", "Tester")

    def test_landing_page(self):
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"ROUGHSET CHALLENGE", res.data)

    def test_join_workflow(self):
        res = self.client.post("/join", data={
            "code": self.code,
            "first_name": "Alice",
            "nickname": "AliceML"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"YOUR MISSION BRIEFING", res.data)

    def test_level_mechanics_and_apis(self):
        with self.client.session_transaction() as sess:
            sess["player_id"] = self.player["id"]
            sess["classroom_id"] = self.classroom["id"]

        # 1. Start mission
        res = self.client.post("/api/start", follow_redirects=True)
        self.assertEqual(res.status_code, 200)

        # 2. Level 1 API Check
        res = self.client.post("/api/check-feature", json={
            "level": 1,
            "attribute": "Hat"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["dispensable"])
        self.assertEqual(data["xp_awarded"], 100)

        # 3. Level 2 API Check (Unlock CORE)
        res = self.client.post("/api/check-core", json={
            "level": 2,
            "attribute": "Fever"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["is_indispensable"])
        self.assertIn("Fever", data["core"])

        # 4. Level 3 API Check (REDUCT)
        res = self.client.post("/api/check-reduct", json={
            "level": 3,
            "attributes": ["A", "C", "F"],
            "attempts": 1
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn("status", data)

        # 5. Quiz answer API
        res = self.client.post("/api/quiz-answer", json={
            "question_id": 1,
            "selected_key": "C"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertTrue(data["correct"])
        self.assertEqual(data["points_awarded"], 100)

        # Double submit check (anti-cheat)
        res2 = self.client.post("/api/quiz-answer", json={
            "question_id": 1,
            "selected_key": "C"
        })
        data2 = res2.get_json()
        self.assertTrue(data2["already_answered"])
        self.assertEqual(data2["points_awarded"], 0)

        # 6. Leaderboard
        res = self.client.get("/leaderboard")
        self.assertEqual(res.status_code, 200)

        res_api = self.client.get("/api/leaderboard")
        self.assertEqual(res_api.status_code, 200)
        self.assertTrue(len(res_api.get_json()["leaderboard"]) >= 1)

    def test_admin_flow(self):
        # Admin login
        res = self.client.post("/admin/login", data={
            "username": "Amenallah",
            "password": "Amen1920"
        }, follow_redirects=True)
        self.assertEqual(res.status_code, 200)
        self.assertIn(b"LIVE CLASSROOM MANAGEMENT", res.data)

        # Admin export CSV
        res_export = self.client.get("/admin/export")
        self.assertEqual(res_export.status_code, 200)
        self.assertEqual(res_export.mimetype, "text/csv")


if __name__ == "__main__":
    unittest.main()
