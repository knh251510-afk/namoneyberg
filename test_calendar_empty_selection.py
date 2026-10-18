import unittest
from streamlit.testing.v1 import AppTest

class CalendarEmptyTests(unittest.TestCase):
    def test_no_country_requests_selection(self):
        app=AppTest.from_string('''
import pandas as pd
import economic_calendar as calendar
calendar.load=lambda:(pd.DataFrame([calendar.event('2026-10-20','10:00','CPI','BLS',calendar.BLS)]),[])
import quote_cache
quote_cache.request=lambda key,fetch,fallback,**kwargs:fallback()
calendar.render()
''').run()
        app.multiselect[0].set_value([]).run()
        self.assertFalse(app.exception)
        self.assertIn('발표 일정을 확인할 경제권을 선택해주세요.',[x.value for x in app.info])

if __name__=='__main__':unittest.main()
