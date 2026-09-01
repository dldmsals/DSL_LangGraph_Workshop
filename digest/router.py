"""
다이어그램의 주황색 마름모에 해당하는 파일.

★ 오늘 여러분이 직접 짤 유일한 함수입니다.

라우터는 노드가 아닙니다. add_node 로 등록하지 않습니다.
State 를 읽고 '다음에 갈 노드 이름'을 문자열로 돌려주기만 합니다.
"""
from digest.state import DigestState, THRESHOLD, MAX_REVISIONS


def route_after_grade(state: DigestState) -> str:
    """
    다이어그램의 화살표에 붙인 조건 라벨 3개를 그대로 옮겨 적으세요.

        점수 ≥ 8                →  "publish"   (합격)
        점수 < 8 이고 횟수 < 3   →  "revise"    (다시 쓰기)
        횟수 ≥ 3                →  "publish"   (기회 소진, 그냥 발송)

    그림의 말 → 코드의 이름:
        점수 = state["score"],    기준 8 = THRESHOLD
        횟수 = state["attempts"], 기준 3 = MAX_REVISIONS

    화살표는 3개인데 목적지는 2개입니다.
    합격이든 재시도 소진이든 결국 발송이고,
    ⚠️ 배지를 붙일지는 publish 노드가 score 를 보고 알아서 정합니다.
    """
    # TODO: 여기를 채우세요 (3줄이면 됩니다)
    raise NotImplementedError(
        "digest/router.py 의 route_after_grade 를 완성하세요.\n"
        "   막히면 --solution 을 붙여서 정답으로 돌려볼 수 있습니다."
    )
