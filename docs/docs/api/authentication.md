---
sidebar_position: 2
title: Authentication
---

# Authentication

The Phantom Banking API uses JWT (JSON Web Tokens) for authentication. This section covers all authentication-related endpoints.

## Register a New User

Register a new user account.

```http
POST /auth/register/
```

### Request Body

```json
{
  "email": "user@example.com",
  "password": "secure_password123",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}
```

### Response

```json
{
  "data": {
    "user_id": "usr_123456",
    "email": "user@example.com",
    "message": "Registration successful. Please verify your email."
  }
}
```

## Login

Authenticate and receive access tokens.

```http
POST /auth/login/
```

### Request Body

```json
{
  "email": "user@example.com",
  "password": "secure_password123"
}
```

### Response

```json
{
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "expires_in": 3600
  }
}
```

## Verify Email

Verify user's email address using the token sent to their email.

```http
POST /auth/verify-email/
```

### Request Body

```json
{
  "token": "verification_token_from_email"
}
```

### Response

```json
{
  "data": {
    "message": "Email verified successfully"
  }
}
```

## Resend Verification Email

Request a new verification email.

```http
POST /auth/resend-verification/
```

### Request Body

```json
{
  "email": "user@example.com"
}
```

### Response

```json
{
  "data": {
    "message": "Verification email sent"
  }
}
```

## Refresh Token

Get a new access token using a refresh token.

```http
POST /auth/token/refresh/
```

### Request Body

```json
{
  "refresh": "your_refresh_token"
}
```

### Response

```json
{
  "data": {
    "access": "new_access_token",
    "expires_in": 3600
  }
}
```

## Logout

Invalidate the current access token.

```http
POST /auth/logout/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Response

```json
{
  "data": {
    "message": "Successfully logged out"
  }
}
```

## Password Reset

Request a password reset email.

```http
POST /auth/password/reset/
```

### Request Body

```json
{
  "email": "user@example.com"
}
```

### Response

```json
{
  "data": {
    "message": "Password reset email sent"
  }
}
```

## Confirm Password Reset

Reset password using the token from the reset email.

```http
POST /auth/password/reset/confirm/
```

### Request Body

```json
{
  "token": "reset_token_from_email",
  "password": "new_secure_password"
}
```

### Response

```json
{
  "data": {
    "message": "Password reset successful"
  }
}
```

## Get User Profile

Retrieve the authenticated user's profile.

```http
GET /auth/profile/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Response

```json
{
  "data": {
    "user_id": "usr_123456",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "created_at": "2024-03-20T12:00:00Z",
    "last_login": "2024-03-20T12:00:00Z"
  }
}
```

## Update User Profile

Update the authenticated user's profile.

```http
PATCH /auth/profile/
```

### Headers

```
Authorization: Bearer your_access_token
```

### Request Body

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}
```

### Response

```json
{
  "data": {
    "user_id": "usr_123456",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "phone_number": "+1234567890",
    "updated_at": "2024-03-20T12:00:00Z"
  }
}
``` 