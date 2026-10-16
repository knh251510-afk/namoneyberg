"""데이터·주간 경계·출처 검증 테스트 (실제 유료 API 호출 없음)."""
import json
import unittest
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import patch
import pandas as pd
import macro_data as d
import macro_ai as ai


class MacroTests(unittest.TestCase):
    def test_week_boundary(self):
        start,end=d.week_bounds(datetime(2026,10,15,10,tzinfo=d.KST))
        self.assertEqual(start.isoformat(),'2026-10-12T00:00:00+09:00')
        sunday,_=d.week_bounds(datetime(2026,10,18,23,tzinfo=d.KST))
        self.assertEqual(sunday,start)

    def test_missing_month_not_shifted(self):
        months=pd.date_range('2020-01-01',periods=15,freq='MS')
        rows=['observation_date,CPIAUCNS']+[f'{date:%Y-%m-%d},{100+i}' for i,date in enumerate(months) if i!=1]
        with patch.object(d,'fetch',return_value=('\n'.join(rows).encode(),{})):
            f,_=d.fred('미국 CPI')
        self.assertNotIn(pd.Timestamp('2021-02-01'),list(f.date))
        self.assertAlmostEqual(f[f.date==pd.Timestamp('2021-01-01')].value.iloc[0],12)

    def test_future_and_previous_week_news_excluded(self):
        rss=b'<rss><channel><item><title>Valid</title><link>https://example.com/a</link><pubDate>Tue, 13 Oct 2026 00:00:00 GMT</pubDate></item><item><title>Old</title><link>https://example.com/b</link><pubDate>Fri, 09 Oct 2026 00:00:00 GMT</pubDate></item><item><title>Future</title><link>https://example.com/c</link><pubDate>Fri, 16 Oct 2026 00:00:00 GMT</pubDate></item></channel></rss>'
        with patch.object(d,'now',return_value=datetime(2026,10,15,tzinfo=d.KST)),patch.object(d,'FEEDS',{'test':'https://example.com/rss'}),patch.object(d,'fetch',return_value=(rss,{})):
            rows,_=d.news()
        self.assertEqual([r['title'] for r in rows],['Valid'])

    def test_unknown_ai_citation_rejected(self):
        result={'headline':'h','summary':'s','themes':[{'category':'산업','title':'t','facts':'f','interpretation':'i','watch':'w','news_ids':['N999']}],'limitations':'l'}
        response=SimpleNamespace(status='completed',output_text=json.dumps(result),usage=None)
        with patch.object(ai,'OpenAI') as client:
            client.return_value.responses.create.return_value=response
            with self.assertRaises(ValueError):ai.overview('dummy','dummy',[{'title':'test','url':'https://example.com','published_at':'2026-10-13T00:00:00+09:00','source':'test'}],[])


if __name__=='__main__':unittest.main()
