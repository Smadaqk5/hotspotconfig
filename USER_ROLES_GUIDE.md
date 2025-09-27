# 👥 Complete User Role System - MikroTik Hotspot Platform

## 🎯 **User Hierarchy Overview**

The platform implements a comprehensive 4-level user hierarchy with specific roles, permissions, and access controls:

```
Super Admin (You)
    ↓
Hotspot Providers (Your Clients)
    ↓
Cashiers/Operators (Provider Employees)
    ↓
End Users (WiFi Customers)
```

---

## 1. 🔴 **Super Admin (Platform Owner)**

### **Who**: You - the owner of the entire platform
### **Access Level**: Full system-wide access
### **Dashboard**: `/super-admin/`

### **Roles & Responsibilities**:
- ✅ **Manage Providers**: Create, approve, suspend, delete hotspot providers
- ✅ **Global Analytics**: View total providers, tickets, users, revenue across all providers
- ✅ **Provider Oversight**: Drill down into any provider's dashboard (view-only or override)
- ✅ **Billing Management**: Manage provider subscriptions and Pesapal integration
- ✅ **Payment Monitoring**: View all payment logs and revenue summaries
- ✅ **System Configuration**: Update pricing plans, default templates, system settings
- ✅ **Support Management**: Handle technical support requests from providers
- ✅ **User Management**: Manage all users across the platform

### **Key Features**:
- Global statistics dashboard
- Provider management interface
- Revenue analytics across all providers
- System-wide configuration
- Payment monitoring and logs

---

## 2. 🟡 **Hotspot Provider (Your Clients)**

### **Who**: Café owners, small ISPs, cyber cafés, business owners
### **Access Level**: Only their own data & hotspot(s)
### **Dashboard**: `/provider/`

### **Roles & Responsibilities**:
- ✅ **Generate Tickets**: Create WiFi tickets/vouchers (time-based, data-based)
- ✅ **Configure Plans**: Set speed/bandwidth limits for different plans
- ✅ **Revenue Tracking**: Monitor their own sales & revenue (daily/weekly/monthly)
- ✅ **User Management**: Manage their hotspot users and active sessions
- ✅ **Customize Portal**: Brand their captive portal (logo, terms, colors)
- ✅ **Download Configs**: Generate MikroTik configuration files
- ✅ **Cashier Management**: Add/manage sub-users (cashiers/operators)
- ✅ **Analytics**: View detailed reports for their business

### **Key Features**:
- Ticket generation and management
- Revenue tracking and analytics
- Cashier/operator management
- MikroTik config generation
- Custom portal branding
- User session monitoring

---

## 3. 🟢 **Cashier/Operator (Provider Employees)**

### **Who**: Employees of hotspot providers (café staff, shop assistants)
### **Access Level**: Limited (assigned by Provider)
### **Dashboard**: `/cashier/`

### **Roles & Responsibilities**:
- ✅ **Generate Tickets**: Create tickets (if permission granted)
- ✅ **Sell Tickets**: Process ticket sales to customers
- ✅ **View Sales**: See sales data (if permission granted)
- ❌ **Revenue Reports**: Cannot see detailed revenue analytics
- ❌ **Router Configs**: Cannot download or modify router configurations
- ❌ **User Management**: Cannot manage other users

### **Permissions (Configurable by Provider)**:
- `can_generate_tickets`: Generate new tickets
- `can_sell_tickets`: Process ticket sales
- `can_view_sales`: View sales data
- `can_manage_users`: Manage end users
- `can_download_configs`: Download MikroTik configs

### **Key Features**:
- Limited dashboard based on permissions
- Ticket generation (if allowed)
- Ticket sales processing
- Basic sales viewing (if allowed)
- Shift management

---

## 4. 🔵 **End Users (WiFi Customers)**

### **Who**: Customers purchasing WiFi access
### **Access Level**: No dashboard - only captive portal
### **Portal**: `/portal/`

### **Roles & Responsibilities**:
- ✅ **Connect to WiFi**: Access the hotspot network
- ✅ **Enter Ticket Code**: Use voucher code in captive portal
- ✅ **Get Access**: Receive time/data access based on ticket
- ❌ **No Dashboard**: Cannot access any management interface

### **User Experience**:
1. Connect to WiFi hotspot
2. Open browser (redirected to captive portal)
3. Enter ticket/voucher code
4. Get access for purchased time/data
5. If ticket expired/invalid → access denied

---

## 🔐 **Access Control System**

### **Permission Decorators**:
```python
@super_admin_required          # Super Admin only
@provider_required             # Provider only
@cashier_required              # Cashier only
@provider_or_cashier_required  # Provider or Cashier
@revenue_access_required        # Revenue management
@router_config_access_required # Router configuration
@user_management_access_required # User management
@cashier_permission_required   # Specific cashier permission
```

### **Role Checking Methods**:
```python
user.is_super_admin_user()     # Check if Super Admin
user.is_provider()             # Check if Provider
user.is_cashier()              # Check if Cashier
user.is_provider_or_cashier()  # Check if Provider or Cashier
user.can_manage_revenue()      # Check revenue access
user.can_manage_router_configs() # Check router access
user.can_manage_users()        # Check user management
```

---

## 🚀 **Dashboard Access Flow**

### **Login Redirects**:
1. **Super Admin** → `/super-admin/`
2. **Provider** → `/provider/`
3. **Cashier** → `/cashier/`
4. **End User** → `/portal/`

### **URL Structure**:
```
/super-admin/          # Super Admin dashboard
/provider/             # Provider dashboard
/cashier/              # Cashier dashboard
/portal/               # End user portal
/admin/                # Django admin
```

---

## 📊 **Data Isolation**

### **Provider Data Isolation**:
- Providers can only see their own data
- Cashiers can only see their assigned provider's data
- Super Admins can see all data
- End Users have no data access

### **Permission-Based Access**:
- Cashiers have configurable permissions
- Providers control cashier access levels
- Super Admins have full system access
- End Users have no management access

---

## 🎯 **Use Cases**

### **Café Owner (Provider)**:
- Manages their café's WiFi hotspot
- Creates tickets for customers
- Hires cashiers to sell tickets
- Monitors revenue and usage

### **Café Staff (Cashier)**:
- Sells tickets to customers
- Generates tickets when needed
- Cannot see detailed revenue
- Cannot modify router settings

### **Customer (End User)**:
- Buys ticket from café
- Connects to WiFi
- Enters ticket code
- Gets internet access

### **Platform Owner (Super Admin)**:
- Manages all café owners
- Monitors global platform usage
- Handles payments and subscriptions
- Provides technical support

---

## 🔧 **Implementation Features**

### **Security**:
- Role-based access control
- Permission decorators
- Data isolation between providers
- Secure ticket validation

### **Scalability**:
- Multi-tenant architecture
- Provider data isolation
- Configurable permissions
- Role-based dashboards

### **User Experience**:
- Intuitive role-based interfaces
- Mobile-responsive design
- Clear permission boundaries
- Seamless user flow

---

## 🎉 **Complete Platform Ready!**

The MikroTik Hotspot Multi-Level Platform now includes:

✅ **4-Level User Hierarchy** - Super Admin → Provider → Cashier → End User
✅ **Role-Based Access Control** - Proper permissions and data isolation
✅ **Comprehensive Dashboards** - Tailored for each user type
✅ **Permission System** - Configurable access levels
✅ **Captive Portal** - End user ticket validation
✅ **Multi-Tenant Architecture** - Provider data isolation
✅ **Scalable Design** - Ready for multiple providers and users

**Your platform is now ready for production use!** 🚀
