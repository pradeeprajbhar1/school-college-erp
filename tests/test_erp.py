import unittest
from app import create_app
from app.extensions import db
from app.models.core import User, Institution, Role
from app.models.student import Student, CourseClass
from app.config import Config

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:' # Fast in-memory DB for unit testing
    WTF_CSRF_ENABLED = False

class ERPTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Seed basic testing environment
        self.inst = Institution(name='Test Academy', code='TEST01')
        db.session.add(self.inst)
        db.session.commit()

        self.user = User(username='testadmin', email='test@admin.com', institution_id=self.inst.id)
        self.user.set_password('pass123')
        db.session.add(self.user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_unauthorized_redirect(self):
        """ Test protected routes redirect unauthenticated users to login """
        response = self.client.get('/dashboard/', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response.location)

    def test_login_logout(self):
        """ Test successful authentication flow """
        response = self.client.post('/auth/login', data={
            'email': 'test@admin.com',
            'password': 'pass123'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_student_crud(self):
        """ Test Student registration and database insertion """
        # Login first
        self.client.post('/auth/login', data={'email': 'test@admin.com', 'password': 'pass123'})
        
        # Create Class
        c = CourseClass(name='Grade 10', institution_id=self.inst.id)
        db.session.add(c)
        db.session.commit()

        # Add Student
        response = self.client.post('/students/add', data={
            'admission_number': 'ADM-999',
            'first_name': 'John',
            'last_name': 'Doe',
            'gender': 'Male',
            'class_id': c.id,
            'guardian_name': 'Robert Doe',
            'contact_number': '9876543210'
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        student = Student.query.filter_by(admission_number='ADM-999').first()
        self.assertIsNotNone(student)
        self.assertEqual(student.first_name, 'John')

if __name__ == '__main__':
    unittest.main()