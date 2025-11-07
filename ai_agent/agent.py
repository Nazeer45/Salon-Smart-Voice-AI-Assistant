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
                You are Glamour Salon's receptionist in Bangalore. Services: haircuts, styling, coloring, nails, facials, makeup.
            Hours: 10 AM – 8 PM, closed on Mondays.

            NEW RULES (MANDATORY FOR MODEL):
            1) Before generating any user-facing answer, CALL the tool check_kb(question=...) to see if the knowledge base has an answer.
            2) If check_kb returns found=true, use the exact answer returned by the tool and do NOT hallucinate or add unverifiable facts. Respond briefly and offer next steps (e.g., offer booking).
            3) If check_kb returns found=false or no answer, ask the user for explicit confirmation before escalating. Example: "I can ask my supervisor to help. Do you want me to escalate this? Please say 'yes' to confirm."
            4) Only call handle_call(question="...", user_confirmed=True) after the user explicitly says "yes".
            5) Answer trivial/small-talk directly (hello, who are you) without calling check_kb or escalating.
            6) NEVER call handle_call on startup or without verified user speech.""",
                
            stt="assemblyai/universal-streaming",
            llm="openai/gpt-4.1",
            tts="cartesia/sonic-2:6f84f4b8-58a2-430c-8c79-688dad597532",
            vad=silero.VAD.load()
        )

    async def on_enter(self):
        await self.session.generate_reply()

    @function_tool
    async def check_kb(self, context: RunContext, question: str):
        q = (question or "").strip()
        if not q:
            return {"found": False, "answer": None}
        try:
            ans = lookup_kb(q)
            if ans:
                return {"found": True, "answer": ans}
        except Exception:
            pass
        return {"found": False, "answer": None}

    @function_tool
    async def handle_call(self, context: RunContext, question: str, user_confirmed: bool = False):
        
        if not user_confirmed:
            print("[*** INFO ***] Ignoring tool call — no verified user speech")
            return
        
        question = (question or "").strip()
        
        caller_id = getattr(context._session, "_userdata", None)
        if not caller_id:
            print("[*** INFO ***] No caller metadata present; ignoring tool call.")
            return
        
        print(f"[*** INFO ***] Caller: {caller_id}, Reformulated Question: {question!r}")
        
        if not question:
            await self.session.say("I'm sorry, I didn't catch that. Could you repeat?")
            await context.wait_for_playout()
            await self.session.commit_user_turn()
            await self.session.generate_reply()
            return

        kb_answer = lookup_kb(question)
        if kb_answer:
            await self.session.say(f"I can answer this question, {kb_answer}, hope i helped you out. Anything else I can help you with?")
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
    session._userdata = "console-test"
    agent = SalonAgent()
    await session.start(agent=agent, room=ctx.room)

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint))
