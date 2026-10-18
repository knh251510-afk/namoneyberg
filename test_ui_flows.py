import unittest
from unittest.mock import patch
from streamlit.testing.v1 import AppTest
class UIFlows(unittest.TestCase):
 def test_home_includes_all_menu_groups(self):
  app=AppTest.from_string('''import streamlit as st
import landing_ui
paths=['home','overview','news','indicators','statistics','quotes','compare','corporate','calendar','glossary']
pages=[st.Page(lambda:None,title=p,url_path=p,default=p=='home') for p in paths]
st.navigation(pages,position='hidden')
landing_ui.render(pages)
''').run()
  self.assertFalse(app.exception)
  self.assertEqual(len(app.get('page_link')),10)
 def test_corporate_missing_key_is_upfront(self):
  with patch('api_settings.read_key',return_value=None):
   app=AppTest.from_string('import corporate_ui;corporate_ui.render()').run()
  self.assertFalse(app.exception);self.assertEqual(len(app.selectbox),0)
  self.assertIn('현재 이용할 수 없습니다',app.info[0].value)
 def test_corporate_changed_conditions_have_next_action(self):
  with patch('api_settings.read_key',return_value='test'),patch('analysis_sources.listed_companies',return_value=[{'name':'삼성전자','stock_code':'005930'}]):
   app=AppTest.from_string('import corporate_ui;corporate_ui.render()').run()
   app.selectbox[0].select_index(0).run()
   app.session_state['corporate_result']={'identity':('005930',2025,'CFS',3),'rows':[],'warnings':[]}
   app.selectbox[1].select(2024).run()
  self.assertFalse(app.exception)
  self.assertTrue(any('조회 조건이 바뀌었습니다' in item.value for item in app.info))
if __name__=='__main__':unittest.main()
