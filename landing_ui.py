"""Compact service directory, using SEED typography and neutral surfaces."""
from html import escape
import streamlit as st

ARTS={'브리핑':('reading','금융가 풍경'),'데이터':('data','통계와 시장 데이터'),'기업 분석':('corporate','기업 재무제표와 계산기'),'발표 일정':('calendar','경제 발표 캘린더와 시계'),'개념 지도':('connections','경제 개념의 연결')}
GROUPS=[
 ('브리핑',[('마켓 오버뷰','이번 주 이슈와 시장 해설','overview'),('뉴스','기사 검색과 원문 확인','news')]),
 ('데이터',[('경제지표','국가별 물가·금리·성장 흐름','indicators'),('국가 통계','KOSIS 통계표 검색과 기간별 분석','statistics'),('시장 시세','주가지수·환율·원자재 가격','quotes'),('데이터 비교','서로 다른 지표를 골라 한눈에 비교','compare')]),
 ('기업 분석',[('기업 분석','기업별 재무제표와 모델링 기초 데이터 · 엑셀 추출','corporate')]),
 ('발표 일정',[('발표 일정','주요 지표 발표값과 정책회의 결정','calendar')]),
 ('개념 지도',[('개념 지도','용어의 뜻과 개념 사이의 관계','glossary')]),
]

def render(pages):
    st.markdown('''<style>
.home-intro{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(240px,1fr);gap:64px;align-items:start;padding:24px 0 36px;margin-bottom:32px;border-bottom:1px solid var(--nb-border)}
.home-intro h1{font-size:30px!important;font-weight:650!important;line-height:1.4!important;letter-spacing:-.8px!important;margin:0 0 14px!important;padding:0!important}
.home-intro p{font-size:15px!important;line-height:1.8!important;color:var(--nb-muted);max-width:500px;margin:0!important;word-break:keep-all}
.home-quick{border-left:2px solid var(--seed-color-palette-carrot-300);padding-left:24px}
.home-quick .quick-label{font-size:12px;color:var(--nb-muted);margin-bottom:8px}
.home-quick a{display:flex;align-items:center;justify-content:space-between;padding:11px 0;font-size:14px;font-weight:550;color:var(--nb-text)!important;text-decoration:none!important;border-bottom:1px solid var(--nb-border)}
.home-quick a:last-child{border:0}.home-quick a span{color:var(--nb-muted);font-weight:400}
.home-directory{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:36px;margin-bottom:36px}
.home-group h2{font-size:14px!important;font-weight:600!important;color:var(--nb-muted)!important;padding:0 0 14px!important;margin:0!important;border-bottom:1px solid var(--nb-border)}
.home-tool{display:block;padding:20px 0;border-bottom:1px solid var(--nb-border);color:var(--nb-text)!important;text-decoration:none!important}
.home-tool .tool-title{display:flex;align-items:center;justify-content:space-between;font-size:16px;font-weight:600;line-height:1.5;letter-spacing:-.25px}
.home-tool .tool-arrow{font-size:16px;color:var(--seed-color-palette-gray-600);font-weight:400;transition:transform .15s ease}
.home-tool p{font-size:13px!important;font-weight:400;line-height:1.65!important;color:var(--nb-muted);margin:6px 20px 0 0!important;word-break:keep-all}
.home-tool:hover .tool-title,.home-quick a:hover{color:var(--seed-color-palette-carrot-800)!important}
.home-tool:hover .tool-arrow{transform:translateX(3px);color:var(--seed-color-palette-carrot-800)}
.home-tool:focus-visible,.home-quick a:focus-visible{outline:2px solid var(--seed-color-palette-carrot-800);outline-offset:4px;border-radius:3px}
.home-note{display:flex;gap:28px;padding:20px 0;border-top:1px solid var(--nb-border);font-size:12px;color:var(--nb-muted);line-height:1.8;flex-wrap:wrap}
.home-note b{font-weight:500;color:var(--nb-text)}
@media(max-width:800px){.home-intro{grid-template-columns:1fr;gap:24px}.home-quick{max-width:440px}.home-directory{grid-template-columns:1fr;gap:28px}.home-intro h1{font-size:26px!important}.home-tool{padding:16px 0}.home-note{gap:8px;flex-direction:column}}
@media(prefers-reduced-motion:reduce){.home-tool .tool-arrow{transition:none}}

.home-art{margin:0 0 20px;overflow:hidden;height:144px;background:#f8f6f2;border-radius:5px}
.home-art img{width:100%;height:100%;object-fit:cover;display:block;transition:transform 400ms cubic-bezier(.2,.7,.3,1)}
.home-tool .tool-title{gap:8px}.home-tool .tool-title>span:first-child{flex:1}
.tool-preview{width:46px;height:24px;color:var(--seed-color-palette-carrot-800);opacity:.45;flex-shrink:0;overflow:visible}
.tool-preview path,.tool-preview rect,.tool-preview circle{vector-effect:non-scaling-stroke}
@keyframes ink-trace{from{stroke-dashoffset:110}to{stroke-dashoffset:0}}
@keyframes paper-read{0%{transform:translateY(2px);opacity:.3}100%{transform:translateY(0);opacity:1}}
@keyframes bar-grow{from{transform:scaleY(.25)}to{transform:scaleY(1)}}
@keyframes node-signal{0%,100%{opacity:.4}50%{opacity:1}}
@media(prefers-reduced-motion:no-preference){
 .home-tool:hover .tool-preview,.home-tool:focus-visible .tool-preview{opacity:1}
 .home-tool:hover .trace,.home-tool:focus-visible .trace{stroke-dasharray:110;animation:ink-trace 650ms ease-out both}
 .home-tool:hover .paper,.home-tool:focus-visible .paper{animation:paper-read 400ms ease-out both}
 .home-tool:hover .bar,.home-tool:focus-visible .bar{transform-origin:center bottom;animation:bar-grow 450ms ease-out both;transform-box:fill-box}
 .home-tool:hover .signal,.home-tool:focus-visible .signal{animation:node-signal 900ms ease-in-out 2}
 .home-group:has(.home-tool:hover) .home-art img{transform:scale(1.035)}
}
@media(prefers-reduced-motion:reduce){.home-art img{transition:none}.tool-preview *{animation:none!important}}
@media(max-width:800px){.home-art{height:160px;max-width:480px}.tool-preview{opacity:.65}}
</style>
<section class="home-intro"><div><h1>경제 데이터와 시장 해설</h1><p>주간 브리핑부터 국가 통계와 시장 시세까지.<br>필요한 자료를 찾아보고, 지표를 직접 비교할 수 있습니다.</p></div>
</section>
''',unsafe_allow_html=True)
    icons={
        'corporate':'<rect class="bar" x="7" y="12" width="6" height="9"/><rect class="bar" x="20" y="7" width="6" height="14"/><path class="trace" d="M4 17L19 10L40 3"/>',
        'overview':'<path class="paper" d="M7 3h28v18H7zM12 8h18M12 12h13M12 16h17"/>',
        'news':'<path class="paper" d="M5 4h35v17H5zM10 8h10v6H10zM24 8h11M24 12h11M10 18h25"/>',
        'calendar':'<path d="M8 5h28v17H8zM8 10h28M15 2v6M29 2v6"/><circle class="signal" cx="22" cy="16" r="2"/>',
        'indicators':'<path class="trace" d="M4 19L13 13L22 15L30 7L41 4"/>',
        'statistics':'<rect class="bar" x="7" y="13" width="6" height="8"/><rect class="bar" x="20" y="7" width="6" height="14"/><rect class="bar" x="33" y="3" width="6" height="18"/>',
        'quotes':'<path class="trace" d="M3 18L11 10L19 15L27 5L35 12L43 4"/>',
        'compare':'<path class="trace" d="M3 18L14 14L25 16L42 4M3 8L14 12L25 5L42 14"/>',
        'glossary':'<path class="trace" d="M9 15L23 6L38 17M23 6L25 21"/><circle class="signal" cx="9" cy="15" r="3"/><circle class="signal" cx="23" cy="6" r="3"/><circle class="signal" cx="38" cy="17" r="3"/>',
    }
    from pathlib import Path
    by_path={page.url_path:page for page in pages}
    by_path['home']=pages[0]
    for offset in range(0,len(GROUPS),3):
        for column,(heading,items) in zip(st.columns(min(3,len(GROUPS)-offset),gap='large'),GROUPS[offset:offset+3]):
            with column:
                with st.container(key='home_group_'+items[0][2]):
                    asset,alt=ARTS[heading]
                    from theme_assets import image_path
                    from ui_theme import mode
                    st.image(str(image_path('home-'+asset,mode())),width='stretch')
                    st.markdown('<h2 class="home-group-title">'+escape(heading)+'</h2>',unsafe_allow_html=True)
                    for label,description,path in items:
                        if path not in by_path:continue
                        with st.container(key='home_tool_'+path):
                            st.page_link(by_path[path],label=label+'　→')
                            st.caption(description)
                            st.markdown('<svg class="tool-preview" viewBox="0 0 46 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true">'+icons[path]+'</svg>',unsafe_allow_html=True)
    st.markdown('<div class="home-note"><span><b>통계 출처</b>　World Bank · BIS · FRED · ECOS · KOSIS</span><span>각 화면에서 자료의 기준 시점과 원문을 확인할 수 있습니다.</span></div>',unsafe_allow_html=True)
