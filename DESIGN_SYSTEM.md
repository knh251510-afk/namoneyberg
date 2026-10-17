# NAMONEYBERG reference-based redesign — 2026-10-17

Primary reference: https://securities.koreainvestment.com/main/Main.jsp
Observed stylesheet: https://securities.koreainvestment.com/inc_renewal/css/common_2021.css?ver=20260620
The renewed site declares Pretendard at weights 100–900. Legacy styles also contain MGothic/Malgun Gothic; these proprietary font assets are not copied. NAMONEYBERG serves its own licensed Pretendard font.

Observed layout: logo and navigation in one horizontal header; thin horizontal market ticker; white page canvas; content sections separated by measured whitespace and rules; brown active states.

Application choices: 1240 px maximum container including 32 px gutters, 21 px wordmark, 14 px navigation at 500, 28 px screen headings, 18–22 px research headings at 600, 15 px reading text with 1.75–1.85 leading, tabular numbers. Compact ticker values at 16 px, no oversized market cards in the header. Warm research lead block, flat reading sections, low-radius native controls, brown primary actions, red rises/blue falls.

This is an original implementation using the observed hierarchy and layout as reference; no KIS logos, marketing images, proprietary fonts or source components are redistributed. No claim of using KIS's internal design system. Existing Tabler/SEED adaptations are superseded as the primary visual direction. Supporting existing open-source asset licenses remain in licenses/.
