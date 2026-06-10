## ADDED Requirements

### Requirement: Login page
The system SHALL provide a login page at `/login` that authenticates users.

#### Scenario: Login form renders
- **WHEN** visiting `/login`
- **THEN** the user SHALL see a form with email input, password input, and submit button
- **AND** the form SHALL have validation: email format required, password non-empty

#### Scenario: Successful login redirects to 2FA or dashboard
- **WHEN** user submits valid credentials
- **THEN** the system SHALL call `POST /api/v1/auth/login`
- **AND** if 2FA is required, SHALL redirect to `/login/2fa`
- **AND** if 2FA is not required, SHALL redirect to `/dashboard`

#### Scenario: Failed login shows error
- **WHEN** user submits invalid credentials
- **THEN** the system SHALL display an error message "Credenciales inválidas"
- **AND** SHALL NOT redirect

### Requirement: 2FA verification page
The system SHALL provide a 2FA verification page at `/login/2fa`.

#### Scenario: 2FA code form renders
- **WHEN** redirected to `/login/2fa`
- **THEN** the user SHALL see a form with a 6-digit code input, submit button, and cancel link

#### Scenario: Valid 2FA code grants access
- **WHEN** user submits a valid 6-digit code
- **THEN** the system SHALL call `POST /api/v1/auth/2fa/verify`
- **AND** SHALL store access token and refresh token
- **AND** SHALL redirect to `/dashboard`

#### Scenario: Invalid 2FA code shows error
- **WHEN** user submits an invalid code
- **THEN** the system SHALL display an error message "Código inválido"
- **AND** SHALL allow retry

### Requirement: Password recovery flow
The system SHALL provide a password recovery flow in 3 steps.

#### Scenario: Recovery request form renders
- **WHEN** visiting `/recovery`
- **THEN** the user SHALL see a form with email input and submit button

#### Scenario: Recovery email sent
- **WHEN** user submits a valid email
- **THEN** the system SHALL call `POST /api/v1/auth/recovery`
- **AND** SHALL show a success message "Si el email existe, recibirás instrucciones"

#### Scenario: Recovery code confirmation form renders
- **WHEN** the recovery process progresses
- **THEN** the user SHALL see a form for entering the recovery code and a new password

#### Scenario: Recovery code confirmed
- **WHEN** user submits a valid code and matching new password
- **THEN** the system SHALL call `POST /api/v1/auth/recovery/confirm`
- **AND** SHALL redirect to `/login` with success message

### Requirement: AuthContext and useAuth hook
The system SHALL provide an AuthContext and `useAuth` hook for session management.

#### Scenario: AuthContext provides session state
- **WHEN** any component calls `useAuth()`
- **THEN** it SHALL receive: `user`, `permissions`, `isAuthenticated`, `isLoading`, `login()`, `logout()`, `verify2fa()`, `requestRecovery()`, `confirmRecovery()`

#### Scenario: Session initialized on app mount
- **WHEN** the app mounts and a stored access token exists
- **THEN** the system SHALL call `GET /api/v1/auth/me` to validate the session
- **AND** SHALL populate user and permissions
- **AND** if the token is invalid, SHALL clear session and redirect to `/login`

### Requirement: Logout
The system SHALL provide a logout function that destroys the session.

#### Scenario: Logout clears session
- **WHEN** user clicks logout
- **THEN** the system SHALL call `POST /api/v1/auth/logout`
- **AND** SHALL clear stored tokens
- **AND** SHALL clear AuthContext state
- **AND** SHALL redirect to `/login`
