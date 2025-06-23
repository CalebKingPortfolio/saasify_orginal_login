import unittest
from app import app


class SaaSifyLoginTests(unittest.TestCase):

    def setUp(self):
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


if __name__ == '__main__':
    unittest.main()
