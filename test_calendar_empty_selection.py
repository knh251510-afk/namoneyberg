import unittest
from streamlit.testing.v1 import AppTest

class CalendarEmptyTests(unittest.TestCase):
    def test_no_country_requests_selection(self):
        import quote_cache
        original_request=quote_cache.request
        app=AppTest.from_string('''
import pandas as pd
import economic_calendar as calendar
from unittest.mock import patch
fixture=(pd.DataFrame([calendar.event('2026-10-20','10:00','CPI','BLS',calendar.BLS)]),[])
with patch.object(calendar,'load',return_value=fixture), patch('quote_cache.request',side_effect=lambda key,fetch,fallback,**kwargs:fallback()):
    calendar.render()
''').run()
        app.multiselect[0].set_value([]).run()
        self.assertFalse(app.exception)
        self.assertIs(quote_cache.request,original_request)
        self.assertIn('발표 일정을 확인할 경제권을 선택해주세요.',[x.value for x in app.info])

    def test_calendar_number_format_retains_small_changes(self):
        from economic_calendar import format_value
        self.assertEqual(format_value(1000.0),'1,000')
        self.assertEqual(format_value(3.4),'3.4')
        self.assertEqual(format_value(0.005,signed=True),'+0.005')
        self.assertEqual(format_value(None),'—')

if __name__=='__main__':unittest.main()
