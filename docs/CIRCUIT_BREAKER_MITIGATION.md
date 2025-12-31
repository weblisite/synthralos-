# Supabase Circuit Breaker Mitigation Guide

## What is the Circuit Breaker?

The Supabase circuit breaker is a **server-side protection mechanism** that automatically blocks database connections after detecting too many failed authentication attempts. This is a security feature that **cannot be disabled** from the client side.

## Why Does It Trigger?

The circuit breaker activates when:
1. **Incorrect database password** - Most common cause
2. **Too many rapid connection attempts** - Connection pool issues
3. **Network connectivity problems** - Temporary connection failures
4. **Malformed connection strings** - URL encoding issues

## How Long Does It Last?

- Typically **5-15 minutes** after the last failed attempt
- The exact duration depends on Supabase's internal logic
- Cannot be manually reset from the application side

## Mitigation Strategies Implemented

### 1. Reduced Connection Pool Size
- **Before**: 10 connections + 5 overflow = 15 total
- **After**: 5 connections + 2 overflow = 7 total
- **Benefit**: Fewer authentication attempts = lower chance of triggering circuit breaker

### 2. Circuit Breaker Detection & Wait Logic
- Application detects when circuit breaker is open
- Automatically waits 5 minutes before retrying
- Prevents repeated failed attempts that keep the breaker open

### 3. Improved Error Handling
- All database operations check circuit breaker status first
- Returns clear error messages with wait times
- Prevents cascading failures

### 4. Connection Pool Optimization
- Faster connection timeouts (10s instead of 15s)
- Shorter pool timeout (30s instead of 60s)
- Better connection recycling

## How to Check Circuit Breaker Status

### Via API Endpoint
```bash
curl http://localhost:8000/api/v1/utils/circuit-breaker-status
```

Response:
```json
{
  "is_open": true,
  "resets_at": "2025-12-30T10:35:00",
  "remaining_seconds": 300,
  "message": "Circuit breaker is open. Wait 300s before retrying."
}
```

### Via Test Script
```bash
cd backend
source .venv/bin/activate
python scripts/test_db_connection.py
```

## How to Fix the Root Cause

### 1. Verify Database Password
Check your `.env` file and ensure `SUPABASE_DB_PASSWORD` or `SUPABASE_DB_URL` is correct:

```bash
# Check if password is correct
cd backend
source .venv/bin/activate
python scripts/test_db_connection.py
```

### 2. Get Correct Connection String from Supabase
1. Go to your Supabase project dashboard
2. Navigate to **Settings** → **Database**
3. Copy the **Connection Pooling** connection string (port 6543)
4. Update `SUPABASE_DB_URL` in your `.env` file

### 3. Wait for Circuit Breaker to Reset
- Wait **5-15 minutes** after fixing the password
- Check status using the API endpoint or script
- Once closed, connections will work normally

## Best Practices

1. **Use Connection Pooling**: Always use the pooler connection (port 6543) instead of direct (port 5432)
2. **Verify Credentials**: Test database connection before deploying
3. **Monitor Circuit Breaker**: Use the status endpoint to check before making requests
4. **Reduce Connection Attempts**: Smaller connection pools reduce authentication attempts
5. **Handle Errors Gracefully**: Implement retry logic with exponential backoff

## Troubleshooting

### Circuit Breaker Keeps Opening
- **Check password**: Most common issue - verify `SUPABASE_DB_PASSWORD` is correct
- **Check connection string**: Ensure URL encoding is correct for special characters
- **Reduce connection pool**: Already optimized, but can reduce further if needed
- **Check Supabase dashboard**: Verify database is accessible from Supabase dashboard

### Application Shows 503 Errors
- Check circuit breaker status: `GET /api/v1/utils/circuit-breaker-status`
- Wait for circuit breaker to reset (5-15 minutes)
- Verify database credentials are correct
- Check backend logs for specific error messages

### Frontend Shows Blank Page
- User needs to log in via Clerk: Navigate to `/login`
- Circuit breaker affects API calls, not authentication
- Check browser console for specific errors

## API Endpoints

- `GET /api/v1/utils/circuit-breaker-status` - Check circuit breaker status (no DB connection)
- `GET /api/v1/utils/health-check` - Basic health check (no DB connection)
- `GET /api/v1/admin/system/health` - Full system health (requires DB, admin only)

## Code Locations

- **Circuit Breaker Logic**: `backend/app/core/db.py`
- **Database Dependency**: `backend/app/api/deps.py`
- **Status Endpoint**: `backend/app/api/routes/utils.py`
- **Test Script**: `backend/scripts/test_db_connection.py`

## Important Notes

⚠️ **The circuit breaker CANNOT be disabled** - it's a Supabase server-side protection.

✅ **The application now handles it gracefully** - waits automatically and provides clear error messages.

🔧 **Fix the root cause** - Verify your database password is correct in `.env`.

⏱️ **Be patient** - Wait 5-15 minutes for the circuit breaker to reset after fixing credentials.
