import unittest
import time
from datetime import timedelta
from app import app


class SaaSifyLoginTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.secret_key = 'test_secret'
        app.permanent_session_lifetime = timedelta(seconds=1)  # Short timeout for testing
        self.client = app.test_client()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_redirect(self):
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 302)

    def test_protected_area_redirect(self):
        response = self.client.get('/protected_area')
        self.assertEqual(response.status_code, 302)

    def test_session_timeout_redirect(self):
        with self.client.session_transaction() as sess:
            sess['user_email'] = 'test@example.com'
            sess['user_name'] = 'Test User'
            sess.permanent = True

        time.sleep(2)  # Wait for session to expire

        response = self.client.get('/protected_area', follow_redirects=True)
        self.assertIn(
            b'Login',
            response.data
        )

if __name__ == '__main__':
    unittest.main()
