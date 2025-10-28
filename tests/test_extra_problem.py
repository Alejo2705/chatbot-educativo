import os
import unittest

# Force tests to use mongomock
os.environ['USE_MOCK_MONGO'] = 'true'

from app import app


class TestExtraProblem(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        from app import users_collection, queries_collection
        users_collection.delete_many({})
        queries_collection.delete_many({})
        users_collection.insert_one({'dni': '22222222', 'nombre': 'Test User'})

    def test_generate_extra_problem_and_saved(self):
        from app import model, queries_collection
        from unittest.mock import patch

        class DummyResp:
            def __init__(self, text):
                self.text = text

        dummy_text = "PROBLEMA:\n[Enunciado de prueba]"

        with patch.object(model, 'generate_content', return_value=DummyResp(dummy_text)):
            # Login first
            resp_login = self.client.post('/validate_dni', json={'dni': '22222222'})
            self.assertEqual(resp_login.status_code, 200)

            # Request extra problem
            resp = self.client.post('/extra_problem', json={'topic': 'Algebra'})
            self.assertEqual(resp.status_code, 200)
            self.assertIn('problem', resp.json)
            self.assertEqual(resp.json['problem'], dummy_text)

            # Verify it was saved in queries_collection
            saved = queries_collection.find_one({'dni': '22222222'})
            self.assertIsNotNone(saved)
            self.assertIn('Problema extra', saved['message'])

    def test_daily_limit_reached(self):
        from app import queries_collection
        import datetime

        # Insert 15 problem records for today
        now = datetime.datetime.now()
        docs = []
        for i in range(15):
            docs.append({'dni': '22222222', 'timestamp': now, 'message': f'problema extra {i}'})
        queries_collection.insert_many(docs)

        # Login
        resp_login = self.client.post('/validate_dni', json={'dni': '22222222'})
        self.assertEqual(resp_login.status_code, 200)

        # Now request another extra problem -> should be rate-limited
        resp = self.client.post('/extra_problem', json={'topic': 'Algebra'})
        self.assertEqual(resp.status_code, 429)
        self.assertIn('error', resp.json)
        self.assertIn('Límite diario alcanzado', resp.json['error'])


if __name__ == '__main__':
    unittest.main()
