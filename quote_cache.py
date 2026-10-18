"""Process-wide non-blocking snapshots. Background workers never render UI."""
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import time
_POOL=ThreadPoolExecutor(max_workers=2,thread_name_prefix='market-snapshot')
_LOCK=Lock()
_STATE={}

def request(name, loader, fallback, ttl=300):
    with _LOCK:
        state=_STATE.setdefault(name,{'value':None,'at':float('-inf'),'future':None})
        future=state['future']
        if future is not None and future.done():
            try:state['value']=future.result()
            except Exception:pass
            state['at']=time.monotonic();state['future']=None
        if state['value'] is None:state['value']=fallback()
        if state['future'] is None and time.monotonic()-state['at']>=ttl:
            state['future']=_POOL.submit(loader)
        return state['value']

def invalidate(name):
    with _LOCK:
        if name in _STATE:_STATE[name]['at']=float('-inf')
