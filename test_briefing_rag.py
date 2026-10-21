import tempfile,unittest
from pathlib import Path
from macro_data import now
from news_retrieval import NewsIndex
from briefing_workflow import build_workflow

class RetrievalWorkflowTests(unittest.TestCase):
    def articles(self):
        a={'title':'US inflation CPI price pressure','excerpt':'Fed interest rates react to inflation','source':'A','url':'https://a.example/cpi','published_at':now().isoformat()}
        b={'title':'Treasury yields respond to Fed policy outlook','excerpt':'US consumer prices change interest rate expectations','source':'B','url':'https://b.example/fed','published_at':now().isoformat()}
        return [a,b,{**a,'source':'C','url':'https://c.example/duplicate'}]
    def generator(self,key,model,docs,snapshot,validate_output):
        assert snapshot['economic_ontology']['version']=='economic-context-v1'
        return {'report':{'headline':'物価','summary':'종합','themes':[{'title':'정책','facts':'물가와 정책을 종합','news_ids':['N1','N2'],'comparison':'물가와 정책 관점 비교','comparison_ids':['N1','N2']}]},'evidence':[{'id':f'N{i+1}',**d} for i,d in enumerate(docs)]}
    def test_real_retriever_and_graph(self):
        with tempfile.TemporaryDirectory() as folder:
            graph=build_workflow(self.generator,NewsIndex(Path(folder)/'index.sqlite'))
            state=graph.invoke({'key':'no-real-key','model':'test','articles':self.articles(),'snapshot':{}})
            self.assertEqual(state['result']['retrieval']['documents'],2)
            self.assertEqual(state['stages'],['index','retrieve','ontology','generate','validate'])
            self.assertTrue(state['result']['validation']['passed'])
    def test_unsupported_ontology_blocks_workflow(self):
        def invalid(*args,**kwargs):
            r=self.generator(*args,**kwargs)
            r['report']['themes'][0]['concept_ids']=['semiconductor']
            return r
        with tempfile.TemporaryDirectory() as folder:
            graph=build_workflow(invalid,NewsIndex(Path(folder)/'index.sqlite'))
            with self.assertRaisesRegex(ValueError,'온톨로지'):
                graph.invoke({'key':'no-real-key','model':'test','articles':self.articles(),'snapshot':{}})

    def test_bad_comparison_rejected(self):
        def invalid(*args,**kwargs):
            r=self.generator(*args,**kwargs);r['report']['themes'][0]['comparison_ids']=['N999'];return r
        with tempfile.TemporaryDirectory() as folder:
            graph=build_workflow(invalid,NewsIndex(Path(folder)/'index.sqlite'))
            with self.assertRaises(ValueError):graph.invoke({'key':'no-real-key','model':'test','articles':self.articles(),'snapshot':{}})
    def test_numeric_warning_keeps_draft_and_reports_progress(self):
        def with_number(*args,**kwargs):
            result=self.generator(*args,**kwargs)
            result['report']['summary']='확인 필요 987654321%'
            return result
        messages=[]
        with tempfile.TemporaryDirectory() as folder:
            graph=build_workflow(with_number,NewsIndex(Path(folder)/'index.sqlite'),progress=messages.append)
            result=graph.invoke({'key':'no-real-key','model':'test','articles':self.articles(),'snapshot':{}})['result']
        self.assertFalse(result['validation']['passed'])
        self.assertTrue(result['validation']['warnings'])
        self.assertEqual(result['workflow']['status'],'needs_review')
        self.assertEqual(len(messages),5)
if __name__=='__main__':unittest.main()
