import unittest
from app import application
from model import db, User, Document, SharedWith, VizShare

class ShareTestCase(unittest.TestCase):
    def setUp(self):
        self.app = application
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF protection for testing
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

            # Create two users: one owner, one viewer
            user1 = User(username='owner', email='o@example.com', password='x')
            user2 = User(username='viewer', email='v@example.com', password='y')
            db.session.add_all([user1, user2])
            db.session.commit()
            self.owner_id = user1.id
            self.viewer_id = user2.id

            # Simulate login as the owner
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.owner_id

            # Add a document owned by the owner
            doc = Document(user_id=self.owner_id, file_name='file.pdf', file_path='uploads/file.pdf')
            db.session.add(doc)
            db.session.commit()
            self.doc_id = doc.id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_share_document_and_dashboard(self):
        rv = self.client.post('/share', data={
            f'share_with_{self.doc_id}[]': str(self.viewer_id),
            'share_viz[]': str(self.viewer_id),
            f'is_shared_{self.doc_id}': 'on',
        }, follow_redirects=True)

        self.assertIn(b'Sharing settings updated', rv.data)

        # Check if document and dashboard were shared successfully
        with self.app.app_context():
            doc_share = SharedWith.query.filter_by(
                document_id=self.doc_id, shared_to_user_id=self.viewer_id
            ).first()
            dash_share = VizShare.query.filter_by(
                owner_id=self.owner_id, shared_to_user_id=self.viewer_id
            ).first()
            self.assertIsNotNone(doc_share)
            self.assertIsNotNone(dash_share)
