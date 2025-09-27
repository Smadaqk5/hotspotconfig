/**
 * Test data fixtures for MikroTik Hotspot Testing
 */

export const testUsers = {
  admin: {
    username: 'admin',
    email: 'admin@hotspotconfig.com',
    password: 'admin123456',
    first_name: 'Admin',
    last_name: 'User',
    phone_number: '+254700000000',
    company_name: 'Hotspot Config Admin'
  },
  operator: {
    username: 'operator1',
    email: 'operator@hotspotconfig.com',
    password: 'operator123456',
    first_name: 'John',
    last_name: 'Operator',
    phone_number: '+254700000001',
    company_name: 'Test ISP'
  },
  customer: {
    username: 'customer1',
    email: 'customer@hotspotconfig.com',
    password: 'customer123456',
    first_name: 'Jane',
    last_name: 'Customer',
    phone_number: '+254700000002',
    company_name: 'Customer Company'
  }
};

export const testTickets = {
  timeBased: {
    name: '1 Hour Ticket',
    type: 'time',
    duration: 3600, // 1 hour in seconds
    price: 50,
    description: '1 hour internet access'
  },
  dataBased: {
    name: '1GB Data Ticket',
    type: 'data',
    data_limit: 1024, // 1GB in MB
    price: 100,
    description: '1GB data allowance'
  }
};

export const testConfigs = {
  mikrotikModel: 'RB750',
  bandwidthProfile: 'Basic',
  voucherType: 'time',
  duration: 3600,
  price: 50
};

export const testPayments = {
  pesapal: {
    success: {
      merchant_reference: 'TEST_REF_001',
      payment_method: 'M-PESA',
      amount: 2500,
      currency: 'KES',
      status: 'COMPLETED'
    },
    failed: {
      merchant_reference: 'TEST_REF_002',
      payment_method: 'M-PESA',
      amount: 2500,
      currency: 'KES',
      status: 'FAILED'
    }
  }
};

export const testSubscriptions = {
  basic: {
    name: 'Basic Plan',
    price: 2500,
    duration_days: 30,
    features: ['Unlimited tickets', 'Basic support']
  },
  professional: {
    name: 'Professional Plan',
    price: 5000,
    duration_days: 30,
    features: ['Unlimited tickets', 'Advanced analytics', 'Priority support']
  }
};
