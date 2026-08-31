"""
다이어그램 왼쪽 아래 'DigestState' 패널에 해당하는 파일.

노드 사이를 흐르는 단 하나의 상태입니다.
"""
from typing_extensions import TypedDict

# ── 실험용 상수 ──────────────────────────────────────────
# Step 3에서 이 숫자들을 바꿔보세요.
THRESHOLD = 8      # 합격 점수          ← 9로 올려보기
MAX_REVISIONS = 3  # 최대 재작성 횟수    ← 1로 줄여보기


class DigestState(TypedDict):
    topic: str             # 실습 주제
    articles: list[dict]   # ← fetch 가 채움      ("기사 목록")
    selected: list[dict]   # ← filter 가 채움     ("고른 기사")
    summary: str           # 현재 요약본           ("요약문")   revise 가 덮어씀
    score: int             # 0-10  ← grade 가 채움 ("점수")
    feedback: str          # 채점자의 지적         ("뭐가 문제인지") → revise 의 입력
    attempts: int          # 재작성 횟수           ("횟수")

# ⚠️ TypedDict 는 기본값을 만들어주지 않습니다.
#    invoke({"topic": "AI"}) 로 시작하면 State 에 attempts 키가 없어서
#    grade 가 읽는 순간 KeyError 가 납니다.
#    → summarize 노드가 attempts: 0 을 넣어줍니다. (nodes.py 참고)
