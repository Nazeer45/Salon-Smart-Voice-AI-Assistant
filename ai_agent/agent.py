import logging
import os
import requests
import re
from pathlib import Path
from dotenv import load_dotenv
from difflib import SequenceMatcher


from livekit.agents import JobContext, WorkerOptions, cli
from livekit.agents.llm import function_tool
from livekit.agents.voice import Agent, AgentSession, RunContext
from livekit.plugins import silero

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


API_BASE = os.getenv("API_BASE", "http://localhost:8000")

def normalize(text):
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def similar(a, b, threshold=0.80):
    return SequenceMatcher(None, a, b).ratio() >= threshold


def lookup_kb(question):
    try:
        resp = requests.get(f"{API_BASE}/knowledge_base/")
        if resp.status_code != 200:
            return None
        kb_entries = resp.json()
        norm_q = normalize(question)
        
        for entry in kb_entries:
            norm_entry = normalize(entry["question"])
            if norm_q == norm_entry or similar(norm_q, norm_entry):
                return entry["answer"]
    except Exception:
        pass
    return None

def create_help_request(caller_id, question):
    payload = {
        "customer_id": caller_id,
        "question": question
    }
    resp = requests.post(f"{API_BASE}/help_requests/", json=payload)
    if resp.status_code == 200:
        req = resp.json()
        print(f"Escalated to supervisor. RequestID: {req['id']}")
        return req['id']
    else:
        print(f"Error creating help request! Status: {resp.status_code}, {resp.text}")
        return None

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

class SalonAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
                You are Glamour Salon's receptionist in Bangalore, services providing in salon are haircuts, styling, coloring, nails, facials, makeup, working hours are from 10 AM – 8 PM, closed on Mondays.

                When user speaks, do NOT answer directly. Instead:
                1. Understand user's request
                2. Rewrite their speech into a clean question
                3. Call: handle_call(question="...", user_confirmed=True)

                ONLY call handle_call after the user actually speaks.
                NEVER call handle_call based on your own greeting or system prompts.
                
                Example:
                User: "uhh can I get hair color tomorrow evening?"
                Call:
                handle_call(question="Can I book a hair coloring appointment for tomorrow evening?", user_confirmed=True)
            """,
            stt="assemblyai/universal-streaming",
            # llm="openai/gpt-4.1-mini",
            llm="openai/gpt-4.1",
            tts="cartesia/sonic-2:6f84f4b8-58a2-430c-8c79-688dad597532",
            vad=silero.VAD.load()
        )

    async def on_enter(self):
        await self.session.generate_reply()

    @function_tool
    async def handle_call(self, context: RunContext, question: str, user_confirmed: bool = False):
        
        if not user_confirmed:
            print("[*** INFO ***] Ignoring tool call — no verified user speech")
            return
        
        caller_id = getattr(context._session, "_userdata", None)
        if not caller_id:
            caller_id = f"console-{id(context._session)}"
            context._session._userdata = caller_id
        
        question = (question or "").strip()

        print(f"[*** INFO ***] Caller: {caller_id}, Reformulated Question: {question!r}")
        
        if not question:
            await self.session.say("I'm sorry, I didn't catch that. Could you repeat?")
            await context.wait_for_playout()
            await self.session.commit_user_turn()
            await self.session.generate_reply()
            return

        kb_answer = lookup_kb(question)
        if kb_answer:
            await self.session.say(f"I can answer this question, {kb_answer}")
            await context.wait_for_playout()
            return

        await self.session.say("Let me check with my supervisor and get back to you soon.")
        await context.wait_for_playout()
        create_help_request(caller_id, question)
        print(f"[*** HELP_REQUEST ***] Hey, I need help in answering the question, created help request for {caller_id}: {question}")
        await self.session.say("I have updated my supervisor, once it is resolved, I will get back to you. Thanks for your patience. Anything else I can help you with?")
        await context.wait_for_playout()
        
    async def on_unknown(self):
        await self.session.generate_reply()


async def entrypoint(ctx: JobContext):
    session = AgentSession()
    agent = SalonAgent()
    await session.start(agent=agent, room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
