"""
Basic tests for the application
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.management import call_command

User = get_user_model()


class BasicAppTest(TestCase):
    """Basic application tests"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
    
    def test_homepage_loads(self):
        """Test that homepage loads successfully"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_login(self):
        """Test admin interface is accessible"""
        response = self.client.get('/admin/')
        self.assertEqual(response.status_code, 302)  # Redirect to login
    
    def test_api_endpoints_exist(self):
        """Test that API endpoints exist"""
        # Test tickets API
        response = self.client.get('/api/tickets/ticket-types/')
        self.assertEqual(response.status_code, 401)  # Unauthorized without login
    
    def test_management_command(self):
        """Test that management command works"""
        try:
            call_command('create_sample_ticket_types')
            # If no exception is raised, the command works
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Management command failed: {e}")


class ModelTest(TestCase):
    """Test basic model functionality"""
    
    def test_user_creation(self):
        """Test user creation"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.username, 'testuser')
        self.assertTrue(user.check_password('testpass123'))
    
    def test_user_str_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.assertEqual(str(user), 'test@example.com')
