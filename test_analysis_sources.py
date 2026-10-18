import unittest
from unittest.mock import patch
import pandas as pd
from analysis_sources import parse_kosis,summary,extract_financials,financial_ratios,request_json,SourceError
import httpx

class SourceTests(unittest.TestCase):
    def test_kosis_dimension_and_missing_values(self):
        base={'ORG_ID':'101','TBL_ID':'T','ITM_ID':'I','ITM_NM':'지표','UNIT_NM':'명','PRD_SE':'M','C1':'00','C1_NM':'전국'}
        f=parse_kosis([{**base,'PRD_DE':'202401','DT':'1,000'},{**base,'PRD_DE':'202402','DT':'-'},{**base,'PRD_DE':'202403','DT':'1,100'},{**base,'C1':'01','PRD_DE':'202401','DT':'99'}])
        self.assertEqual(len(f),3);self.assertEqual(f.series.nunique(),2)
        s=summary(f[f.series==f.series.iloc[0]])
        self.assertEqual(s['delta'],100);self.assertAlmostEqual(s['pct'],10)
        self.assertEqual(s['high']['value'],1100)
    def test_kosis_annual_a_code_preserves_real_values(self):
        row={'ORG_ID':'101','TBL_ID':'DT_2IFS002','ITM_ID':'T001','ITM_NM':'총지수','UNIT_NM':'지수','PRD_SE':'A','PRD_DE':'2025','DT':'116.605','C1':'1005','C1_NM':'대한민국'}
        annual=parse_kosis([row])
        self.assertEqual(len(annual),1)
        self.assertEqual(annual.iloc[0]['value'],116.605)
        self.assertEqual(annual.iloc[0]['date'],pd.Timestamp('2025-01-01'))
        canonical=parse_kosis([{**row,'PRD_SE':'Y'}])
        self.assertEqual(annual.iloc[0]['series'],canonical.iloc[0]['series'])

    def test_negative_and_zero_baselines(self):
        for base in [0,-1]:
            f=pd.DataFrame({'date':pd.to_datetime(['2024-01-01','2024-02-01']),'value':[base,2]})
            self.assertIsNone(summary(f)['pct'])
    def test_dart_ambiguity_and_ratios(self):
        rows=[{'sj_div':'IS','account_id':'ifrs-full_Revenue','thstrm_amount':'1,000','currency':'KRW'}, {'sj_div':'IS','account_id':'dart_OperatingIncomeLoss','thstrm_amount':'(100)','currency':'KRW'}]
        cur=extract_financials(rows)
        self.assertEqual(cur['매출액'],1000);self.assertEqual(cur['영업이익'],-100)
        self.assertEqual(financial_ratios(cur)['영업이익률'],-10)
        cur=extract_financials(rows+[dict(rows[0],thstrm_amount='2000')])
        self.assertIsNone(cur['매출액'])
        self.assertIsNone(financial_ratios({'자본':-1,'순이익':10},{'자본':100})['ROE'])
    def test_bundled_company_resolution_has_no_network(self):
        from analysis_sources import resolve_dart_company
        resolve_dart_company.clear()
        with patch('analysis_sources.dart_companies') as directory, patch('analysis_sources.httpx.post') as html:
            company=resolve_dart_company('005930','test-key')
            self.assertEqual(company['corp_code'],'00126380')
            html.assert_not_called()
            directory.assert_not_called()

    def test_company_resolution_falls_back_for_new_listing(self):
        from analysis_sources import resolve_dart_company
        resolve_dart_company.clear()
        company={'name':'신규기업','stock_code':'999998','corp_code':'99999998'}
        with patch('analysis_sources.dart_companies',return_value=[company]), patch('analysis_sources.httpx.post',side_effect=httpx.ConnectError('unavailable')):
            self.assertEqual(resolve_dart_company('999998','key'),company)
            with self.assertRaises(SourceError):resolve_dart_company('999997','key')

    def test_secret_error_sanitized(self):
        with patch('analysis_sources.httpx.get',side_effect=httpx.ConnectError('https://example.com?apiKey=SECRET')):
            with self.assertRaises(SourceError) as caught:request_json('https://example.com',{})
            self.assertNotIn('SECRET',str(caught.exception))
if __name__=='__main__':unittest.main()
