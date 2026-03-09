import pandas as pd
import ast
import re
import numpy as np
import os
from groq import Groq
from sentence_transformers import SentenceTransformer, util
from dotenv import load_dotenv

# ---------------- LOAD ENV VARIABLES ----------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=GROQ_API_KEY)


# ---------------- SBERT MODEL ----------------
# Downloads automatically on first run (~90MB) then loads from cache
model = SentenceTransformer("all-MiniLM-L6-v2")


# ---------------- LOAD DATASET ----------------
try:
    df = pd.read_csv("data/clean_jobs.csv")
except FileNotFoundError:
    df = pd.DataFrame(columns=["job_title", "skills"])


# ---------------- NORMALIZE TEXT ----------------
def normalize_title(text):

    if pd.isna(text) or str(text).lower() == "nan":
        return ""

    text = str(text).lower().strip()

    text = re.sub(r"[^a-z0-9\s,]", " ", text)

    text = re.sub(r"\s+", " ", text)

    return text.strip()


# Preprocess job titles for faster matching
df["job_title_clean"] = df["job_title"].apply(normalize_title)


# ---------------- AI FALLBACK ----------------
def fetch_skills_from_ai(role):

    try:

        prompt = f"Identify exactly 8 core technical skills for a {role}. Return as comma-separated values only."

        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama-3.1-8b-instant",
            temperature=0.3,
            max_tokens=100
        )

        response_text = chat_completion.choices[0].message.content

        return [s.strip().lower() for s in response_text.split(",") if s.strip()]

    except Exception:

        return ["python", "sql", "git", "cloud computing"]


# ---------------- MAIN ANALYSIS ----------------
def analyze_skills(role, user_skills_str):

    target_role_clean = normalize_title(role)

    required_skills = []
    source = "Internal Database"

    # ----- DATABASE SEARCH -----
    exact_match = df[df["job_title_clean"] == target_role_clean]

    if exact_match.empty:

        contains_match = df[
            df["job_title_clean"].str.contains(
                target_role_clean,
                na=False,
                regex=False
            )
        ]

    else:
        contains_match = exact_match

    valid_rows = contains_match[contains_match["skills"].notna()]

    if not valid_rows.empty:

        best_row = valid_rows.loc[
            valid_rows["job_title_clean"].str.len().idxmin()
        ]

        raw_skills_str = str(best_row["skills"]).strip()

        source = "Verified Local Database"

        try:

            if raw_skills_str.startswith("["):

                required_skills = [
                    s.strip().lower()
                    for s in ast.literal_eval(raw_skills_str)
                ]

            else:

                required_skills = [
                    s.strip().lower()
                    for s in raw_skills_str.split(",")
                    if s.strip()
                ]

        except Exception:

            required_skills = [
                s.strip().lower()
                for s in raw_skills_str
                .replace("[", "")
                .replace("]", "")
                .replace("'", "")
                .split(",")
            ]

    else:

        required_skills = fetch_skills_from_ai(role)
        source = "Real-time AI Intelligence"


    # ----- USER SKILL CLEANING -----
    clean_input = user_skills_str.replace("\n", ",").replace("\t", ",").lower()

    clean_input = re.sub(r"[^a-z0-9\s,]", " ", clean_input)

    user_skills = sorted(
        list(
            set(
                [
                    s.strip()
                    for s in re.split(r"[,\s]+", clean_input)
                    if len(s.strip()) > 1
                ]
            )
        )
    )

    matched = []
    missing = []
    reasoning_log = []

    if not user_skills:

        return [], required_skills, 0, {
            "source": source,
            "methodology": "No skills extracted from input"
        }


    # ----- SBERT COMPARISON -----
    user_embeddings = model.encode(user_skills, convert_to_tensor=True)

    for req in required_skills:

        if str(req).lower() == "nan" or not req:
            continue

        clean_req = normalize_title(req)

        is_direct = any(u == clean_req or u in clean_req for u in user_skills)

        req_emb = model.encode(clean_req, convert_to_tensor=True)

        cos_scores = util.cos_sim(req_emb, user_embeddings)[0]

        max_sim = float(np.max(cos_scores.tolist()))

        if is_direct or max_sim > 0.60:

            matched.append(req)

            reason = "Keyword Match" if is_direct else f"Semantic Match ({int(max_sim*100)}%)"

            reasoning_log.append({
                "skill": req,
                "status": "Matched",
                "reason": reason
            })

        else:

            missing.append(req)

            reasoning_log.append({
                "skill": req,
                "status": "Missing",
                "reason": f"Semantic Gap ({int(max_sim*100)}%)"
            })


    score = int((len(matched) / len(required_skills)) * 100) if required_skills else 0

    explanation = {
        "source": source,
        "methodology": "S-BERT Transformer (MiniLM-L6)",
        "detailed_log": reasoning_log
    }

    return matched, missing, score, explanation