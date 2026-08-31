"""
실행 담당.

  uv run python -m digest.run --step 1              # 일자 그래프
  uv run python -m digest.run --step 2              # 루프 그래프
  uv run python -m digest.run --step 2 --fake-llm   # API 키 없이
  uv run python -m digest.run --step 2 --offline    # 네트워크 없이
  uv run python -m digest.run --step 2 --solution   # 정답 라우터로
"""
import argparse

from dotenv import load_dotenv
from langgraph.errors import GraphRecursionError

from digest import nodes
from digest.graph import build_graph
from digest.llm import get_llm, get_grader


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--step", type=int, choices=[0, 1, 2], default=2)
    p.add_argument("--topic", default="인공지능")
    p.add_argument("--offline", action="store_true", help="RSS 대신 샘플 데이터 사용")
    p.add_argument("--fake-llm", action="store_true", help="API 키 없이 실행")
    p.add_argument("--solution", action="store_true", help="정답 라우터 사용")
    args = p.parse_args()

    load_dotenv()
    nodes.setup(get_llm(args.fake_llm), get_grader(args.fake_llm), args.offline)

    if args.solution:
        from solutions.router import route_after_grade
    else:
        from digest.router import route_after_grade

    graph = build_graph(step=args.step, route_fn=route_after_grade)

    print(f"\n=== STEP {args.step} 그래프 ===")
    print(graph.get_graph().draw_ascii())

    print(f"=== 실행 (주제: {args.topic}) ===")
    # recursion_limit 을 낮게 둡니다.
    # attempts += 1 을 빠뜨리면 무한루프 대신 여기서 바로 에러가 납니다.
    try:
        graph.invoke({"topic": args.topic}, {"recursion_limit": 20})
    except NotImplementedError as e:
        _box("아직 빈칸이 남아 있습니다", str(e))
    except GraphRecursionError:
        _box(
            "무한루프에 빠졌습니다",
            "revise 노드가 attempts 를 올려주지 않으면 grade 와 revise 를 영원히 오갑니다.\n"
            "digest/nodes.py 의 revise 가 attempts: state['attempts'] + 1 을\n"
            "반환하는지 확인하세요.",
        )
    except Exception as e:
        if "RESOURCE_EXHAUSTED" not in str(e) and "429" not in str(e):
            raise
        _box(
            "Gemini 호출 한도에 걸렸습니다",
            "무료 티어는 계정마다 분당 호출 수가 정해져 있습니다.\n"
            "루프 한 번에 최대 8회를 부르니 연속 실행하면 금방 찹니다.\n\n"
            "  · 1분 기다렸다가 다시 실행하거나\n"
            "  · --fake-llm 을 붙여 키 없이 계속하세요\n"
            "  · 조원끼리는 한 명만 돌리는 게 안전합니다",
        )


def _box(title: str, body: str):
    print("\n" + "━" * 60)
    print(f"  {title}")
    print("━" * 60)
    for line in body.splitlines():
        print("  " + line)
    print("━" * 60 + "\n")


if __name__ == "__main__":
    main()
