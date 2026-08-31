"""
[2단계] 조건부 엣지 = n8n의 IF 노드
실행: uv run python learn/02_conditional.py

핵심: 라우터는 '다음 노드의 이름(문자열)'을 반환하는 그냥 함수다.
"""
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


class State(TypedDict):
    text: str
    length: int
    verdict: str


def measure(state: State) -> dict:
    n = len(state["text"])
    print(f"  [measure] 길이={n}")
    return {"length": n}


def mark_short(state: State) -> dict:
    print("  [mark_short] 짧음")
    return {"verdict": "짧습니다"}


def mark_long(state: State) -> dict:
    print("  [mark_long] 김")
    return {"verdict": "깁니다"}


# ── 라우터 ────────────────────────────────────────────────
# State를 읽고 '다음에 갈 노드 이름'을 문자열로 반환합니다.
# 이 함수 자체는 노드가 아닙니다. 그래프에 등록하지 않습니다.
def route(state: State) -> str:
    return "long" if state["length"] >= 10 else "short"


builder = StateGraph(State)
builder.add_node("measure", measure)
builder.add_node("mark_short", mark_short)
builder.add_node("mark_long", mark_long)

builder.add_edge(START, "measure")

# add_conditional_edges(출발노드, 라우터함수, {라우터반환값: 실제노드이름})
# 3번째 인자(매핑)는 생략 가능하지만, 넣어야 그래프 그림이 제대로 그려집니다.
builder.add_conditional_edges(
    "measure",
    route,
    {"short": "mark_short", "long": "mark_long"},
)

builder.add_edge("mark_short", END)
builder.add_edge("mark_long", END)

graph = builder.compile()


if __name__ == "__main__":
    print("=== 그래프 모양 ===")
    print(graph.get_graph().draw_ascii())

    for text in ["hi", "hello langgraph"]:
        print(f"\n=== 실행: {text!r} ===")
        print(graph.invoke({"text": text})["verdict"])
