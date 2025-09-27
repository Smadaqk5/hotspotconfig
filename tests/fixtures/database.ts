/**
 * Database setup and teardown utilities for testing
 */

import { test as base } from '@playwright/test';
import { testUsers } from './test-data';

export interface DatabaseFixtures {
  setupDatabase: () => Promise<void>;
  cleanupDatabase: () => Promise<void>;
  createTestUser: (userData: any) => Promise<any>;
  deleteTestUser: (username: string) => Promise<void>;
}

export const test = base.extend<DatabaseFixtures>({
  setupDatabase: async ({}, use) => {
    const setupDatabase = async () => {
      // Setup test database
      console.log('Setting up test database...');
      
      // Create test users
      for (const [role, userData] of Object.entries(testUsers)) {
        await createTestUser(userData);
      }
      
      console.log('Test database setup complete');
    };
    
    await use(setupDatabase);
  },

  cleanupDatabase: async ({}, use) => {
    const cleanupDatabase = async () => {
      // Cleanup test database
      console.log('Cleaning up test database...');
      
      // Delete test users
      for (const [role, userData] of Object.entries(testUsers)) {
        await deleteTestUser(userData.username);
      }
      
      console.log('Test database cleanup complete');
    };
    
    await use(cleanupDatabase);
  },

  createTestUser: async ({}, use) => {
    const createTestUser = async (userData: any) => {
      // Mock API call to create user
      console.log(`Creating test user: ${userData.username}`);
      return userData;
    };
    
    await use(createTestUser);
  },

  deleteTestUser: async ({}, use) => {
    const deleteTestUser = async (username: string) => {
      // Mock API call to delete user
      console.log(`Deleting test user: ${username}`);
    };
    
    await use(deleteTestUser);
  }
});

export { expect } from '@playwright/test';
