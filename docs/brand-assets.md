# Brand assets

- `static/brand/namoneyberg-wordmark.webp`: user-supplied full wordmark, lossily compressed without changing layout; displayed as home link.
- `static/brand/namoneyberg-social.jpg`: user-supplied full-resolution logo for sharing.
- `static/brand/namoneyberg-icon.png`: 256px icon made with the built-in image tool.

Icon edit prompt: preserve the supplied heavy geometric letterforms; retain only black 나 and blue 버, side by side on white; remove 머, 니, 그 and period; no decoration.

Streamlit Community Cloud generates link-preview images from a daily screenshot. The separate social image is provided for platforms that permit a custom upload; it is not represented as a custom Cloud Open Graph setting.

Dark header: `static/brand/namoneyberg-wordmark-dark.webp`. Built-in image edit prompt: preserve exact wordmark geometry, change black letters to off-white and blue letters to soft blue, remove white background to transparent alpha, no glow or shadow. Original uploaded wordmark remains unchanged.

Current header: `static/brand/namoneyberg-english.webp`, user-supplied English wordmark with compression only. Dark mode uses CSS inversion and screen blending to preserve its letterforms.

Current icon: `static/brand/namoneyberg-icon.png`, single uppercase N extracted with the built-in image tool from the English wordmark. Prompt: retain only the original heavy black N, preserve its shape and proportions, center on white square with 15% margin, no decoration or additional letters. This replaces the earlier 나버 icon.
