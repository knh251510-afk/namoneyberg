"""최근접 날짜 툴팁과 기간 내 극값을 표시하는 공통 시계열 차트."""
import altair as alt
import pandas as pd
from datetime import datetime
from zoneinfo import ZoneInfo

def timeseries(frame,x,y,unit,group=None,color='#9cc5f0',height=350,domain=None):
    alt.data_transformers.disable_max_rows()
    today=pd.Timestamp(datetime.now(ZoneInfo('Asia/Seoul')).date())
    f=frame.dropna(subset=[x,y]).reset_index(drop=True).copy()
    f[x]=pd.to_datetime(f[x]).dt.tz_localize(None)
    f=f[f[x].between(pd.Timestamp('2000-01-01'),today)].copy()
    if f.empty:return alt.Chart(pd.DataFrame({x:[],y:[]})).mark_line().properties(height=height)
    lo,hi=(pd.Timestamp(domain[0]),pd.Timestamp(domain[1])) if domain else (pd.Timestamp('2000-01-01'),today)
    lo=max(lo,pd.Timestamp('2000-01-01'));hi=min(hi,today)
    tip=([alt.Tooltip(group+':N',title='계열')] if group else [])+[alt.Tooltip(x+':T',title='날짜',format='%Y-%m-%d'),alt.Tooltip(y+':Q',title=unit,format=',.4f')]
    base=alt.Chart(f).encode(x=alt.X(x+':T',title=None,scale=alt.Scale(domain=[alt.DateTime(year=lo.year,month=lo.month,date=lo.day),alt.DateTime(year=hi.year,month=hi.month,date=hi.day)],nice=False)),y=alt.Y(y+':Q',title=unit,scale=alt.Scale(zero=False)))
    if group:base=base.encode(color=alt.Color(group+':N',legend=alt.Legend(orient='bottom')))
    if group:
        visible=alt.selection_point(fields=[group],bind='legend',toggle='true',clear=False,empty=False,value=[{group:str(v)} for v in f[group].dropna().unique()])
        base=base.encode(opacity=alt.condition(visible,alt.value(1),alt.value(0)))
    line=base.mark_line(strokeWidth=2,**({} if group else {'color':color}))
    hover=alt.selection_point(nearest=True,on='pointerover',fields=[x],empty=False,clear='pointerout')
    targets=base.mark_point(opacity=0,size=100).encode(opacity=alt.value(0),tooltip=tip).add_params(hover)
    if group:targets=targets.transform_filter(visible)
    rule=alt.Chart(f).mark_rule(color='#7f8994',strokeDash=[3,3]).encode(x=x+':T',tooltip=tip).transform_filter(hover)
    parts=[line,targets,rule]
    groups=f.groupby(group,sort=False) if group else [(None,f)]
    extrema=[]
    for _,sub in groups:
        for kind,idx in [('최고',sub[y].idxmax()),('최저',sub[y].idxmin())]:
            row=sub.loc[idx].to_dict();row['극값']=kind;row['표시']=f'{kind} {row[y]:,.2f}';extrema.append(row)
    e=pd.DataFrame(extrema)
    for kind,dy in [('최고',-13),('최저',16)]:
        b=alt.Chart(e[e['극값']==kind]).encode(x=x+':T',y=y+':Q',tooltip=[alt.Tooltip('극값:N')]+tip)
        if group:b=b.encode(color=alt.Color(group+':N',legend=None),opacity=alt.condition(visible,alt.value(1),alt.value(0)))
        parts.extend([b.mark_point(shape='diamond',filled=True,size=95,**({} if group else {'color':'#5cd5ed'})),b.mark_text(dy=dy,fontSize=10,color='#bdd3ed').encode(text='표시:N')])
    result=alt.layer(*parts).properties(height=height).resolve_scale(x='shared',y='shared')
    if group:result=result.add_params(visible)
    return result
