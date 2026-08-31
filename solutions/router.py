"""정답. 막혔을 때만 보세요."""
from digest.state import DigestState, THRESHOLD, MAX_REVISIONS


def route_after_grade(state: DigestState) -> str:
    if state["score"] >= THRESHOLD:
        return "publish"                    # 합격
    if state["attempts"] >= MAX_REVISIONS:
        return "publish"                    # 기회 소진 → 배지 달고 발송
    return "revise"                         # 다시 쓰기
