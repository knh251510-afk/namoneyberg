"""Calculate source observations in code; never ask a model to invent returns."""
import pandas as pd

def observations(frame,meta,kind):
    if frame.empty:return []
    rows=[]
    groups=frame.groupby('country') if 'country' in frame else [('series',frame)]
    for country,part in groups:
        f=part.dropna(subset=['value']).sort_values('date').tail(2)
        if f.empty:continue
        cur=f.iloc[-1];prev=f.iloc[-2] if len(f)>1 else None
        rows.append({'series':kind,'country':country,'value':float(cur.value),'observation_date':str(cur.date),'previous':None if prev is None else float(prev.value),'previous_date':None if prev is None else str(prev.date),'change':None if prev is None else float(cur.value-prev.value),'source_url':meta.get('url'),'stale':bool(meta.get('stale'))})
    return rows

def build(fetch,market_loader):
    from concurrent.futures import ThreadPoolExecutor
    jobs=[('cpi',''),('policy',''),('wb','gdp'),('wb','unemployment')]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results=list(pool.map(lambda job:fetch(*job),jobs))
    series=[];unavailable=[]
    for job,(frame,meta,error) in zip(jobs,results):
        if error:unavailable.append('/'.join(job));continue
        series.extend(observations(frame,meta,'/'.join(job)))
    try:markets=market_loader()
    except Exception:markets=[];unavailable.append('weekly_markets')
    return {'observations':series,'markets':markets,'unavailable':unavailable,'rules':'관측일은 발표일이 아니다. 연간 자료는 이번 주 발표로 쓰지 않는다. 시장 주간 변화는 코드 계산값만 사용한다.'}
