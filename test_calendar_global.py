import unittest
from calendar_global import events,make
class CalendarGlobalTests(unittest.TestCase):
    def test_regions_and_korean_releases(self):
        rows=events()
        self.assertEqual({r['country'] for r in rows},{'한국','미국','일본','유로존','영국'})
        self.assertTrue(any(r['title']=='한국 소비자물가' and r['when'].strftime('%Y-%m-%d')=='2026-11-03' for r in rows))
    def test_unknown_time_is_explicit(self):
        row=make('2026-10-30','일본','회의','BOJ')
        self.assertFalse(row['time_known'])
    def test_dst_converts_us_decision_to_next_korean_day(self):
        row=make('2026-10-28','미국','FOMC','Federal Reserve','14:00','America/New_York')
        self.assertEqual(row['when'].strftime('%Y-%m-%d %H:%M'),'2026-10-29 03:00')
        row=make('2026-12-09','미국','FOMC','Federal Reserve','14:00','America/New_York')
        self.assertEqual(row['when'].strftime('%Y-%m-%d %H:%M'),'2026-12-10 04:00')
if __name__=='__main__':unittest.main()

class CalendarDescriptionsTests(unittest.TestCase):
    def test_importance_and_explanation(self):
        from calendar_explain import explain
        score,note=explain('한국 소비자물가')
        self.assertEqual(score,3);self.assertIn('물가',note)
    def test_korean_periods(self):
        rows=events()
        for title,day,period in [('한국 소비자물가','2026-12-31','2026-12'),('한국 산업활동동향','2026-03-04','2026-01'),('한국 고용동향','2026-01-14','2025-12')]:
            row=next(r for r in rows if r['title']==title and r['when'].strftime('%Y-%m-%d')==day)
            self.assertEqual(row['target_period'],period)
    def test_foreign_actual_requires_matching_month(self):
        import pandas as pd
        from calendar_international_values import values
        row={'country':'한국','title':'한국 소비자물가','target_period':'2026-09'}
        frame=pd.DataFrame({'country':['KOR','KOR'],'date':pd.to_datetime(['2026-08-01','2026-09-01']),'value':[2.1,2.3]})
        value=values(row,(frame,{}));self.assertAlmostEqual(value['change'],.2)
        self.assertIsNone(values({**row,'target_period':'2026-10'},(frame,{})))
