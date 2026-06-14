-- Fix existing users - Give them STARTER trial (14 days)

UPDATE users
SET
    account_type = 'starter',
    trial_started_at = NOW(),
    trial_ends_at = NOW() + INTERVAL '14 days',
    trial_status = 'active'
WHERE trial_started_at IS NULL;

-- Verify the changes
SELECT
    email,
    name,
    role,
    account_type,
    trial_status,
    trial_ends_at
FROM users
ORDER BY created_at DESC;
