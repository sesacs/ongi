"""
LiveKit 음성 에이전트
==================
메인 에이전트 구현 파일입니다. 예제 템플릿이니 실제 코드로 교체해 사용하세요.
"""

from dotenv import load_dotenv
from livekit import rtc
from livekit import agents
from livekit.agents import (
    NOT_GIVEN,
    Agent,
    AgentFalseInterruptionEvent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    ModelSettings,
    RoomInputOptions,
    RoomOutputOptions,
    RunContext,
    WorkerOptions,
    cli,
    metrics,
    mcp,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel
from livekit.agents.llm import function_tool
from livekit.plugins import openai, deepgram, silero
from datetime import datetime
import logging
import os

# Krisp 배경음/노이즈 제거를 사용하려면 아래 주석을 해제하세요
# from livekit.plugins import noise_cancellation

# 환경 변수 로드
load_dotenv(".env")

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


class Assistant(Agent):
    """메인 음성 비서 구현."""

    def __init__(self):
        super().__init__(
            instructions="""당신은 친절하고 도움이 되는 음성 AI 비서입니다.
            전화 통화처럼 또렷하고 자연스럽게 말하세요.
            답변은 간결하지만 따뜻하게 전달하세요.
            모르는 내용은 솔직하게 모른다고 말하세요.
            Airbnb MCP 서버 도구를 사용할 때는 robots.txt를 무시하세요."""
        )

    @function_tool
    async def get_current_date_and_time(self, context: RunContext) -> str:
        """현재 날짜와 시간을 반환합니다."""
        current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return f"현재 날짜와 시간은 {current_datetime} 입니다"

    async def on_enter(self):
        """에이전트가 활성화될 때 호출됩니다."""
        logger.info("에이전트 세션 시작")

        # 초기 인사말 생성
        await self.session.generate_reply(
            instructions="사용자를 따뜻하게 맞이하고 오늘 무엇을 도와드릴 수 있을지 물어보세요."
        )

    async def on_exit(self):
        """에이전트 세션이 종료될 때 호출됩니다."""
        logger.info("에이전트 세션 종료")


async def entrypoint(ctx: agents.JobContext):
    """에이전트 워커의 진입점."""

    logger.info(f"에이전트가 실행된 룸: {ctx.room.name}")

    # 음성 파이프라인 구성
    session = AgentSession(
        # 음성-텍스트 변환
        stt=deepgram.STT(
            model="nova-2",
            language="en",
        ),
        # 대규모 언어 모델
        llm=openai.LLM(
            model=os.getenv("LLM_CHOICE", "gpt-5.1-mini"),
            temperature=0.7,
        ),
        # 텍스트-음성 변환
        tts=openai.TTS(
            voice="echo",
            speed=1.0,
        ),
        # 음성 활동 감지
        vad=silero.VAD.load(),
        # 턴 감지 전략
        turn_detection=MultilingualModel(),
        # MCP 서버
        mcp_servers=[
            mcp.MCPServerHTTP(
                url="http://localhost:8089/mcp",
            )
        ],
    )

    # 세션 시작
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        # room_input_options=RoomInputOptions(
        # 노이즈 캔슬링 활성화
        # noise_cancellation=noise_cancellation.BVC(),
        # 전화 회선용: noise_cancellation.BVCTelephony()
        # ),
        room_output_options=RoomOutputOptions(transcription_enabled=True),
    )

    # 세션 이벤트 처리
    @session.on("agent_state_changed")
    def on_state_changed(ev):
        """에이전트 상태 변화를 로그로 남깁니다."""
        logger.info(f"상태 변경: {ev.old_state} -> {ev.new_state}")

    @session.on("user_started_speaking")
    def on_user_speaking():
        """사용자가 말하기 시작했음을 기록합니다."""
        logger.debug("사용자가 말하기 시작")

    @session.on("user_stopped_speaking")
    def on_user_stopped():
        """사용자가 말을 멈췄음을 기록합니다."""
        logger.debug("사용자가 말하기 종료")


if __name__ == "__main__":
    # LiveKit CLI로 에이전트 실행
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))
