"""Pure series preparation: no interpolation or invented observations."""
import numpy as np
import pandas as pd

MODES=['원래 값','시작값 = 100','시작 대비 변화율 (%)','시작 대비 차이','표준화 · Z-score']

def prepare(frame,start,end,frequency='원래 주기',aggregation='마지막 값',overlap=True):
    f=frame.copy()
    f['date']=pd.to_datetime(f['date'],errors='coerce',utc=True).dt.tz_localize(None)
    f['value']=pd.to_numeric(f['value'],errors='coerce').replace([np.inf,-np.inf],np.nan)
    f=f.dropna(subset=['date','value']).sort_values('date').drop_duplicates(['series','date'],keep='last')
    f=f[f.date.between(pd.Timestamp(start),pd.Timestamp(end))]
    if frequency!='원래 주기' and not f.empty:
        freq={'월간':'M','분기':'Q','연간':'Y'}[frequency]
        # Only aggregate real observations; do not carry a value into an empty bucket.
        f['bucket']=f.date.dt.to_period(freq)
        if aggregation=='평균':
            f=f.groupby(['series','bucket'],as_index=False).agg(value=('value','mean'),date=('date','max'))
        else:f=f.groupby(['series','bucket'],sort=False).tail(1)
        f=f[['series','date','value']]
    if overlap and not f.empty:
        lo=f.groupby('series').date.min().max();hi=f.groupby('series').date.max().min()
        f=f[f.date.between(lo,hi)]
    return f.reset_index(drop=True)

def transform(frame,mode):
    parts=[]
    for name,sub in frame.groupby('series',sort=False):
        sub=sub.sort_values('date').copy();base=sub.value.iloc[0]
        if mode in ('시작값 = 100','시작 대비 변화율 (%)'):
            if base<=0:raise ValueError(name+': 시작값이 0 이하입니다. 차이 또는 표준화를 선택해주세요.')
            sub['value']=sub.value/base*100-(100 if mode=='시작 대비 변화율 (%)' else 0)
        elif mode=='시작 대비 차이':sub['value']=sub.value-base
        elif mode=='표준화 · Z-score':
            std=sub.value.std(ddof=0);sub['value']=(sub.value-sub.value.mean())/std if std>0 else 0.0
        parts.append(sub)
    return pd.concat(parts,ignore_index=True) if parts else frame.copy()
