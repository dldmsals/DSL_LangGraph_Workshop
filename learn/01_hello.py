"""
[1단계] LangGraph의 3요소: State · Node · Edge
실행: uv run python learn/01_hello.py

n8n 대응:  State = 노드 사이를 흐르던 JSON
          Node  = 캔버스 위의 네모 하나
          Edge  = 네모를 잇는 선
"""
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END


# ── 1) State ──────────────────────────────────────────────
# 그래프 전체가 공유하는 데이터의 '모양'을 미리 선언합니다.
class State(TypedDict):
    topic: str
    draft: str


# ── 2) Node ───────────────────────────────────────────────
# 노드는 그냥 함수입니다.
#   입력: 현재 State 전체
#   출력: '내가 바꾼 부분'만 담은 dict  ← 전체를 반환할 필요 없음!
def write(state: State) -> dict:
    print(f"  [write]  topic={state['topic']!r}")
    return {"draft": f"{state['topic']} is fun"}


def shout(state: State) -> dict:
    print(f"  [shout]  draft={state['draft']!r}")
    return {"draft": state["draft"].upper() + "!!!"}


# ── 3) Graph ──────────────────────────────────────────────
builder = StateGraph(State)

builder.add_node("write", write)      # 네모 놓기
builder.add_node("shout", shout)

builder.add_edge(START, "write")      # 선 잇기
builder.add_edge("write", "shout")
builder.add_edge("shout", END)

graph = builder.compile()             # 실행 가능한 그래프로 확정


if __name__ == "__main__":
    print("=== 그래프 모양 ===")
    print(graph.get_graph().draw_ascii())

    print("\n=== 실행 ===")
    result = graph.invoke({"topic": "LangGraph"})

    print("\n=== 최종 State ===")
    print(result)
