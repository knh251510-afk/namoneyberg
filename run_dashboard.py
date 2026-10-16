"""VS Code에서 ▶ 버튼으로 대시보드 실행."""
import subprocess
import sys
import webbrowser
from pathlib import Path
from urllib.request import urlopen

URL='http://127.0.0.1:8501'
if __name__=='__main__':
    try:
        with urlopen(URL+'/_stcore/health',timeout=2) as response:
            running=response.status==200
    except Exception:running=False
    if running:
        webbrowser.open(URL)
        print('이미 실행 중인 대시보드를 열었습니다.')
    else:
        subprocess.run([sys.executable,'-m','streamlit','run',str(Path(__file__).with_name('dashboard.py')),
                        '--server.address','127.0.0.1','--server.port','8501',
                        '--browser.gatherUsageStats','false'],check=False)
