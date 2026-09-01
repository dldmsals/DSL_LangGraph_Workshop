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

        build_graph(step=2, route_fn=route_after_grade, solution=True)
        print(f"{OK} 그래프 조립")
    except Exception as e:
        print(f"{NG} 그래프 조립 — {e}")
        fails.append("graph")

    if not os.getenv("GOOGLE_API_KEY"):
        print(f"{NG} GOOGLE_API_KEY 없음")
        print("    1) https://aistudio.google.com/apikey 에서 발급 (무료)")
        print("    2) cp .env.example .env")
        print("    3) .env 를 열어 키를 붙여넣기")
        fails.append("api key")
    else:
        try:
            import warnings

            warnings.filterwarnings("ignore")
            from digest.llm import get_llm

            get_llm().invoke("ok")
            print(f"{OK} GOOGLE_API_KEY — 실제 호출 성공")
        except Exception as e:
            msg = str(e)
            print(f"{NG} GOOGLE_API_KEY 는 있지만 호출이 안 됩니다")
            if "API_KEY_INVALID" in msg or "API key not valid" in msg:
                print("    키가 잘못됐습니다. .env 의 값을 다시 확인하세요.")
            elif "RESOURCE_EXHAUSTED" in msg or "429" in msg:
                print("    호출 한도입니다. 1분 뒤 다시 실행해 보세요.")
            else:
                print(f"    {type(e).__name__}: {msg[:120]}")
            fails.append("api call")

    hook = os.getenv("SLACK_WEBHOOK_URL") or os.getenv("DISCORD_WEBHOOK_URL")
    if not hook:
        print(f"{NG} SLACK_WEBHOOK_URL 없음")
        print("    운영진 공지의 웹훅 주소를 .env 에 넣으세요 (README 3번 참고)")
        print("    (.env 의 '# SLACK_WEBHOOK_URL=...' 줄에서 # 을 지우고 주소 붙여넣기)")
        fails.append("slack webhook")
    elif not hook.startswith(
        (
            "https://hooks.slack.com/",
            "https://discord.com/api/webhooks/",
            "https://discordapp.com/api/webhooks/",
        )
    ):
        print(f"{NG} 웹훅 주소 형식이 이상합니다")
        print("    https://hooks.slack.com/services/... 전체를 그대로 붙여넣어야 합니다")
        fails.append("slack webhook")
    else:
        kind = "Discord" if "discord" in hook else "Slack"
        print(f"{OK} {kind} 웹훅 주소")

    print()
    if fails:
        print(f"{NG} {len(fails)}개 항목 실패. 위 안내를 따라 해결한 뒤 다시 실행하세요.")
        sys.exit(1)
    print("🎉 All good — 준비 완료입니다!")


if __name__ == "__main__":
    main()
