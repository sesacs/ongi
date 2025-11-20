# LiveKit 음성 에이전트

[한국어](README.md) | [English](README.en.md)

LiveKit 기반의 음성 AI 에이전트 예제로, MCP(Model Context Protocol) 서버 연동을 통해 실시간 대화형 AI를 구현합니다.

## 기획서
- [2025년 새싹 해커톤 AI 서비스 기획서 (PDF)](docs/2025년_새싹_해커톤_AI_서비스_기획서_최종.pdf)
- [기획서 낭독 음성 (page 1 -> 2~3 -> 4 -> 5~7 -> 8~10 -> 11)](voice/기획서_스크립트_full.mp3)

## 주요 기능
- 🎤 지연이 낮은 자연스러운 음성 대화
- 🔄 중단 감지 및 이어 말하기가 가능한 실시간 상호작용
- 🛠️ MCP 서버를 통한 툴 연동
- 🎯 OpenAI, Deepgram, Cartesia 등 다양한 제공자 선택
- 🔌 커스텀 툴/에이전트 확장이 용이한 구조

## 사전 준비
- Python 3.11
- API 키
  - OpenAI API 키
  - Deepgram API 키
  - LiveKit 자격 증명(선택: LiveKit Cloud 배포 시)

## 빠른 시작
### 1. 의존성 설치
```bash
uv sync
```

### 2. 환경 변수 설정
`.env.example`을 복사해 채워 넣습니다.
```bash
cp .env.example .env
```
필수:
- `OPENAI_API_KEY`
- `DEEPGRAM_API_KEY`

옵션(LiveKit Cloud 배포):
- `LIVEKIT_URL`
- `LIVEKIT_API_KEY`
- `LIVEKIT_API_SECRET`

### 3. 필요 모델 파일 받기
```bash
# 기본 에이전트용
uv run python livekit_basic_agent.py download-files

# MCP 에이전트용
uv run python livekit_mcp_agent.py download-files
```

### 4. 실행
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
