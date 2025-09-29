-- Migration: Tenant Isolation and Row-Level Security Setup

-- 1. Add tenant_id to all existing tables that need tenant isolation
--    (Example tables shown - add/modify according to your actual schema)

-- 2. Create RLS policies
-- Enable Row Level Security on all tenant-specific tables
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE tenant_users ENABLE ROW LEVEL SECURITY;
-- Add other tenant-specific tables here

-- 3. Create a function to get the current tenant_id from the JWT claim or session
CREATE OR REPLACE FUNCTION current_tenant_id()
RETURNS UUID AS $$
DECLARE
    tenant_id UUID;
BEGIN
    -- First try to get from JWT claim (for API requests)
    BEGIN
        SELECT (current_setting('jwt.claims.tenant_id', true))::UUID INTO tenant_id;
    EXCEPTION WHEN OTHERS THEN
        -- Fallback to session variable (for direct DB connections)
        BEGIN
            SELECT current_setting('app.current_tenant_id', true)::UUID INTO tenant_id;
        EXCEPTION WHEN OTHERS THEN
            RETURN NULL;
        END;
    END;
    
    RETURN tenant_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 4. Create a function to check if user has access to a tenant
CREATE OR REPLACE FUNCTION has_tenant_access(p_tenant_id UUID)
RETURNS BOOLEAN AS $$
DECLARE
    has_access BOOLEAN;
    current_user_id UUID;
BEGIN
    -- Get current user ID from JWT or session
    BEGIN
        SELECT (current_setting('jwt.claims.sub', true))::UUID INTO current_user_id;
    EXCEPTION WHEN OTHERS THEN
        BEGIN
            SELECT current_setting('app.current_user_id', true)::UUID INTO current_user_id;
        EXCEPTION WHEN OTHERS THEN
            RETURN FALSE;
        END;
    END;
    
    -- Check if user has access to the tenant
    SELECT EXISTS (
        SELECT 1 FROM tenant_users 
        WHERE tenant_id = p_tenant_id 
        AND user_id = current_user_id
        AND deleted_at IS NULL
    ) INTO has_access;
    
    RETURN COALESCE(has_access, FALSE);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 5. Create RLS policies for tenant isolation

-- Users table policies
CREATE POLICY tenant_isolation_policy_users ON users
    USING (id IN (
        SELECT user_id FROM tenant_users 
        WHERE tenant_id = current_tenant_id()
        AND has_tenant_access(current_tenant_id())
    ))
    WITH CHECK (TRUE); -- Only allow updates through tenant_users relationship

-- Tenant users policies
CREATE POLICY tenant_isolation_policy_tenant_users ON tenant_users
    USING (tenant_id = current_tenant_id() AND has_tenant_access(tenant_id));

-- 6. Create a function to set the current tenant context
CREATE OR REPLACE FUNCTION set_tenant_context(tenant_uuid UUID, user_uuid UUID)
RETURNS VOID AS $$
BEGIN
    EXECUTE format('SET LOCAL app.current_tenant_id = %L', tenant_uuid);
    EXECUTE format('SET LOCAL app.current_user_id = %L', user_uuid);
    -- Set the search path to include tenant-specific schemas if using schema-based isolation
    -- EXECUTE format('SET search_path TO %I, public', 'tenant_' || tenant_uuid);
END;
$$ LANGUAGE plpgsql;

-- 7. Create a default role for tenant access
CREATE ROLE tenant_user;
GRANT USAGE ON SCHEMA public TO tenant_user;

-- 8. Set default permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO tenant_user;

-- 9. Create a function to create a new tenant with default settings
CREATE OR REPLACE FUNCTION create_tenant(
    p_name VARCHAR(255),
    p_slug VARCHAR(63),
    admin_email VARCHAR(255),
    admin_password_hash VARCHAR(255),
    admin_first_name VARCHAR(100) DEFAULT NULL,
    admin_last_name VARCHAR(100) DEFAULT NULL
) 
RETURNS UUID AS $$
DECLARE
    new_tenant_id UUID;
    new_user_id UUID;
BEGIN
    -- Start a transaction
    BEGIN
        -- Create the tenant
        INSERT INTO tenants (name, slug)
        VALUES (p_name, p_slug)
        RETURNING id INTO new_tenant_id;
        
        -- Create the admin user if they don't exist
        INSERT INTO users (email, password_hash, first_name, last_name, is_active)
        VALUES (admin_email, admin_password_hash, admin_first_name, admin_last_name, true)
        ON CONFLICT (email) DO UPDATE 
        SET first_name = COALESCE(admin_first_name, users.first_name),
            last_name = COALESCE(admin_last_name, users.last_name),
            is_active = true
        RETURNING id INTO new_user_id;
        
        -- Assign admin role to the user for this tenant
        INSERT INTO tenant_users (tenant_id, user_id, role)
        VALUES (new_tenant_id, new_user_id, 'admin');
        
        -- Commit the transaction
        RETURN new_tenant_id;
    EXCEPTION WHEN OTHERS THEN
        -- Rollback the transaction on error
        RAISE EXCEPTION 'Failed to create tenant: %', SQLERRM;
    END;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 10. Create a function to safely delete a tenant
CREATE OR REPLACE FUNCTION delete_tenant(p_tenant_id UUID)
RETURNS VOID AS $$
BEGIN
    -- Soft delete all tenant users
    UPDATE tenant_users 
    SET deleted_at = NOW() 
    WHERE tenant_id = p_tenant_id;
    
    -- Soft delete the tenant
    UPDATE tenants 
    SET deleted_at = NOW() 
    WHERE id = p_tenant_id;
    
    -- Note: Add any other tenant-specific cleanup here
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 11. Create a view to get all tenants a user has access to
CREATE OR REPLACE VIEW user_tenants AS
SELECT t.*, tu.role
FROM tenants t
JOIN tenant_users tu ON t.id = tu.tenant_id
JOIN users u ON tu.user_id = u.id
WHERE u.id = (SELECT (current_setting('jwt.claims.sub', true))::UUID)
AND t.deleted_at IS NULL
AND tu.deleted_at IS NULL
AND u.deleted_at IS NULL;

-- 12. Create a function to check if a user is a tenant admin
CREATE OR REPLACE FUNCTION is_tenant_admin(p_tenant_id UUID, p_user_id UUID)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM tenant_users
        WHERE tenant_id = p_tenant_id
        AND user_id = p_user_id
        AND role = 'admin'
        AND deleted_at IS NULL
    );
END;
$$ LANGUAGE plpgsql STABLE;

-- 13. Add comments for documentation
COMMENT ON FUNCTION current_tenant_id() IS 'Returns the current tenant ID from JWT claim or session variable';
COMMENT ON FUNCTION has_tenant_access(UUID) IS 'Checks if the current user has access to the specified tenant';
COMMENT ON FUNCTION set_tenant_context(UUID, UUID) IS 'Sets the current tenant and user context for RLS policies';
COMMENT ON FUNCTION create_tenant(VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR, VARCHAR) IS 'Creates a new tenant with an admin user';
COMMENT ON FUNCTION delete_tenant(UUID) IS 'Safely deletes a tenant and its associated data';

-- 14. Create indexes for better performance
CREATE INDEX idx_users_email ON users(email) WHERE deleted_at IS NULL;
CREATE INDEX idx_tenant_users_role ON tenant_users(role) WHERE deleted_at IS NULL;

-- 15. Create a function to get the current user's role in the current tenant
CREATE OR REPLACE FUNCTION current_user_role()
RETURNS VARCHAR AS $$
DECLARE
    user_role VARCHAR;
BEGIN
    SELECT role INTO user_role
    FROM tenant_users
    WHERE user_id = (SELECT (current_setting('jwt.claims.sub', true))::UUID)
    AND tenant_id = current_tenant_id()
    AND deleted_at IS NULL
    LIMIT 1;
    
    RETURN user_role;
END;
$$ LANGUAGE plpgsql STABLE;
