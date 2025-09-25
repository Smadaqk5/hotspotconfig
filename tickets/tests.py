"""
Tests for tickets app
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from tickets.models import TicketType, Ticket, TicketSale, TicketBatch
import json

User = get_user_model()


class TicketTypeModelTest(TestCase):
    """Test TicketType model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
    def test_ticket_type_creation(self):
        """Test creating a ticket type"""
        ticket_type = TicketType.objects.create(
            name='1 Hour WiFi',
            ticket_type='time',
            duration_hours=1,
            price=50.00,
            currency='KES',
            created_by=self.user
        )
        
        self.assertEqual(ticket_type.name, '1 Hour WiFi')
        self.assertEqual(ticket_type.ticket_type, 'time')
        self.assertEqual(ticket_type.duration_hours, 1)
        self.assertEqual(ticket_type.price, 50.00)
        self.assertTrue(ticket_type.is_active)
    
    def test_duration_display(self):
        """Test duration display property"""
        ticket_type = TicketType.objects.create(
            name='2 Hours WiFi',
            ticket_type='time',
            duration_hours=2,
            price=80.00,
            currency='KES',
            created_by=self.user
        )
        
        self.assertEqual(ticket_type.duration_display, '2 hours')
    
    def test_price_display(self):
        """Test price display property"""
        ticket_type = TicketType.objects.create(
            name='1GB Data',
            ticket_type='data',
            data_limit_gb=1,
            price=100.00,
            currency='KES',
            created_by=self.user
        )
        
        self.assertEqual(ticket_type.price_display, 'KES 100.00')


class TicketModelTest(TestCase):
    """Test Ticket model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.ticket_type = TicketType.objects.create(
            name='1 Hour WiFi',
            ticket_type='time',
            duration_hours=1,
            price=50.00,
            currency='KES',
            created_by=self.user
        )
    
    def test_ticket_creation(self):
        """Test creating a ticket"""
        ticket = Ticket.objects.create(
            ticket_type=self.ticket_type,
            user=self.user,
            username='testuser1',
            password='123456'
        )
        
        self.assertEqual(ticket.ticket_type, self.ticket_type)
        self.assertEqual(ticket.user, self.user)
        self.assertEqual(ticket.username, 'testuser1')
        self.assertEqual(ticket.status, 'active')
        self.assertTrue(ticket.is_active)
    
    def test_ticket_expiry(self):
        """Test ticket expiry logic"""
        ticket = Ticket.objects.create(
            ticket_type=self.ticket_type,
            user=self.user,
            username='testuser2',
            password='123456'
        )
        
        # Test is_expired method
        self.assertFalse(ticket.is_expired())
        
        # Test expire method
        ticket.expire()
        self.assertEqual(ticket.status, 'expired')
        self.assertTrue(ticket.is_expired())
    
    def test_ticket_activation(self):
        """Test ticket activation"""
        ticket = Ticket.objects.create(
            ticket_type=self.ticket_type,
            user=self.user,
            username='testuser3',
            password='123456'
        )
        
        # Test activate method
        ticket.activate()
        self.assertEqual(ticket.status, 'used')
        self.assertTrue(ticket.is_used())


class TicketAPITest(TestCase):
    """Test Ticket API endpoints"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.ticket_type = TicketType.objects.create(
            name='1 Hour WiFi',
            ticket_type='time',
            duration_hours=1,
            price=50.00,
            currency='KES',
            created_by=self.user
        )
    
    def test_ticket_type_list_api(self):
        """Test ticket type list API"""
        response = self.client.get('/api/tickets/ticket-types/')
        self.assertEqual(response.status_code, 401)  # Unauthorized without login
    
    def test_ticket_list_api_authenticated(self):
        """Test ticket list API with authentication"""
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get('/api/tickets/tickets/')
        self.assertEqual(response.status_code, 200)
    
    def test_create_ticket_api(self):
        """Test creating ticket via API"""
        self.client.login(email='test@example.com', password='testpass123')
        
        data = {
            'ticket_type': self.ticket_type.id,
            'username': 'testuser4',
            'password': '123456'
        }
        
        response = self.client.post(
            '/api/tickets/tickets/',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Ticket.objects.filter(username='testuser4').exists())


class TicketBatchTest(TestCase):
    """Test TicketBatch model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.ticket_type = TicketType.objects.create(
            name='1 Hour WiFi',
            ticket_type='time',
            duration_hours=1,
            price=50.00,
            currency='KES',
            created_by=self.user
        )
    
    def test_batch_creation(self):
        """Test creating a ticket batch"""
        batch = TicketBatch.objects.create(
            name='Test Batch',
            ticket_type=self.ticket_type,
            user=self.user,
            quantity=5,
            username_prefix='TB',
            password_length=6
        )
        
        self.assertEqual(batch.name, 'Test Batch')
        self.assertEqual(batch.quantity, 5)
        self.assertFalse(batch.is_generated)
    
    def test_batch_generation(self):
        """Test generating tickets for a batch"""
        batch = TicketBatch.objects.create(
            name='Test Batch',
            ticket_type=self.ticket_type,
            user=self.user,
            quantity=3,
            username_prefix='TB',
            password_length=6
        )
        
        # Generate tickets
        batch.generate_tickets()
        
        # Check that tickets were created
        tickets = Ticket.objects.filter(ticket_type=self.ticket_type, user=self.user)
        self.assertEqual(tickets.count(), 3)
        
        # Check that batch is marked as generated
        batch.refresh_from_db()
        self.assertTrue(batch.is_generated)


class TicketSaleTest(TestCase):
    """Test TicketSale model"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123'
        )
        
        self.ticket_type = TicketType.objects.create(
            name='1 Hour WiFi',
            ticket_type='time',
            duration_hours=1,
            price=50.00,
            currency='KES',
            created_by=self.user
        )
        
        self.ticket = Ticket.objects.create(
            ticket_type=self.ticket_type,
            user=self.user,
            username='testuser5',
            password='123456'
        )
    
    def test_ticket_sale_creation(self):
        """Test creating a ticket sale"""
        sale = TicketSale.objects.create(
            ticket=self.ticket,
            sold_by=self.user,
            sale_price=50.00,
            payment_method='cash',
            customer_name='John Doe',
            customer_phone='+254712345678'
        )
        
        self.assertEqual(sale.ticket, self.ticket)
        self.assertEqual(sale.sold_by, self.user)
        self.assertEqual(sale.sale_price, 50.00)
        self.assertEqual(sale.payment_method, 'cash')
        self.assertEqual(sale.customer_name, 'John Doe')