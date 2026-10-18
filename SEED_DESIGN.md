# SEED Design integration

Source: https://github.com/daangn/seed-design
Documentation: https://seed-design.io/react/getting-started/installation/manual
Package: @seed-design/css 3.0.3, downloaded from the official npm registry.
License: Apache-2.0; original LICENSE and NOTICE are preserved in assets/vendor/seed/package.

The unchanged official base.min.css supplies typography, color, spacing, radius,
and motion tokens. seed_theme.py loads it locally without CDN calls. The local
assets/seed-streamlit.css maps those tokens to Streamlit's native widgets.
It is our adapter, not an upstream React component implementation. No Daangn
logos or trademarks are used. A React migration has not been completed.

Applied patterns: orange primary action, neutral secondary action, soft neutral
field fill, visible keyboard focus, rounded selected navigation, segmented tabs,
readable financial numbers, centered desktop content with mobile gutters.
Price rise/fall semantic colors remain red/blue, independent of orange actions.

Keep official vendor files unchanged; edit only the adapter. On an upgrade,
check all referenced CSS variables and recheck focus, selected, disabled states,
corporate tables, multiselects, and small viewport overflow.
