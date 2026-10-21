"""브리핑 게시 전 결정적 검증. 경제적 해석의 진실성까지 보장하지는 않습니다."""
import json,re
from urllib.parse import urlsplit

VERSION='grounding-v1'

def numbers(text):
    return [float(x.replace(',','')) for x in re.findall(r'(?<![A-Za-z])[-+]?\d[\d,]*(?:\.\d+)?',text)]

def validate(report,evidence,snapshot,strict_numbers=True):
    lookup={x['id']:x for x in evidence};errors=[];warnings=[]
    if not report.get('themes'):errors.append('종합할 근거가 충분한 주제가 없습니다.')
    for theme in report.get('themes',[]):
        ids=list(dict.fromkeys(theme.get('news_ids',[])))
        if any(i not in lookup for i in ids):errors.append('존재하지 않는 출처 ID');continue
        urls={lookup[i].get('url') for i in ids}
        if len(urls)<2:errors.append(theme['title']+': 서로 다른 기사 근거가 2건 미만')
        if any(urlsplit(u or '').scheme not in ('http','https') for u in urls):errors.append('잘못된 출처 URL')
        support=' '.join(json.dumps(lookup[i],ensure_ascii=False) for i in ids)+' '+json.dumps(snapshot,ensure_ascii=False)
        supported=numbers(support)
        missing=[n for n in numbers(' '.join(theme.get(field,'') for field in ('title','facts','interpretation','watch','comparison'))) if not any(abs(n-s)<=0.011 for s in supported)]
        if missing:(errors if strict_numbers else warnings).append(theme['title']+': 근거에서 확인되지 않는 수치 '+', '.join(map(str,missing)))
    all_support=numbers(json.dumps(evidence,ensure_ascii=False)+' '+json.dumps(snapshot,ensure_ascii=False,default=str))
    for field in ('headline','summary'):
        missing=[n for n in numbers(report.get(field,'')) if not any(abs(n-s)<=0.011 for s in all_support)]
        if missing:(errors if strict_numbers else warnings).append(field+': 근거 없는 수치 '+', '.join(map(str,missing)))
    if errors:raise ValueError('근거 검증 실패로 게시하지 않았습니다. '+' / '.join(errors[:4]))
    return {'version':VERSION,'passed':not warnings,'warnings':warnings,'checks':['출처 ID','서로 다른 기사 2건','출처 URL','종합 흐름 수치 근거'],'limits':'수치 일치는 단위·인과관계의 정확성 보장이 아니며 원문 전체 검증은 아님'}
