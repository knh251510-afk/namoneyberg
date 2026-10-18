"""Small, versioned economic ontology. Relations are conditional context, not news facts."""
import re

VERSION = 'economic-context-v1'
# Stable identifiers, readable labels, entity types, explicit aliases.
CONCEPTS = {
 'cpi': ('소비자물가', 'indicator', ['CPI','consumer price','소비자물가']),
 'ppi': ('생산자물가', 'indicator', ['PPI','producer price','생산자물가']),
 'pce': ('PCE 물가', 'indicator', ['PCE','personal consumption expenditure','개인소비지출 물가']),
 'policy_rate': ('정책금리', 'policy', ['policy rate','interest rate','기준금리','정책금리','금리 인하','금리 인상']),
 'central_bank': ('중앙은행', 'institution', ['Fed','FOMC','Federal Reserve','ECB','BOJ','연준','한국은행','일본은행','중앙은행']),
 'bond_yield': ('국채 수익률', 'market', ['Treasury yield','bond yield','국채금리','국채 금리','국채 수익률']),
 'fx': ('환율', 'market', ['exchange rate','currency','환율','원화','달러 강세','달러 약세']),
 'oil': ('원유·에너지', 'commodity', ['crude','oil','OPEC','유가','원유','에너지']),
 'employment': ('고용', 'indicator', ['employment','payroll','unemployment','고용','실업','일자리']),
 'wages': ('임금', 'indicator', ['wage','wages','임금']),
 'gdp': ('경제 성장', 'indicator', ['GDP','economic growth','경제성장','성장률']),
 'trade': ('무역', 'indicator', ['export','exports','import','imports','tariff','수출','수입','관세','무역']),
 'equity': ('주식시장', 'market', ['stocks','equities','Nasdaq','KOSPI','증시','주가','코스피','나스닥']),
 'semiconductor': ('반도체', 'industry', ['semiconductor','chips','HBM','반도체','메모리']),
 'ai': ('AI 투자', 'industry', ['AI','artificial intelligence','인공지능','AI 투자']),
}
# Relationships never encode an unconditional price prediction.
RELATIONS = [
 ('ppi','cpi','may_transmit','생산 단계 가격은 소비자 가격으로 전가될 수 있으나 수요·마진에 따라 다르다.'),
 ('oil','ppi','may_affect','에너지 가격은 생산 비용과 일부 생산자 가격에 영향을 줄 수 있다.'),
 ('oil','cpi','may_affect','에너지 가격의 소비자물가 영향은 가중치·정책·환율에 따라 다르다.'),
 ('cpi','policy_rate','informs','물가 흐름은 정책 판단의 핵심 재료다. 중앙은행은 성장·고용·금융 여건을 함께 살펴 금리 경로를 결정한다.'),
 ('pce','policy_rate','informs','미국 PCE 물가는 연준의 판단 자료이며 고용·전망과 함께 해석한다.'),
 ('employment','policy_rate','informs','고용은 경기·물가 전망을 통해 정책 기대에 연결될 수 있다.'),
 ('wages','cpi','may_affect','임금은 서비스 비용과 연결되지만 생산성·마진에 따라 전가가 다르다.'),
 ('central_bank','policy_rate','sets','중앙은행별 관할과 정책 수단을 구분해야 한다.'),
 ('policy_rate','bond_yield','may_affect','정책 경로 기대는 국채 수익률에 영향을 주며 장기물에는 기간 프리미엄도 작용한다.'),
 ('policy_rate','fx','may_affect','국가 간 금리차와 예상 경로는 환율의 여러 결정 요인 중 하나다.'),
 ('bond_yield','equity','may_affect','할인율은 주식 가치에 연결되지만 실적·위험 선호가 함께 작용한다.'),
 ('fx','trade','may_affect','환율은 수출입 가격과 채산성에 연결되며 계약 통화·시차에 따라 다르다.'),
 ('trade','gdp','contributes_to','순수출은 GDP의 구성 요소다. 소비·투자·정부지출과 함께 성장에 기여한다.'),
 ('employment','gdp','related_to','고용과 성장은 연결되지만 생산성·경제활동참가율을 함께 확인한다.'),
 ('ai','semiconductor','may_affect','AI 투자는 반도체 수요에 연결될 수 있으나 품목별 수요와 공급을 구분한다.'),
 ('semiconductor','trade','related_to','반도체 생산·수출은 국가·기업·기간별로 구분해야 한다.'),
]
COUNTRIES = {'USA':['United States','US','미국'], 'KOR':['Korea','한국'],
             'CHN':['China','중국'], 'JPN':['Japan','일본'], 'EMU':['eurozone','유로존']}

def matches(text, alias):
    # ASCII boundaries prevent AI in "said" and US in "business".
    pattern = re.escape(alias)
    if alias[0].isascii() and alias[0].isalnum(): pattern = r'(?<![A-Za-z0-9])'+pattern
    if alias[-1].isascii() and alias[-1].isalnum(): pattern += r'(?![A-Za-z0-9])'
    return bool(re.search(pattern,text,re.I))

def concepts(text):
    return [key for key,(_,_,aliases) in CONCEPTS.items() if any(matches(text,a) for a in aliases)]

def annotate(article):
    text = article.get('title','')+' '+article.get('excerpt','')
    return {'url':article.get('url',''), 'concept_ids':concepts(text),
            'countries':[key for key,aliases in COUNTRIES.items() if any(matches(text,a) for a in aliases)]}

def context(articles):
    annotations = [annotate(a) for a in articles]
    present = {c for a in annotations for c in a['concept_ids']}
    relations = [{'source':a,'target':b,'type':kind,'caution':note}
                 for a,b,kind,note in RELATIONS if a in present and b in present]
    return {'version':VERSION,'concepts':[{'id':c,'label':CONCEPTS[c][0],'type':CONCEPTS[c][1]} for c in sorted(present)],
            'articles':annotations,'relations':relations,
            'rule':'편집된 개념 관계는 조건부 해석 맥락이며 이번 주 사실·인과관계·시장 반응의 증거가 아니다. 국가·기간·단위가 다르면 직접 비교하지 말 것.'}

def validate_concepts(report,evidence):
    lookup={a['id']:set(annotate(a)['concept_ids']) for a in evidence}
    for theme in report.get('themes',[]):
        supported=set().union(*(lookup.get(i,set()) for i in theme.get('news_ids',[])))
        ids=theme.get('concept_ids',[])
        if not set(ids)<=supported:
            raise ValueError('온톨로지 검증 실패: 인용 뉴스에서 확인되지 않는 개념입니다.')
    return {'version':VERSION,'passed':True,'scope':'개념 ID와 인용 기사 연결; 인과관계 진실성 검증은 아님'}
