## ADDED Requirements

### Requirement: Sidebar navigation
The system SHALL provide a collapsible sidebar as the primary navigation, following the Stitch design.

#### Scenario: Sidebar renders expanded by default
- **WHEN** the app loads on a screen ≥1024px
- **THEN** the sidebar SHALL be 260px wide
- **AND** SHALL show the Activia Trace logo and subtitle
- **AND** SHALL show navigation items with icon and label

#### Scenario: Sidebar can be collapsed
- **WHEN** user clicks the collapse toggle
- **THEN** the sidebar SHALL collapse to 64px width
- **AND** SHALL show only icons, hiding labels
- **AND** the state SHALL persist across page reloads

#### Scenario: Sidebar menu items filtered by permissions
- **WHEN** rendering the sidebar menu
- **THEN** only modules that the user has permission for SHALL be shown
- **AND** the active route SHALL be highlighted with the `secondary-container` background

#### Scenario: Sidebar has bottom section with Help and Logout
- **WHEN** viewing the sidebar
- **THEN** at the bottom SHALL be "Ayuda" link with help icon and "Cerrar Sesión" with logout icon
- **AND** "Cerrar Sesión" SHALL use the error color (#ba1a1a)

### Requirement: Topbar
The system SHALL provide a top header bar with global actions.

#### Scenario: Topbar shows user info and actions
- **WHEN** viewing the topbar
- **THEN** it SHALL display: search input, tenant selector, notification bell icon, user avatar

#### Scenario: Search input exists
- **WHEN** viewing the topbar
- **THEN** a search input with placeholder "Buscar estudiante, factura o acta..." SHALL be visible
- **AND** the search SHALL be styled as a rounded input with search icon

### Requirement: Impersonation banner
The system SHALL display an impersonation banner when the admin is acting on behalf of another user.

#### Scenario: Impersonation banner visible when impersonating
- **WHEN** the current session has `impersonating: true`
- **THEN** a banner SHALL appear below the topbar
- **AND** SHALL show "MODO ADMINISTRADOR: Estás operando como [usuario impersonado]"
- **AND** SHALL have a "Revertir" button to end impersonation

#### Scenario: Impersonation banner hidden in normal mode
- **WHEN** the current session is not impersonating
- **THEN** the impersonation banner SHALL NOT be rendered

### Requirement: Logout flow
The system SHALL provide a logout flow accessible from the sidebar.

#### Scenario: Logout from sidebar
- **WHEN** user clicks "Cerrar Sesión" in the sidebar
- **THEN** the system SHALL show a confirmation dialog "¿Estás seguro de que deseas cerrar sesión?"
- **AND** if confirmed, SHALL execute the logout function
- **AND** SHALL redirect to `/login`

### Requirement: Dashboard placeholder page
The system SHALL provide a dashboard page at `/dashboard` as the post-login landing page.

#### Scenario: Dashboard renders welcome message
- **WHEN** visiting `/dashboard` after login
- **THEN** the system SHALL display "Panel de Control General"
- **AND** a welcome message SHALL be shown with the user's name

### Requirement: UI primitives (shadcn/ui style)
The system SHALL provide base UI components styled with the Stitch design tokens.

#### Scenario: UI components exist
- **WHEN** inspecting `src/components/ui/`
- **THEN** the following components SHALL exist: `Button`, `Input`, `Card`, `Badge`, `Avatar`, `Skeleton`, `Toast`, `Dialog`
- **AND** each component SHALL use `cn()` utility (tailwind-merge + clsx) for className merging

#### Scenario: Card follows Stitch design
- **WHEN** rendering a Card component
- **THEN** it SHALL have white background, 1px solid border `outline-variant` (#c6c6cd), and `rounded` border radius (0.5rem)

#### Scenario: Badge shows status correctly
- **WHEN** rendering a Badge with variant "success"
- **THEN** it SHALL use green background (`bg-green-100`) with green text (`text-green-800`)
- **WHEN** rendering a Badge with variant "warning"
- **THEN** it SHALL use amber background with amber text
- **WHEN** rendering a Badge with variant "error"
- **THEN** it SHALL use red background with red text
