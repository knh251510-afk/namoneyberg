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
    by_path={page.url_path:page for page in pages}
    from theme_assets import image_path
    from ui_theme import mode
    st.markdown('''<style>
.home-intro{padding:20px 0 28px;margin-bottom:20px}
.home-intro h1{font-size:30px!important;line-height:1.4!important;padding:0!important;margin:0 0 12px!important;letter-spacing:-.7px}
.home-intro p{font-size:15px!important;line-height:1.8;color:var(--nb-muted)}
[class*="st-key-home_card_"]{position:relative!important;height:320px!important;min-height:320px!important;overflow:hidden;border-radius:10px;background:var(--nb-surface);isolation:isolate;gap:0!important;transition:transform 200ms ease,box-shadow 200ms ease}
[class*="st-key-home_card_"] [data-testid="stFullScreenFrame"]>div,[class*="st-key-home_card_"] [data-testid="stImage"],[class*="st-key-home_card_"] [data-testid="stImageContainer"]{width:100%!important;max-width:100%!important}
[class*="st-key-home_card_"] img{width:100%!important;height:320px!important;object-fit:cover;transition:transform 450ms ease,filter 250ms ease}
[class*="st-key-home_card_"] [data-testid="stImageContainer"]:after{content:"";position:absolute;inset:0;pointer-events:none;background:linear-gradient(180deg,transparent 25%,#111111bd 100%)}
[class*="st-key-home_card_"] [data-testid="stImageContainer"]{position:relative}
[class*="st-key-home_card_"] [data-testid="stImage"] button{display:none!important}
.stApp .home-card-title{position:absolute;left:22px;bottom:22px;z-index:2;font-size:23px!important;font-weight:650!important;color:#fff!important;margin:0!important;padding:0!important;transition:opacity 160ms ease}
[class*="st-key-home_menu_"]{position:absolute!important;inset:0;z-index:3;padding:22px!important;justify-content:center;gap:0!important;background:transparent;opacity:0;visibility:hidden;transform:translateY(8px);transition:opacity 200ms ease,transform 200ms ease,visibility 200ms}
[class*="st-key-home_menu_"] [data-testid="stPageLink"] a{padding:4px 0!important;border-radius:5px;background:transparent!important;min-height:30px}
[class*="st-key-home_menu_"] [data-testid="stPageLink"] a p{font-size:15px!important;font-weight:600!important;color:#fff!important}
[class*="st-key-home_menu_"] [data-testid="stCaptionContainer"] p{font-size:12px!important;line-height:1.6!important;color:#e5e5e5!important;margin:0 0 13px!important;min-height:20px}
[class*="st-key-home_menu_"] [data-testid="stPageLink"] a:hover,[class*="st-key-home_menu_"] [data-testid="stPageLink"] a:focus-visible{background:#ffffff20!important;outline:1px solid #ffffff70}
[class*="st-key-home_card_"]:hover,[class*="st-key-home_card_"]:focus-within{transform:translateY(-3px);box-shadow:0 10px 24px #10231b18}
[class*="st-key-home_card_"] img{filter:saturate(.82) contrast(.96)}
[class*="st-key-home_card_"]:hover img,[class*="st-key-home_card_"]:focus-within img{transform:scale(1.025);filter:brightness(.28) saturate(.82)}
[class*="st-key-home_card_"]:hover [class*="st-key-home_menu_"],[class*="st-key-home_card_"]:focus-within [class*="st-key-home_menu_"]{opacity:1;visibility:visible;transform:none}
[class*="st-key-home_card_"]:hover .home-card-title,[class*="st-key-home_card_"]:focus-within .home-card-title{opacity:0}
[class*="st-key-home_card_"] [class*="st-key-home_menu_"]{visibility:visible}
[class*="st-key-home_menu_"] [data-testid="stCaptionContainer"]{margin:0!important;padding:0!important}
[class*="st-key-home_menu_"] [data-testid="stPageLink"] a p{line-height:1.5!important;margin:0!important}
[class*="st-key-home_menu_"] [data-testid="stElementContainer"]{margin:0!important}
.stApp [class*="st-key-home_menu_"] [class*="st-key-home_tool_"]{padding:0!important;border:0!important;background:transparent!important;box-shadow:none!important;gap:0!important}\n.stApp [class*="st-key-home_menu_"] .tool-preview{position:absolute!important;right:0!important;top:5px!important;width:40px;height:22px;color:#e8e8e8;pointer-events:none}\n.stApp [class*="st-key-home_menu_"] [data-testid="stPageLink"] a{padding-right:45px!important}\n.home-note{font-size:12px;color:var(--nb-muted);padding:20px 0;border-top:1px solid var(--nb-border);margin-top:24px}
@media(hover:none){[class*="st-key-home_card_"] img{filter:brightness(.28) saturate(.82)}[class*="st-key-home_menu_"]{opacity:1;visibility:visible;transform:none;padding-top:64px!important;background:transparent}.stApp .home-card-title{top:20px;bottom:auto;font-size:20px!important}[class*="st-key-home_card_"]:focus-within .home-card-title{opacity:1}}
@keyframes ink-trace{from{stroke-dashoffset:110}to{stroke-dashoffset:0}}
@keyframes paper-read{from{transform:translateY(2px);opacity:.3}to{transform:translateY(0);opacity:1}}
@keyframes bar-grow{from{transform:scaleY(.25)}to{transform:scaleY(1)}}
@keyframes node-signal{0%,100%{opacity:.4}50%{opacity:1}}
@media(prefers-reduced-motion:no-preference){
[class*="st-key-home_tool_"]:focus-within .trace{stroke-dasharray:110;animation:ink-trace 650ms ease-out both}
[class*="st-key-home_tool_"]:focus-within .bar{transform-origin:center bottom;transform-box:fill-box;animation:bar-grow 450ms ease-out both}
[class*="st-key-home_tool_"]:focus-within .paper{animation:paper-read 400ms ease-out both}
[class*="st-key-home_tool_"]:focus-within .signal{animation:node-signal 900ms ease-in-out 2}
}
@media(prefers-reduced-motion:reduce){.tool-preview *{animation:none!important}} 
@media(prefers-reduced-motion:reduce){[class*="st-key-home_card_"],[class*="st-key-home_card_"] img,[class*="st-key-home_menu_"]{transition:none!important;transform:none!important}}
</style><section class="home-intro"><h1>경제 데이터와 시장 해설</h1><p>시장의 흐름부터 데이터 분석까지, 필요한 도구를 선택하세요.</p></section>''',unsafe_allow_html=True)
    for offset in range(0,len(GROUPS),3):
        columns=st.columns(3,gap='large')
        for column,(heading,items) in zip(columns,GROUPS[offset:offset+3]):
            with column:
                key=items[0][2]
                with st.container(key='home_card_'+key):
                    asset,_=ARTS[heading]
                    st.image(str(image_path('home-'+asset,mode())),width='stretch')
                    st.markdown('<h2 class="home-card-title">'+escape(heading)+'</h2>',unsafe_allow_html=True)
                    with st.container(key='home_menu_'+key):
                        for label,description,path in items:
                            if path in by_path:
                                with st.container(key='home_tool_'+path):
                                    st.page_link(by_path[path],label=label+' →')
                                    st.caption(description)
                                    st.markdown('<svg class="tool-preview" viewBox="0 0 46 24" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true">'+icons[path]+'</svg>',unsafe_allow_html=True)
    st.markdown('<div class="home-note">통계 출처　World Bank · BIS · FRED · ECOS · KOSIS</div>',unsafe_allow_html=True)
