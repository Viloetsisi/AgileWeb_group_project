import unittest
from app import application
from model import db, User, JobHistory

class JobTestCase(unittest.TestCase):
    def setUp(self):
        self.app = application
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False  # ✅ 关闭 CSRF 验证
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            user = User(username='jobuser', email='job@example.com', password='123')
            db.session.add(user)
            db.session.commit()
            self.user_id = user.id

            # 模拟登录状态
            with self.client.session_transaction() as sess:
                sess['user_id'] = self.user_id

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()

    def test_submit_job_history(self):
        rv = self.client.post('/jobs', data={
            'company_name': 'OpenAI',
            'position': 'AI Engineer',
            'start_date': '2022-01-01',
            'end_date': '2023-01-01',
            'salary': 100000,
            'description': 'Worked on GPT models',
            'submit': True
        }, follow_redirects=True)

        self.assertIn(b'Job history uploaded successfully', rv.data)

        # 检查数据库记录是否写入
        with self.app.app_context():
            job = JobHistory.query.filter_by(user_id=self.user_id).first()
            self.assertIsNotNone(job)
            self.assertEqual(job.company_name, 'OpenAI')
            self.assertEqual(job.position, 'AI Engineer')
