from accounts.models import Provider, User, Cashier

# Get the first provider
provider = Provider.objects.first()
if provider:
    print(f'Found provider: {provider.business_name}')
    
    # Create cashier user
    user, created = User.objects.get_or_create(
        email='cashier@test.com',
        defaults={
            'username': 'testcashier',
            'first_name': 'Test',
            'last_name': 'Cashier',
            'user_type': 'cashier',
            'is_verified': True,
            'is_active': True,
        }
    )
    
    if created:
        user.set_password('Cashier123!')
        user.save()
        print('Created cashier user: cashier@test.com')
    else:
        print('Cashier user already exists')
    
    # Create cashier profile
    cashier, cashier_created = Cashier.objects.get_or_create(
        user=user,
        defaults={
            'provider': provider,
            'employee_id': 'CASH001',
            'can_generate_tickets': True,
            'can_sell_tickets': True,
            'can_view_sales': True,
            'can_manage_users': False,
            'can_download_configs': False,
        }
    )
    
    if cashier_created:
        print('Created cashier profile')
    else:
        print('Cashier profile already exists')
    
    print('Cashier Login: cashier@test.com / Cashier123!')
else:
    print('No providers found')
