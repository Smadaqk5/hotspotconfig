/**
 * Test Setup and Configuration
 * Global test setup and teardown
 */

import { test as base } from '@playwright/test';
import { setupDatabase, cleanupDatabase } from '../fixtures/database';

// Global setup
async function globalSetup() {
  console.log('Setting up test environment...');
  
  // Setup test database
  await setupDatabase();
  
  console.log('Test environment setup complete');
}

// Global teardown
async function globalTeardown() {
  console.log('Cleaning up test environment...');
  
  // Cleanup test database
  await cleanupDatabase();
  
  console.log('Test environment cleanup complete');
}

export { globalSetup, globalTeardown };
