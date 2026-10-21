import tempfile,unittest
from pathlib import Path
from unittest.mock import patch
import pandas as pd
import briefing_store as store
from briefing_context import observations

class PublicationTests(unittest.TestCase):
    def report(self,stamp):
        return {'report':{'headline':'물가와 금리','summary':'근거 종합','themes':[]},'generated_at':stamp,'period':{'start':'2026-10-05T00:00:00+09:00','end':'2026-10-09T00:00:00+09:00'}}
    def test_archive_survives_session_and_new_week(self):
        with tempfile.TemporaryDirectory() as folder:
            store.save(self.report('2026-10-09T12:00:00+09:00'),folder)
            store.save(self.report('2026-10-16T12:00:00+09:00'),folder)
            self.assertEqual(len(store.archive(folder)),2)
            self.assertEqual(store.latest(folder)['generated_at'],'2026-10-16T12:00:00+09:00')
    def test_invalid_files_do_not_break_archive(self):
        with tempfile.TemporaryDirectory() as folder:
            Path(folder,'overview_bad.json').write_text('{bad')
            self.assertIsNone(store.latest(folder))
    def test_publishing_requires_admin_before_network(self):
        with patch('admin_auth.is_admin',return_value=False),patch('briefing_store.requests.put') as put:
            with self.assertRaises(PermissionError):store.publish(self.report('2026-10-16T12:00:00+09:00'))
            put.assert_not_called()
    def test_public_report_excludes_editorial_history(self):
        value=self.report('2026-10-16T12:00:00+09:00')
        value['editorial_changes']={'before':{'summary':'draft'}}
        published=store.public_report(value)
        self.assertNotIn('editorial_changes',published)
        self.assertIn('editorial_changes',value)
        self.assertEqual(published['report'],value['report'])
    def test_observations_keep_each_country(self):
        f=pd.DataFrame({'country':['USA','USA','KOR','KOR'],'date':pd.to_datetime(['2026-08-01','2026-09-01']*2),'value':[3,3.2,2,2.1]})
        rows=observations(f,{'url':'https://example.org'},'cpi')
        self.assertEqual(len(rows),2)
        self.assertAlmostEqual(next(x for x in rows if x['country']=='USA')['change'],.2)
if __name__=='__main__':unittest.main()
