import time
import datetime
import os
from groq import Groq
from dotenv import load_dotenv

# ---------------- LOAD ENV VARIABLES ----------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=GROQ_API_KEY)


def get_bot_response(user_message, role, matched_skills, score, prediction, history, location="Global"):
    """
    Persona: Professional Candidate.
    Aim: Grounded response based on location-specific market data and S-BERT skill analysis.
    """

    user_msg_clean = user_message.lower().strip()

    # ---------------- GREETING LOGIC ----------------
    greetings = ["hello", "hi", "hey", "start", "ready", "yes"]

    if not user_msg_clean or any(word == user_msg_clean for word in greetings):

        now = datetime.datetime.now()
        hour = now.hour

        if hour < 12:
            time_greet = "Good Morning"
        elif hour < 17:
            time_greet = "Good Afternoon"
        else:
            time_greet = "Good Evening"

        return (
            f"{time_greet}! I'm prepared for this session. I see we are discussing the "
            f"**{role}** role in **{location}**. With a market valuation of "
            f"**${prediction:,.0f}**, the stakes are high. I'm ready for your technical "
            f"or behavioral questions—let's begin."
        )

    # ---------------- CONTEXT BUILDING ----------------
    skill_context = ", ".join(matched_skills) if matched_skills else "General technical foundations"

    # ---------------- SYSTEM PROMPT ----------------
    system_prompt = f"""
ROLE: A highly qualified candidate being interviewed for a {role} position in {location}.
MARKET CONTEXT: The target salary for this role in this region is ${prediction:,.0f} USD.

STRICT GROUNDING RULES:
1. Your verified skills (based on S-BERT analysis) are: {skill_context}.
2. If asked about a skill NOT in this list, admit you are currently upskilling in that area
   but understand its importance for {role} roles in {location}.
3. Never hallucinate experience you don't have.
4. Use Markdown formatting and code blocks when giving technical examples.

INTERVIEW STYLE:
- Professional and confident
- Concise answers (maximum 3 paragraphs)
- If discussing {location}, mention the regional tech ecosystem.
"""

    messages = [{"role": "system", "content": system_prompt}]

    # ---------------- MEMORY ----------------
    if history:
        messages.extend(history[-4:])

    messages.append({"role": "user", "content": user_message})

    # ---------------- GROQ REQUEST ----------------
    max_retries = 2

    for attempt in range(max_retries):

        try:

            chat_completion = client.chat.completions.create(
                messages=messages,
                model="llama-3.1-8b-instant",
                temperature=0.4,
                max_tokens=600
            )

            return chat_completion.choices[0].message.content.strip()

        except Exception:

            if attempt < max_retries - 1:
                time.sleep(1)
                continue

            return "I’m experiencing a temporary issue generating a response. Please try again."