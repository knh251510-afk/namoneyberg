import unittest
from pathlib import Path
from theme_tokens import colors,css
from theme_assets import image_path
from streamlit.testing.v1 import AppTest
class ThemeModes(unittest.TestCase):
 def test_shared_tokens_have_readable_text(self):
  def luminance(h):
   c=[int(h[i:i+2],16)/255 for i in (1,3,5)]
   return sum(w*(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4) for w,v in zip([.2126,.7152,.0722],c))
  for mode in ['light','dark']:
   t=colors(mode)
   for key in ['text','muted','accent']:
    a,b=sorted([luminance(t[key]),luminance(t['bg'])]);self.assertGreaterEqual((b+.05)/(a+.05),4.5)
   self.assertIn('color-scheme:'+mode,css(mode))
 def test_toggle_updates_theme_without_api(self):
  app=AppTest.from_string('''import ui_theme
ui_theme.apply()
ui_theme.control()
import streamlit as st
st.write(ui_theme.mode())
''').run()
  self.assertFalse(app.exception)
  app.button[0].click().run()
  self.assertFalse(app.exception);self.assertEqual(app.session_state['color_mode'],'dark')
  app.button[0].click().run();self.assertEqual(app.session_state['color_mode'],'light')
 def test_images_stay_local(self):
  for name in ['home-reading','home-data','home-connections','brief-macro','brief-global','brief-industry']:
   for mode in ['light','dark']:
    path=image_path(name,mode)
    self.assertTrue(path.exists());self.assertTrue(path.name.endswith('-'+mode+'.jpg'))
   self.assertNotEqual(image_path(name,'light').read_bytes(),image_path(name,'dark').read_bytes())
if __name__=='__main__':unittest.main()
