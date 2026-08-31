"""실습용 Excalidraw 템플릿 생성기.  실행: python3 tools/make_templates.py"""
import json
import random
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "excalidraw"
BLUE, RED, YELLOW = "#a5d8ff", "#ffc9c9", "#ffec99"


def _base(el_id, typ, x, y, w, h):
    return {
        "id": el_id, "type": typ, "x": x, "y": y, "width": w, "height": h,
        "angle": 0, "strokeColor": "#1e1e1e", "backgroundColor": "transparent",
        "fillStyle": "solid", "strokeWidth": 2, "strokeStyle": "solid",
        "roughness": 1, "opacity": 100, "groupIds": [], "frameId": None,
        "roundness": None, "seed": random.randint(1, 2**31),
        "version": 1, "versionNonce": random.randint(1, 2**31),
        "isDeleted": False, "boundElements": [], "updated": 1,
        "link": None, "locked": False,
    }


def card(el_id, x, y, label, color=BLUE, w=200, h=80):
    box = _base(el_id, "rectangle", x, y, w, h)
    box["backgroundColor"] = color
    box["roundness"] = {"type": 3}
    box["boundElements"] = [{"type": "text", "id": el_id + "_t"}]

    txt = _base(el_id + "_t", "text", x + 10, y + h / 2 - 12, w - 20, 25)
    txt.update({
        "text": label, "originalText": label, "fontSize": 20, "fontFamily": 2,
        "textAlign": "center", "verticalAlign": "middle",
        "containerId": el_id, "lineHeight": 1.25, "autoResize": True,
    })
    return [box, txt]


def label(el_id, x, y, text, size=28, color="#1e1e1e"):
    t = _base(el_id, "text", x, y, 700, size * 1.25)
    t.update({
        "text": text, "originalText": text, "fontSize": size, "fontFamily": 2,
        "textAlign": "left", "verticalAlign": "top", "containerId": None,
        "lineHeight": 1.25, "autoResize": True, "strokeColor": color,
    })
    return [t]


def write(name, elements):
    doc = {
        "type": "excalidraw", "version": 2, "source": "https://excalidraw.com",
        "elements": elements,
        "appState": {"gridSize": None, "viewBackgroundColor": "#ffffff"},
        "files": {},
    }
    p = OUT / name
    p.write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"  {p.name}  ({len(elements)} elements)")


# n8n 세션에서 만든 것과 동일한 4단계. 미션 1-a 는 이것만 잇습니다.
CARDS = ["뉴스 가져오기", "기사 고르기", "요약하기", "보내기"]
X0, Y0, GAP = 120, 300, 60
PARK_Y = Y0 + 320          # 부품 보관소


def build_canvas(title, sub):
    """참가자 배포본 = 발표자 마스터. 세션 내내 이 한 장에 덧그립니다."""
    els = label("t", X0, 120, title)
    els += label("s", X0, 165, sub, size=16, color="#868e96")

    for i, name in enumerate(CARDS):
        els += card(f"c{i}", X0 + i * (200 + GAP), Y0, name)

    # ── 부품 보관소 ──────────────────────────────────────
    # 점수 매기기 → 미션 1-b,  다시 쓰기 / 횟수 +1 → 미션 2·3
    els += label("plabel", X0, PARK_Y - 45,
                 "─────  부품 보관소 · 필요할 때 끌어올려 쓰세요  ─────",
                 size=15, color="#adb5bd")
    els += card("park_grade", X0, PARK_Y, "점수 매기기", BLUE)
    els += card("park_rev", X0 + 200 + GAP, PARK_Y, "다시 쓰기", RED)
    els += card("park_cnt", X0 + 2 * (200 + GAP), PARK_Y, "횟수 +1", YELLOW)
    return els


def main():
    OUT.mkdir(exist_ok=True)
    random.seed(7)
    write("D1_참가자_배포본.excalidraw", build_canvas(
        "미션 1 — n8n 에서 만든 그 워크플로를 그대로 그려보세요",
        "네 개를 순서대로 잇기만 하면 됩니다. 화살표 도구(→) 를 쓰세요.",
    ))
    random.seed(7)
    write("MASTER_발표자용.excalidraw", build_canvas(
        "LangGraph 실습 — 발표자 마스터",
        "미션마다 참가자와 같이 덧그립니다. (참가자 배포본과 동일한 사본)",
    ))


if __name__ == "__main__":
    main()
