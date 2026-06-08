---
name: Technical Academic Enterprise
colors:
  surface: '#f7f9fb'
  surface-dim: '#d8dadc'
  surface-bright: '#f7f9fb'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f2f4f6'
  surface-container: '#eceef0'
  surface-container-high: '#e6e8ea'
  surface-container-highest: '#e0e3e5'
  on-surface: '#191c1e'
  on-surface-variant: '#45464d'
  inverse-surface: '#2d3133'
  inverse-on-surface: '#eff1f3'
  outline: '#76777d'
  outline-variant: '#c6c6cd'
  surface-tint: '#565e74'
  primary: '#000000'
  on-primary: '#ffffff'
  primary-container: '#131b2e'
  on-primary-container: '#7c839b'
  inverse-primary: '#bec6e0'
  secondary: '#505f76'
  on-secondary: '#ffffff'
  secondary-container: '#d0e1fb'
  on-secondary-container: '#54647a'
  tertiary: '#000000'
  on-tertiary: '#ffffff'
  tertiary-container: '#001d31'
  on-tertiary-container: '#188ace'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#dae2fd'
  primary-fixed-dim: '#bec6e0'
  on-primary-fixed: '#131b2e'
  on-primary-fixed-variant: '#3f465c'
  secondary-fixed: '#d3e4fe'
  secondary-fixed-dim: '#b7c8e1'
  on-secondary-fixed: '#0b1c30'
  on-secondary-fixed-variant: '#38485d'
  tertiary-fixed: '#cce5ff'
  tertiary-fixed-dim: '#93ccff'
  on-tertiary-fixed: '#001d31'
  on-tertiary-fixed-variant: '#004b73'
  background: '#f7f9fb'
  on-background: '#191c1e'
  surface-variant: '#e0e3e5'
typography:
  headline-lg:
    fontFamily: Geist
    fontSize: 30px
    fontWeight: '600'
    lineHeight: 38px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Geist
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Geist
    fontSize: 18px
    fontWeight: '600'
    lineHeight: 26px
  body-lg:
    fontFamily: Geist
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  body-sm:
    fontFamily: Geist
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 18px
  label-md:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Geist
    fontSize: 11px
    fontWeight: '600'
    lineHeight: 14px
  mono-data:
    fontFamily: Geist Mono
    fontSize: 13px
    fontWeight: '400'
    lineHeight: 20px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  sidebar-width: 260px
  sidebar-collapsed: 64px
  container-max: 1440px
---

## Brand & Style
The design system is engineered for high-stakes academic administration, prioritizing **Information Density** and **Clarity** over decorative elements. The brand personality is authoritative, precise, and systematic, catering to registrars, educators, and technical auditors.

The aesthetic follows a **Modern Enterprise SaaS** approach:
- **Systematic Order:** Every element follows a strict logical hierarchy to reduce cognitive load during complex data entry.
- **Precision-Focused:** High-contrast borders and subtle tonal shifts replace heavy shadows to maintain a clean, "technical" feel.
- **Utilitarian Elegance:** Whitespace is used strategically—not to be "airy," but to create clear separation between dense data clusters.

## Colors
The palette is rooted in a "Deep Institutional Blue" to convey stability and trust.

- **Primary:** Deep Slate Blue (#0F172A) used for navigation, headers, and primary actions.
- **Surface & Neutrals:** A range of cool slates. The background uses a very light grey (#F8FAFC) to reduce eye strain during long sessions.
- **Functional Accents:**
    - **Success (Green):** For passing grades and approved workflows.
    - **Warning (Amber):** For pending tasks or academic delays.
    - **Error/Audit (Red):** For failed validations or critical compliance alerts.
- **Interface Borders:** Use a subtle Slate-200 (#E2E8F0) to define table structures without adding visual noise.

## Typography
This design system utilizes **Geist** to leverage its technical, Swiss-inspired precision. The typeface is optimized for tabular data and small-scale interface labels.

- **Data Density:** Use `body-sm` (13px) as the standard for table cells and form inputs to maximize information on-screen.
- **Headlines:** Keep headings restrained. Use `headline-sm` for card titles and section headers.
- **Monospace Utility:** While Geist is the primary family, use its monospaced numeric variants for grades, IDs, and financial figures to ensure perfect vertical alignment in tables.
- **Hierarchy:** Use font weight (500 and 600) rather than large size increases to differentiate information levels.

## Layout & Spacing
The layout follows a **Fixed-Fluid Hybrid** model designed for widescreen dashboards.

- **Grid:** A 12-column grid is used for dashboard layouts, but table views utilize a fluid 100% width with horizontal scrolling for overflow.
- **Sidebar:** A collapsible primary navigation anchored to the left. 
    - *Expanded:* 260px for full labels and nesting.
    - *Collapsed:* 64px showing only high-contrast icons.
- **Gutter Strategy:** A tight 16px (md) gutter between data cards to maintain high density, with 24px (lg) outer margins for the main viewport.
- **Vertical Rhythm:** Components are spaced using 4px increments to ensure tight alignment in form-heavy views.

## Elevation & Depth
In this design system, depth is communicated through **Tonal Layering** rather than traditional shadows, keeping the UI flat and professional.

- **Level 0 (Background):** #F8FAFC (Slate 50).
- **Level 1 (Cards/Sidebar):** Pure white (#FFFFFF) with a 1px border (#E2E8F0).
- **Level 2 (Popovers/Modals):** Pure white with a very subtle, tight shadow (0 4px 6px -1px rgb(0 0 0 / 0.1)) to lift it off the data grid.
- **Active States:** Subtle inset shadows or 2px primary-colored borders indicate focus in form fields and selected table rows.

## Shapes
The shape language is "Soft" yet disciplined. 

- **Standard Radius:** 0.25rem (4px) is the default for buttons, inputs, and checkboxes. This creates a modern feel while remaining sharp enough for an enterprise environment.
- **Large Components:** Cards and modals use 0.5rem (8px) to provide a clear container definition.
- **Interactive Elements:** Avoid pills or circles unless used for status pips or user avatars.

## Components
Consistent styling across the platform ensures the technical user feels in control.

- **Tables:** The core component. Features include "Sticky" headers, row hovering (Slate 50), and horizontal scroll indicators. Header cells use `label-sm` with a subtle grey background.
- **Buttons:**
    - *Primary:* Solid Deep Blue (#0F172A), white text.
    - *Secondary:* White background, Slate 200 border, Slate 700 text.
    - *Ghost:* No border, used for alignment in headers and filters.
- **Inputs:** 40px height for standard, 32px for "compact" table filters. Labels are always top-aligned.
- **Advanced Filters:** A persistent horizontal bar above tables. Uses "Chips" to show active filter parameters that can be cleared individually.
- **Skeletons:** Use a subtle pulse animation with a Slate-100 to Slate-200 gradient. Ensure skeletons mirror the exact height and roundedness of the components they replace (e.g., 40px bars for inputs).
- **Chips/Badges:** Small, low-saturation backgrounds with high-saturation text for status (e.g., Light Green background with Dark Green text for "Approved").