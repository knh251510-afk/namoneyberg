"""Vectorized BIS wide-to-long parsing; preserve units and actual missing values."""
import re
import pandas as pd

def long_frame(frame, reverse, monthly=False, definitions=False):
    pattern=r'\d{4}-\d{2}' if monthly else r'\d{4}-\d{2}-\d{2}'
    columns=[c for c in frame.columns if re.fullmatch(pattern,str(c)) and c>='2000-01']
    selected=frame[frame.REF_AREA.isin(reverse)].copy()
    selected['country']=selected.REF_AREA.map(reverse)
    ids=['country']
    if definitions:
        selected['definition']=selected['COMPILATION'].astype(str) if 'COMPILATION' in selected else ''
        ids.append('definition')
    out=selected[ids+columns].melt(id_vars=ids,var_name='date',value_name='value')
    out['value']=pd.to_numeric(out.value,errors='coerce')
    out=out.dropna(subset=['value'])
    out['date']=pd.to_datetime(out.date,format='%Y-%m' if monthly else '%Y-%m-%d')
    return out.sort_values('date').reset_index(drop=True)
