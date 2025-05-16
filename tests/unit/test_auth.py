import unittest
from app import application
from model import db, User
from flask import url_for

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = application
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_signup_login_logout(self):
        with self.app.app_context():
            # Test user signup
            rv = self.client.post('/signup', data={
                'username': 'testuser',
                'email': 'test@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            }, follow_redirects=True)
            self.assertIn(b'Account created', rv.data)

            # Test login
            rv = self.client.post('/login', data={
                'username': 'testuser',
                'password': 'password123'
            }, follow_redirects=True)
            self.assertIn(b'Logged in successfully', rv.data)

            # Test logout
            rv = self.client.get('/logout', follow_redirects=True)
            self.assertIn(b'Log In', rv.data)
