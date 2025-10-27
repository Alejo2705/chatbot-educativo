import unittest
from app import app

class TestValidateDNIEndpoint(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

        # Limpiar la colección de usuarios antes de cada prueba
        from app import users_collection
        users_collection.delete_many({})

        # Insertar un usuario de prueba
        users_collection.insert_one({
            'dni': '12345678',
            'nombre': 'Usuario de Prueba'
        })

    def test_valid_dni(self):
        response = self.app.post('/validate_dni', json={'dni': '12345678'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', response.json)
        self.assertTrue(response.json['success'])
        self.assertIn('message', response.json)

    def test_invalid_dni_format(self):
        response = self.app.post('/validate_dni', json={'dni': '1234'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('success', response.json)
        self.assertFalse(response.json['success'])
        self.assertIn('error', response.json)
        self.assertEqual(response.json['error'], 'DNI inválido. Debe contener exactamente 8 dígitos.')

    def test_nonexistent_user(self):
        response = self.app.post('/validate_dni', json={'dni': '87654321'})
        self.assertEqual(response.status_code, 404)
        self.assertIn('success', response.json)
        self.assertFalse(response.json['success'])
        self.assertIn('error', response.json)

if __name__ == '__main__':
    unittest.main()

