/**
 * Pesapal payment API mocks for testing
 */

export const pesapalMocks = {
  success: {
    url: 'https://cybqa.pesapal.com/pesapalv3/api/Transactions/GetTransactionStatus',
    method: 'GET',
    response: {
      payment_method: 'M-PESA',
      amount: 2500,
      currency: 'KES',
      status: 'COMPLETED',
      merchant_reference: 'TEST_REF_001',
      pesapal_transaction_id: 'PESAPAL_TXN_001',
      payment_account: '254700000000'
    }
  },
  
  failed: {
    url: 'https://cybqa.pesapal.com/pesapalv3/api/Transactions/GetTransactionStatus',
    method: 'GET',
    response: {
      payment_method: 'M-PESA',
      amount: 2500,
      currency: 'KES',
      status: 'FAILED',
      merchant_reference: 'TEST_REF_002',
      pesapal_transaction_id: 'PESAPAL_TXN_002',
      error_message: 'Insufficient funds'
    }
  },
  
  pending: {
    url: 'https://cybqa.pesapal.com/pesapalv3/api/Transactions/GetTransactionStatus',
    method: 'GET',
    response: {
      payment_method: 'M-PESA',
      amount: 2500,
      currency: 'KES',
      status: 'PENDING',
      merchant_reference: 'TEST_REF_003',
      pesapal_transaction_id: 'PESAPAL_TXN_003'
    }
  }
};

export const mockPesapalAPI = (page: any, scenario: 'success' | 'failed' | 'pending' = 'success') => {
  const mock = pesapalMocks[scenario];
  
  return page.route(mock.url, route => {
    route.fulfill({
      status: 200,
      contentType: 'application/json',
      body: JSON.stringify(mock.response)
    });
  });
};
