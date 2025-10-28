import os
import unittest

# Use mock DB for tests
os.environ['USE_MOCK_MONGO'] = 'true'

from app import app

class TestResources(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True
        from app import resources_collection, users_collection
        # Clear collections
        resources_collection.delete_many({})
        users_collection.delete_many({})
        # Insert test user
        users_collection.insert_one({'dni': '22222222', 'nombre': 'Test User'})
        # Insert resources for topic 'Algebra'
        resources_collection.insert_many([
            {'topic': 'Algebra', 'tipo': 'video', 'titulo': 'Intro Álgebra', 'url': 'https://vid.example/algebra', 'descripcion': 'Video introductorio'},
            {'topic': 'Algebra', 'tipo': 'artículo', 'titulo': 'Ecuaciones', 'url': 'https://art.example/ecuaciones', 'descripcion': 'Artículo sobre ecuaciones'},
            {'topic': 'Algebra', 'tipo': 'ejercicio', 'titulo': 'Práctica Álgebra', 'url': 'https://exe.example/practica', 'descripcion': 'Conjunto de ejercicios'},
        ])

    def test_resources_ai_response_returns_three_categorized_links(self):
        # Login first
        resp = self.client.post('/validate_dni', json={'dni': '22222222'})
        self.assertEqual(resp.status_code, 200)

        # Ask for resources
        resp2 = self.client.post('/chat', json={'message': 'recursos adicionales de Algebra'})
        self.assertEqual(resp2.status_code, 200)
        body = resp2.json.get('response', '')
        # Should contain at least the three urls we inserted
        self.assertIn('https://vid.example/algebra', body)
        self.assertIn('https://art.example/ecuaciones', body)
        self.assertIn('https://exe.example/practica', body)
        # Should include category headings (case-insensitive)
        bl = body.lower()
        self.assertIn('video', bl)
        self.assertTrue('artículo' in bl or 'articulo' in bl)
        self.assertIn('ejercicio', bl)

    def test_no_resources_returns_expected_message(self):
        # Login first
        resp = self.client.post('/validate_dni', json={'dni': '22222222'})
        self.assertEqual(resp.status_code, 200)

        # Ask for a topic with no resources inserted
        resp2 = self.client.post('/chat', json={'message': 'recursos adicionales de Física'})
        self.assertEqual(resp2.status_code, 200)
        body = resp2.json.get('response', '')
        self.assertEqual(body, 'No tengo recursos disponibles para este tema, inténtalo con otro')

    def test_api_failure_returns_expected_error_message(self):
        # Login first
        resp = self.client.post('/validate_dni', json={'dni': '22222222'})
        self.assertEqual(resp.status_code, 200)

        # Patch the resources_collection.find to raise an exception to simulate API failure
        import app as app_module
        from unittest.mock import patch

        def raise_exc(*args, **kwargs):
            raise Exception('Simulated API failure')

        with patch.object(app_module.resources_collection, 'find', side_effect=raise_exc):
            resp2 = self.client.post('/chat', json={'message': 'recursos adicionales de Algebra'})
            self.assertEqual(resp2.status_code, 200)
            body = resp2.json.get('response', '')
            self.assertEqual(body, 'Error al obtener recursos adicionales, por favor vuelve a intentarlo más tarde')

if __name__ == '__main__':
    unittest.main()
