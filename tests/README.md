# MikroTik Hotspot Ticketing System - End-to-End Tests

This directory contains comprehensive end-to-end tests for the MikroTik Hotspot Ticketing & Config Platform using Playwright.

## 🧪 Test Coverage

### 1. Landing Page Tests (`landing-page.spec.ts`)
- ✅ Homepage loads successfully
- ✅ Hero section content and CTAs
- ✅ Navigation links functionality
- ✅ Pricing plans display
- ✅ Features section
- ✅ Testimonials and FAQ
- ✅ Mobile responsiveness

### 2. Authentication Tests (`authentication.spec.ts`)
- ✅ User registration with valid/invalid data
- ✅ Login with username/email
- ✅ Password validation
- ✅ Logout functionality
- ✅ Form validation
- ✅ Remember me functionality
- ✅ Forgot password flow

### 3. Subscription & Payments (`subscription-payments.spec.ts`)
- ✅ Subscription plan display
- ✅ Pesapal payment integration
- ✅ Payment success/failure handling
- ✅ Subscription management
- ✅ Payment history
- ✅ Billing & invoicing
- ✅ Subscription renewal

### 4. Dashboard Tests (`dashboard.spec.ts`)
- ✅ Dashboard overview
- ✅ Stats cards display
- ✅ Quick actions
- ✅ Recent activity
- ✅ Subscription status
- ✅ Navigation functionality

### 5. Ticket Management (`ticket-management.spec.ts`)
- ✅ Time-based ticket generation (1h, 1d)
- ✅ Data-based ticket generation (1GB, 5GB)
- ✅ Ticket validation
- ✅ Ticket display and management
- ✅ Ticket expiry logic
- ✅ Ticket actions (delete, toggle status)
- ✅ Ticket export (CSV, Excel, PDF)
- ✅ Ticket printing
- ✅ Ticket analytics

### 6. Config Generator (`config-generator.spec.ts`)
- ✅ MikroTik model selection
- ✅ Configuration generation
- ✅ Configuration download (.rsc, .txt)
- ✅ Configuration preview
- ✅ Template management
- ✅ Configuration history
- ✅ Configuration validation

### 7. Admin Panel (`admin-panel.spec.ts`)
- ✅ Admin dashboard
- ✅ User management
- ✅ Billing template management
- ✅ Config template management
- ✅ Payment logs
- ✅ System settings
- ✅ Permission levels
- ✅ System health

### 8. Sales Tracking (`sales-tracking.spec.ts`)
- ✅ Revenue calculation
- ✅ Revenue dashboard
- ✅ Analytics & reports
- ✅ Date range filtering
- ✅ Export functionality
- ✅ Real-time updates
- ✅ Performance metrics
- ✅ Comparative analysis

## 🚀 Running Tests

### Prerequisites
```bash
# Install Node.js dependencies
npm install

# Install Playwright browsers
npx playwright install

# Install Python dependencies
pip install -r requirements.txt
```

### Local Testing
```bash
# Run all tests
npm test

# Run tests in headed mode (see browser)
npm run test:headed

# Run tests with UI mode
npm run test:ui

# Run specific test file
npx playwright test landing-page.spec.ts

# Run tests for specific browser
npx playwright test --project=chromium

# Debug tests
npm run test:debug
```

### CI/CD Testing
```bash
# Tests run automatically on:
# - Push to main/develop branches
# - Pull requests
# - Daily at 2 AM (scheduled)
# - Multiple browsers (Chrome, Firefox, Safari)
# - Multiple Node.js versions (18, 20)
```

## 📊 Test Reports

### Local Reports
```bash
# Generate HTML report
npm run test:report

# View test results
npx playwright show-report
```

### CI/CD Reports
- Test results are uploaded as artifacts
- Videos are captured on test failures
- Reports are available for 30 days
- Merged reports combine all browser results

## 🔧 Configuration

### Test Configuration (`playwright.config.ts`)
- **Base URL**: `http://localhost:8000`
- **Browsers**: Chrome, Firefox, Safari
- **Mobile**: iPhone 12, Pixel 5
- **Retries**: 2 on CI, 0 locally
- **Screenshots**: On failure
- **Videos**: On failure
- **Traces**: On first retry

### Test Data (`tests/fixtures/test-data.ts`)
- Test users (admin, operator, customer)
- Test tickets (time-based, data-based)
- Test configurations
- Test payments (Pesapal mocks)
- Test subscriptions

### Database Setup (`tests/fixtures/database.ts`)
- Database setup/teardown
- Test user creation/deletion
- Data cleanup between tests

## 🎯 Test Scenarios

### Critical User Journeys
1. **New User Registration** → Dashboard → Generate Tickets → Sell Tickets
2. **Admin Login** → User Management → System Settings
3. **Payment Flow** → Pesapal Integration → Subscription Activation
4. **Ticket Generation** → Config Download → Router Setup

### Edge Cases
- Invalid form submissions
- Network failures
- Payment timeouts
- Database errors
- Permission violations

### Performance Tests
- Page load times
- API response times
- Database query performance
- File download speeds

## 🐛 Debugging Tests

### Debug Mode
```bash
# Run in debug mode
npx playwright test --debug

# Debug specific test
npx playwright test landing-page.spec.ts --debug
```

### Test Artifacts
- **Screenshots**: Captured on failure
- **Videos**: Recorded for failed tests
- **Traces**: Detailed execution traces
- **Logs**: Console and network logs

### Common Issues
1. **Timeout errors**: Increase timeout in config
2. **Element not found**: Check selectors and wait conditions
3. **Network issues**: Mock external APIs
4. **Database errors**: Ensure test database is clean

## 📈 Test Metrics

### Coverage Goals
- **Functional Coverage**: 100% of user stories
- **Browser Coverage**: Chrome, Firefox, Safari
- **Device Coverage**: Desktop, Mobile, Tablet
- **API Coverage**: All endpoints tested

### Performance Targets
- **Page Load**: < 3 seconds
- **API Response**: < 1 second
- **Test Execution**: < 10 minutes per browser
- **CI/CD Pipeline**: < 30 minutes total

## 🔄 Continuous Integration

### GitHub Actions Workflow
- **Triggers**: Push, PR, Schedule
- **Matrix**: Node.js 18/20, 3 browsers
- **Artifacts**: Reports, videos, traces
- **Notifications**: Slack/Email on failure

### Test Environment
- **Database**: PostgreSQL (Supabase)
- **Server**: Django development server
- **Browser**: Playwright managed browsers
- **OS**: Ubuntu Latest

## 📝 Writing New Tests

### Test Structure
```typescript
import { test, expect } from '@playwright/test';

test.describe('Feature Name', () => {
  test.beforeEach(async ({ page }) => {
    // Setup code
  });

  test('should do something', async ({ page }) => {
    // Test steps
    await page.goto('/');
    await page.click('button');
    await expect(page.locator('text')).toBeVisible();
  });
});
```

### Best Practices
1. **Use data-testid attributes** for reliable selectors
2. **Wait for elements** before interacting
3. **Mock external APIs** for consistent testing
4. **Clean up data** between tests
5. **Use page objects** for complex interactions

## 🚨 Troubleshooting

### Common Issues
1. **Tests flaky**: Add proper waits and retries
2. **Selectors break**: Use stable selectors (data-testid)
3. **Database conflicts**: Use transactions or cleanup
4. **Network timeouts**: Mock external services

### Getting Help
- Check test logs in CI/CD artifacts
- Review screenshots/videos for failures
- Use debug mode for step-by-step execution
- Consult Playwright documentation

## 📚 Resources

- [Playwright Documentation](https://playwright.dev/)
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)
- [GitHub Actions](https://docs.github.com/en/actions)
- [Test Best Practices](https://playwright.dev/docs/best-practices)
