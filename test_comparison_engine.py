import unittest
import pandas as pd
from comparison_engine import prepare,transform
import chart_ui

class ComparisonTests(unittest.TestCase):
    def frame(self):
        return pd.DataFrame({'series':['A','A','A','B','B'], 'date':['2020-01-01','2020-01-20','2020-03-01','2020-01-10','2020-03-01'],'value':[10,20,40,2,4]})
    def test_monthly_no_fill(self):
        f=prepare(self.frame(),'2020-01-01','2020-12-31','월간','평균',False)
        self.assertNotIn(2,f.date.dt.month.to_list())
        self.assertEqual(f[(f.series=='A') & (f.date.dt.month==1)].value.iloc[0],15)
    def test_overlap_and_transform(self):
        f=prepare(self.frame(),'2020-01-01','2020-12-31',overlap=True)
        self.assertEqual(f.date.min(),pd.Timestamp('2020-01-10'))
        z=transform(f,'표준화 · Z-score')
        self.assertTrue(all(abs(v)<1e-9 for v in z.groupby('series').value.mean()))
        indexed=transform(f,'시작값 = 100')
        self.assertEqual(indexed.groupby('series').first().value.to_list(),[100,100])
    def test_negative_baseline(self):
        f=self.frame();f.loc[0,'value']=-1
        with self.assertRaises(ValueError):transform(f,'시작 대비 변화율 (%)')
        self.assertEqual(transform(f,'시작 대비 차이').value.iloc[0],0)
    def test_invalid_and_duplicates(self):
        f=pd.concat([self.frame(),self.frame().iloc[:1]])
        f=prepare(f,'2020-01-01','2020-12-31',overlap=False)
        self.assertEqual(len(f),5)
    def test_chart_domain(self):
        f=self.frame();f.date=pd.to_datetime(f.date)
        spec=chart_ui.timeseries(f,'date','value','test',group='series',domain=('2020-01-01','2020-12-31')).to_dict()
        self.assertEqual(spec['layer'][0]['encoding']['x']['scale']['domain'][0]['year'],2020)
if __name__=='__main__':unittest.main()
