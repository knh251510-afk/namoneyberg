"""Verified 2026 official schedules; unknown release times stay unknown."""
from datetime import datetime
from zoneinfo import ZoneInfo
KST=ZoneInfo('Asia/Seoul')
SOURCES={
 '국가데이터처':'https://sri.kostat.go.kr/ansk/file/schedule_2026.pdf',
 '한국은행':'https://www.bok.or.kr/portal/singl/crncyPolicyDrcMtg/listYear.do?menuNo=200761&mtgSe=A',
 'ECB':'https://www.ecb.europa.eu/press/calendars/mgcgc/html/index.en.html',
 'BOJ':'https://www.boj.or.jp/en/mopo/mpmsche_minu/m_ref/mref250731a.pdf',
 'BOE':'https://www.bankofengland.co.uk/monetary-policy/upcoming-mpc-dates',
 'Federal Reserve':'https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm',
}

def make(day,country,title,source,clock=None,zone='Asia/Seoul'):
    at=datetime.fromisoformat(day+'T'+(clock or '00:00')).replace(tzinfo=ZoneInfo(zone)).astimezone(KST)
    return {'when':at,'country':country,'title':title,'source':source,'url':SOURCES[source],'time_known':bool(clock),'schedule_checked':'2026-10-18'}

def events():
    rows=[]
    stats={
      '소비자물가':['02-03','03-06','04-02','05-06','06-02','07-02','08-04','09-02','10-02','11-03','12-02','12-31'],
      '고용동향':['01-14','02-11','03-18','04-15','05-13','06-11','07-15','08-12','09-09','10-16','11-11','12-16'],
      '산업활동동향':['01-30','03-04','03-31','04-30','05-29','06-30','07-31','08-31','09-30','10-30','11-30','12-30'],
    }
    for title,days in stats.items():
        for index,day in enumerate(days):
            row=make('2026-'+day,'한국','한국 '+title,'국가데이터처')
            ordinal=2026*12+(0 if title=='소비자물가' else -1)+index
            row['target_period']=f'{ordinal//12:04d}-{ordinal%12+1:02d}'
            rows.append(row)
    # Regular meetings are labeled as meetings rather than assuming every meeting decides a rate.
    for day in ['01-15','01-22','02-12','02-26','03-12','03-26','04-10','04-23','05-14','05-28','06-11','06-24','07-16','07-23','08-13','08-27','09-10','09-22','10-22','10-29','11-12','11-26','12-10','12-23']:
        rows.append(make('2026-'+day,'한국','한국은행 금융통화위원회 정기회의','한국은행'))
    for day in ['02-05','03-19','04-30','06-11','07-23','09-10','10-29','12-17']:
        rows.append(make('2026-'+day,'유로존','ECB 통화정책 결정','ECB','14:15','Europe/Berlin'))
    for day in ['01-23','03-19','04-28','06-16','07-31','09-18','10-30','12-18']:
        rows.append(make('2026-'+day,'일본','BOJ 금융정책결정회의 결과','BOJ'))
    for day in ['02-05','03-19','04-30','06-18','07-30','09-17','11-05','12-17']:
        rows.append(make('2026-'+day,'영국','BOE 통화정책 결정','BOE','12:00','Europe/London'))
    for day in ['01-28','03-18','04-29','06-17','07-29','09-16','10-28','12-09']:
        rows.append(make('2026-'+day,'미국','FOMC 통화정책 결정','Federal Reserve','14:00','America/New_York'))
    return rows
