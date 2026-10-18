"""Safe DART HTTPS diagnostics: never retain keys, URLs, headers or exception text."""
import time
import httpx

DART_API='https://opendart.fss.or.kr/api/list.json'


def probe(key,ipv4=False,wait=4):
    phase='요청 준비'
    started=time.monotonic()
    def trace(event,info):
        nonlocal phase
        if event.endswith('connect_tcp.started'):phase='DNS·TCP 연결'
        elif event.endswith('start_tls.started'):phase='TLS 보안 연결'
        elif event.endswith('receive_response_headers.started'):phase='서버 응답 대기'
    try:
        transport=httpx.HTTPTransport(local_address='0.0.0.0',retries=0) if ipv4 else None
        with httpx.Client(transport=transport,timeout=httpx.Timeout(max(8,wait),connect=wait),trust_env=not ipv4) as client:
            response=client.get(DART_API,params={'crtfc_key':key.strip(),'corp_code':'00126380','page_count':'1','page_no':'1'},extensions={'trace':trace})
            response.raise_for_status()
            payload=response.json()
        status=payload.get('status') if isinstance(payload,dict) else None
        return {'경로':'IPv4 직접 연결' if ipv4 else '기본 연결','단계':'API 응답 수신','결과':'정상' if status in ('000','013') else 'DART 코드 '+str(status),'초':round(time.monotonic()-started,2)}
    except (httpx.HTTPError,ValueError) as exc:
        return {'경로':'IPv4 직접 연결' if ipv4 else '기본 연결','단계':phase,'결과':type(exc).__name__,'초':round(time.monotonic()-started,2)}


def diagnostics(key):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=2) as pool:
        return list(pool.map(lambda ipv4:probe(key,ipv4),[False,True]))
