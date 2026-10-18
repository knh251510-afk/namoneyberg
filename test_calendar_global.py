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
