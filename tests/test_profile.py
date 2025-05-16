import unittest
from app import application
from model import db, User, Profile

class ProfileTestCase(unittest.TestCase):
    def setUp(self):
        self.app = application
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            u = User(username='u1', email='e@e.com', password='x')
            db.session.add(u)
            db.session.commit()
            self.user_id = u.id

            # Simulate a logged-in user session
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.user_id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_edit_profile(self):
        rv = self.client.post('/edit_profile', data={
            'full_name': 'John Smith',
            'education': 'Bachelor',
            'gpa': 'D',
            'communication_skill': '3',
            'working_experience': '2',
            'submit': True
        }, follow_redirects=True)
        self.assertIn(b'Profile updated successfully', rv.data)
