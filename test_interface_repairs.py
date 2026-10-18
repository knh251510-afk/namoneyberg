import io,zipfile,unittest
from pathlib import Path
from analysis_sources import parse_dart_companies,parse_dart_search,dart_search,SourceError
class RepairTests(unittest.TestCase):
    def test_dart_reports_invalid_key_without_echoing_credentials(self):
        with self.assertRaisesRegex(SourceError,'인증키가 유효하지'):
            parse_dart_companies(b'<result><status>010</status></result>')
    def test_dart_reports_ip_restriction(self):
        with self.assertRaisesRegex(SourceError,'IP'):
            parse_dart_companies(b'<result><status>012</status></result>')
    def test_dart_company_archive(self):
        out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as z:z.writestr('CORPCODE.xml','<result><list><corp_name>상장기업</corp_name><corp_code>00126380</corp_code><stock_code>005930</stock_code></list><list><stock_code> </stock_code></list></result>')
        self.assertEqual(parse_dart_companies(out.getvalue())[0]['stock_code'],'005930')
    def test_public_company_search_parser(self):
        html='<table id="corpTable"><tr><td><a href="javascript:select(\'00126380\');">삼성전자</a></td><td>005930</td></tr></table>'
        self.assertEqual(parse_dart_search(html),[{'name':'삼성전자','corp_code':'00126380','stock_code':'005930'}])
        self.assertEqual(parse_dart_search('<table id="corpTable"></table>'),[])
        with self.assertRaises(SourceError):parse_dart_search('<html>maintenance</html>')
    def test_search_uses_small_public_endpoint(self):
        from unittest.mock import patch,Mock
        response=Mock(text='<table id="corpTable"></table>')
        with patch('analysis_sources.httpx.post',return_value=response) as post,patch('analysis_sources.dart_companies') as directory:
            dart_search.clear()
            self.assertEqual(dart_search('없는기업','test-key'),[])
            directory.assert_not_called()
            self.assertNotIn('test-key',str(post.call_args))
    def test_category_images_are_embedded_jpegs(self):
        from briefing_ui import category_image,CATEGORIES
        for asset in CATEGORIES.values():
            uri=category_image(asset)
            self.assertTrue(uri.startswith('data:image/jpeg;base64,'));self.assertLess(len(uri),150000)
if __name__=='__main__':unittest.main()
