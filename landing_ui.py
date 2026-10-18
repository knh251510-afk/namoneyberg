"""Public introduction and clear entry points into the existing app."""
import streamlit as st

def render():
    st.markdown('''<style>
.nb-intro{padding:42px 0 36px;border-bottom:1px solid var(--nb-border);position:relative}
.nb-intro .eyebrow{font-size:12px;font-weight:700;letter-spacing:2px;color:var(--seed-color-palette-carrot-800);margin-bottom:20px}
.nb-intro h1{font-size:clamp(32px,4.4vw,52px)!important;line-height:1.25!important;letter-spacing:-2px!important;margin:0 0 24px!important;max-width:760px}
.nb-intro p{max-width:620px;color:var(--nb-muted);font-size:16px!important;line-height:1.8!important}
.nb-intro .intro-actions{display:flex;gap:12px;flex-wrap:wrap;margin:28px 0 8px}
.nb-intro a{display:inline-flex;padding:12px 20px;border-radius:12px;text-decoration:none!important;font-size:14px;font-weight:700;background:var(--seed-color-bg-brand-solid);color:white!important}
.nb-intro a.secondary{background:var(--nb-soft);color:var(--nb-text)!important}
.nb-section-label{font-size:12px;color:var(--nb-muted);letter-spacing:1px;margin:32px 0 12px}
.nb-features{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px;margin:20px 0 36px}
.nb-feature{display:block;padding:24px;border:1px solid var(--nb-border);border-radius:16px;text-decoration:none!important;color:var(--nb-text)!important;background:white;transition:border-color .16s,transform .16s}
.nb-feature:hover{border-color:var(--seed-color-palette-carrot-400);transform:translateY(-2px)}
.nb-feature .index{font-size:12px;font-weight:700;color:var(--seed-color-palette-carrot-800)}
.nb-feature h3{margin:16px 0 10px!important;font-size:18px!important}
.nb-feature p{font-size:14px!important;line-height:1.7!important;color:var(--nb-muted);margin:0 0 20px}
.nb-feature .go{font-size:12px;font-weight:600;color:var(--nb-text)}
.nb-start{background:var(--nb-soft);padding:24px;border-radius:16px;margin-bottom:24px;line-height:1.8}
.nb-start b{display:block;margin-bottom:8px}.nb-start p{margin:0;color:var(--nb-muted);font-size:14px!important}
@media(max-width:780px){.nb-features{grid-template-columns:repeat(2,minmax(0,1fr))}.nb-intro{padding-top:24px}}
@media(max-width:480px){.nb-features{grid-template-columns:1fr}.nb-intro h1{letter-spacing:-1px!important}}
@media(prefers-reduced-motion:reduce){.nb-feature{transition:none}.nb-feature:hover{transform:none}}
</style>
<section class="nb-intro"><div class="eyebrow">NAMONEYBERG / ECONOMIC RESEARCH</div>
<h1>경제의 숫자와 뉴스,<br>연결해서 읽는 곳.</h1>
<p>세계 경제의 흐름을 브리핑으로 살펴보고, 통계와 시장 데이터를 직접 비교하세요. 낯선 개념은 관계 지도를 통해 이해할 수 있습니다.</p>
<div class="intro-actions"><a href="/overview" target="_self">마켓 오버뷰 읽기 ↗</a><a class="secondary" href="/compare" target="_self">데이터 직접 비교하기 →</a></div></section>
<div class="nb-section-label">EXPLORE / 무엇을 할 수 있나요?</div>''',unsafe_allow_html=True)
    features=[
        ('마켓 오버뷰','여러 뉴스에서 공통 흐름을 모아 시장 의미와 확인할 변수를 읽습니다. 출처도 함께 살펴볼 수 있습니다.','overview'),
        ('경제지표 · 통계','국가별 물가·금리·성장 지표와 KOSIS 국내 통계를 탐색하고 증감·기간 최고·최저를 확인합니다.','statistics'),
        ('데이터 비교','경제권과 지표를 조합하고 표시 기준을 바꿔 시계열의 움직임을 비교합니다.','compare'),
        ('시장 시세','주가지수·환율·원자재·디지털 자산의 최신 제공 시세와 추이를 살펴봅니다.','quotes'),
        ('경제 개념 지도','우주처럼 펼쳐진 지도를 탐색하며 개념의 뜻과 개념 사이의 조건부 관계를 이해합니다.','glossary'),
        ('발표 일정 · 뉴스','주요 경제지표 발표 일정을 확인하고 관심 있는 뉴스의 원문으로 이동합니다.','calendar'),
    ]
    cards=[]
    for i,(name,description,path) in enumerate(features,1):
        cards.append(f'<a class="nb-feature" href="/{path}" target="_self"><span class="index">0{i}</span><h3>{name}</h3><p>{description}</p><span class="go">살펴보기 →</span></a>')
    st.markdown('<div class="nb-features">'+''.join(cards)+'</div>',unsafe_allow_html=True)
    st.markdown('<div class="nb-start"><b>처음이라면 이렇게 시작하세요.</b><p>마켓 오버뷰에서 흐름 파악 → 궁금한 숫자를 데이터로 비교 → 경제 개념 지도에서 연결 관계 확인</p></div>',unsafe_allow_html=True)
