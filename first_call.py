"""첫 실습: 가상 자료를 OpenAI API로 분석하기."""

import os
from getpass import getpass

from openai import OpenAI, APIConnectionError, APIStatusError


def main():
    # 환경변수가 없으면 화면에 표시되지 않는 입력창으로 키를 받습니다.
    # 입력한 키는 파일에 저장하지 않습니다.
    api_key = os.environ.get("OPENAI_API_KEY") or getpass("API 키 입력 (화면에 표시되지 않음): ")
    if not api_key.strip():
        print("키가 입력되지 않았습니다. 다시 실행해주세요.")
        return

    client = OpenAI(api_key=api_key.strip(), max_retries=0, timeout=60)
    source = """
    [학습용 가상 자료 — 실제 경제 통계가 아님]
    A사의 중국 매출은 전체 매출의 30%다.
    중국 시장의 이번 분기 주문량은 전년 동기 대비 8% 감소했다.
    A사의 원자재 수입 대금은 미국 달러로 결제한다.
    환율 변동 폭과 환헤지 여부는 자료에 제시되지 않았다.
    """

    try:
        response = client.responses.create(
            model=os.environ.get("OPENAI_MODEL", "gpt-6-astra"),
            instructions=(
                "한국어로 답하세요. 제공된 자료만 사용하세요. "
                "리스크 2개를 각각 '리스크 / 원문 근거 / 추가 확인 사항'으로 정리하세요. "
                "확인된 사실과 추론을 구분하고, 없는 수치나 사실을 만들지 마세요. "
                "전체 답변은 400자 이내로 작성하세요."
            ),
            input=source,
            max_output_tokens=1200,
            store=False,
        )
    except APIConnectionError:
        print("연결 실패: 인터넷 연결을 확인해주세요.")
        return
    except APIStatusError as error:
        # 오류 본문이나 키는 출력하지 않습니다.
        print(f"API 오류: HTTP {error.status_code}")
        print(f"오류 코드: {error.code or '없음'}")
        print(f"오류 유형: {error.type or '없음'}")
        print("401: 키 확인 / 429: 크레딧·요청 한도 확인 / 403·404: 모델 접근 권한 확인")
        return

    print("\n--- 분석 결과 ---")
    print(response.output_text or "텍스트 응답이 없습니다. 출력 한도 등을 확인해주세요.")
    if response.usage:
        print(f"\n입력 토큰: {response.usage.input_tokens}, 출력 토큰: {response.usage.output_tokens}")


if __name__ == "__main__":
    main()
