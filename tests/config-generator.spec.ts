/**
 * Config Generator Tests
 * Tests MikroTik configuration generation and download functionality
 */

import { test, expect } from '@playwright/test';
import { testUsers, testConfigs } from './fixtures/test-data';

test.describe('Config Generator', () => {
  test.beforeEach(async ({ page }) => {
    // Login as customer
    await page.goto('/login/');
    await page.fill('input[name="username"]', testUsers.customer.username);
    await page.fill('input[name="password"]', testUsers.customer.password);
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });

  test.describe('Config Template Selection', () => {
    test('should display available MikroTik models', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Check MikroTik model selection
      await expect(page.locator('h2')).toContainText('Generate MikroTik Configuration');
      await expect(page.locator('label')).toContainText('MikroTik Model');
      
      // Check model options
      const modelSelect = page.locator('select[name="mikrotik_model"]');
      await expect(modelSelect).toBeVisible();
      await expect(modelSelect.locator('option')).toContainText('RB750');
      await expect(modelSelect.locator('option')).toContainText('RB760');
      await expect(modelSelect.locator('option')).toContainText('RB450G');
    });

    test('should display bandwidth profiles', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Check bandwidth profile selection
      await expect(page.locator('label')).toContainText('Bandwidth Profile');
      
      // Check profile options
      const profileSelect = page.locator('select[name="bandwidth_profile"]');
      await expect(profileSelect).toBeVisible();
      await expect(profileSelect.locator('option')).toContainText('Basic');
      await expect(profileSelect.locator('option')).toContainText('Standard');
      await expect(profileSelect.locator('option')).toContainText('Premium');
    });

    test('should display voucher types', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Check voucher type selection
      await expect(page.locator('label')).toContainText('Voucher Type');
      
      // Check type options
      const typeSelect = page.locator('select[name="voucher_type"]');
      await expect(typeSelect).toBeVisible();
      await expect(typeSelect.locator('option')).toContainText('Time-based');
      await expect(typeSelect.locator('option')).toContainText('Data-based');
    });
  });

  test.describe('Configuration Generation', () => {
    test('should generate basic hotspot configuration', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Fill configuration form
      await page.selectOption('select[name="mikrotik_model"]', testConfigs.mikrotikModel);
      await page.selectOption('select[name="bandwidth_profile"]', testConfigs.bandwidthProfile);
      await page.selectOption('select[name="voucher_type"]', testConfigs.voucherType);
      await page.fill('input[name="duration"]', testConfigs.duration.toString());
      await page.fill('input[name="price"]', testConfigs.price.toString());
      await page.fill('input[name="hotspot_name"]', 'Test Hotspot');
      await page.fill('input[name="dns_server"]', '8.8.8.8');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Configuration generated successfully');
    });

    test('should generate advanced hotspot configuration', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Fill advanced configuration
      await page.selectOption('select[name="mikrotik_model"]', 'RB760');
      await page.selectOption('select[name="bandwidth_profile"]', 'Premium');
      await page.selectOption('select[name="voucher_type"]', 'data');
      await page.fill('input[name="data_limit"]', '1024');
      await page.fill('input[name="price"]', '200');
      await page.fill('input[name="hotspot_name"]', 'Premium Hotspot');
      await page.fill('input[name="dns_server"]', '1.1.1.1');
      await page.check('input[name="enable_captive_portal"]');
      await page.fill('textarea[name="custom_message"]', 'Welcome to our hotspot!');
      
      // Submit form
      await page.click('button[type="submit"]');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Configuration generated successfully');
    });

    test('should validate required fields', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Try to submit empty form
      await page.click('button[type="submit"]');
      
      // Should show validation errors
      await expect(page.locator('input[name="mikrotik_model"]:invalid')).toBeVisible();
      await expect(page.locator('input[name="bandwidth_profile"]:invalid')).toBeVisible();
      await expect(page.locator('input[name="voucher_type"]:invalid')).toBeVisible();
    });
  });

  test.describe('Configuration Download', () => {
    test('should download .rsc configuration file', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Fill and submit form
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.selectOption('select[name="bandwidth_profile"]', 'Basic');
      await page.selectOption('select[name="voucher_type"]', 'time');
      await page.fill('input[name="duration"]', '3600');
      await page.fill('input[name="price"]', '50');
      await page.fill('input[name="hotspot_name"]', 'Test Hotspot');
      await page.click('button[type="submit"]');
      
      // Click download button
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Download .rsc")');
      const download = await downloadPromise;
      
      // Should download .rsc file
      expect(download.suggestedFilename()).toContain('.rsc');
    });

    test('should download configuration as text file', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Generate configuration
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.selectOption('select[name="bandwidth_profile"]', 'Basic');
      await page.selectOption('select[name="voucher_type"]', 'time');
      await page.fill('input[name="duration"]', '3600');
      await page.fill('input[name="price"]', '50');
      await page.fill('input[name="hotspot_name"]', 'Test Hotspot');
      await page.click('button[type="submit"]');
      
      // Click download as text
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Download .txt")');
      const download = await downloadPromise;
      
      // Should download .txt file
      expect(download.suggestedFilename()).toContain('.txt');
    });

    test('should preview configuration before download', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Generate configuration
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.selectOption('select[name="bandwidth_profile"]', 'Basic');
      await page.selectOption('select[name="voucher_type"]', 'time');
      await page.fill('input[name="duration"]', '3600');
      await page.fill('input[name="price"]', '50');
      await page.fill('input[name="hotspot_name"]', 'Test Hotspot');
      await page.click('button[type="submit"]');
      
      // Click preview button
      await page.click('button:has-text("Preview")');
      
      // Should show preview modal
      await expect(page.locator('text=Configuration Preview')).toBeVisible();
      await expect(page.locator('pre')).toBeVisible();
    });
  });

  test.describe('Configuration Content', () => {
    test('should substitute placeholders correctly', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Fill form with specific values
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.selectOption('select[name="bandwidth_profile"]', 'Basic');
      await page.selectOption('select[name="voucher_type"]', 'time');
      await page.fill('input[name="duration"]', '3600');
      await page.fill('input[name="price"]', '50');
      await page.fill('input[name="hotspot_name"]', 'My Hotspot');
      await page.fill('input[name="dns_server"]', '8.8.8.8');
      await page.click('button[type="submit"]');
      
      // Preview configuration
      await page.click('button:has-text("Preview")');
      
      // Check placeholders are substituted
      await expect(page.locator('pre')).toContainText('My Hotspot');
      await expect(page.locator('pre')).toContainText('3600');
      await expect(page.locator('pre')).toContainText('50');
      await expect(page.locator('pre')).toContainText('8.8.8.8');
    });

    test('should include correct MikroTik commands', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Generate configuration
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.selectOption('select[name="bandwidth_profile"]', 'Basic');
      await page.selectOption('select[name="voucher_type"]', 'time');
      await page.fill('input[name="duration"]', '3600');
      await page.fill('input[name="price"]', '50');
      await page.fill('input[name="hotspot_name"]', 'Test Hotspot');
      await page.click('button[type="submit"]');
      
      // Preview configuration
      await page.click('button:has-text("Preview")');
      
      // Check MikroTik commands are present
      await expect(page.locator('pre')).toContainText('/ip hotspot');
      await expect(page.locator('pre')).toContainText('/ip hotspot user');
      await expect(page.locator('pre')).toContainText('/ip hotspot profile');
    });

    test('should include bandwidth profile settings', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Generate configuration with specific bandwidth
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.selectOption('select[name="bandwidth_profile"]', 'Premium');
      await page.selectOption('select[name="voucher_type"]', 'time');
      await page.fill('input[name="duration"]', '3600');
      await page.fill('input[name="price"]', '100');
      await page.fill('input[name="hotspot_name"]', 'Premium Hotspot');
      await page.click('button[type="submit"]');
      
      // Preview configuration
      await page.click('button:has-text("Preview")');
      
      // Check bandwidth settings
      await expect(page.locator('pre')).toContainText('rate-limit');
      await expect(page.locator('pre')).toContainText('10M/10M');
    });
  });

  test.describe('Configuration Templates', () => {
    test('should display available templates', async ({ page }) => {
      await page.goto('/dashboard/config-generator/templates/');
      
      // Check templates section
      await expect(page.locator('h2')).toContainText('Configuration Templates');
      
      // Check template cards
      const templateCards = page.locator('.grid > div');
      await expect(templateCards).toHaveCount(3);
      
      // Check template names
      await expect(page.locator('h3')).toContainText('Basic Hotspot');
      await expect(page.locator('h3')).toContainText('Advanced Hotspot');
      await expect(page.locator('h3')).toContainText('Enterprise Hotspot');
    });

    test('should allow template selection', async ({ page }) => {
      await page.goto('/dashboard/config-generator/templates/');
      
      // Click on basic template
      await page.click('button:has-text("Use Template")').first();
      
      // Should redirect to config generator with template pre-filled
      await expect(page).toHaveURL(/.*config-generator/);
      await expect(page.locator('select[name="mikrotik_model"]')).toHaveValue('RB750');
    });

    test('should allow custom template creation', async ({ page }) => {
      await page.goto('/dashboard/config-generator/templates/');
      
      // Click create template
      await page.click('button:has-text("Create Template")');
      
      // Should open template creation form
      await expect(page.locator('h2')).toContainText('Create Custom Template');
      await expect(page.locator('input[name="template_name"]')).toBeVisible();
    });
  });

  test.describe('Configuration History', () => {
    test('should display generated configurations', async ({ page }) => {
      await page.goto('/dashboard/config-generator/history/');
      
      // Check history table
      await expect(page.locator('table')).toBeVisible();
      await expect(page.locator('th')).toContainText('Configuration Name');
      await expect(page.locator('th')).toContainText('Model');
      await expect(page.locator('th')).toContainText('Generated');
      await expect(page.locator('th')).toContainText('Actions');
    });

    test('should allow re-downloading previous configurations', async ({ page }) => {
      await page.goto('/dashboard/config-generator/history/');
      
      // Click download button for first configuration
      const downloadPromise = page.waitForEvent('download');
      await page.click('button:has-text("Download")').first();
      const download = await downloadPromise;
      
      // Should download configuration file
      expect(download.suggestedFilename()).toContain('.rsc');
    });

    test('should allow deleting configuration history', async ({ page }) => {
      await page.goto('/dashboard/config-generator/history/');
      
      // Click delete button for first configuration
      await page.click('button:has-text("Delete")').first();
      
      // Confirm deletion
      await page.click('button:has-text("Confirm Delete")');
      
      // Should show success message
      await expect(page.locator('.bg-green-100')).toContainText('Configuration deleted successfully');
    });
  });

  test.describe('Configuration Validation', () => {
    test('should validate MikroTik model compatibility', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Select incompatible model and profile
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.selectOption('select[name="bandwidth_profile"]', 'Enterprise');
      await page.click('button[type="submit"]');
      
      // Should show compatibility warning
      await expect(page.locator('.bg-yellow-100')).toContainText('Model compatibility warning');
    });

    test('should validate bandwidth limits', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Set invalid bandwidth values
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.selectOption('select[name="bandwidth_profile"]', 'Custom');
      await page.fill('input[name="upload_speed"]', '1000'); // Too high for RB750
      await page.fill('input[name="download_speed"]', '1000');
      await page.click('button[type="submit"]');
      
      // Should show bandwidth warning
      await expect(page.locator('.bg-yellow-100')).toContainText('Bandwidth limit warning');
    });

    test('should validate network settings', async ({ page }) => {
      await page.goto('/dashboard/config-generator/');
      
      // Set invalid network settings
      await page.selectOption('select[name="mikrotik_model"]', 'RB750');
      await page.fill('input[name="dns_server"]', 'invalid-dns');
      await page.fill('input[name="gateway"]', '192.168.1.999'); // Invalid IP
      await page.click('button[type="submit"]');
      
      // Should show validation errors
      await expect(page.locator('.bg-red-100')).toContainText('Invalid DNS server');
      await expect(page.locator('.bg-red-100')).toContainText('Invalid gateway IP');
    });
  });
});
