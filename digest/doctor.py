"""
사전 과제용 헬스체크.

  uv run python -m digest.doctor

전부 ✅ 면 준비 완료입니다. 세션 전날까지 돌려보세요.
"""
import os
import sys

from dotenv import load_dotenv

OK, NG = "✅", "❌"


def main():
    load_dotenv()
    fails = []

    v = sys.version_info
    if (3, 12) <= (v.major, v.minor) < (3, 14):
        print(f"{OK} 파이썬 {v.major}.{v.minor}.{v.micro}")
    else:
        print(f"{NG} 파이썬 {v.major}.{v.minor} — 3.12 또는 3.13 이 필요합니다")
        fails.append("python")

    for mod, label in [
        ("langgraph", "langgraph"),
        ("langchain_google_genai", "langchain-google-genai"),
        ("feedparser", "feedparser"),
        ("grandalf", "grandalf (그래프 그림용)"),
    ]:
        try:
            __import__(mod)
            print(f"{OK} {label}")
        except ImportError:
            print(f"{NG} {label} — 'uv sync' 를 실행하세요")
            fails.append(label)

    try:
        from digest.graph import build_graph
        from solutions.router import route_after_grade

        build_graph(step=2, route_fn=route_after_grade)
        print(f"{OK} 그래프 조립")
    except Exception as e:
        print(f"{NG} 그래프 조립 — {e}")
        fails.append("graph")

    if os.getenv("GOOGLE_API_KEY"):
        print(f"{OK} GOOGLE_API_KEY 설정됨")
    else:
        print("⚠️  GOOGLE_API_KEY 없음 — --fake-llm 으로는 실습 가능합니다")
        print("    https://aistudio.google.com/apikey (무료, 카드 등록 불필요)")

    print()
    if fails:
        print(f"{NG} {len(fails)}개 항목 실패. 위 안내를 따라 해결한 뒤 다시 실행하세요.")
        sys.exit(1)
    print("🎉 All good — 준비 완료입니다!")


if __name__ == "__main__":
    main()
