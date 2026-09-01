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


def build_graph(step: int, route_fn=None, solution: bool = False):
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

            if solution:
                from solutions.wiring import wire_step2
                wire_step2(builder, route_fn)
            else:
                # ── ★ 오늘 따라 칠 두 줄 ──────────────────────────
                #   ① 갈림길        grade 에서 라우터(route_fn)가 고른 곳으로
                #                   → add_conditional_edges
                #   ② 뒤로 가는 선  revise → grade   ★ 사이클!
                #                   → add_edge
                #
                # 막히면 --solution 으로 완성된 배선을 볼 수 있습니다.
                # ────────────────────────────────────────────────
                pass

    builder.add_edge("publish", END)

    # 두 줄을 입력하기 전에는 grade 에서 길이 끊겨 발송까지 못 갑니다.
    if step == 2 and not solution:
        missing = []
        if "grade" not in builder.branches:
            missing.append("① 갈림길 (add_conditional_edges)")
        if ("revise", "grade") not in builder.edges:
            missing.append('② 뒤로 가는 선 (add_edge("revise", "grade"))')
        if missing:
            raise NotImplementedError(
                "digest/graph.py 의 ★ 표시된 곳이 아직 비어 있습니다:\n"
                + "".join(f"   · {m}\n" for m in missing)
                + "   막히면 --solution 을 붙여서 완성된 배선으로 돌려볼 수 있습니다."
            )

    return builder.compile()
