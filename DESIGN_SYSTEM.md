# NAMONEYBERG UI rules

Adapted for Streamlit from Tabler's open-source design tokens (retrieved 2026-10-17).
Source: https://github.com/tabler/tabler/blob/dev/core/scss/_variables.scss
License: licenses/Tabler-LICENSE.txt (MIT). This is a token adaptation, not the complete Bootstrap/Tabler runtime.

- Spacing: 4 / 8 / 16 / 24 / 32 px; page width 1248 px including gutters.
- Typography: Pretendard; body 14 px; page title 28 px; section 22 px; topic 16–18 px; metadata 11–12 px.
- Surface: white cards on #f6f8fb; border #dce1e7; radius 6 px.
- Brand override: navy #243f63 and brown #82664f. Market rises red, falls blue.
- Desktop: 24 px gutters; 24 px card padding. Narrow screens: 12–16 px gutters, stacked brief labels/cards.
- Tabs: 44 px height with selected brown underline. Form geometry remains native BaseWeb.
- Interaction: visible keyboard focus, hover states, reduced-motion support; ticker pauses on hover/focus.
- Change tokens in ui_theme.py; avoid anonymous generated Streamlit CSS class selectors.

GitHub changes intentionally contain UI assets only; local news caches, credentials and generated reports are not synchronized.
