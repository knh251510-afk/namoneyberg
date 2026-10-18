import unittest
from economic_ontology import CONCEPTS, RELATIONS, annotate, context, validate_concepts

class OntologyTests(unittest.TestCase):
    def test_graph_integrity(self):
        for a,b,kind,caution in RELATIONS:
            self.assertIn(a,CONCEPTS);self.assertIn(b,CONCEPTS)
            self.assertTrue(kind);self.assertTrue(caution)

    def test_alias_boundaries(self):
        a=annotate({'title':'Business said demand improved'})
        self.assertNotIn('ai',a['concept_ids']);self.assertNotIn('USA',a['countries'])
        a=annotate({'title':'미국 CPI와 한국 기준금리, AI 반도체'})
        self.assertTrue({'cpi','policy_rate','ai','semiconductor'}<=set(a['concept_ids']))
        self.assertEqual(a['countries'],['USA','KOR'])

    def test_relations_require_both_concepts(self):
        self.assertEqual(context([{'title':'CPI'}])['relations'],[])
        c=context([{'title':'CPI'}, {'title':'정책금리'}])
        self.assertEqual([(r['source'],r['target']) for r in c['relations']],[('cpi','policy_rate')])

    def test_citation_scoped_validation(self):
        evidence=[{'id':'N1','title':'CPI'}, {'id':'N2','title':'유가'}]
        report={'themes':[{'news_ids':['N1'],'concept_ids':['cpi']}]}
        self.assertTrue(validate_concepts(report,evidence)['passed'])
        report['themes'][0]['concept_ids']=['oil']
        with self.assertRaises(ValueError):validate_concepts(report,evidence)
        report['themes'][0]['concept_ids']=['invented']
        with self.assertRaises(ValueError):validate_concepts(report,evidence)

if __name__=='__main__':unittest.main()
