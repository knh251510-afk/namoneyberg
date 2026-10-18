import unittest
from unittest.mock import patch
import pandas as pd
from calendar_values import values
from calendar_decisions import parse_feed,result,is_policy
from analysis_sources import listed_companies
class FollowupTests(unittest.TestCase):
 def test_one_character_company_candidates(self):
  found={c['name'] for c in listed_companies() if '삼' in c['name']}
  self.assertTrue({'삼성전자','삼성SDI'}.issubset(found))
 def test_cpi_fallback_requires_target_month(self):
  row={'title':'CPI 소비자물가','when':pd.Timestamp('2026-10-14',tz='Asia/Seoul')}
  frame=pd.DataFrame({'country':['USA','USA'],'date':pd.to_datetime(['2026-08-01','2026-09-01']),'value':[2.8,3.0]})
  found=values(row,{'CPIAUCNS':None,'_cpi_yoy':(frame,{})})
  self.assertAlmostEqual(found['value'],3.0);self.assertAlmostEqual(found['change'],.2)
  self.assertIsNone(values({**row,'when':pd.Timestamp('2026-11-10',tz='Asia/Seoul')},{'_cpi_yoy':(frame,{})}))
 def test_policy_result_matches_country_and_day(self):
  raw=b'<rss><channel><item><title>Federal Reserve issues FOMC statement</title><link>https://www.federalreserve.gov/newsevents/pressreleases/monetary20260916a.htm</link><pubDate>Wed, 16 Sep 2026 14:00:00 -0400</pubDate><description>Policy decision excerpt</description></item></channel></rss>'
  rows=parse_feed(raw,'미국')
  row={'country':'미국','when':pd.Timestamp('2026-09-17',tz='Asia/Seoul')}
  self.assertEqual(result(row,rows)['summary'],'Policy decision excerpt')
  self.assertIsNone(result({**row,'country':'한국'},rows))
  self.assertTrue(is_policy('ECB 통화정책 결정'));self.assertFalse(is_policy('CPI 소비자물가'))
if __name__=='__main__':unittest.main()
