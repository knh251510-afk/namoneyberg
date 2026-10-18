"""Published reports: atomic local cache + optional GitHub Contents persistence."""
import base64,json,os,tempfile,re
from datetime import datetime
from pathlib import Path
import requests
import streamlit as st
ROOT=Path(__file__).resolve().parent/'macro_reports'
BUNDLED=Path(__file__).resolve().parent/'published_briefings'

def valid(value):
    try:
        r=value['report']
        return isinstance(r['headline'],str) and isinstance(r['summary'],str) and isinstance(r['themes'],list) and bool(value['generated_at'])
    except (KeyError,TypeError):return False

def setting(name,default=''):
    value=os.environ.get(name)
    if value:return value
    try:
        import streamlit as st
        return st.secrets.get(name,default)
    except Exception:return default

def remote_config():
    repo=setting('BRIEFING_GITHUB_REPO','knh251510-afk/namoneyberg')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+',repo):raise ValueError('브리핑 저장소 이름을 확인해주세요.')
    return repo,setting('BRIEFING_GITHUB_TOKEN')

def remote_ready():return bool(remote_config()[1])

def _remote_reports():
    # No token in a URL, logs or report payload. Public repository reads need no token.
    repo,token=remote_config();headers={'Accept':'application/vnd.github+json'}
    if token:headers['Authorization']='Bearer '+token
    r=requests.get(f'https://api.github.com/repos/{repo}/contents/published_briefings',headers=headers,timeout=12)
    if r.status_code==404:return []
    r.raise_for_status();rows=[]
    for item in r.json():
        if item.get('name','').startswith('overview_') and item['name'].endswith('.json'):
            rows.append(item)
    return rows

def _remote_read(item):
    repo,token=remote_config();headers={'Accept':'application/vnd.github+json'}
    if token:headers['Authorization']='Bearer '+token
    r=requests.get(f'https://api.github.com/repos/{repo}/contents/published_briefings/{item["name"]}',headers=headers,timeout=12);r.raise_for_status()
    value=json.loads(base64.b64decode(r.json()['content']))
    return value if valid(value) else None

def archive(folder=None):
    roots=[Path(folder)] if folder else [ROOT,BUNDLED]
    candidates=[]
    for root in roots:
        for path in root.glob('overview_*.json'):
            try:
                value=json.loads(path.read_text())
                if valid(value):candidates.append(value)
            except (OSError,ValueError):continue
    def stamp(r):
        try:return datetime.fromisoformat(r['generated_at']).timestamp()
        except (ValueError,TypeError):return 0
    unique={r['generated_at']:r for r in candidates}
    return sorted(unique.values(),key=stamp,reverse=True)

def latest(folder=None):
    reports=archive(folder)
    return reports[0] if reports else None

@st.cache_data(ttl=300,show_spinner=False)
def sync_remote():
    for item in _remote_reports():
        if (ROOT/item['name']).exists():continue
        value=_remote_read(item)
        if value:_save_local(value)

def _save_local(value,folder=None):
    if not valid(value):raise ValueError('브리핑 저장 형식을 확인해주세요.')
    root=Path(folder) if folder else ROOT;root.mkdir(exist_ok=True,parents=True)
    name='overview_'+datetime.fromisoformat(value['generated_at']).strftime('%Y%m%d_%H%M%S_%f')+'.json'
    fd,tmp=tempfile.mkstemp(prefix='.brief-',suffix='.tmp',dir=root)
    try:
        with os.fdopen(fd,'w') as out:
            json.dump(value,out,ensure_ascii=False,indent=2);out.flush();os.fsync(out.fileno())
        os.replace(tmp,root/name)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    return root/name

def save(value,folder=None):return _save_local(value,folder)

def publish(value):
    import admin_auth
    if not admin_auth.is_admin():raise PermissionError('관리자만 게시할 수 있습니다.')
    if not valid(value):raise ValueError('브리핑 저장 형식을 확인해주세요.')
    repo,token=remote_config()
    if not token:raise ValueError('영구 게시를 위해 Streamlit Secrets의 BRIEFING_GITHUB_TOKEN을 등록해주세요.')
    name='overview_'+datetime.fromisoformat(value['generated_at']).strftime('%Y%m%d_%H%M%S_%f')+'.json'
    r=requests.put(f'https://api.github.com/repos/{repo}/contents/published_briefings/{name}',headers={'Authorization':'Bearer '+token,'Accept':'application/vnd.github+json'},json={'message':'Publish reviewed market briefing','content':base64.b64encode(json.dumps(value,ensure_ascii=False,indent=2).encode()).decode(),'branch':'main'},timeout=25)
    if r.status_code not in (200,201):raise ValueError(f'GitHub 게시 저장 실패 (HTTP {r.status_code}). 저장소 Contents 쓰기 권한을 확인해주세요.')
    return _save_local(value)
