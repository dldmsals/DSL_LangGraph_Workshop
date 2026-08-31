# LangGraph 실습 — 뉴스 다이제스트 + 자기평가 루프

DSL 2026 Fall 정규세션 · n8n 세션에 이어지는 LangGraph 파트

---

## 초기 세팅

```bash
git clone https://github.com/dldmsals/DSL_LangGraph_Workshop.git
cd DSL_LangGraph_Workshop
uv sync
uv run python -m digest.doctor
```

`🎉 All good` 이 나오면 준비 완료입니다.

### API 키 발급 (필수)

**세션 전에 반드시 발급받아 오세요.** 무료이고 카드 등록도 필요 없습니다.

1. [aistudio.google.com/apikey](https://aistudio.google.com/apikey) 접속 → `Create API key`
2. 키를 담을 `.env` 파일을 만듭니다

   ```bash
   cp .env.example .env
   ```

3. 방금 만든 `.env` 를 편집기로 열어 발급받은 키를 붙여넣습니다

   ```
   GOOGLE_API_KEY=AIza... 여기에 본인 키
   ```

4. 제대로 됐는지 확인합니다

   ```bash
   uv run python -m digest.doctor
   ```

`.env` 는 비밀값을 담는 파일이라 `.gitignore` 에 걸려 있어 깃에 올라가지 않습니다.
레포에는 빈 양식인 `.env.example` 만 들어 있고, 각자 복사해서 자기 키를 채워 쓰는 방식입니다.

**정말 발급이 안 될 때만** 모든 명령 뒤에 `--fake-llm` 을 붙이세요.
가짜 LLM 이 대신 답하고 노드 코드는 그대로라 흐름은 따라올 수 있지만,
실제 모델이 매번 다르게 채점하는 걸 못 보게 됩니다.

---

## 실행 — 그림 세 장이 각각 코드입니다

```bash
uv run python -m digest.run --step 0     # n8n 에서 만든 그 워크플로  (미션 1-a)
uv run python -m digest.run --step 1     # 점수 매기기를 끼워 넣은 일자 (미션 1-c)
uv run python -m digest.run --step 2     # 루프                      (미션 2·3)
```

| step | 그래프 | 실행하면 |
|---|---|---|
| 0 | `수집 → 필터 → 요약 → 발송` | 요약이 잘 나왔는지 **아무도 확인하지 않습니다** |
| 1 | `… → 요약 → 채점 → 발송` | `점수=5` 를 찍어놓고 **그냥 발송합니다** |
| 2 | `채점 ⇄ 재작성` 사이클 | 5 → 7 → 9 로 올라간 뒤 발송합니다 |

| 옵션 | 용도 |
|---|---|
| `--offline` | RSS 대신 `data/sample_feed.json` 사용 (네트워크 불안정할 때) |
| `--fake-llm` | API 키 없이 실행. 노드 코드는 그대로입니다 |
| `--solution` | 정답 라우터로 실행 (막혔을 때) |
| `--topic 반도체` | 주제 변경 |

## 코드는 다이어그램과 1:1 입니다

| 다이어그램 | 파일 |
|---|---|
| 왼쪽 아래 `DigestState` 패널 | `digest/state.py` |
| 네모들 (뉴스 가져오기, 요약하기 …) | `digest/nodes.py` |
| 주황색 마름모 (`route_after_grade`) | `digest/router.py` ← **오늘 채울 빈칸** |
| 화살표들 (`add_edge`) | `digest/graph.py` |

---

## 오늘 여러분이 짤 코드

`digest/router.py` 의 함수 하나뿐입니다.

```python
def route_after_grade(state: DigestState) -> str:
    # 다이어그램의 화살표 3개를 그대로 옮겨 적으세요
    ...
```

나머지는 전부 완성 코드로 제공됩니다.

---

## Excalidraw 템플릿

`excalidraw/` 파일을 [excalidraw.com](https://excalidraw.com) 에서 열면 됩니다
(로그인 불필요 — 메뉴 → 파일 열기).

| 파일 | 용도 |
|---|---|
| `D1_참가자_배포본` | **55분 내내 이 한 장만 씁니다.** 미션마다 덧그려 완성본까지 자랍니다 |

메인 줄에는 **n8n 세션과 동일한 4개**(`뉴스 가져오기 · 기사 고르기 · 요약하기 · 보내기`)만
놓여 있습니다. `점수 매기기` · `다시 쓰기` · `횟수 +1` 은 캔버스 아래
**부품 보관소**에 있고, 미션마다 직접 끌어올려 씁니다.

## 처음 LangGraph 를 배우는 발표자용

`learn/` 폴더에 개념만 뽑은 최소 예제가 순서대로 있습니다.
1~3 은 API 키도 네트워크도 필요 없습니다.

```bash
uv run python learn/01_hello.py        # State · Node · Edge
uv run python learn/02_conditional.py  # 조건부 엣지 (분기)
uv run python learn/03_loop.py         # 루프 (사이클)  ★ 핵심
uv run python learn/04_llm.py          # 진짜 LLM 붙이기 (키 필요)
```

---

## 알아두면 좋은 것

- `--fake-llm` 의 가짜 채점기는 **3번째 재작성에서 반드시 통과**하도록 만들어져 있습니다.
  루프 흐름을 보여주기 위한 것이라, 실제 LLM 처럼 매번 결과가 달라지지는 않습니다.
- `recursion_limit` 을 20 으로 낮춰뒀습니다. `revise` 가 `attempts` 를 올리지 않으면
  무한루프 대신 안내 메시지가 뜹니다.
- 발송은 `DISCORD_WEBHOOK_URL` 또는 `SLACK_WEBHOOK_URL` 환경변수가 있으면 웹훅으로,
  없으면 콘솔로 출력합니다.
