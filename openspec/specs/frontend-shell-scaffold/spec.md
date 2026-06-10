## ADDED Requirements

### Requirement: Project scaffolding
The system SHALL provide a Vite + React 18 + TypeScript project at `trace-app/` with the following configuration.

#### Scenario: Vite dev server starts
- **WHEN** running `npm run dev` in `trace-app/`
- **THEN** the Vite dev server SHALL start on port 5173 with HMR enabled

#### Scenario: TypeScript compiles without errors
- **WHEN** running `npx tsc --noEmit`
- **THEN** the compiler SHALL exit with code 0 and no errors

#### Scenario: Production build completes
- **WHEN** running `npm run build`
- **THEN** Vite SHALL output the production bundle to `trace-app/dist/`

### Requirement: Feature-based directory structure
The project SHALL follow a feature-based directory structure under `src/`.

#### Scenario: Required directories exist
- **WHEN** inspecting `trace-app/src/`
- **THEN** the following directories SHALL exist: `api/`, `assets/`, `components/ui/`, `config/`, `features/auth/`, `features/shell/`, `hooks/`, `providers/`, `services/`, `types/`, `utils/`
- **AND** each feature directory SHALL contain subdirectories: `components/`, `hooks/`, `services/`, `types/`, `pages/`

### Requirement: Design tokens configuration
Tailwind CSS SHALL be configured with the design tokens from the Stitch design system.

#### Scenario: Tailwind config has Stitch tokens
- **WHEN** inspecting `tailwind.config.ts`
- **THEN** the config SHALL extend colors with: `background`, `surface`, `surface-container-lowest`, `surface-container-low`, `surface-container`, `surface-container-high`, `surface-container-highest`, `on-surface`, `on-surface-variant`, `outline`, `outline-variant`, `primary`, `on-primary`, `primary-container`, `on-primary-container`, `secondary`, `secondary-container`, `error`, `error-container`
- **AND** SHALL extend fontFamily with `Geist` and `Geist Mono`
- **AND** SHALL extend spacing with `sidebar-width` (260px) and `sidebar-collapsed` (64px)
- **AND** SHALL extend fontSize with `headline-lg`, `headline-md`, `headline-sm`, `body-lg`, `body-md`, `body-sm`, `label-md`, `label-sm`, `mono-data`

### Requirement: Dependency installation
The project SHALL include and properly configure: React 18, React Router v6, TanStack Query, React Hook Form, Zod, Axios, Tailwind CSS, Vitest, React Testing Library, MSW, class-variance-authority, tailwind-merge, clsx.

#### Scenario: All deps are installable
- **WHEN** running `npm ci`
- **THEN** all packages SHALL install without warnings or errors

#### Scenario: Imports resolve correctly
- **WHEN** running `npx tsc --noEmit`
- **THEN** all imports from installed packages SHALL resolve without errors
