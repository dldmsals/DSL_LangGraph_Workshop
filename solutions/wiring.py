"""
graph.py 의 ★ 빈칸 두 줄의 정답.

--solution 으로 실행하면 digest/graph.py 의 빈칸 대신 이 배선이 쓰입니다.
"""


def wire_step2(builder, route_fn):
    builder.add_conditional_edges(
        "grade",        # 어디서 갈라지나
        route_fn,       # 어디로 갈지 정하는 함수 (router.py)
        {"revise": "revise", "publish": "publish"},
    )
    builder.add_edge("revise", "grade")   # ★ 뒤로 가는 선 = 사이클
                                          #   n8n 이 못 하던 그 한 줄
