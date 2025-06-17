---
sidebar_position: 1
title: Introduction
---

# Phantom Banking API

Welcome to the Phantom Banking API documentation. This API allows you to integrate payment processing, merchant management, and customer services into your applications.

## Base URL

All API endpoints are relative to the base URL:

```
https://api.phantombanking.com/api/v1
```

## Authentication

The Phantom Banking API uses JWT (JSON Web Tokens) for authentication. To authenticate your requests, include your API key in the Authorization header:

```bash
Authorization: Bearer YOUR_API_KEY
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute for standard accounts
- 1000 requests per minute for enterprise accounts

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Maximum requests per window
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit window resets

## Response Format

All responses are returned in JSON format with the following structure:

```json
{
  "data": {
    // Response data here
  },
  "meta": {
    "timestamp": "2024-03-20T12:00:00Z",
    "request_id": "req_123456"
  }
}
```

## Error Handling

Errors follow a standard format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable error message",
    "details": {
      // Additional error details
    }
  }
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests
- 500: Internal Server Error

## API Versioning

The current version of the API is v1. The version is included in the URL path. We maintain backward compatibility within major versions.

## Support

For API support, please contact:
- Email: api-support@phantombanking.com
- Developer Portal: https://developers.phantombanking.com
- Status Page: https://status.phantombanking.com 