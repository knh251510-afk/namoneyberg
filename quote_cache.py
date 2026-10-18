"""Process-wide non-blocking snapshots. Background workers never render UI."""
from concurrent.futures import ThreadPoolExecutor
from threading import Lock
import time
_POOLS={
    'market':ThreadPoolExecutor(max_workers=2,thread_name_prefix='market-snapshot'),
    'calendar':ThreadPoolExecutor(max_workers=4,thread_name_prefix='calendar-snapshot'),
    'general':ThreadPoolExecutor(max_workers=2,thread_name_prefix='data-snapshot'),
}

def pool_for(name):
    kind='market' if name.startswith('market-') else ('calendar' if name.startswith('calendar-') else 'general')
    return _POOLS[kind]
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
            state['future']=pool_for(name).submit(loader)
        return state['value']

def invalidate(name):
    with _LOCK:
        if name in _STATE:_STATE[name]['at']=float('-inf')
