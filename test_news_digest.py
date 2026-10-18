import unittest
from datetime import datetime,timedelta,timezone
from news_digest import relative_time,select_digest,summary_text,time_markup

class NewsDigestTests(unittest.TestCase):
    def setUp(self):self.now=datetime(2026,10,19,1,tzinfo=timezone(timedelta(hours=9)))
    def test_relative_times(self):
        for seconds,label in [(5,'방금'),(120,'2분 전'),(10800,'3시간 전'),(86400,'1일 전'),(691200,'8일 전')]:
            self.assertEqual(relative_time(self.now-timedelta(seconds=seconds),self.now),label)
    def test_digest_keeps_sources_and_existing_summary(self):
        rows=[{'title':'Inflation and interest rates','excerpt':'Prices increased. Officials are reviewing policy.','url':f'https://example.org/{i}','source':f'Source {i}','published_at':(self.now-timedelta(hours=i)).isoformat()} for i in range(1,6)]
        selected=select_digest(rows,self.now)
        self.assertEqual(len(selected),4)
        self.assertTrue(all(summary_text(r)==r['excerpt'] for r in selected))
        self.assertIn('title="2026.10.19 00:00 KST"',time_markup(rows[0],self.now))
        self.assertEqual(select_digest([{**rows[0],'url':'javascript:bad'}],self.now),[])

if __name__=='__main__':unittest.main()
