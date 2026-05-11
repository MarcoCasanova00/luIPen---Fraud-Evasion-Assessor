# Security Documentation

## Overview

The Fraud Evasion Penetration Testing Tool implements multiple security layers for safe operation.

## Implemented Security Measures

### 1. Input Validation
- Strict type checking on all API inputs
- Range validation for numeric fields (0-20000 for distances, 0-100 for ratios)
- URL format validation for target_url
- IP address format validation (IPv4)
- Boolean normalization for checkbox fields

### 2. Rate Limiting
- 30 requests per minute on `/api/score`
- 20 requests per 2 minutes on `/api/report`
- 30 requests per minute on `/api/geoip/distance`
- Per-endpoint and per-IP tracking

### 3. HTTP Security Headers
- Content-Security-Policy (CSP)
- X-Content-Type-Options: nosniff
- X-Frame-Options: SAMEORIGIN
- Referrer-Policy: strict-origin-when-cross-origin
- Permissions-Policy restrictions

### 4. Secure Logging
- No sensitive data in logs (IPs masked, passwords redacted)
- Security event tracking
- Structured log format
- No stack traces in production responses

### 5. Cookie Security
- HttpOnly cookies
- SameSite=Lax attribute
- Secure flag in production HTTPS

### 6. CSRF Protection
- CSRF token validation on state-changing routes
- Origin/Referer validation

### 7. Error Handling
- Custom error pages for 400, 404, 405, 429, 500
- No sensitive information in error messages
- Consistent error response format

### 8. Configuration
- Environment-based configuration (dev/test/prod)
- No hardcoded secrets
- .env.example provided

## Security Best Practices

1. **Never expose debug mode in production**
2. **Use HTTPS in production deployments**
3. **Rotate SECRET_KEY regularly**
4. **Keep dependencies updated**
5. **Review logs for suspicious activity**
6. **Limit request body size (16KB max)**
7. **Deploy in isolated network environment**

## Deployment Considerations

This tool should be deployed in a sandboxed environment with:
- No access to production databases
- No connection to real payment systems
- Network isolation from critical infrastructure
- Regular security audits
- Monitoring for abuse patterns

## Vulnerability Reporting

If you discover a security vulnerability in this tool, please report it to the maintainers. Do NOT disclose security issues publicly until they have been addressed.