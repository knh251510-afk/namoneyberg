"""Compact service directory, using SEED typography and neutral surfaces."""
from html import escape
import streamlit as st

GROUPS=[
 ('시장 읽기',[
  ('마켓 오버뷰','이번 주 이슈와 시장 해설','overview'),
  ('경제 뉴스','기사 검색과 원문 확인','news'),
  ('발표 일정','주요 지표의 발표일과 발표값','calendar'),
 ]),
 ('데이터 살펴보기',[
  ('경제지표','국가별 물가·금리·성장 흐름','indicators'),
  ('국가 통계','KOSIS 통계표 검색과 기간별 분석','statistics'),
  ('시장 시세','주가지수·환율·원자재 가격','quotes'),
 ]),
 ('비교하고 이해하기',[
  ('데이터 비교','서로 다른 지표를 골라 한눈에 비교','compare'),
  ('경제 개념 지도','용어의 뜻과 개념 사이의 관계','glossary'),
 ]),
]

def render():
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
</style>
<section class="home-intro"><div><h1>경제 데이터와 시장 해설</h1><p>주간 브리핑부터 국가 통계와 시장 시세까지.<br>필요한 자료를 찾아보고, 지표를 직접 비교할 수 있습니다.</p></div>
<nav class="home-quick" aria-label="추천 시작점"><div class="quick-label">바로 시작하기</div><a href="/overview" target="_self">이번 주 마켓 오버뷰 <span>→</span></a><a href="/compare" target="_self">데이터 비교하기 <span>→</span></a></nav></section>
''',unsafe_allow_html=True)
    groups=[]
    for heading,items in GROUPS:
        links=[]
        for label,description,path in items:
            links.append(f'<a class="home-tool" href="/{path}" target="_self"><span class="tool-title">{escape(label)}<span class="tool-arrow" aria-hidden="true">↗</span></span><p>{escape(description)}</p></a>')
        groups.append('<section class="home-group"><h2>'+escape(heading)+'</h2>'+''.join(links)+'</section>')
    st.markdown('<div class="home-directory">'+''.join(groups)+'</div>',unsafe_allow_html=True)
    st.markdown('<div class="home-note"><span><b>통계 출처</b>　World Bank · BIS · FRED · ECOS · KOSIS</span><span>각 화면에서 자료의 기준 시점과 원문을 확인할 수 있습니다.</span></div>',unsafe_allow_html=True)
