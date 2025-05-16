import unittest
from datetime import date
from app import application
from model import db, User, Profile, Document

class DashboardTestCase(unittest.TestCase):
    def setUp(self):
        self.app = application
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()
            user = User(username='dash', email='dash@example.com', password='123')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

            # Simulate login session
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.user_id

            # Add test profile using a valid Python date object
            profile = Profile(
                user_id=self.user_id,
                full_name='Dash User',
                education='Bachelor',
                school='UWA',
                graduation_date=date(2023, 1, 1),  # Must use datetime.date for SQLite DATE fields
                career_goal='Python,Communication',
            )
            db.session.add(profile)

            # Add uploaded document
            doc = Document(user_id=self.user_id, file_name='cv.pdf', file_path='uploads/cv.pdf')
            db.session.add(doc)

            db.session.commit()

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_dashboard_view(self):
        rv = self.client.get('/dashboard', follow_redirects=True)
        self.assertIn(b'Documents Uploaded', rv.data)
        self.assertIn(b'Last Job-Fit Score', rv.data)
