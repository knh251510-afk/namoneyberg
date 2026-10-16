"""같은 자료와 모델에 두 프롬프트를 적용하고 결과를 저장합니다."""

import json
import os
from datetime import datetime
from getpass import getpass
from pathlib import Path

from openai import OpenAI, APIConnectionError, APIStatusError


SOURCE = """[학습용 가상 자료 — 실제 경제 통계가 아님]
A사의 중국 매출은 전체 매출의 30%다.
중국 시장의 이번 분기 주문량은 전년 동기 대비 8% 감소했다.
A사의 원자재 수입 대금은 미국 달러로 결제한다.
환율 변동 폭과 환헤지 여부는 자료에 제시되지 않았다.
"""

# 두 버전 모두 같은 언어·분량·리스크 수 조건을 사용합니다.
COMMON = "한국어로 기업 리스크 2개를 분석하세요. 전체 답변은 400자 이내로 작성하세요. "
PROMPTS = {
    "v1_basic": COMMON,
    "v2_grounded": COMMON + (
        "제공된 자료만 사용하세요. 각 항목을 '리스크 / 원문 근거 / 추가 확인 사항'으로 정리하세요. "
        "확인된 사실과 추론을 구분하고, 없는 수치나 사실을 만들지 마세요. "
        "시장 전체의 주문 감소를 A사의 주문 감소로 단정하지 마세요. "
        "환율 방향이나 환헤지 여부가 없으면 확인이 필요하다고 명시하세요."
    ),
}


def main():
    print("프롬프트 비교: API를 총 2회 호출하며 사용 비용이 발생합니다.")
    key = os.environ.get("OPENAI_API_KEY") or getpass("API 키 입력 (화면에 표시되지 않음): ")
    if not key.strip():
        print("키가 입력되지 않았습니다.")
        return
    client = OpenAI(api_key=key.strip(), max_retries=0, timeout=60)
    model = os.environ.get("OPENAI_MODEL", "gpt-6-astra")
    results = []
    for version, prompt in PROMPTS.items():
        print(f"\n--- {version} 실행 중 ---")
        try:
            response = client.responses.create(
                model=model,
                instructions=prompt,
                input=SOURCE,
                max_output_tokens=1200,
                store=False,
            )
        except APIConnectionError:
            print("연결 실패. 완료된 결과가 있다면 저장합니다.")
            break
        except APIStatusError as error:
            print(f"HTTP {error.status_code} / 오류 코드: {error.code or '없음'}")
            break
        result = {
            "version": version,
            "prompt": prompt,
            "output": response.output_text,
            "status": response.status,
            "usage": response.usage.model_dump() if response.usage else None,
        }
        results.append(result)
        print(response.output_text or "텍스트 응답 없음. 완료 상태를 확인하세요.")
        print(f"완료 상태: {response.status}")

    if not results:
        return
    folder = Path(__file__).resolve().parent / "results"
    folder.mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    data = {"model": model, "source": SOURCE, "results": results}
    (folder / f"comparison_{stamp}.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    sections = ["# 프롬프트 비교 실습", f"모델: {model}", "## 가상 원문", SOURCE]
    for item in results:
        sections.extend([f"## {item['version']}", "### 지시문", item["prompt"],
                         "### 출력", item["output"] or "텍스트 없음", f"상태: {item['status']}"])
    sections.extend([
        "## 직접 평가할 기준",
        "- 시장 주문량 감소를 A사 주문량 감소로 단정했는가?",
        "- 환율 상승이나 비용 증가를 이미 일어난 사실로 단정했는가?",
        "- 원문에 없는 수치나 사실을 추가했는가?",
        "- 사실과 추론이 구분되는가?",
        "- 추가 확인 사항이 구체적인가?",
        "단일 자료·버전별 1회 실행의 탐색 결과입니다. 일반적인 성능 개선을 입증하지 않습니다.",
    ])
    report = folder / f"comparison_{stamp}.md"
    report.write_text("\n\n".join(sections), encoding="utf-8")
    print(f"\n결과 저장: {report}")
    print("키는 결과 파일에 저장하지 않았습니다.")


if __name__ == "__main__":
    main()
