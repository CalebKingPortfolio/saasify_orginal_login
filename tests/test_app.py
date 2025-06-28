import unittest
import time
import sqlite3
from datetime import timedelta
from app import app


class SaaSifyLocalLoginTests(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.secret_key = 'test_secret'
        app.permanent_session_lifetime = timedelta(seconds=1)
        self.client = app.test_client()

        # Make sure admin user exists
        conn = sqlite3.connect("users.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email = ?",
            ("admin@saasify.com",)
        )

        if not cursor.fetchone():
            from werkzeug.security import generate_password_hash
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (?, ?)",
                ("admin@saasify.com", generate_password_hash("admin"))
            )
        conn.commit()
        conn.close()

    def test_home_page(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post('/login', data={
            'email': 'admin@saasify.com',
            'password': 'admin'
        }, follow_redirects=True)
        self.assertIn(b'Welcome', response.data)

    def test_login_failure(self):
        response = self.client.post('/login', data={
            'email': 'admin@saasify.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        self.assertIn(b'Invalid email or password', response.data)

    def test_protected_area_requires_login(self):
        response = self.client.get('/protected_area', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    def test_session_timeout_redirect(self):
        with self.client.session_transaction() as sess:
            sess['user_email'] = 'admin@saasify.com'
            sess['user_name'] = 'Admin'
            sess.permanent = True

        time.sleep(2)
        response = self.client.get('/protected_area', follow_redirects=True)
        self.assertIn(b'Login', response.data)

    def test_secure_cookie_settings(self):
        self.assertTrue(app.config['SESSION_COOKIE_SECURE'])
        self.assertTrue(app.config['SESSION_COOKIE_HTTPONLY'])
        self.assertEqual(app.config['SESSION_COOKIE_SAMESITE'], 'Lax')


if __name__ == '__main__':
    unittest.main()
