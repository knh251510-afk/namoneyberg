"""One briefing feature and four consistently sized tool groups."""
from html import escape
import streamlit as st
from theme_assets import image_path
from ui_theme import mode

ARTS={'브리핑':('reading','금융가 풍경'),'데이터':('data','통계와 시장 데이터'),'기업 분석':('corporate','기업 재무제표와 계산기'),'발표 일정':('calendar','경제 발표 캘린더와 시계'),'개념 지도':('connections','경제 개념의 연결')}
GROUPS=[
 ('브리핑',[('마켓 오버뷰','이번 주 이슈와 시장 해설','overview'),('뉴스','기사 검색과 원문 확인','news')]),
 ('데이터',[('경제지표','국가별 물가·금리·성장 흐름','indicators'),('국가 통계','KOSIS 통계표 검색과 기간별 분석','statistics'),('시장 시세','주가지수·환율·원자재 가격','quotes'),('데이터 비교','서로 다른 지표를 골라 한눈에 비교','compare')]),
 ('기업 분석',[('기업 분석','기업별 재무제표와 모델링 기초 데이터 · 엑셀 추출','corporate')]),
 ('발표 일정',[('발표 일정','주요 지표 발표값과 정책회의 결정','calendar')]),
 ('개념 지도',[('개념 지도','용어의 뜻과 개념 사이의 관계','glossary')]),
]
DESCRIPTIONS={'데이터':'국가별 지표와 통계를 살펴보고, 필요한 시계열을 비교합니다.','기업 분석':'기업 재무제표를 연도별로 정리하고 엑셀로 가져갑니다.','발표 일정':'발표된 수치와 정책회의 결정, 앞으로의 일정을 확인합니다.','개념 지도':'경제 용어의 뜻과 개념 사이의 관계를 지도로 살펴봅니다.'}

def render(pages):
    by_path={p.url_path:p for p in pages}
    st.markdown('''<style>
.home-intro{padding:14px 0 26px!important;margin-bottom:8px!important;border-bottom:0!important;display:block!important}
.home-intro h1{font-size:28px!important;letter-spacing:-.7px;line-height:1.4;margin:0 0 10px!important;padding:0!important}
.home-intro p{font-size:14px!important;color:var(--nb-muted);margin:0!important;line-height:1.7}
.st-key-home_featured{padding:2px 0}
.st-key-home_featured img{height:210px!important;width:100%!important;object-fit:cover;border-radius:6px}
.st-key-home_featured h2{font-size:21px!important;line-height:1.5!important;padding:0!important;margin:3px 0!important}
.st-key-home_featured [data-testid="stCaptionContainer"] p{font-size:12px!important}
.st-key-home_featured [data-testid="stMarkdownContainer"] p{font-size:14px!important;line-height:1.75}
[class*="st-key-home_group_"] [data-testid="stFullScreenFrame"] > div,.st-key-home_featured [data-testid="stFullScreenFrame"] > div{width:100%!important;max-width:100%!important}
.home-tools-heading{font-size:18px!important;margin:24px 0 4px!important;padding:0!important}
.st-key-home_group_indicators,.st-key-home_group_corporate,.st-key-home_group_calendar,.st-key-home_group_glossary{min-height:350px!important;gap:12px!important}
.stApp h2.home-group-title{font-size:18px!important;font-weight:650!important;color:var(--nb-text)!important;line-height:1.5!important;padding:0!important;margin:0!important}
[class*="st-key-home_group_"] img{height:145px!important;width:100%!important;object-fit:cover;border-radius:5px;transition:filter 150ms ease-out}
[class*="st-key-home_group_"] [data-testid="stCaptionContainer"] p{font-size:13px!important;line-height:1.7!important;min-height:42px;margin:0!important}
[class*="st-key-home_group_"] [data-testid="stPageLink"] a{min-height:40px!important;padding:8px 10px!important;border-radius:5px;background:var(--nb-surface);color:var(--nb-text)!important}
[class*="st-key-home_group_"] [data-testid="stPageLink"] a:hover{background:var(--nb-soft)!important;color:var(--nb-accent)!important}
[class*="st-key-home_group_"] [data-testid="stPageLink"] a p{font-size:13px!important;font-weight:550!important;color:inherit!important}
.home-note{font-size:12px;color:var(--nb-muted);padding:18px 0;border-top:1px solid var(--nb-border);line-height:1.7}
@media(max-width:700px){.home-intro h1{font-size:25px!important}.st-key-home_featured img{height:165px!important}.st-key-home_group_indicators,.st-key-home_group_corporate,.st-key-home_group_calendar,.st-key-home_group_glossary{min-height:0!important}.stApp h2.home-group-title{font-size:17px!important}}
</style><section class="home-intro"><h1>경제 데이터와 시장 해설</h1><p>시장을 읽고, 데이터를 비교하고, 경제의 연결을 이해합니다.</p></section>''',unsafe_allow_html=True)
    import briefing_store
    latest=briefing_store.latest()
    with st.container(key='home_featured',border=True):
        picture,content=st.columns([1,2],gap='large',vertical_alignment='center')
        with picture:st.image(str(image_path('home-reading',mode())),width='stretch')
        with content:
            st.caption('브리핑')
            headline=latest['report']['headline'] if latest else '이번 주 시장의 흐름을 살펴보세요'
            st.markdown('## '+headline)
            if latest:
                summary=latest['report']['summary']
                st.write(summary[:130].rsplit(' ',1)[0]+'…' if len(summary)>130 else summary)
                st.caption('최신화 '+latest['generated_at'][:16].replace('T',' ')+' KST')
            else:st.caption('게시된 시장 해설과 관련 뉴스를 확인합니다.')
            first,second=st.columns(2)
            if 'overview' in by_path:
                with first:st.page_link(by_path['overview'],label='마켓 오버뷰 →')
            if 'news' in by_path:
                with second:st.page_link(by_path['news'],label='뉴스 →')
    st.markdown('<h2 class="home-tools-heading">분석 도구</h2>',unsafe_allow_html=True)
    tools=GROUPS[1:]
    for offset in range(0,len(tools),2):
        for column,(heading,items) in zip(st.columns(2,gap='large'),tools[offset:offset+2]):
            with column:
                with st.container(key='home_group_'+items[0][2],border=True):
                    asset,_=ARTS[heading]
                    st.image(str(image_path('home-'+asset,mode())),width='stretch')
                    st.markdown('<h2 class="home-group-title">'+escape(heading)+'</h2>',unsafe_allow_html=True)
                    st.caption(DESCRIPTIONS[heading])
                    for index in range(0,len(items),2):
                        for link_col,(label,_,path) in zip(st.columns(2),items[index:index+2]):
                            if path in by_path:
                                with link_col:st.page_link(by_path[path],label=label+' →')
    st.markdown('<div class="home-note">통계 출처　World Bank · BIS · FRED · ECOS · KOSIS<br>각 화면에서 자료의 기준 시점과 원문을 확인할 수 있습니다.</div>',unsafe_allow_html=True)
