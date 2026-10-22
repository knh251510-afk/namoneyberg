# 테마 이미지

홈은 5개 그룹의 고유한 이미지 카드를 사용합니다. 파일은 `static/home-{reading,data,corporate,calendar,connections}-{light,dark}.jpg`이며, 마켓 오버뷰는 `static/brief-{macro,global,industry}-{light,dark}.jpg`를 사용합니다.

원본 구도·사물·카메라와 크롭을 유지하고 조명·시간대만 바꾸는 방식으로 생성·편집한 이미지입니다. 최적화된 로컬 JPEG를 전환하므로 테마 변경 때 API 생성 요청은 발생하지 않습니다. 동일 주제의 구형 단일 홈 이미지는 중복이라 제거했습니다.

`static/brief-{macro,global,industry}.png`는 기존 포털과 CSS에서 여전히 참조하므로 유지합니다. 자산을 삭제할 때는 코드와 스타일의 동적 경로까지 확인해야 합니다.

색상 원본은 `theme_tokens.py`, 경로 선택은 `theme_assets.py`입니다. 기본 테마는 라이트이며 모드 선택은 현재 세션에서 공유됩니다. 생성 초기 프롬프트는 `docs/home-artwork.json`에 남겨 둡니다.
