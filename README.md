# 온기 – 먼저 전화 걸어오는 정서 돌봄 음성 AI

“먼저 연락하고 기억하는” 능동형 말벗 AI 서비스 기획을 담았습니다. 상단은 서비스 콘셉트, 하단은 기술 실행 정보로 분리해 확인할 수 있습니다.

## 서비스 개요
- 대상: 외로움·정서적 고립을 겪는 노인 및 1인 가구
- 방향: AI를 수동형 도구에서 능동형 동반자로 재설계해 “누군가 나를 챙긴다”는 안정감 제공
- 핵심 가치: 정서 교감, 지속적 관계 형성, 고독사·치매 예방 기여

## 해커톤 기획 자료
- [2025년 새싹 해커톤 AI 서비스 기획서 (PDF)](docs/2025년_새싹_해커톤_AI_서비스_기획서_진짜최종.pdf?raw=1)
- 기획서 낭독 음성 (page 1 → 2~3 → 4 → 5~7 → 8~10 → 11)
  - [웹에서 바로 재생](https://htmlpreview.github.io/?https://raw.githubusercontent.com/sesacs/ongi/main/docs/index.html)
  - [MP3 직접 링크](https://raw.githubusercontent.com/sesacs/ongi/main/voice/%EA%B8%B0%ED%9A%8C%EC%84%9C_%EC%8A%A4%ED%81%AC%EB%A6%BD%ED%8A%B8_full.mp3)

## 서비스 특징
- 능동 발신: 예약/이벤트(생일·기념일·위험 알림) 기반으로 AI가 먼저 전화
- 캐릭터 선택: 손녀/손자, 친구, 상담자 등 목소리·톤을 선택해 친밀감 형성
- 자연스러운 대화: 맥락 이해와 이전 대화 기억, 자유로운 주제 전환
- 모니터링: 통화 요약, 감정 변화 추적, 돌봄 기관 연계 가능

## 배경과 목적
- 1인 가구 비율 36.1%(2024), 고독사·치매 위험 증가, 대화 상대 부재
- 기존 AI의 한계: 사용자가 먼저 말해야 반응 → 오히려 고립감을 강화
- 목표: “기억하고 먼저 연락하는 AI”로 정서적 안정과 생활 리듬 유지 지원

## 구현 로드맵
- 1차: CLI/앱/웹 기반 음성 대화, 캐릭터 페르소나, 기본 음성/LLM 파이프라인
- 2차: Twilio 발신, 스케줄러(시간·이벤트 기반)
- 3차: 감정 표현 TTS 튜닝, 대화 분석 제공, 오픈소스 STT 실험

## 데이터·모델·스택
- 데이터: `kresnik/zeroth_korean` 음성 데이터(모델 미세조정)
- 모델: GPT-5.1 계열 대화, Deepgram STT, OpenAI/ElevenLabs TTS
- 기술 스택: Python, LangChain, 음성/통화 인프라(Twilio 등), Deepgram STT, OpenAI GPT·TTS, RDB(PostgreSQL/SQLite), 벡터DB(Chroma/pgvector), 프론트엔드 React/Next.js

## 기대 효과
- 개인: 정서 고립 감소, 규칙적 생활 리듬 유지, “누군가 신경 쓴다”는 안정감
- 사회: 고독사·치매 예방 기여, 돌봄 효율 및 조기 위험 탐지 향상
- 경제/기술: 의료·돌봄 비용 절감, 1인 가구 시장 확장, 능동형 AI 상호작용 사례 축적

---

## 기술 실행 정보
LiveKit 기반 음성 에이전트 예제를 포함해, 기획을 실험·확장할 때 필요한 실행 방법을 정리했습니다.

### 주요 기능
- 🎤 지연이 낮은 자연스러운 음성 대화
- 🔄 중단 감지 및 이어 말하기가 가능한 실시간 상호작용
- 🛠️ MCP 서버를 통한 툴 연동
- 🎯 OpenAI, Deepgram, Cartesia 등 다양한 제공자 선택
- 🔌 커스텀 툴/에이전트 확장이 용이한 구조

### 사전 준비
- Python 3.11
- API 키
  - OpenAI API 키
  - Deepgram API 키
  - LiveKit 자격 증명(선택: LiveKit Cloud 배포 시)

### 빠른 시작
```bash
uv sync
cp .env.example .env
```
필수 환경 변수: `OPENAI_API_KEY`, `DEEPGRAM_API_KEY`
옵션(LiveKit Cloud): `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET`

모델 파일 다운로드:
```bash
# 기본 에이전트용
uv run python livekit_basic_agent.py download-files

# MCP 에이전트용
uv run python livekit_mcp_agent.py download-files
```

실행:
```bash
# 기본 에이전트
uv run python livekit_basic_agent.py console

# MCP 에이전트 (MCP 서버 연동)
uv run python livekit_mcp_agent.py console

# 개발 모드 (LiveKit 연결, 선택)
uv run python livekit_basic_agent.py dev

# 프로덕션 모드
uv run python livekit_basic_agent.py start
```

## 구성 요소
### 음성 파이프라인 기본값
- STT: Deepgram Nova-2
- LLM: OpenAI GPT-5.1-mini (환경변수 `LLM_CHOICE`로 변경 가능)
- TTS: OpenAI Echo
- VAD: Silero VAD
- 턴 감지: Multilingual Model

### MCP 서버 설정 예시 (`livekit_mcp_agent.py`)
```python
session = AgentSession(
    # ... 생략 ...
    mcp_servers=[mcp.MCPServerHTTP(url="http://localhost:8089/mcp")],
)
```

### 커스텀 툴 추가 예시
```python
from livekit.agents.llm import function_tool
from datetime import datetime

class Assistant(Agent):
    @function_tool
    async def get_current_time(self, context: RunContext) -> str:
        return datetime.now().strftime("%I:%M %p")
```

## 프로젝트 구조
```
livekit-agent/
├── livekit_basic_agent.py   # 기본 예제 에이전트
├── livekit_mcp_agent.py     # MCP 연동 에이전트
├── pyproject.toml           # 의존성
├── .env.example             # 환경 변수 템플릿
├── Dockerfile               # 컨테이너 배포 예시
└── README.md
```

## LiveKit Cloud 배포 개요
1) [LiveKit Cloud](https://cloud.livekit.io/) 가입  
2) LiveKit CLI 설치 (`winget install LiveKit.LiveKitCLI` / `brew install livekit` / `curl -sSL https://get.livekit.io/ | bash`)  
3) `lk cloud auth`로 인증  
4) `lk app env -w`로 환경 변수 설정  
5) 에이전트 실행: `livekit_basic_agent.py dev/start` 또는 `livekit_mcp_agent.py console`  

---
더 자세한 설정 옵션과 최적화 팁은 영어 문서에서 확인하세요: [README.en.md](README.en.md)
