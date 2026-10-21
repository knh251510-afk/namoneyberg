"""LangGraph: 수집 자료 색인 → LangChain 검색 → 종합 → 초안 정리."""
from typing import TypedDict,Any
from langgraph.graph import StateGraph,START,END
from macro_data import week_bounds
from news_retrieval import NewsIndex
import economic_ontology as ontology

class BriefingState(TypedDict,total=False):
    key:str
    model:str
    articles:list
    snapshot:dict
    retrieved:list
    groups:list
    ontology_context:dict
    result:dict
    stages:list

def build_workflow(generator=None,index=None,progress=None):
    index=index or NewsIndex()
    def ingest(s):
        index.ingest(s['articles']);return {'stages':['index']}
    def retrieve(s):
        start,end=week_bounds()
        selected,groups=index.retrieve(start,end)
        return {'retrieved':selected,'groups':groups,'stages':s['stages']+['retrieve']}
    def connect(s):
        return {'ontology_context':ontology.context(s['retrieved']),'stages':s['stages']+['ontology']}
    def generate(s):
        if generator is None:
            from macro_ai import _generate_overview
            fn=_generate_overview
        else:fn=generator
        result=fn(s['key'],s['model'],s['retrieved'],{**s['snapshot'],'retrieval_groups':s['groups'],'economic_ontology':s['ontology_context']})
        return {'result':result,'stages':s['stages']+['generate']}
    def prepare(s):
        r=s['result']
        r['ontology']=s['ontology_context']
        r['retrieval']={'method':'TF-IDF character n-gram / LangChain retriever tool','groups':s['groups'],'documents':len(s['retrieved'])}
        r['workflow']={'engine':'LangGraph','stages':s['stages']+['prepare'],'status':'draft'}
        return {'result':r,'stages':s['stages']+['prepare']}
    graph=StateGraph(BriefingState)
    labels={'index':'뉴스 색인','retrieve':'뉴스 검색','ontology':'개념 연결','generate':'초안 작성','prepare':'초안 정리'}
    def guarded(name,node):
        def run_stage(state):
            if progress:progress(labels[name]+' 중…')
            try:return node(state)
            except ValueError as exc:
                raise ValueError(labels[name]+' 단계: '+str(exc)) from exc
        return run_stage
    for name,node in [('index',ingest),('retrieve',retrieve),('ontology',connect),('generate',generate),('prepare',prepare)]:
        graph.add_node(name,guarded(name,node))
    graph.add_edge(START,'index');graph.add_edge('index','retrieve');graph.add_edge('retrieve','ontology');graph.add_edge('ontology','generate');graph.add_edge('generate','prepare');graph.add_edge('prepare',END)
    return graph.compile()

def run(key,model,articles,snapshot,progress=None):
    # No checkpoint/tracing of the API credential. Only the final non-secret result is returned.
    from langsmith import tracing_context
    with tracing_context(enabled=False):
        graph=build_workflow()
        initial={'key':key,'model':model,'articles':articles,'snapshot':snapshot}
        if progress is None:return graph.invoke(initial)['result']
        # Streamlit updates must run on the caller's UI thread, not a graph worker.
        next_labels={'index':'뉴스 검색 중…','retrieve':'개념 연결 중…',
                     'ontology':'초안 작성 중…','generate':'초안 정리 중…','prepare':'초안 준비 완료'}
        progress('뉴스 색인 중…')
        result=None
        for update in graph.stream(initial,stream_mode='updates'):
            for stage,values in update.items():
                if 'result' in values:result=values['result']
                progress(next_labels.get(stage,'브리핑 처리 중…'))
        return result
