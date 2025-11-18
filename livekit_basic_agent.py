"""
LiveKit 음성 에이전트 - 빠른 시작
==================================
가장 단순한 LiveKit 음성 AI 비서 예제입니다.
필요한 것은 OpenAI와 Deepgram API 키뿐입니다.
"""

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RunContext
from livekit.agents.llm import function_tool
from livekit.plugins import openai, deepgram, silero
from datetime import datetime
import os

# 환경 변수 로드
load_dotenv(".env")

class Assistant(Agent):
    """가벼운 음성 AI 비서."""

    def __init__(self):
        super().__init__(
            instructions="""당신은 친절하고 도움이 되는 음성 AI 비서입니다.
            사용자의 질문에 또렷하고 자연스럽게 답하고, 모르는 내용은 솔직히 모른다고 말하세요.
            필요한 정보를 간결하고 따뜻하게 안내하세요."""
        )

    @function_tool
    async def get_current_date_and_time(self, context: RunContext) -> str:
        """현재 날짜와 시간을 반환합니다."""
        current_datetime = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        return f"현재 날짜와 시간은 {current_datetime} 입니다"

async def entrypoint(ctx: agents.JobContext):
    """에이전트의 진입점입니다."""

    # 필수 구성 요소로 음성 파이프라인을 설정
    session = AgentSession(
        stt=deepgram.STT(model="nova-2"),
        llm=openai.LLM(model=os.getenv("LLM_CHOICE", "gpt-5.1-mini")),
        tts=openai.TTS(voice="echo"),
        vad=silero.VAD.load(),
    )

    # 세션 시작
    await session.start(
        room=ctx.room,
        agent=Assistant()
    )

    # 초기 인사말 생성
    await session.generate_reply(
        instructions="사용자를 따뜻하게 맞이하고 오늘 무엇을 도와드릴 수 있을지 물어보세요."
    )

if __name__ == "__main__":
    # 에이전트 실행
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
