import unittest
from threading import Event
import time
import pandas as pd
from bis_frame import long_frame
import quote_cache

class LoadingTests(unittest.TestCase):
 def test_bis_preserves_values_and_missing(self):
  f=pd.DataFrame([{'REF_AREA':'US','COMPILATION':'A','1999-12-31':4,'2000-01-01':'1.25','2000-01-02':None},{'REF_AREA':'XX','COMPILATION':'B','2000-01-01':90}])
  result=long_frame(f,{'US':'USA'},definitions=True)
  self.assertEqual(len(result),1);self.assertEqual(result.value.iloc[0],1.25)
  self.assertEqual(result.country.iloc[0],'USA');self.assertEqual(result.definition.iloc[0],'A')
 def test_monthly(self):
  f=pd.DataFrame([{'REF_AREA':'JP','2000-01':'-1.5','2000-02':'0','2000-03':'..'}])
  r=long_frame(f,{'JP':'JPN'},monthly=True)
  self.assertEqual(r.value.tolist(),[-1.5,0]);self.assertEqual(str(r.date.iloc[-1].date()),'2000-02-01')
 def test_background_does_not_block_or_duplicate(self):
  started=Event();release=Event();calls=[]
  def loader():
   calls.append(1);started.set();release.wait(2);return ['new']
  name='test-nonblocking-'+str(time.monotonic())
  try:
   before=time.monotonic();r=quote_cache.request(name,loader,lambda:['saved'])
   self.assertLess(time.monotonic()-before,.2);self.assertEqual(r,['saved'])
   self.assertTrue(started.wait(1));quote_cache.request(name,loader,lambda:[])
   self.assertEqual(len(calls),1)
  finally:release.set()
  future=quote_cache._STATE[name]['future'];future.result(timeout=1)
  self.assertEqual(quote_cache.request(name,loader,lambda:[]),['new'])

if __name__=='__main__':unittest.main()
