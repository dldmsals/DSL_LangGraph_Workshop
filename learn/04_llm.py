"""
[4단계] 가짜 채점기를 진짜 LLM으로 교체
실행: uv run python learn/04_llm.py

3단계와 그래프 구조는 100% 동일합니다.
바뀐 것은 write / grade / revise 노드의 '속'뿐입니다.
→ 이것이 LangGraph의 요점: 흐름(그래프)과 내용(노드)이 분리된다.
"""
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

THRESHOLD = 8
MAX_REVISIONS = 3

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash")


# ── 채점 결과의 '모양'을 Pydantic으로 선언 ────────────────
# with_structured_output에 넘기면 LLM이 반드시 이 형식으로 답합니다.
# (문자열 파싱 지옥에서 해방되는 지점)
class Grade(BaseModel):
    score: int = Field(description="0~10점", ge=0, le=10)
    feedback: str = Field(description="점수를 깎은 이유와 개선 지시. 한 문장.")


grader = llm.with_structured_output(Grade)


class State(TypedDict):
    topic: str
    draft: str
    score: int
    feedback: str
    attempts: int


def write(state: State) -> dict:
    print("  [write]   초안 작성 중...")
    msg = llm.invoke(
        f"'{state['topic']}'을(를) 처음 듣는 사람에게 3문장으로 설명해줘. 설명만 출력해."
    )
    return {"draft": msg.text.strip(), "attempts": 0}


def grade(state: State) -> dict:
    result = grader.invoke(
        "당신은 깐깐한 편집자입니다. 아래 글을 0~10점으로 채점하세요.\n"
        "기준: (1) 3문장인가 (2) 전문용어 없이 쉬운가 (3) 구체적 예시가 있는가\n"
        "웬만하면 7점 이하를 주고, 세 기준을 모두 만족할 때만 8점 이상을 주세요.\n\n"
        f"[글]\n{state['draft']}"
    )
    print(f"  [grade]   점수={result.score} — {result.feedback}")
    return {"score": result.score, "feedback": result.feedback}


def revise(state: State) -> dict:
    n = state["attempts"] + 1
    print(f"  [revise]  {n}번째 재작성 중...")
    msg = llm.invoke(
        f"아래 글을 편집자 피드백에 따라 고쳐 써주세요. 고친 글만 출력하세요.\n\n"
        f"[글]\n{state['draft']}\n\n"
        f"[피드백]\n{state['feedback']}"
    )
    return {"draft": msg.text.strip(), "attempts": n}


def publish(state: State) -> dict:
    tag = "" if state["score"] >= THRESHOLD else "  ⚠️ 품질 미달(재시도 소진)"
    print(f"\n=== 최종 결과 (점수 {state['score']}){tag} ===")
    print(state["draft"])
    return {}


def route_after_grade(state: State) -> str:
    if state["score"] >= THRESHOLD:
        return "publish"
    if state["attempts"] >= MAX_REVISIONS:
        return "publish"
    return "revise"


builder = StateGraph(State)
builder.add_node("write", write)
builder.add_node("grade", grade)
builder.add_node("revise", revise)
builder.add_node("publish", publish)

builder.add_edge(START, "write")
builder.add_edge("write", "grade")
builder.add_conditional_edges(
    "grade", route_after_grade, {"revise": "revise", "publish": "publish"}
)
builder.add_edge("revise", "grade")
builder.add_edge("publish", END)

graph = builder.compile()


if __name__ == "__main__":
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit(
            ".env 파일에 GOOGLE_API_KEY를 넣어주세요. (.env.example 참고)"
        )
    graph.invoke({"topic": "LangGraph"})
