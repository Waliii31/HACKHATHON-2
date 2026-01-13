# Authentication Feature Specification

## Overview
This specification defines the authentication system for the Todo application. The system implements a split architecture where frontend handles user authentication flows using Better Auth, while the backend solely verifies JWT tokens for API access. This specification explicitly prohibits mock implementations and manual token handling.

## Critical Compliance Requirements
- **NO MOCK AUTH IMPLEMENTATIONS**: Any implementation that simulates authentication functionality without actual Better Auth integration is strictly forbidden
- **NO MANUAL TOKEN HANDLING**: Storing, retrieving, or managing authentication tokens through localStorage, sessionStorage, or cookies outside of Better Auth's control is prohibited
- **STRICT JWT VERIFICATION ONLY**: Backend must only verify JWT tokens; never issue, create, or store session information
- **MANDATORY BETTER AUTH INTEGRATION**: All authentication functionality must use Better Auth client libraries

## User Signup

### Process Flow
- User navigates to signup page
- User provides email, password, and optional name
- Frontend validates input format (email format, password strength)
- **ACTUAL Better Auth processes registration request** (no mocks allowed)
- User account is created in Better Auth system
- Session established through Better Auth client
- JWT token obtained from Better Auth session

### Requirements
- Email must be unique across all users
- Password must meet minimum strength requirements (8+ characters)
- Email verification may be required depending on Better Auth configuration
- User profile is created with basic information
- **MUST use Better Auth client functions (no custom auth)**

### Success Response
- Session established through Better Auth client
- User redirected to dashboard/home
- Authentication state updated via Better Auth hooks
- JWT token available through Better Auth session

### Error Cases
- Duplicate email: Return appropriate error message from Better Auth
- Invalid email format: Display validation error from Better Auth
- Weak password: Display validation error from Better Auth
- Network errors: Handle gracefully with Better Auth error handling
- **NO CUSTOM ERROR HANDLING**: All auth errors must come from Better Auth

## User Signin

### Process Flow
- User navigates to signin page
- User provides email and password
- Frontend validates input format
- **ACTUAL Better Auth processes authentication request** (no mocks allowed)
- Credentials are verified by Better Auth against stored hash
- Session established through Better Auth client
- JWT token obtained from Better Auth session

### Requirements
- Existing account must exist with provided email
- Password must match stored hash
- Account must be in active state
- Rate limiting applied by Better Auth to prevent brute force attacks
- **MUST use Better Auth client functions (no custom auth)**

### Success Response
- Session established through Better Auth client
- User redirected to dashboard/home
- Authentication state updated via Better Auth hooks
- JWT token available through Better Auth session

### Error Cases
- Invalid credentials: Return generic error message from Better Auth
- Locked account: Display appropriate message from Better Auth
- Network errors: Handle through Better Auth error handling
- Account inactive: Message provided by Better Auth
- **NO CUSTOM ERROR HANDLING**: All auth errors must come from Better Auth

## Session Handling via Better Auth (Frontend Only)

### Session Management
- **Better Auth manages session state in frontend** (no manual session handling)
- Session tokens managed exclusively by Better Auth (no manual localStorage)
- Session persistence across browser restarts handled by Better Auth
- Automatic session refresh handled by Better Auth
- **NO MANUAL TOKEN STORAGE**: Do not store tokens in localStorage, sessionStorage, or cookies manually

### Frontend Responsibilities
- Initialize Better Auth client with proper configuration
- Use Better Auth hooks (useAuth, etc.) for authentication state
- Redirect unauthenticated users from protected routes using Better Auth session
- Provide user information through Better Auth session object
- Handle session expiration through Better Auth lifecycle

### Session Lifecycle
- Session begins upon successful authentication through Better Auth
- Session persistence handled by Better Auth
- Session terminated through Better Auth signOut function
- Session expiration handled automatically by Better Auth

## JWT Acquisition from Better Auth

### Token Retrieval Process
- JWT token must be obtained from Better Auth session object
- Use Better Auth's session.token property or equivalent
- **NO MANUAL TOKEN EXTRACTION**: Do not manually decode or manipulate tokens
- **NO LOCAL STORAGE**: Do not store tokens outside of Better Auth's control

### Token Contents
- Subject (sub): User unique identifier from Better Auth
- Issuer (iss): Better Auth provider identifier
- Expiration (exp): Unix timestamp from Better Auth
- Issued at (iat): Unix timestamp from Better Auth
- Claims: Provided by Better Auth only

## JWT Transmission to Backend

### API Request Process
- Obtain JWT token from Better Auth session object
- Attach token to API requests using Authorization: Bearer {token} header
- Use Better Auth session token directly without modification
- **NO MANUAL TOKEN HANDLING**: Do not store, decode, or manipulate tokens manually

### Transmission Requirements
- JWT must be attached to Authorization header of all protected API requests
- Token must come directly from Better Auth session (no intermediaries)
- Proper error handling for token expiration/invalidation
- **NO CUSTOM TOKEN MANAGEMENT**: All token handling must go through Better Auth

## JWT Verification in Backend

### Verification Process
- Backend receives API request with Authorization header
- Extracts JWT from "Bearer [token]" format
- Verifies token signature using Better Auth's public key or shared secret
- Validates token expiration and other claims
- Extracts user identity from token payload

### Backend Requirements
- Verify token signature against Better Auth's configured key
- Check token expiration (exp claim)
- Validate issuer (iss claim) from Better Auth
- Extract and validate user identifier
- Return appropriate error for invalid tokens
- **VERIFY ONLY**: Backend must never issue, create, or manage tokens

### Verification Failures
- Invalid signature: Return 401 Unauthorized
- Expired token: Return 401 Unauthorized
- Invalid issuer: Return 401 Unauthorized
- Missing token: Return 401 Unauthorized
- Malformed token: Return 401 Unauthorized

## Token Expiration

### Expiration Handling
- JWTs have expiration time set by Better Auth
- Frontend uses Better Auth's built-in refresh mechanism
- Automatic token refresh handled by Better Auth
- Session invalidated through Better Auth when token expires

### Refresh Mechanism
- Better Auth handles token refresh automatically
- Refresh tokens managed by Better Auth
- Seamless experience for end users through Better Auth
- **NO CUSTOM REFRESH LOGIC**: All refresh handling must be through Better Auth

## Unauthorized Behavior (401 Responses)

### Backend 401 Scenarios
- Missing Authorization header
- Invalid/malformed JWT
- Expired JWT
- Invalid token signature
- Revoked/invalidated token

### 401 Response Format
```
HTTP/1.1 401 Unauthorized
Content-Type: application/json

{
  "detail": "Authentication credentials were not provided/are invalid"
}
```

### Frontend Handling of 401
- Clear Better Auth session through signOut function
- Redirect to login page
- Display appropriate message to user
- Preserve original destination for post-login redirect

### Security Considerations
- Generic error messages to avoid information disclosure
- Logging of unauthorized access attempts
- Potential rate limiting for repeated failures
- Prevention of token harvesting attempts

## Architecture Clarifications

### Frontend Responsibilities
- Handle all authentication UI flows (signup, signin, profile) through Better Auth
- Manage user sessions using Better Auth client only (no custom session management)
- Obtain and transmit JWTs from Better Auth session to backend APIs
- Protect routes based on Better Auth session status
- Handle authentication state changes through Better Auth hooks

### Backend Responsibilities
- Verify JWT validity and authenticity only
- Validate token claims and expiration only
- Authorize access based on user identity from JWT
- Return 401 responses for invalid tokens
- Implement business logic based on authenticated user from JWT
- **NEVER ISSUE TOKENS**: Backend must never create, issue, or manage authentication tokens
- **NEVER STORE SESSIONS**: Backend must not maintain session state

### No Shared Session Database
- Backend does not maintain session state
- Authentication state managed entirely by Better Auth in frontend
- Backend relies solely on JWT verification (never consults frontend)
- Scalability achieved through stateless authentication
- No need for distributed session storage

### Communication Flow
- Frontend authenticates users through Better Auth client
- JWT tokens obtained from Better Auth session object
- API requests include JWT from Better Auth session in Authorization header
- Backend verifies JWT independently without consulting frontend
- Response includes necessary data based on authenticated user from JWT

## Compliance Verification
Any implementation that violates these requirements will be rejected:
- ✅ Uses actual Better Auth client libraries
- ✅ Does not implement mock authentication
- ✅ Does not manually handle tokens outside Better Auth
- ✅ Backend only verifies JWT (never issues)
- ✅ Frontend only obtains tokens from Better Auth session
- ✅ All auth state managed through Better Auth hooks/functions