## ADDED Requirements

### Requirement: Axios instance with base configuration
The system SHALL provide a centralized Axios instance with default configuration.

#### Scenario: Axios instance has base URL from env
- **WHEN** inspecting the Axios instance
- **THEN** its `baseURL` SHALL be set from `VITE_API_URL` environment variable
- **AND** its `timeout` SHALL be 30 seconds
- **AND** its `headers` SHALL include `Content-Type: application/json`

#### Scenario: Axios instance injects Authorization header
- **WHEN** a request is made and an access token exists
- **THEN** the interceptor SHALL add `Authorization: Bearer <token>` header
- **AND** SHALL add `X-Tenant-ID` header from the JWT payload

### Requirement: Automatic token refresh on 401
The system SHALL transparently refresh expired access tokens when receiving a 401 response.

#### Scenario: Single 401 triggers refresh
- **WHEN** a request returns 401
- **THEN** the interceptor SHALL call `POST /api/v1/auth/refresh` with the stored refresh token
- **AND** if refresh succeeds, SHALL retry the original request with the new token
- **AND** SHALL update the stored access token

#### Scenario: Multiple simultaneous 401s trigger single refresh
- **WHEN** multiple requests return 401 simultaneously
- **THEN** only one refresh request SHALL be made
- **AND** all queued requests SHALL be replayed with the new token after refresh succeeds

#### Scenario: Refresh failure redirects to login
- **WHEN** the refresh request fails with 401
- **THEN** the interceptor SHALL clear stored tokens
- **AND** SHALL redirect to `/login?reason=session_expired`
- **AND** SHALL reject all queued requests

### Requirement: 403 handling
The system SHALL handle 403 Forbidden responses gracefully.

#### Scenario: 403 shows access denied notification
- **WHEN** any request returns 403
- **THEN** the interceptor SHALL display a toast/notification "No tienes permiso para realizar esta acción"
- **AND** SHALL reject the request with the error
