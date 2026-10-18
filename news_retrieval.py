"""저장된 RSS 뉴스의 TF-IDF 검색. 임베딩 모델을 사용하지 않는 lexical RAG."""
import hashlib,json,re,sqlite3
from pathlib import Path
from typing import Any,List
from datetime import datetime,timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.tools import tool
from pydantic import ConfigDict
from macro_data import CACHE,now

QUERIES={
 '미국 물가·정책':'US inflation CPI PPI PCE Fed interest rates 미국 물가 금리 연준',
 '고용·경기':'employment jobs GDP growth recession unemployment 고용 실업 성장 경기',
 '주식·채권':'stocks equities bonds Treasury yields market rally selloff 증시 주가 국채 금리',
 '환율·무역':'dollar currency exchange exports imports tariffs trade 달러 환율 수출 무역 관세',
 '중국·아시아':'China Japan Korea economy stimulus growth 중국 일본 한국 경기 부양',
 'AI·반도체':'AI artificial intelligence semiconductor chips Nvidia TSMC memory 반도체 인공지능 메모리',
 '에너지':'oil energy OPEC crude war supply inflation 원유 유가 에너지 중동',
}

def fingerprint(article):
    text=re.sub(r'\W+',' ',(article.get('title','')+' '+article.get('excerpt','')).lower()).strip()
    return hashlib.sha256(text.encode()).hexdigest()

class NewsRetriever(BaseRetriever):
    model_config=ConfigDict(arbitrary_types_allowed=True)
    docs:List[Document]
    vectorizer:Any
    matrix:Any
    k:int=5
    def _get_relevant_documents(self,query,*,run_manager=None):
        scores=cosine_similarity(self.vectorizer.transform([query]),self.matrix).ravel()
        picked=[];used=set()
        for i in scores.argsort()[::-1]:
            if scores[i]<0.04:continue
            doc=self.docs[int(i)];fp=doc.metadata['fingerprint']
            if fp in used:continue
            used.add(fp)
            # Text near-duplicates are not treated as independent corroboration.
            if any(float(cosine_similarity(self.matrix[int(i)],self.matrix[j])[0,0])>.92 for j in picked):continue
            picked.append(int(i))
            if len(picked)>=self.k:break
        return [Document(page_content=self.docs[i].page_content,metadata={**self.docs[i].metadata,'retrieval_score':float(scores[i])}) for i in picked]

class NewsIndex:
    def __init__(self,path=None):
        self.path=Path(path) if path else CACHE/'news_rag.sqlite3'
        self.path.parent.mkdir(exist_ok=True,parents=True)
        with sqlite3.connect(self.path) as db:
            db.execute('CREATE TABLE IF NOT EXISTS news(url TEXT PRIMARY KEY, fingerprint TEXT, published TEXT, body TEXT)')
    def ingest(self,articles):
        rows=[]
        for a in articles:
            if not a.get('url','').startswith(('https://','http://')):continue
            clean={k:a.get(k,'') for k in ('url','title','excerpt','source','published_at')}
            clean['excerpt']=str(clean['excerpt'])[:2000]
            rows.append((clean['url'],fingerprint(clean),clean['published_at'],json.dumps(clean,ensure_ascii=False)))
        with sqlite3.connect(self.path) as db:
            db.executemany('INSERT OR REPLACE INTO news VALUES(?,?,?,?)',rows)
    def retrieve(self,start,end):
        docs=[]
        with sqlite3.connect(self.path) as db:
            rows=db.execute('SELECT fingerprint,body FROM news').fetchall()
        for fp,body in rows:
            a=json.loads(body)
            try:date=datetime.fromisoformat(a['published_at'])
            except (ValueError,TypeError):continue
            if date.tzinfo is None:continue
            if not start<=date<=end:continue
            docs.append(Document(page_content=a['title']+'\n'+a['excerpt'],metadata={**a,'fingerprint':fp}))
        if len(docs)<2:raise ValueError('비교 가능한 기간 내 뉴스 근거가 2건 미만입니다.')
        vectorizer=TfidfVectorizer(analyzer='char_wb',ngram_range=(3,5),max_features=40000,sublinear_tf=True)
        matrix=vectorizer.fit_transform([d.page_content for d in docs])
        retriever=NewsRetriever(docs=docs,vectorizer=vectorizer,matrix=matrix)
        @tool
        def search_news(query:str)->list:
            """주제와 관련된 기간 내 뉴스 근거를 검색합니다. 제목·RSS 요약만 반환합니다."""
            return [d.metadata for d in retriever.invoke(query)]
        groups=[];selected={}
        for topic,query in QUERIES.items():
            hits=search_news.invoke({'query':query})
            if len(hits)<2:continue
            # Group relevance is a candidate relation, not proof of same event or contradiction.
            groups.append({'topic':topic,'articles':[h['url'] for h in hits]})
            for h in hits:selected[h['url']]=h
        if len(selected)<2:raise ValueError('서로 비교할 뉴스 검색 근거가 부족합니다.')
        return list(selected.values()),groups
