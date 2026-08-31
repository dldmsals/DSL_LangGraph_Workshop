# LangGraph 실습 — 뉴스 다이제스트 + 자기평가 루프

DSL 2026 Fall 정규세션 · n8n 세션에 이어지는 LangGraph 파트

---

## 초기 세팅

### 0. uv 설치 (처음이라면)

파이썬과 패키지를 알아서 맞춰주는 도구입니다. 이미 있으면 건너뛰세요.

> **파이썬은 따로 설치하지 않아도 됩니다.**
> uv 가 이 프로젝트에 필요한 3.12 를 자동으로 받아옵니다 (25MB, 몇 초).
> 컴퓨터에 파이썬이 아예 없거나, 버전이 달라도 상관없습니다.
> uv 자체도 파이썬이 필요 없는 독립 실행 파일입니다.

```bash
uv --version          # 버전이 나오면 설치되어 있는 것
```

없다면 — **macOS / Linux**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows** (PowerShell)

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

설치 후 터미널을 새로 열어야 인식됩니다.

### 1. 레포 받고 설치

```bash
git clone https://github.com/dldmsals/DSL_LangGraph_Workshop.git
cd DSL_LangGraph_Workshop
uv sync
```

설치는 여기까지입니다. 준비 확인(doctor)은 아래에서 API 키와 Slack 웹훅까지 넣은 뒤에 돌립니다.

### 2. API 키 발급 (필수)

**세션 전에 반드시 발급받아 오세요.** 무료이고 카드 등록도 필요 없습니다.

1. [aistudio.google.com/apikey](https://aistudio.google.com/apikey) 접속 → `Create API key`
2. 키를 담을 `.env` 파일을 만듭니다

   ```bash
   cp .env.example .env          # Windows cmd 라면:  copy .env.example .env
   ```

3. 방금 만든 `.env` 를 편집기로 열어 발급받은 키를 붙여넣습니다

   ```
   GOOGLE_API_KEY=AIza... 여기에 본인 키
   ```

`.env` 는 비밀값을 담는 파일이라 `.gitignore` 에 걸려 있어 깃에 올라가지 않습니다.
레포에는 빈 양식인 `.env.example` 만 들어 있고, 각자 복사해서 자기 키를 채워 쓰는 방식입니다.

**정말 발급이 안 될 때만** 모든 명령 뒤에 `--fake-llm` 을 붙이세요.
가짜 LLM 이 대신 답하고 노드 코드는 그대로라 흐름은 따라올 수 있지만,
실제 모델이 매번 다르게 채점하는 걸 못 보게 됩니다.

### 3. Slack 웹훅 주소 발급 (필수)

완성된 다이제스트를 터미널이 아니라 **본인 Slack DM 으로 발송**하기 위한 주소입니다.

1. [api.slack.com/apps](https://api.slack.com/apps) 접속 → `Create an App` → **`Blank app`** 선택 → `Continue`
   (화면이 예전 버전이면 `From scratch` 를 고르면 됩니다. `AI agent` 등 템플릿은 필요 없습니다)
2. 앱 이름(아무거나)과 워크스페이스(**DSL**)를 고르고 생성
3. 왼쪽 메뉴 `Incoming Webhooks` → 스위치를 `On` → 맨 아래 `Add New Webhook to Workspace`
4. 목적지 드롭다운에서 **본인 이름(DM)** 을 고르면 `https://hooks.slack.com/services/...` 주소가 생깁니다
   — 다이제스트가 각자 자기 DM 으로 옵니다. 채널을 고르지 마세요

   > 드롭다운에 본인 이름이 없다면: Slack 에서 **나와의 DM** 을 한 번 열어
   > 아무 메시지나 보낸 뒤 이 페이지를 새로고침하세요. 그래도 없으면
   > **Slackbot** 을 골라도 됩니다 — 마찬가지로 본인에게만 옵니다
5. `.env` 를 열어 `SLACK_WEBHOOK_URL` 줄의 주석(`#`)을 지우고 본인 주소를 붙여넣습니다

   ```
   SLACK_WEBHOOK_URL=https://hooks.slack.com/services/... 여기에 본인 주소
   ```

6. 마지막으로 전체 점검합니다

   ```bash
   uv run python -m digest.doctor
   ```

   `🎉 All good` 이 나오면 준비 완료입니다.

> 명령 앞의 **`uv run` 을 빼먹지 마세요.** 그냥 `python` 으로 돌리면
> 시스템에 깔린 다른 파이썬이 잡혀서 버전 오류가 납니다.

---

## doctor 가 실패할 때

| 메시지 | 원인 · 해결 |
|---|---|
| `uv: command not found` | uv 미설치. 위 **0. uv 설치** 참고 |
| `파이썬 3.x — 3.12 또는 3.13 이 필요합니다` | `uv run` 을 빼먹었습니다. 컴퓨터에 깔린 파이썬이 아니라 uv 가 받아온 3.12 를 써야 합니다. `uv run python -m digest.doctor` |
| `langgraph — 'uv sync' 를 실행하세요` | `uv sync` 를 안 했거나 레포 폴더 밖에서 실행했습니다 |
| `GOOGLE_API_KEY 없음` | `.env` 파일이 없습니다. 파일명이 `.env.txt` 로 저장되지 않았는지 확인하세요 |
| `키가 잘못됐습니다` | 키를 복사할 때 앞뒤 공백이나 따옴표가 딸려 들어갔습니다 |
| `SLACK_WEBHOOK_URL 없음` | `.env` 의 `# SLACK_WEBHOOK_URL=...` 줄에서 `#` 을 안 지웠거나 주소를 안 넣었습니다. 위 **3. Slack 웹훅 주소 발급** 참고 |
| `웹훅 주소 형식이 이상합니다` | 주소는 `https://hooks.slack.com/services/` 로 시작해야 합니다. 복사가 잘렸는지 확인하세요 |
| `호출 한도입니다` | 1분 기다렸다 다시 실행하세요 |
| 그 외 연결 오류 | 학교·사내망 차단일 수 있습니다. 다른 네트워크에서 시도해 보세요 |

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
놓여 있습니다. `점수 매기기` · `다시 쓰기` · `attempts + 1` 은 캔버스 아래
**부품 보관소**에 있고, 미션마다 직접 끌어올려 씁니다.

## 복습용 — 개념만 뽑은 최소 예제

`learn/` 폴더에는 RSS·웹훅 같은 걸 다 걷어내고 **LangGraph 개념만 남긴** 짧은 파일이
순서대로 들어 있습니다. 실습 전 예습이나 실습 후 복습에 쓰세요.

**1~3 은 API 키도 네트워크도 필요 없습니다.** 바로 돌아갑니다.

```bash
uv run python learn/01_hello.py        # State · Node · Edge  (8줄짜리 최소 그래프)
uv run python learn/02_conditional.py  # 조건부 엣지 — 갈라지는 선
uv run python learn/03_loop.py         # 루프 — 뒤로 가는 선   ★ 이 실습의 핵심
uv run python learn/04_llm.py          # 03 에 진짜 LLM 만 붙인 것 (키 필요)
```

`03` 과 `04` 를 나란히 열어보세요. **그래프 구조가 글자 하나까지 똑같습니다.**
바뀐 건 노드 함수의 속뿐이에요. 흐름(그래프)과 내용(노드)이 분리된다는 게
LangGraph 의 요점입니다.

---

## 알아두면 좋은 것

- `--fake-llm` 의 가짜 채점기는 **3번째 재작성에서 반드시 통과**하도록 만들어져 있습니다.
  루프 흐름을 보여주기 위한 것이라, 실제 LLM 처럼 매번 결과가 달라지지는 않습니다.
- `recursion_limit` 을 20 으로 낮춰뒀습니다. `revise` 가 `attempts` 를 올리지 않으면
  무한루프 대신 안내 메시지가 뜹니다.
- 발송은 `DISCORD_WEBHOOK_URL` 또는 `SLACK_WEBHOOK_URL` 환경변수가 있으면 웹훅으로,
  없으면 콘솔로 출력합니다.
