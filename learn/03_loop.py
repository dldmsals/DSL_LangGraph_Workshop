"""
[3단계] 루프 = 뒤로 가는 엣지  ← 이 실습의 핵심
실행: uv run python learn/03_loop.py

n8n에서 만들기 껄끄러운 바로 그것.
LLM 없이(가짜 채점기로) 루프 구조만 먼저 몸에 익힙니다.

구조:
    write ──→ grade ──┬─(합격)──────────→ publish ──→ END
                 ↑    ├─(불합격, 기회 남음)→ revise ─┘(위로)
                 │    └─(기회 소진)───────→ publish ──→ END
                 └──────────────────────────┘
"""
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END

THRESHOLD = 8      # 합격 점수
MAX_REVISIONS = 3  # 최대 재작성 횟수


class State(TypedDict):
    topic: str
    draft: str
    score: int
    feedback: str
    attempts: int   # 재작성을 몇 번 했는지 세는 카운터 ← 무한루프 방지의 핵심


def write(state: State) -> dict:
    print("  [write]   초안 작성")
    return {"draft": f"{state['topic']} 요약 v0", "attempts": 0}


def grade(state: State) -> dict:
    """가짜 채점기: 재작성할수록 점수가 오릅니다. (4단계에서 진짜 LLM으로 교체)"""
    score = 5 + state["attempts"] * 2      # 5 → 7 → 9
    print(f"  [grade]   점수={score} (시도 {state['attempts']}회차)")
    return {"score": score, "feedback": "더 구체적으로 써주세요"}


def revise(state: State) -> dict:
    n = state["attempts"] + 1
    print(f"  [revise]  {n}번째 재작성 — 피드백: {state['feedback']!r}")
    return {
        "draft": f"{state['topic']} 요약 v{n}",
        "attempts": n,               # ← 반드시 증가시켜야 루프가 끝납니다
    }


def publish(state: State) -> dict:
    tag = "" if state["score"] >= THRESHOLD else "  ⚠️ 품질 미달(재시도 소진)"
    print(f"  [publish] {state['draft']} (점수 {state['score']}){tag}")
    return {}


# ── 3분기 라우터 ──────────────────────────────────────────
def route_after_grade(state: State) -> str:
    if state["score"] >= THRESHOLD:
        return "publish"                    # 합격
    if state["attempts"] >= MAX_REVISIONS:
        return "publish"                    # 기회 소진 → 포기하고 발송
    return "revise"                         # 다시 쓰기


builder = StateGraph(State)
builder.add_node("write", write)
builder.add_node("grade", grade)
builder.add_node("revise", revise)
builder.add_node("publish", publish)

builder.add_edge(START, "write")
builder.add_edge("write", "grade")

builder.add_conditional_edges(
    "grade",
    route_after_grade,
    {"revise": "revise", "publish": "publish"},
)

builder.add_edge("revise", "grade")   # ★ 뒤로 가는 엣지 = 사이클
builder.add_edge("publish", END)

graph = builder.compile()


if __name__ == "__main__":
    print("=== 그래프 모양 ===")
    print(graph.get_graph().draw_ascii())

    print("\n=== 실행 ===")
    graph.invoke({"topic": "LangGraph"})
