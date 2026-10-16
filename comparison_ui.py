"""읽기 쉬운 HTML 비교표: 값·기간을 한 셀에 배치합니다."""
from html import escape
import pandas as pd
import streamlit as st


def period(value, monthly=False):
    if pd.isna(value):return '관측 없음'
    try:return pd.Timestamp(value).strftime('%Y.%m' if monthly else '%Y')
    except (ValueError,TypeError):return str(value)


def render(frame,columns,country_col='경제권'):
    # columns: (표시 제목, 값 열, 기간 열, 단위, 주기)
    headers='<th scope="col">경제권</th>'+''.join(
        f'<th scope="col">{escape(title)}<small>{escape(unit)}</small></th>' for title,_,_,unit,_ in columns)
    rows=[]
    for _,r in frame.iterrows():
        cells=[f'<th scope="row">{escape(str(r[country_col]))}</th>']
        for _,value_col,date_col,unit,monthly in columns:
            v=r.get(value_col)
            number='—' if pd.isna(v) else f'{float(v):,.2f}'
            stamp=period(r.get(date_col),monthly)
            prev=r.get(value_col+' 이전',r.get('previous') if value_col=='value' else None)
            change=r.get(value_col+' 증감',r.get('change') if value_col=='value' else None)
            extra=''
            details=escape(stamp)
            if prev is not None and not pd.isna(prev):
                delta=f'{float(change):+.2f}' if change is not None and not pd.isna(change) else '—'
                cls='rise' if change is not None and change>0 else ('fall' if change is not None and change<0 else 'flat')
                arrow='▲' if cls=='rise' else ('▼' if cls=='fall' else '−')
                details+=f' · 이전 {float(prev):,.2f}'
                extra=f'<small class="{cls}">{arrow} {delta} %p</small>'
            cells.append(f'<td><span class="value">{number}</span><small class="observation">{details}</small>{extra}</td>')
        rows.append('<tr>'+''.join(cells)+'</tr>')
    st.markdown('<div class="comparison-wrap"><table class="comparison-table"><thead><tr>'+headers+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>',unsafe_allow_html=True)

    with st.expander('비교 기준',expanded=False):
        st.caption('증감은 직전 관측 대비 차이(%p)입니다. CPI는 월간, GDP·실업률은 연간, 정책금리는 일간 관측 기준입니다.')

def compact(frame,columns,label_col):
    """columns: (제목, 열, 소수 자릿수 또는 None)."""
    head=''.join(f'<th scope="col">{escape(title)}</th>' for title,_,_ in columns)
    rows=[]
    for _,r in frame.iterrows():
        cells=[]
        for title,key,decimals in columns:
            v=r.get(key)
            if v is None or pd.isna(v):text='—'
            elif decimals is not None:
                try:text=f'{float(v):,.{decimals}f}'
                except (ValueError,TypeError):text=str(v)
            else:text=str(v)
            tag='th' if key==label_col else 'td'
            cls=''
            if any(word in key for word in ('변화','증감')) and v is not None and not pd.isna(v):
                try:cls='rise' if float(v)>0 else ('fall' if float(v)<0 else 'flat')
                except (ValueError,TypeError):pass
            cells.append(f'<{tag} class="{cls}">{escape(text)}</{tag}>')
        rows.append('<tr>'+''.join(cells)+'</tr>')
    st.markdown('<div class="comparison-wrap"><table class="comparison-table"><thead><tr>'+head+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div>',unsafe_allow_html=True)
