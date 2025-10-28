import os
import unittest

# Force tests to use mongomock to avoid network calls
os.environ['USE_MOCK_MONGO'] = 'true'

from app import app


class TestSessionBehavior(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()
        self.client.testing = True

        # Prepare DB: clear users and add a test user
        from app import users_collection
        users_collection.delete_many({})
        users_collection.insert_one({
            'dni': '22222222',
            'nombre': 'Test User'
        })

    def test_protected_endpoint_requires_login(self):
        # Accessing a protected endpoint without login should return 401
        resp = self.client.get('/grades')
        self.assertEqual(resp.status_code, 401)

    def test_me_endpoint_requires_login(self):
        # /me should be protected and return 401 when not logged in
        resp = self.client.get('/me')
        self.assertEqual(resp.status_code, 401)

    def test_invalid_dni_format_keeps_on_login_screen(self):
        # Submit an invalid DNI (too short / non-numeric)
        resp = self.client.post('/validate_dni', json={'dni': '1234'})
        self.assertEqual(resp.status_code, 400)
        self.assertIn('success', resp.json)
        self.assertFalse(resp.json['success'])
        self.assertIn('error', resp.json)
        self.assertEqual(resp.json['error'], 'DNI inválido. Debe contener exactamente 8 dígitos.')

        # Ensure session was NOT established: protected endpoints remain blocked
        resp_me = self.client.get('/me')
        self.assertEqual(resp_me.status_code, 401)
        resp_grades = self.client.get('/grades')
        self.assertEqual(resp_grades.status_code, 401)

        # Now login with a valid DNI to ensure the user can retry and authenticate
        resp_ok = self.client.post('/validate_dni', json={'dni': '22222222'})
        self.assertEqual(resp_ok.status_code, 200)
        resp_grades_ok = self.client.get('/grades')
        self.assertEqual(resp_grades_ok.status_code, 200)

    def test_unregistered_dni_shows_error_and_keeps_on_login_screen(self):
        # Submit a well-formed but unregistered DNI
        resp = self.client.post('/validate_dni', json={'dni': '33333333'})
        self.assertEqual(resp.status_code, 404)
        self.assertIn('success', resp.json)
        self.assertFalse(resp.json['success'])
        self.assertIn('error', resp.json)
        self.assertIn('DNI no es válido', resp.json['error'])

        # Ensure session was NOT established: protected endpoints remain blocked
        self.assertEqual(self.client.get('/me').status_code, 401)
        self.assertEqual(self.client.get('/grades').status_code, 401)

    def test_block_after_multiple_failed_attempts_and_temporary_lock(self):
        # Ensure lockout works after MAX_DNI_ATTEMPTS failed attempts
        from app import LOCKOUT_TIME
        # Use small lockout in test to speed up
        import app as app_module
        app_module.LOCKOUT_TIME = 1

        # Make MAX_DNI_ATTEMPTS (3) failed attempts with unregistered DNI
        for i in range(app_module.MAX_DNI_ATTEMPTS):
            resp = self.client.post('/validate_dni', json={'dni': '33333333'})
            # should be 404 each time
            self.assertEqual(resp.status_code, 404)

        # Next attempt should be blocked with 429
        resp_blocked = self.client.post('/validate_dni', json={'dni': '33333333'})
        self.assertEqual(resp_blocked.status_code, 429)
        self.assertIn('error', resp_blocked.json)
        self.assertIn('Demasiados intentos', resp_blocked.json['error'])

        # Wait for lockout to expire, then try a valid login
        import time
        time.sleep(app_module.LOCKOUT_TIME + 0.2)

        # Now valid login should succeed
        resp_ok = self.client.post('/validate_dni', json={'dni': '22222222'})
        self.assertEqual(resp_ok.status_code, 200)

    def test_session_is_set_after_validate_dni_and_allows_access(self):
        # Login with valid DNI
        resp = self.client.post('/validate_dni', json={'dni': '22222222'})
        self.assertEqual(resp.status_code, 200)
        self.assertIn('success', resp.json)
        self.assertTrue(resp.json['success'])
        # The response should include a personalized greeting with the user's name
        self.assertIn('message', resp.json)
        self.assertIn('Test User', resp.json['message'])

        # After login, /me should return user info
        me = self.client.get('/me')
        self.assertEqual(me.status_code, 200)
        self.assertIn('dni', me.json)
        self.assertIn('name', me.json)
        self.assertEqual(me.json['dni'], '22222222')
        self.assertEqual(me.json['name'], 'Test User')

    def test_logout_clears_session_and_blocks_protected_endpoints(self):
        # Login with valid DNI
        resp = self.client.post('/validate_dni', json={'dni': '22222222'})
        self.assertEqual(resp.status_code, 200)

        # Confirm protected endpoint accessible
        resp_ok = self.client.get('/grades')
        self.assertEqual(resp_ok.status_code, 200)

        # Logout
        resp_logout = self.client.post('/logout')
        self.assertEqual(resp_logout.status_code, 200)
        self.assertIn('message', resp_logout.json)
        self.assertIn('Sesión cerrada', resp_logout.json['message'])

        # After logout, protected endpoint should be blocked
        resp_after = self.client.get('/grades')
        self.assertEqual(resp_after.status_code, 401)
        # Re-login and verify protected endpoint is accessible again
        resp_relogin = self.client.post('/validate_dni', json={'dni': '22222222'})
        self.assertEqual(resp_relogin.status_code, 200)

        resp2 = self.client.get('/grades')
        self.assertEqual(resp2.status_code, 200)
        # Should return grades structure
        self.assertIn('grades', resp2.json)


if __name__ == '__main__':
    unittest.main()
