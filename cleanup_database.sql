-- Clean up Django migration issues
-- Run this in your Supabase SQL editor

-- Delete existing permissions that are causing conflicts
DELETE FROM auth_permission WHERE content_type_id = 5 AND codename = 'add_session';

-- Reset migration state
DELETE FROM django_migrations WHERE app = 'auth';
DELETE FROM django_migrations WHERE app = 'contenttypes';
DELETE FROM django_migrations WHERE app = 'sessions';

-- Clean up any duplicate permissions
DELETE FROM auth_permission WHERE id NOT IN (
    SELECT MIN(id) FROM auth_permission 
    GROUP BY content_type_id, codename
);

-- Reset sequences
SELECT setval('auth_permission_id_seq', (SELECT MAX(id) FROM auth_permission));
SELECT setval('django_content_type_id_seq', (SELECT MAX(id) FROM django_content_type));
