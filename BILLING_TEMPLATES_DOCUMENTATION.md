# Billing Templates Documentation

## Overview

The Billing Templates feature allows administrators to create predefined billing plans with specific bandwidth (Mbps) and duration settings. Users can select these templates when generating MikroTik configurations, and the system will automatically apply the appropriate bandwidth and duration settings to the generated configuration.

## Features

### 1. Billing Template Management
- **Bandwidth Configuration**: Set download and upload speeds in Mbps
- **Duration Settings**: Configure duration types (hourly, daily, weekly, monthly) with values
- **Pricing**: Set prices in different currencies (default: KES)
- **Categories**: Organize templates into categories (Basic, Premium, Enterprise)
- **Popular Plans**: Mark templates as popular for highlighting
- **Sort Order**: Control display order of templates

### 2. Template Variables
When a billing template is used in config generation, the following variables are available:

```jinja2
{{ billing_template.name }}           # Template name
{{ bandwidth_mbps }}                 # Download speed in Mbps
{{ upload_mbps }}                    # Upload speed in Mbps
{{ duration_seconds }}               # Duration in seconds
{{ bandwidth_bytes }}                # Bandwidth in bytes per second
{{ upload_bandwidth_bytes }}         # Upload bandwidth in bytes per second
{{ duration_type }}                  # Duration type (hourly, daily, etc.)
{{ duration_value }}                 # Duration value
{{ billing_template.price }}         # Template price
{{ billing_template.currency }}      # Currency
```

### 3. API Endpoints

#### Public Endpoints (No Authentication Required)
- `GET /api/billing-templates/` - List all active billing templates
- `GET /api/billing-templates/popular/` - List popular billing templates
- `GET /api/billing-templates/categories/` - List billing template categories
- `GET /api/billing-templates/category/{id}/` - Get templates by category
- `GET /api/billing-templates/search/` - Search templates with filters
- `GET /api/billing-templates/{id}/` - Get specific template details

#### Authenticated Endpoints
- `GET /api/billing-templates/{id}/config-data/` - Get template data for config generation
- `GET /api/billing-templates/usage/` - Get user's billing template usage
- `POST /api/billing-templates/track-usage/` - Track template usage
- `GET /api/billing-templates/stats/` - Get billing template statistics

### 4. Admin Interface

#### Billing Template Admin
- **List View**: Shows templates with bandwidth, duration, price, and usage statistics
- **Bulk Actions**: Activate/deactivate, mark as popular, bulk price updates
- **Advanced Filtering**: Filter by active status, popularity, duration type
- **Search**: Search by name and description

#### Category Management
- **Categories**: Organize templates into logical groups
- **Color Coding**: Visual distinction with hex color codes
- **Template Count**: Shows number of active templates per category

#### Usage Tracking
- **Usage Records**: Track which templates are used by which users
- **Statistics**: View usage patterns and popular templates
- **Dashboard**: Comprehensive statistics dashboard

### 5. Sample Templates

The system comes with pre-configured sample templates:

#### Basic Plans
- **Basic Daily - 2Mbps**: 2Mbps down, 1Mbps up, 1 day, KES 50
- **Basic Weekly - 5Mbps**: 5Mbps down, 2Mbps up, 1 week, KES 300
- **Basic Monthly - 10Mbps**: 10Mbps down, 5Mbps up, 1 month, KES 1000

#### Premium Plans
- **Premium Daily - 10Mbps**: 10Mbps down, 5Mbps up, 1 day, KES 100
- **Premium Weekly - 20Mbps**: 20Mbps down, 10Mbps up, 1 week, KES 600
- **Premium Monthly - 50Mbps**: 50Mbps down, 25Mbps up, 1 month, KES 2500

#### Enterprise Plans
- **Enterprise Daily - 50Mbps**: 50Mbps down, 25Mbps up, 1 day, KES 500
- **Enterprise Weekly - 100Mbps**: 100Mbps down, 50Mbps up, 1 week, KES 2000
- **Enterprise Monthly - 200Mbps**: 200Mbps down, 100Mbps up, 1 month, KES 8000

#### Hourly Plans
- **Hourly - 5Mbps**: 5Mbps down, 2Mbps up, 1 hour, KES 10
- **Hourly - 10Mbps**: 10Mbps down, 5Mbps up, 1 hour, KES 20

### 6. Configuration Generation

When generating a MikroTik configuration with a billing template:

1. **Template Selection**: User selects a billing template
2. **Variable Injection**: Template variables are injected into the config template
3. **Bandwidth Configuration**: Download/upload speeds are set according to template
4. **Duration Settings**: Session timeouts and limits are configured
5. **Usage Tracking**: Template usage is recorded for analytics

### 7. MikroTik Template Example

```jinja2
# Hotspot Configuration with Billing Template
# Template: {{ billing_template.name }}
# Bandwidth: {{ bandwidth_mbps }}Mbps down / {{ upload_mbps }}Mbps up
# Duration: {{ duration_value }} {{ duration_type }}(s)

# User Profile
/ip hotspot user profile add name="{{ billing_template.name }}" 
    rate-limit="{{ bandwidth_mbps }}M/{{ upload_mbps }}M"
    session-timeout={{ duration_seconds }}

# Queue Configuration
/queue simple add name="{{ billing_template.name }}_queue" 
    target=ether1 
    max-limit="{{ bandwidth_mbps }}M/{{ upload_mbps }}M"
```

### 8. Database Schema

#### BillingTemplate Model
```python
class BillingTemplate(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    mbps = models.PositiveIntegerField()  # Download speed
    upload_mbps = models.PositiveIntegerField()  # Upload speed
    duration_type = models.CharField(choices=DURATION_CHOICES)
    duration_value = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    is_active = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)
```

#### BillingTemplateUsage Model
```python
class BillingTemplateUsage(models.Model):
    template = models.ForeignKey(BillingTemplate)
    user = models.ForeignKey(User)
    generated_config = models.ForeignKey(GeneratedConfig)
    used_at = models.DateTimeField(auto_now_add=True)
```

### 9. Usage Examples

#### API Usage
```python
# Get all billing templates
GET /api/billing-templates/

# Get popular templates
GET /api/billing-templates/popular/

# Search templates
GET /api/billing-templates/search/?min_mbps=5&max_mbps=50&duration_type=monthly

# Generate config with billing template
POST /api/config/generate/
{
    "template_id": 1,
    "billing_template_id": 3,
    "config_name": "My Hotspot Config",
    "hotspot_name": "MyHotspot",
    "hotspot_ip": "192.168.1.1",
    "dns_servers": "8.8.8.8,8.8.4.4",
    "voucher_type_id": 1,
    "bandwidth_profile_id": 1
}
```

#### Admin Usage
1. **Create Template**: Go to Admin → Billing Templates → Add Template
2. **Set Bandwidth**: Configure download/upload speeds
3. **Set Duration**: Choose duration type and value
4. **Set Price**: Enter price and currency
5. **Categorize**: Assign to appropriate category
6. **Activate**: Mark as active and optionally popular

### 10. Benefits

1. **Standardization**: Consistent billing plans across all configurations
2. **Flexibility**: Easy to add new plans and modify existing ones
3. **Analytics**: Track which plans are most popular
4. **Automation**: Automatic bandwidth and duration configuration
5. **User Experience**: Clear pricing and plan options for users
6. **Admin Control**: Full control over plan creation and management

### 11. Future Enhancements

- **Dynamic Pricing**: Time-based pricing adjustments
- **Plan Combinations**: Multiple template combinations
- **Usage Analytics**: Detailed usage statistics and reporting
- **Auto-scaling**: Automatic plan recommendations based on usage
- **Integration**: Integration with external billing systems
- **Notifications**: Alerts for plan changes and updates

## Conclusion

The Billing Templates feature provides a comprehensive solution for managing MikroTik hotspot billing plans. It offers flexibility, ease of use, and powerful analytics capabilities while maintaining the simplicity needed for effective hotspot management.
