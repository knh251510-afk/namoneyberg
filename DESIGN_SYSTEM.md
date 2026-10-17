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

## Editorial refinement — 2026-10-17

References: https://www.datawrapper.de/academy/what-to-consider-when-choosing-colors-for-data-visualization ; https://design-system.economist.com/ ; https://github.com/orioncactus/pretendard

Design interpretation (not a copied brand): warm ivory #f5f3ee canvas, ink #252b2e, petrol #234657 navigation, copper #986348 accents. White plotting surfaces, quiet gridlines, category colors reserved for actual series. Pretendard for Korean/Latin consistency; restrained 650 headings and tabular numeric text. Compact current readings replace oversized metric cards.

## Korean enterprise rules

Source: Daangn SEED https://seed-design.io/foundations/typography (accessed 2026-10-17), spacing/state guides. This is a Streamlit adaptation of published numerical/interaction rules, not an installed SEED React library or use of Daangn brand assets.

- Scale: supporting 12/16 px, body 14/19 px (long explanatory text allowed larger leading), section 18/24 px, screen title 26/35 px.
- Weight roles: regular 400, medium 500, bold 700; remove ad-hoc 650/750 weights from shared CSS.
- Article lead 16/24 px; white surface, visibly selected controls, disabled action when comparison has fewer than two elements.
- Selection tray shows chosen series and count before navigation; supports removal, clearing and a single primary compare action.
- NAMONEYBERG palette and Korean financial rise/fall semantics remain product-specific overrides.
