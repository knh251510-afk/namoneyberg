import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import dart_storage
import analysis_sources


class DartStorageTests(unittest.TestCase):
    def rows(self):
        return [{'corp_code':'00126380','bsns_year':'2025','sj_div':'IS','account_id':'ifrs-full_Revenue','thstrm_amount':'100','crtfc_key':'DO_NOT_SAVE'}]

    def test_snapshot_identity_and_secrets(self):
        with tempfile.TemporaryDirectory() as folder:
            p=dart_storage.write_snapshot(folder,'00126380',2025,'CFS',self.rows(),'2026-10-19T00:00:00+09:00')
            text=next(Path(folder).glob('*.json')).read_text()
            self.assertNotIn('DO_NOT_SAVE',text)
            self.assertNotIn('crtfc_key',text)
            self.assertIsNotNone(dart_storage.validate(p,'00126380',2025,'CFS'))
            self.assertIsNone(dart_storage.validate(p,'00126380',2024,'CFS'))
            self.assertIsNone(dart_storage.validate(p,'00126380',2025,'OFS'))
            p['rows'][0]['corp_code']='99999999'
            self.assertIsNone(dart_storage.validate(p,'00126380',2025,'CFS'))

    def test_saved_data_avoid_dart_request(self):
        analysis_sources.dart_statement_with_meta.clear()
        payload={'rows':self.rows(),'retrieved_at':'2026-10-15T00:00:00+09:00'}
        with patch('dart_storage.read_snapshot',return_value=payload),patch('analysis_sources.request_json') as network:
            rows,meta=analysis_sources.dart_statement_with_meta('00126380',2025,'CFS','test-key')
            self.assertEqual(rows,payload['rows'])
            self.assertTrue(meta['saved'])
            network.assert_not_called()

    def test_bad_response_does_not_overwrite_saved_data(self):
        with tempfile.TemporaryDirectory() as folder:
            dart_storage.write_snapshot(folder,'00126380',2025,'CFS',self.rows(),'2026-10-19T00:00:00+09:00')
            with self.assertRaises(ValueError):
                dart_storage.write_snapshot(folder,'00126380',2025,'CFS',[],'2026-10-19T01:00:00+09:00')
            self.assertEqual(len(json.loads(next(Path(folder).glob('*.json')).read_text())['rows']),1)

if __name__=='__main__':unittest.main()
