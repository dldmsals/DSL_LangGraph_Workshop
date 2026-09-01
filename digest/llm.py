"""
LLM 준비 담당.

--fake-llm 을 쓰면 API 키 없이도 똑같은 그래프가 돌아갑니다.
중요한 점: nodes.py 코드는 진짜/가짜 어느 쪽이든 한 글자도 바뀌지 않습니다.
"""
import logging
import os
import warnings

from pydantic import BaseModel, Field

# SDK 가 뿜는 안내성 경고를 끕니다. 실습 화면이 지저분해지기만 합니다.
logging.getLogger("google_genai").setLevel(logging.ERROR)
logging.getLogger("google_genai.models").setLevel(logging.ERROR)
warnings.filterwarnings("ignore", module="langchain_google_genai")


# ── 채점 결과의 '모양' ────────────────────────────────────
# with_structured_output 에 넘기면 LLM이 반드시 이 형식으로 답합니다.
class Grade(BaseModel):
    score: int = Field(description="0~10점", ge=0, le=10)
    feedback: str = Field(description="점수를 깎은 이유와 개선 지시. 한 문장.")


# ── 가짜 LLM (API 키 없이 실습용) ──────────────────────────
class _FakeMessage:
    """진짜 LLM 응답과 같은 방식으로 .text 를 제공합니다."""

    def __init__(self, content: str):
        self.text = content


class FakeLLM:
    """호출할수록 조금씩 나아지는 글을 뱉는 가짜 LLM."""

    def __init__(self):
        self.calls = 0

    def invoke(self, prompt: str):
        self.calls += 1
        if self.calls == 1:
            return _FakeMessage(
                "오늘 여러 곳에서 인공지능 관련 소식이 나왔습니다. "
                "여러 기업이 다양한 발표를 했습니다. 앞으로도 계속 지켜봐야 할 것 같습니다."
            )
        return _FakeMessage(
            f"[{self.calls - 1}차 수정] 오늘 AI 업계에서는 세 가지 소식이 있었습니다. "
            "첫째, 새로운 모델이 공개됐습니다. 둘째, 반도체 공급 계약이 체결됐습니다. "
            "셋째, 규제 논의가 시작됐습니다."
        )


class FakeGrader:
    """재작성할수록 점수를 올려주는 가짜 채점기. (5 → 7 → 9)"""

    def __init__(self):
        self.calls = 0

    def invoke(self, prompt: str) -> Grade:
        self.calls += 1
        score = min(5 + (self.calls - 1) * 2, 10)
        notes = [
            "내용이 두루뭉술합니다. 구체적인 회사명과 숫자를 넣어주세요.",
            "많이 나아졌지만 아직 '~인 것 같다' 같은 모호한 표현이 남아 있습니다.",
            "기준을 모두 만족합니다.",
        ]
        return Grade(score=score, feedback=notes[min(self.calls - 1, 2)])


# ── 준비 함수 ────────────────────────────────────────────
# 모델을 바꾸려면 .env 에 GEMINI_MODEL=... 을 넣으면 됩니다.
DEFAULT_MODEL = "gemini-3.5-flash-lite"   # 빠르고 무료 한도가 넉넉합니다


def _chat():
    from langchain_google_genai import ChatGoogleGenerativeAI

    _require_key()
    # Gemini 3.x 는 temperature 를 무시하므로 넘기지 않습니다 (경고만 나옵니다).
    return ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL", DEFAULT_MODEL))


def get_llm(fake: bool = False):
    return FakeLLM() if fake else _chat()


def get_grader(fake: bool = False):
    return FakeGrader() if fake else _chat().with_structured_output(Grade)


def _require_key():
    if not os.getenv("GOOGLE_API_KEY"):
        raise SystemExit(
            "\n GOOGLE_API_KEY 가 없습니다.\n"
            "   1) https://aistudio.google.com/apikey 에서 무료 발급\n"
            "   2) .env 파일에 GOOGLE_API_KEY=... 저장\n"
            "   또는 키 없이 실습하려면 --fake-llm 을 붙이세요.\n"
        )
