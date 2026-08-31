"""
다이어그램의 '선'들에 해당하는 파일.

여러분이 Excalidraw 에서 그은 화살표가 여기 한 줄씩 대응합니다.
세 단계의 그림이 각각 실행 가능합니다.

  step 0 : n8n 에서 만든 그 워크플로       (미션 1-a)
  step 1 : 점수 매기기를 끼워 넣은 일자     (미션 1-c)
  step 2 : 루프                            (미션 2·3)
"""
from langgraph.graph import StateGraph, START, END

from digest.state import DigestState
from digest import nodes


def build_graph(step: int, route_fn=None):
    builder = StateGraph(DigestState)

    # ── 네모 놓기 (add_node) ─────────────────────────────
    # 왼쪽이 '이름표', 오른쪽이 실제 함수입니다. 둘은 달라도 됩니다.
    builder.add_node("fetch", nodes.fetch)
    builder.add_node("filter", nodes.filter_articles)
    builder.add_node("summarize", nodes.summarize)
    builder.add_node("publish", nodes.publish)

    # ── 선 잇기 (add_edge) ───────────────────────────────
    builder.add_edge(START, "fetch")
    builder.add_edge("fetch", "filter")
    builder.add_edge("filter", "summarize")

    if step == 0:
        # 요약이 잘 나왔는지 아무도 확인하지 않습니다.
        builder.add_edge("summarize", "publish")

    else:
        builder.add_node("grade", nodes.grade)
        builder.add_edge("summarize", "grade")

        if step == 1:
            # 점수를 매겨놓고 아무것도 안 하고 그냥 발송합니다.
            builder.add_edge("grade", "publish")

        else:
            builder.add_node("revise", nodes.revise)
            builder.add_conditional_edges(
                "grade",        # 어디서 갈라지나
                route_fn,       # 어디로 갈지 정하는 함수 (router.py)
                {"revise": "revise", "publish": "publish"},
            )
            builder.add_edge("revise", "grade")   # ★ 뒤로 가는 선 = 사이클
                                                  #   n8n 이 못 하던 그 한 줄

    builder.add_edge("publish", END)
    return builder.compile()
