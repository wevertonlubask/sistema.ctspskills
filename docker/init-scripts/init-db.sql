-- Initialization script for CT-SPSkills database
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE ct_spskills TO postgres;

-- Create schemas (optional, for better organization)
-- CREATE SCHEMA IF NOT EXISTS identity;
-- CREATE SCHEMA IF NOT EXISTS training;
-- CREATE SCHEMA IF NOT EXISTS assessment;
-- CREATE SCHEMA IF NOT EXISTS modality;
-- CREATE SCHEMA IF NOT EXISTS analytics;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'CT-SPSkills database initialized successfully!';
END $$;
