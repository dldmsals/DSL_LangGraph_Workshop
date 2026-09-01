"""
다이어그램의 '네모'들에 해당하는 파일.

노드는 그냥 함수입니다.
  입력: 현재 State 전체
  출력: '내가 바꾼 부분'만 담은 dict   ← 전체를 반환할 필요 없음
"""
import json
import os
from pathlib import Path

import requests

from digest.state import DigestState, THRESHOLD, MAX_REVISIONS

_llm = None
_grader = None
_offline = False
_slack = False

DATA = Path(__file__).resolve().parent.parent / "data" / "sample_feed.json"


def setup(llm, grader, offline: bool, slack: bool = False):
    """run.py 가 시작할 때 한 번 불러줍니다."""
    global _llm, _grader, _offline, _slack
    _llm, _grader, _offline, _slack = llm, grader, offline, slack


# ── 뉴스 가져오기 ─────────────────────────────────────────
def fetch(state: DigestState) -> dict:
    if _offline:
        articles = json.loads(DATA.read_text(encoding="utf-8"))["articles"]
        print(f"  [fetch]     오프라인 샘플 {len(articles)}건 로드")
        return {"articles": articles}

    import feedparser

    topic = state["topic"]
    url = f"https://news.google.com/rss/search?q={topic}&hl=ko&gl=KR&ceid=KR:ko"
    feed = feedparser.parse(url)
    articles = [
        {"title": e.title, "summary": getattr(e, "summary", ""), "link": e.link}
        for e in feed.entries[:15]
    ]
    print(f"  [fetch]     RSS {len(articles)}건 수집")
    return {"articles": articles}


# ── 기사 고르기 ───────────────────────────────────────────
# 함수 이름이 filter_articles 인 이유: filter 는 파이썬 기본 함수라 못 씁니다.
# 그래프에 등록할 때의 '이름표'는 "filter" 로 따로 붙입니다. (graph.py 참고)
def filter_articles(state: DigestState) -> dict:
    seen, selected = set(), []
    for a in state["articles"]:
        if a["title"] in seen:
            continue
        seen.add(a["title"])
        selected.append(a)
        if len(selected) == 3:
            break
    print(f"  [filter]    {len(selected)}건 선별")
    return {"selected": selected}


# ── 요약하기 ─────────────────────────────────────────────
def summarize(state: DigestState) -> dict:
    if not state["selected"]:
        return {"summary": "오늘은 관련 기사가 없습니다", "attempts": 0}

    body = "\n".join(f"- {a['title']}: {a['summary']}" for a in state["selected"])
    msg = _llm.invoke(f"다음 기사들을 요약해줘.\n\n{body}")

    print("  [summarize] 초안 작성")
    return {"summary": msg.text.strip(), "attempts": 0}  # ★ attempts 초기화


# ── 점수 매기기 ───────────────────────────────────────────
def grade(state: DigestState) -> dict:
    result = _grader.invoke(
        "당신은 깐깐한 편집자입니다. 아래 뉴스 다이제스트를 0~10점으로 채점하세요.\n"
        "기준: (1) 3문장 이내인가 (2) 구체적인 회사명·숫자가 있는가 "
        "(3) '~인 것 같다' 같은 모호한 표현이 없는가\n"
        "웬만하면 7점 이하를 주고, 세 기준을 모두 만족할 때만 8점 이상을 주세요.\n\n"
        f"[다이제스트]\n{state['summary']}"
    )
    print(f"  [grade]     점수={result.score} — {result.feedback}")
    return {"score": result.score, "feedback": result.feedback}


# ── 다시 쓰기 ─────────────────────────────────────────────
def revise(state: DigestState) -> dict:
    n = state["attempts"] + 1
    print(f"  [revise]    {n}번째 재작성")
    msg = _llm.invoke(
        "아래 다이제스트를 편집자 피드백에 따라 고쳐 쓰세요. 고친 글만 출력하세요.\n\n"
        f"[다이제스트]\n{state['summary']}\n\n"
        f"[피드백]\n{state['feedback']}"
    )
    return {
        "summary": msg.text.strip(),
        "attempts": n,  # ★ 안 올리면 무한루프
    }


# ── 보내기 ───────────────────────────────────────────────
def publish(state: DigestState) -> dict:
    score = state.get("score")          # step 0 에는 채점 단계가 없습니다
    if score is None:
        badge, score_txt = "", ""
    elif score >= THRESHOLD:
        badge, score_txt = "", f" (점수 {score}/10)"
    elif state["attempts"] >= MAX_REVISIONS:
        badge, score_txt = "  ⚠️ 품질 미달 (재시도 소진)", f" (점수 {score}/10)"
    else:
        badge, score_txt = "  ⚠️ 품질 미달", f" (점수 {score}/10)"
    text = (
        f"📰 오늘의 {state['topic']} 다이제스트{score_txt}{badge}\n\n"
        f"{state['summary']}\n\n"
        + "\n".join(f"· {a['title']}" for a in state["selected"])
    )

    url = os.getenv("DISCORD_WEBHOOK_URL") or os.getenv("SLACK_WEBHOOK_URL")
    if _slack and url:
        payload = {"content": text} if "discord" in url else {"text": text}
        r = requests.post(url, json=payload, timeout=10)
        print(f"  [publish]   웹훅 발송 (HTTP {r.status_code}){badge}")
    else:
        why = "웹훅 미설정" if _slack else "--slack 미지정"
        print(f"  [publish]   콘솔 출력 ({why}){badge}")
        print("\n" + "─" * 60 + f"\n{text}\n" + "─" * 60)
    return {}
