"""
Management command to create sample billing templates
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from billing_templates.models import BillingTemplate, BillingTemplateCategory

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample billing templates for testing'

    def handle(self, *args, **options):
        # Create categories
        categories = [
            {
                'name': 'Basic Plans',
                'description': 'Basic internet plans for small businesses',
                'color': '#3B82F6',
                'sort_order': 1
            },
            {
                'name': 'Premium Plans',
                'description': 'High-speed plans for businesses',
                'color': '#10B981',
                'sort_order': 2
            },
            {
                'name': 'Enterprise Plans',
                'description': 'Enterprise-grade plans for large organizations',
                'color': '#F59E0B',
                'sort_order': 3
            }
        ]
        
        created_categories = {}
        for cat_data in categories:
            category, created = BillingTemplateCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            created_categories[cat_data['name']] = category
            if created:
                self.stdout.write(f'Created category: {category.name}')
        
        # Create billing templates
        templates = [
            # Basic Plans
            {
                'name': 'Basic Daily - 2Mbps',
                'description': 'Basic daily plan with 2Mbps download speed',
                'mbps': 2,
                'upload_mbps': 1,
                'duration_type': 'daily',
                'duration_value': 1,
                'price': 50.00,
                'currency': 'KES',
                'is_popular': True,
                'sort_order': 1,
                'category': 'Basic Plans'
            },
            {
                'name': 'Basic Weekly - 5Mbps',
                'description': 'Weekly plan with 5Mbps download speed',
                'mbps': 5,
                'upload_mbps': 2,
                'duration_type': 'weekly',
                'duration_value': 1,
                'price': 300.00,
                'currency': 'KES',
                'is_popular': True,
                'sort_order': 2,
                'category': 'Basic Plans'
            },
            {
                'name': 'Basic Monthly - 10Mbps',
                'description': 'Monthly plan with 10Mbps download speed',
                'mbps': 10,
                'upload_mbps': 5,
                'duration_type': 'monthly',
                'duration_value': 1,
                'price': 1000.00,
                'currency': 'KES',
                'is_popular': True,
                'sort_order': 3,
                'category': 'Basic Plans'
            },
            
            # Premium Plans
            {
                'name': 'Premium Daily - 10Mbps',
                'description': 'Premium daily plan with 10Mbps download speed',
                'mbps': 10,
                'upload_mbps': 5,
                'duration_type': 'daily',
                'duration_value': 1,
                'price': 100.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 4,
                'category': 'Premium Plans'
            },
            {
                'name': 'Premium Weekly - 20Mbps',
                'description': 'Premium weekly plan with 20Mbps download speed',
                'mbps': 20,
                'upload_mbps': 10,
                'duration_type': 'weekly',
                'duration_value': 1,
                'price': 600.00,
                'currency': 'KES',
                'is_popular': True,
                'sort_order': 5,
                'category': 'Premium Plans'
            },
            {
                'name': 'Premium Monthly - 50Mbps',
                'description': 'Premium monthly plan with 50Mbps download speed',
                'mbps': 50,
                'upload_mbps': 25,
                'duration_type': 'monthly',
                'duration_value': 1,
                'price': 2500.00,
                'currency': 'KES',
                'is_popular': True,
                'sort_order': 6,
                'category': 'Premium Plans'
            },
            
            # Enterprise Plans
            {
                'name': 'Enterprise Daily - 50Mbps',
                'description': 'Enterprise daily plan with 50Mbps download speed',
                'mbps': 50,
                'upload_mbps': 25,
                'duration_type': 'daily',
                'duration_value': 1,
                'price': 500.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 7,
                'category': 'Enterprise Plans'
            },
            {
                'name': 'Enterprise Weekly - 100Mbps',
                'description': 'Enterprise weekly plan with 100Mbps download speed',
                'mbps': 100,
                'upload_mbps': 50,
                'duration_type': 'weekly',
                'duration_value': 1,
                'price': 2000.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 8,
                'category': 'Enterprise Plans'
            },
            {
                'name': 'Enterprise Monthly - 200Mbps',
                'description': 'Enterprise monthly plan with 200Mbps download speed',
                'mbps': 200,
                'upload_mbps': 100,
                'duration_type': 'monthly',
                'duration_value': 1,
                'price': 8000.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 9,
                'category': 'Enterprise Plans'
            },
            
            # Hourly Plans
            {
                'name': 'Hourly - 5Mbps',
                'description': 'Hourly plan with 5Mbps download speed',
                'mbps': 5,
                'upload_mbps': 2,
                'duration_type': 'hourly',
                'duration_value': 1,
                'price': 10.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 10,
                'category': 'Basic Plans'
            },
            {
                'name': 'Hourly - 10Mbps',
                'description': 'Hourly plan with 10Mbps download speed',
                'mbps': 10,
                'upload_mbps': 5,
                'duration_type': 'hourly',
                'duration_value': 1,
                'price': 20.00,
                'currency': 'KES',
                'is_popular': False,
                'sort_order': 11,
                'category': 'Premium Plans'
            }
        ]
        
        # Get or create a superuser for created_by field
        try:
            admin_user = User.objects.filter(is_superuser=True).first()
            if not admin_user:
                admin_user = User.objects.create_superuser(
                    username='admin',
                    email='admin@example.com',
                    password='admin123'
                )
        except Exception:
            admin_user = None
        
        created_count = 0
        for template_data in templates:
            category_name = template_data.pop('category')
            category = created_categories[category_name]
            
            template, created = BillingTemplate.objects.get_or_create(
                name=template_data['name'],
                defaults={
                    **template_data,
                    'created_by': admin_user
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'Created template: {template.name}')
                
                # Assign to category
                template.category_assignments.create(category=category)
            else:
                self.stdout.write(f'Template already exists: {template.name}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} billing templates')
        )
