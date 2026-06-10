## ADDED Requirements

### Requirement: Route definitions
The system SHALL define routes using React Router v6 with lazy-loaded feature pages.

#### Scenario: Public routes are accessible without auth
- **WHEN** visiting `/login`, `/login/2fa`, or `/recovery`
- **THEN** the route SHALL render without authentication
- **AND** if user is already authenticated, SHALL redirect to `/dashboard`

#### Scenario: Protected routes require authentication
- **WHEN** visiting any route that is not public
- **THEN** the system SHALL require a valid access token
- **AND** if not authenticated, SHALL redirect to `/login`

#### Scenario: Route not found shows 404
- **WHEN** visiting an undefined route
- **THEN** the system SHALL display a 404 page with "Página no encontrada" message and a link to `/dashboard`

### Requirement: ProtectedRoute component
The system SHALL provide a `ProtectedRoute` component that guards routes by permission.

#### Scenario: ProtectedRoute renders children when authenticated
- **WHEN** user is authenticated and has the required permission
- **THEN** `ProtectedRoute` SHALL render `<Outlet />`

#### Scenario: ProtectedRoute redirects when not authenticated
- **WHEN** user is not authenticated
- **THEN** `ProtectedRoute` SHALL redirect to `/login`

#### Scenario: ProtectedRoute shows forbidden when missing permission
- **WHEN** user is authenticated but lacks the required `modulo:accion` permission
- **THEN** `ProtectedRoute` SHALL render a "Sin permisos suficientes" page with 403 status
- **AND** SHALL NOT redirect to login

### Requirement: PublicRoute component
The system SHALL provide a `PublicRoute` component for auth pages.

#### Scenario: PublicRoute renders children when not authenticated
- **WHEN** user is not authenticated
- **THEN** `PublicRoute` SHALL render `<Outlet />`

#### Scenario: PublicRoute redirects to dashboard when authenticated
- **WHEN** user is already authenticated
- **THEN** `PublicRoute` SHALL redirect to `/dashboard`

### Requirement: Lazy loading
Feature pages SHALL be lazy-loaded with React Suspense.

#### Scenario: Lazy loading works
- **WHEN** navigating to a feature route for the first time
- **THEN** React.lazy() SHALL load the page component
- **AND** a loading skeleton SHALL be displayed during load
