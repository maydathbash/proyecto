from django.test import TestCase
from .models import User  # Assuming you have a User model in cuentas/models.py

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.check_password('testpassword'))

    def test_user_str(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_user_email(self):
        self.assertEqual(self.user.email, 'testuser@example.com')

    def test_user_password(self):
        self.assertTrue(self.user.check_password('testpassword'))

# Add more tests as needed for other models and functionalities in the cuentas app.