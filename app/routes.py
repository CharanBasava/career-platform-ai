import time
import random
import pickle
import pandas as pd
import numpy as np
import re
import pdfkit
import requests
import os
from datetime import datetime
from flask import render_template, request, session, jsonify, make_response, url_for, redirect, flash
from groq import Groq
from dotenv import load_dotenv

from app.sbert_logic import analyze_skills
from app.resources import get_resources
from app.bot_logic import get_bot_response
from app.resume_parser import parse_resume


# ---------------- ENVIRONMENT VARIABLES ----------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in environment variables")

client = Groq(api_key=GROQ_API_KEY)


# ---------------- LOAD SALARY MODEL ----------------
try:
    salary_model = pickle.load(open("models/salary_model.pkl", "rb"))
except FileNotFoundError:
    print("❌ Critical: salary_model.pkl missing.")


# ---------------- PDF CONFIG ----------------
try:
    pdf_config = pdfkit.configuration()
except:
    pdf_config = None


# ---------------- ROUTE INITIALIZATION ----------------
def init_routes(app):

    @app.route("/")
    def index():
        return render_template("index.html")


    @app.route("/dashboard", methods=["GET", "POST"])
    def dashboard():

        if request.method == "GET":
            role = session.get("role")

            if not role:
                return redirect(url_for("index"))

            return render_template(
                "dashboard.html",
                role=role,
                matched=session.get("matched_skills", []),
                missing=session.get("missing_skills", []),
                score=session.get("score", 0),
                salary=session.get("prediction", 0),
                resources=get_resources(session.get("missing_skills", [])),
                explanation=session.get("explanation", {})
            )

        # -------- USER INPUT --------
        role = request.form.get("role", "").strip()
        state = request.form.get("state", "Global").strip()
        manual_skills = request.form.get("skills", "").strip()

        resume_file = request.files.get("resume")

        if not manual_skills and (not resume_file or resume_file.filename == ""):
            flash("Please provide your skills either by typing them or uploading a resume.", "danger")
            return redirect(url_for("index"))

        resume_skills = ""

        if resume_file and resume_file.filename != "":
            upload_folder = "temp_uploads"

            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            temp_path = os.path.join(upload_folder, resume_file.filename)

            resume_file.save(temp_path)

            resume_skills = ", ".join(parse_resume(temp_path))

            os.remove(temp_path)

        user_skills = f"{manual_skills}, {resume_skills}".strip(", ")

        matched, missing, score, explanation = analyze_skills(role, user_skills)

        # -------- SALARY PREDICTION --------
        try:

            level = "SE" if any(w in role.lower() for w in ["sr", "senior", "lead", "manager"]) else "MI"

            input_df = pd.DataFrame([{
                "required_skills": user_skills,
                "experience_level": level,
                "company_location": state,
                "years_experience": 5,
                "industry": "Technology"
            }])

            raw_prediction = float(salary_model.predict(input_df)[0])

            if raw_prediction < 1000:
                raw_prediction *= 1000

            pred_usd = raw_prediction * (0.9 + (score / 1000.0))

            prediction = float(np.clip(pred_usd, 45000.0, 200000.0))

        except Exception as e:

            print(f"Prediction Error: {e}")
            prediction = 85000.0

        session.update({
            "role": role,
            "state": state,
            "missing_skills": missing,
            "matched_skills": matched,
            "score": score,
            "prediction": prediction,
            "explanation": explanation,
            "chat_history": []
        })

        session.modified = True

        return redirect(url_for("dashboard"))


    @app.route("/bot")
    def bot_page():

        role = session.get("role")

        if not role:
            return redirect(url_for("index"))

        return render_template(
            "bot.html",
            role=role,
            prediction=session.get("prediction", 0)
        )


    # ---------------- JOB SEARCH ----------------
    @app.route("/jobs")
    def show_jobs():

        role = session.get("role")
        location = session.get("state", "United States")
        matched_skills = session.get("matched_skills", [])

        if not role:
            return redirect(url_for("index"))

        india_states = [
            "Karnataka", "Maharashtra", "Telangana",
            "Delhi", "Tamil Nadu", "Gujarat",
            "India", "Andhra Pradesh", "West Bengal"
        ]

        is_india = any(s.lower() in location.lower() for s in india_states)

        country_code = "in" if is_india else "us"

        base_url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"

        common_params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": 8,
            "max_days_old": 30
        }

        role_jobs = []
        seen_job_ids = set()

        try:

            r_params = {**common_params, "what": role, "where": location}

            r_res = requests.get(base_url, params=r_params)

            raw_role_results = r_res.json().get("results", [])

            for job in raw_role_results:

                jid = job.get("id")

                if jid not in seen_job_ids:
                    role_jobs.append(job)
                    seen_job_ids.add(jid)

        except Exception as e:
            print(f"Role Search Error: {e}")


        skill_jobs = []

        top_skills = matched_skills[:3] if matched_skills else [role]

        for skill in top_skills:

            try:

                s_params = {**common_params, "what": skill, "where": location}

                s_res = requests.get(base_url, params=s_params)

                results = s_res.json().get("results", [])

                for job in results:

                    jid = job.get("id")

                    if jid not in seen_job_ids:
                        skill_jobs.append(job)
                        seen_job_ids.add(jid)

                if len(skill_jobs) >= 12:
                    break

            except Exception as e:
                print(f"Error searching for skill '{skill}': {e}")


        return render_template(
            "jobs.html",
            role=role,
            role_jobs=role_jobs,
            skill_jobs=skill_jobs,
            skills=", ".join(top_skills),
            location=location,
            is_india=is_india
        )


    # ---------------- PDF REPORT ----------------
    @app.route("/download_report")
    def download_report():

        formatted_salary = "{:,.0f}".format(float(session.get("prediction", 0)))

        data = {
            "role": session.get("role"),
            "state": session.get("state"),
            "salary": formatted_salary,
            "score": session.get("score", 0),
            "matched": session.get("matched_skills", []),
            "missing": session.get("missing_skills", []),
            "explanation": session.get("explanation", {}),
            "resources": get_resources(session.get("missing_skills", [])),
            "date": datetime.now().strftime("%B %d, %Y")
        }

        html = render_template("report_pdf.html", **data)

        try:

            if pdf_config:
                pdf = pdfkit.from_string(html, False, configuration=pdf_config)
            else:
                pdf = pdfkit.from_string(html, False)

            response = make_response(pdf)

            response.headers["Content-Type"] = "application/pdf"
            response.headers["Content-Disposition"] = f'attachment; filename={session.get("role")}_Report.pdf'

            return response

        except Exception as e:

            return f"PDF Error: {str(e)}"


    # ---------------- CHATBOT API ----------------
    @app.route("/api/chat", methods=["POST"])
    def chat():

        user_msg = request.json.get("message", "").strip()

        role = session.get("role", "AI Professional")

        bot_reply = get_bot_response(
            user_msg,
            role,
            session.get("matched_skills", []),
            session.get("score", 0),
            session.get("prediction", 0),
            session.get("chat_history", []),
            location=session.get("state", "Global")
        )

        history = session.get("chat_history", [])

        history.append({"role": "user", "content": user_msg})
        history.append({"role": "assistant", "content": bot_reply})

        session["chat_history"] = history[-6:]

        session.modified = True

        return jsonify({"response": bot_reply})