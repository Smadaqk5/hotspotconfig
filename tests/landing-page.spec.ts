/**
 * Landing Page Tests
 * Tests the homepage functionality and navigation
 */

import { test, expect } from '@playwright/test';

test.describe('Landing Page', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should load homepage successfully', async ({ page }) => {
    await expect(page).toHaveTitle(/MikroTik Hotspot Ticketing System/);
    await expect(page.locator('h1')).toContainText('Monetize Your WiFi Easily');
  });

  test('should display hero section with correct content', async ({ page }) => {
    // Check hero section is visible
    const heroSection = page.locator('section.bg-gradient-to-r');
    await expect(heroSection).toBeVisible();
    
    // Check main heading
    await expect(page.locator('h1')).toContainText('Monetize Your WiFi Easily');
    await expect(page.locator('h1')).toContainText('With MikroTik Hotspot Tickets');
    
    // Check description
    await expect(page.locator('p')).toContainText('Generate, sell, and manage internet tickets/vouchers');
    
    // Check CTA buttons
    await expect(page.locator('a[href="#pricing"]')).toContainText('Start Selling Tickets');
    await expect(page.locator('a[href="#features"]')).toContainText('How It Works');
  });

  test('should have working navigation links', async ({ page }) => {
    // Test navigation links
    await expect(page.locator('a[href="/"]')).toContainText('Home');
    await expect(page.locator('a[href="#pricing"]')).toContainText('Pricing');
    await expect(page.locator('a[href="#features"]')).toContainText('Features');
    await expect(page.locator('a[href="#contact"]')).toContainText('Contact');
    
    // Test navigation functionality
    await page.click('a[href="#pricing"]');
    await expect(page.locator('#pricing')).toBeVisible();
    
    await page.click('a[href="#features"]');
    await expect(page.locator('#features')).toBeVisible();
  });

  test('should display pricing plans correctly', async ({ page }) => {
    // Navigate to pricing section
    await page.click('a[href="#pricing"]');
    
    // Check pricing section is visible
    await expect(page.locator('#pricing')).toBeVisible();
    await expect(page.locator('h2')).toContainText('Simple, Transparent Pricing');
    
    // Check all three pricing plans
    const pricingPlans = page.locator('.grid.grid-cols-1.md\\:grid-cols-3 > div');
    await expect(pricingPlans).toHaveCount(3);
    
    // Check Basic plan
    await expect(page.locator('h3')).toContainText('Basic');
    await expect(page.locator('h3')).toContainText('KES 2,500');
    
    // Check Professional plan
    await expect(page.locator('h3')).toContainText('Professional');
    await expect(page.locator('h3')).toContainText('KES 5,000');
    
    // Check Enterprise plan
    await expect(page.locator('h3')).toContainText('Enterprise');
    await expect(page.locator('h3')).toContainText('KES 10,000');
  });

  test('should have working subscribe buttons', async ({ page }) => {
    // Navigate to pricing section
    await page.click('a[href="#pricing"]');
    
    // Check subscribe buttons redirect to registration
    const subscribeButtons = page.locator('button:has-text("Get Started")');
    await expect(subscribeButtons).toHaveCount(3);
    
    // Click first subscribe button
    await subscribeButtons.first().click();
    
    // Should redirect to registration page
    await expect(page).toHaveURL(/.*register/);
  });

  test('should display features section', async ({ page }) => {
    // Navigate to features section
    await page.click('a[href="#features"]');
    
    // Check features section is visible
    await expect(page.locator('#features')).toBeVisible();
    await expect(page.locator('h2')).toContainText('How It Works');
    
    // Check feature steps
    const featureSteps = page.locator('.grid.grid-cols-1.md\\:grid-cols-4 > div');
    await expect(featureSteps).toHaveCount(4);
    
    // Check step titles
    await expect(page.locator('h3')).toContainText('Create Ticket Types');
    await expect(page.locator('h3')).toContainText('Generate Tickets');
    await expect(page.locator('h3')).toContainText('Sell & Track');
    await expect(page.locator('h3')).toContainText('Auto-Expiry');
  });

  test('should display testimonials section', async ({ page }) => {
    // Scroll to testimonials
    await page.locator('section:has-text("What Our Customers Say")').scrollIntoViewIfNeeded();
    
    // Check testimonials section
    await expect(page.locator('h2')).toContainText('What Our Customers Say');
    
    // Check testimonial cards
    const testimonials = page.locator('.grid.grid-cols-1.md\\:grid-cols-3 > div');
    await expect(testimonials).toHaveCount(3);
    
    // Check testimonial content
    await expect(page.locator('h4')).toContainText('John Mwangi');
    await expect(page.locator('h4')).toContainText('Sarah Wanjiku');
    await expect(page.locator('h4')).toContainText('Peter Kimani');
  });

  test('should display FAQ section', async ({ page }) => {
    // Scroll to FAQ section
    await page.locator('section:has-text("Frequently Asked Questions")').scrollIntoViewIfNeeded();
    
    // Check FAQ section
    await expect(page.locator('h2')).toContainText('Frequently Asked Questions');
    
    // Check FAQ items
    const faqItems = page.locator('.space-y-6 > div');
    await expect(faqItems).toHaveCount(5);
    
    // Check FAQ questions
    await expect(page.locator('h3')).toContainText('What types of tickets can I create?');
    await expect(page.locator('h3')).toContainText('How do tickets automatically expire?');
    await expect(page.locator('h3')).toContainText('Can I print tickets for my customers?');
  });

  test('should have working footer links', async ({ page }) => {
    // Scroll to footer
    await page.locator('footer').scrollIntoViewIfNeeded();
    
    // Check footer sections
    await expect(page.locator('footer h3')).toContainText('Hotspot Config');
    await expect(page.locator('footer h3')).toContainText('Quick Links');
    await expect(page.locator('footer h3')).toContainText('Support');
    await expect(page.locator('footer h3')).toContainText('Contact');
    
    // Check footer links
    await expect(page.locator('footer a[href="/"]')).toContainText('Home');
    await expect(page.locator('footer a[href="#pricing"]')).toContainText('Pricing');
    await expect(page.locator('footer a[href="#features"]')).toContainText('Features');
  });

  test('should be responsive on mobile', async ({ page }) => {
    // Set mobile viewport
    await page.setViewportSize({ width: 375, height: 667 });
    
    // Check mobile navigation
    await expect(page.locator('nav')).toBeVisible();
    
    // Check hero section is still visible
    await expect(page.locator('h1')).toBeVisible();
    
    // Check pricing section stacks properly
    await page.click('a[href="#pricing"]');
    const pricingCards = page.locator('.grid.grid-cols-1.md\\:grid-cols-3 > div');
    await expect(pricingCards.first()).toBeVisible();
  });
});
