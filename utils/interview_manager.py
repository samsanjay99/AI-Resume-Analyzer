"""
Mock Interview Manager
Handles question generation, transcript scoring, PDF report generation,
and database persistence for the AI Mock Interview feature.
"""
import os
import re
import json
from datetime import datetime
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()

import google.generativeai as genai

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.lib import colors
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        HRFlowable, KeepTogether
    )
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

from config.database import get_database_connection


class InterviewManager:
    def __init__(self):
        load_dotenv()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)

    @staticmethod
    def setup_interview_tables():
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS mock_interviews (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER,
                        job_role VARCHAR(200),
                        job_description TEXT,
                        difficulty VARCHAR(20) DEFAULT 'medium',
                        interview_type VARCHAR(30) DEFAULT 'mixed',
                        language VARCHAR(10) DEFAULT 'en',
                        question_count INTEGER DEFAULT 5,
                        questions JSONB,
                        expected_answers JSONB,
                        skills_to_test JSONB,
                        status VARCHAR(20) DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS interview_feedback (
                        id SERIAL PRIMARY KEY,
                        interview_id INTEGER REFERENCES mock_interviews(id) ON DELETE CASCADE UNIQUE,
                        user_id INTEGER,
                        transcript JSONB,
                        total_score INTEGER DEFAULT 0,
                        communication_score INTEGER DEFAULT 0,
                        technical_score INTEGER DEFAULT 0,
                        problem_solving_score INTEGER DEFAULT 0,
                        confidence_score INTEGER DEFAULT 0,
                        relevance_score INTEGER DEFAULT 0,
                        category_scores JSONB,
                        strengths TEXT,
                        areas_for_improvement TEXT,
                        per_question_feedback JSONB,
                        skill_gaps JSONB,
                        final_assessment TEXT,
                        improvement_plan TEXT,
                        filler_word_count INTEGER DEFAULT 0,
                        avg_answer_length FLOAT DEFAULT 0,
                        pdf_path VARCHAR(500),
                        created_at TIMESTAMP DEFAULT NOW()
                    )
                """)
                conn.commit()
                return True
        except Exception as e:
            print(f"Error creating interview tables: {e}")
            return False

    def generate_questions(self, job_role, difficulty="medium", interview_type="mixed",
                           question_count=5, job_description="", resume_skills=None, language="en"):
        if not self.google_api_key:
            return self._fallback_questions(job_role, question_count)

        # ── Build rich context from every available signal ──────────
        resume_block = ""
        if resume_skills:
            skills_str = ", ".join(resume_skills[:20])
            resume_block = f"""
CANDIDATE RESUME SKILLS (use these to ask targeted questions):
{skills_str}
→ Pick 2-3 skills from this list and ask the candidate to explain their depth of experience with them.
→ If a skill looks weak or absent but is required for {job_role}, ask about it to expose the gap."""

        jd_block = ""
        if job_description and job_description.strip():
            jd_block = f"""
JOB DESCRIPTION (extract key requirements for targeted questions):
{job_description[:1200]}
→ Identify the top 3 technical requirements and 2 soft-skill requirements from this JD.
→ At least 2 questions MUST test those specific JD requirements directly."""

        # Difficulty maps to experience depth
        diff_map = {
            "easy": (
                "FRESHER / JUNIOR (0-1 year):\n"
                "- Ask about fundamentals, not architecture decisions\n"
                "- Focus on what they LEARNED in projects/college\n"
                "- Avoid production-scale or leadership questions\n"
                "- Example depth: 'What is X and how have you used it?'"
            ),
            "medium": (
                "MID-LEVEL (2-4 years):\n"
                "- Ask about real project decisions and trade-offs\n"
                "- Include one scenario-based problem to solve\n"
                "- Test both hands-on skills and some system thinking\n"
                "- Example depth: 'Describe a time you had to choose between X and Y — what did you decide and why?'"
            ),
            "hard": (
                "SENIOR / LEAD (5+ years):\n"
                "- Ask about architecture, scale, mentoring, ownership\n"
                "- Include complex trade-off and failure/recovery scenarios\n"
                "- Test leadership, strategic thinking, and cross-team impact\n"
                "- Example depth: 'How would you design X for 10 million users?'"
            ),
        }.get(difficulty, "")

        # Interview type maps to question distribution
        type_map = {
            "technical": (
                "TECHNICAL INTERVIEW — Question distribution:\n"
                "- 70% pure technical (concepts, code logic, system design for this role)\n"
                "- 20% technical scenario (debugging, trade-offs, architecture decisions)\n"
                "- 10% past technical project deep-dive\n"
                "DO NOT ask generic HR or culture questions."
            ),
            "behavioral": (
                "BEHAVIORAL INTERVIEW — Question distribution:\n"
                "- 60% STAR method (Situation-Task-Action-Result stories)\n"
                "- 25% soft skills (communication, conflict, teamwork, deadlines)\n"
                "- 15% motivation and career goals\n"
                "Each question must start with: 'Tell me about a time...' or 'Describe a situation...'"
            ),
            "hr": (
                "HR ROUND — Question distribution:\n"
                "- 40% culture fit and values alignment\n"
                "- 30% career goals and motivation for this role\n"
                "- 20% salary expectations and availability\n"
                "- 10% team and work-style preferences\n"
                "Keep questions conversational and open-ended."
            ),
            "mixed": (
                "MIXED INTERVIEW — Question distribution:\n"
                "- 35% technical (role-specific concepts and skills)\n"
                "- 35% behavioral (real examples using STAR method)\n"
                "- 20% situational (hypothetical work scenarios)\n"
                "- 10% HR (motivation, goals, culture fit)\n"
                "Vary question types — do not ask two technical in a row."
            ),
        }.get(interview_type, "")

        prompt = f"""You are a senior hiring manager and expert interviewer at a top tech company.
Your task: generate a TAILORED, HIGH-QUALITY mock interview for the following candidate.

═══════════════════════════════════════════════
ROLE BEING INTERVIEWED FOR: {job_role}
═══════════════════════════════════════════════

EXPERIENCE LEVEL — {diff_map}

INTERVIEW TYPE — {type_map}
{resume_block}
{jd_block}

═══════════════════════════════════════════════
GENERATE EXACTLY {question_count} QUESTIONS
═══════════════════════════════════════════════

STRICT RULES:
1. Every question MUST be specific to {job_role} — no generic questions like "Tell me about yourself" unless it is Q1 as an opener.
2. If resume skills were provided, at least 2 questions must directly reference a skill from that list.
3. If a job description was provided, at least 2 questions must test a requirement from that JD.
4. Questions will be READ ALOUD by a voice AI — write them as natural speech, short sentences.
5. NO special characters: no /, *, #, bullet points, numbered lists, or markdown.
6. For expected_answers: list the KEY POINTS a strong candidate should cover — be specific.
7. For skills_to_test: list the actual skills/competencies each question evaluates.

Return ONLY valid JSON with no markdown fences, no extra text:
{{
  "questions": ["Q1 text", "Q2 text", "Q3 text"],
  "expected_answers": [
    "Strong answer for Q1 should include: point A, point B, point C",
    "Strong answer for Q2 should cover: X, Y, Z with specific examples"
  ],
  "skills_to_test": ["skill tested by Q1", "skill tested by Q2"],
  "interview_focus": "one sentence describing what this interview specifically tests"
}}"""

        try:
            # Try models in order of preference
            last_err = None
            response = None
            for model_name in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    print(f"✅ Questions generated with {model_name}")
                    break
                except Exception as e:
                    last_err = e
                    print(f"⚠️ {model_name} failed: {str(e)[:80]}, trying next...")
                    continue

            if response is None:
                raise last_err
            
            text = response.text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'^```\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            data = json.loads(text)
            if not isinstance(data.get("questions"), list):
                raise ValueError("Invalid structure")
            return {
                "success": True,
                "questions": data["questions"][:question_count],
                "expected_answers": data.get("expected_answers", []),
                "skills_to_test": data.get("skills_to_test", []),
                "interview_focus": data.get("interview_focus", ""),
            }
        except Exception as e:
            print(f"Question generation error: {e}")
            return self._fallback_questions(job_role, question_count)

    def _fallback_questions(self, job_role, count):
        questions = [
            f"Tell me about yourself and your background as a {job_role}.",
            "What are your greatest professional strengths?",
            "Describe a challenging project you worked on and how you handled it.",
            "Where do you see yourself in five years?",
            "Why are you interested in this role?",
            "How do you handle working under pressure or tight deadlines?",
            "Describe your experience working in a team environment.",
        ]
        return {
            "success": True,
            "questions": questions[:count],
            "expected_answers": ["Honest, structured answer" for _ in range(count)],
            "skills_to_test": ["communication", "problem-solving", "teamwork"],
        }

    def evaluate_interview(self, transcript, questions, expected_answers, skills_to_test, job_role):
        if not transcript:
            return self._empty_feedback()

        user_answers = [m for m in transcript if m.get("role") == "user"]
        filler_count = self._count_filler_words(transcript)
        avg_len      = self._avg_answer_length(transcript)

        # Build detailed Q&A comparison table
        qa_table = ""
        for i, q in enumerate(questions):
            candidate_ans = user_answers[i]["content"] if i < len(user_answers) else "(No answer given)"
            expected      = expected_answers[i] if i < len(expected_answers) else "Clear, relevant answer"
            skill         = skills_to_test[i] if i < len(skills_to_test) else "general"
            qa_table += f"""
─── Question {i+1} ───────────────────────────────
Skill being tested : {skill}
Question           : {q}
Expected key points: {expected}
Candidate answered : {candidate_ans}
Word count         : {len(candidate_ans.split())} words
"""

        prompt = f"""You are a strict but fair senior interview coach evaluating a mock interview.

Role interviewing for: {job_role}
Total questions: {len(questions)}
Candidate filler words used: {filler_count}
Average answer length: {avg_len} words

{qa_table}

EVALUATION INSTRUCTIONS:
1. Score each competency 0-100. Be honest — do not inflate scores.
   - 80-100: Exceptional, covers all key points with examples
   - 60-79:  Good, covers most points but lacks depth or examples
   - 40-59:  Average, covers surface level only
   - 20-39:  Weak, misses most key points
   - 0-19:   Did not answer or completely off-topic

2. For per_question_feedback:
   - Compare EXACTLY what the candidate said vs the expected key points
   - If they missed specific expected points, name them in key_points_missed
   - Write suggested_rephrasing as a COMPLETE BETTER ANSWER (2-4 sentences)
     that they could have given — make it specific to the question and role

3. skill_gaps: List specific skills the candidate clearly lacks based on weak answers
   (these will be used to recommend courses — be specific e.g. "React Hooks" not just "React")

4. improvement_plan: Write 4-5 concrete action items the candidate can do this week
   (e.g. "Practice explaining system design by drawing architecture diagrams out loud")

Return ONLY valid JSON, no markdown:
{{
  "total_score": 0,
  "category_scores": {{
    "communication":      {{"score": 0, "comment": "2-3 sentence specific feedback"}},
    "technical_knowledge":{{"score": 0, "comment": "2-3 sentence specific feedback"}},
    "problem_solving":    {{"score": 0, "comment": "2-3 sentence specific feedback"}},
    "confidence_clarity": {{"score": 0, "comment": "2-3 sentence specific feedback"}},
    "relevance":          {{"score": 0, "comment": "2-3 sentence specific feedback"}}
  }},
  "per_question_feedback": [
    {{
      "question": "exact question text",
      "score": 0,
      "feedback": "what was good and what was missing",
      "suggested_rephrasing": "complete better answer they should have given",
      "key_points_missed": ["specific point 1", "specific point 2"]
    }}
  ],
  "strengths": "2-3 paragraph identifying genuine strengths with specific examples from answers",
  "areas_for_improvement": "2-3 paragraph identifying the most critical gaps with specific examples",
  "skill_gaps": ["specific skill 1", "specific skill 2", "specific skill 3"],
  "final_assessment": "1 paragraph overall verdict and hiring recommendation",
  "improvement_plan": "4-5 numbered action items with specific tasks"
}}"""

        try:
            # Try models in order of preference
            last_err = None
            response = None
            for model_name in ["gemini-2.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]:
                try:
                    model = genai.GenerativeModel(model_name)
                    response = model.generate_content(prompt)
                    print(f"✅ Evaluation done with {model_name}")
                    break
                except Exception as e:
                    last_err = e
                    print(f"⚠️ {model_name} failed: {str(e)[:80]}, trying next...")
                    continue

            if response is None:
                raise last_err
            
            text = response.text.strip()
            text = re.sub(r'^```json\s*', '', text)
            text = re.sub(r'^```\s*', '', text)
            text = re.sub(r'\s*```$', '', text)
            data = json.loads(text)
            data["filler_word_count"] = filler_count
            data["avg_answer_length"] = avg_len
            data["success"] = True
            # Normalize: Gemini sometimes returns lists for string fields
            for str_field in ("strengths", "areas_for_improvement", "final_assessment", "improvement_plan"):
                val = data.get(str_field, "")
                if isinstance(val, list):
                    data[str_field] = "\n".join(str(v) for v in val)
                elif not isinstance(val, str):
                    data[str_field] = str(val)
            return data
        except Exception as e:
            print(f"Evaluation error: {e} — using rule-based fallback scorer")
            return self._fallback_score(transcript, questions, filler_count, avg_len)

    def _count_filler_words(self, transcript):
        fillers = ["um", "uh", "like", "you know", "basically", "literally",
                   "actually", "sort of", "kind of", "i mean"]
        count = 0
        for msg in transcript:
            if msg.get("role") == "user":
                text = msg["content"].lower()
                for f in fillers:
                    count += text.count(f)
        return count

    def _avg_answer_length(self, transcript):
        answers = [m["content"] for m in transcript if m.get("role") == "user"]
        if not answers:
            return 0.0
        return round(sum(len(a.split()) for a in answers) / len(answers), 1)

    def _fallback_score(self, transcript, questions, filler_count, avg_len):
        """Rule-based scorer used when Gemini is unavailable. Never returns 0/100."""
        user_answers = [m for m in transcript if m.get("role") == "user"]
        total_q      = len(questions)
        answered     = len(user_answers)

        # Completion rate (0-40 pts)
        completion   = min(answered / max(total_q, 1), 1.0)
        comp_score   = round(completion * 40)

        # Average answer length score (0-30 pts): 50+ words = full marks
        len_score    = min(round((avg_len / 50) * 30), 30)

        # Filler word penalty (0-10 pts deducted)
        filler_pen   = min(filler_count * 2, 10)

        # Base quality score (0-30 pts): reward non-trivial answers
        quality = 0
        for ans in user_answers:
            words = len(ans.get("content", "").split())
            if words >= 30:
                quality += 10
            elif words >= 15:
                quality += 6
            elif words >= 5:
                quality += 3
        quality_score = min(round((quality / max(answered, 1))), 30)

        total = max(comp_score + len_score + quality_score - filler_pen, 10)

        per_q = []
        for i, q in enumerate(questions):
            ans = user_answers[i]["content"] if i < answered else "(No answer)"
            wc  = len(ans.split())
            sc  = min(round((wc / 50) * 100), 100) if wc > 0 else 0
            per_q.append({
                "question": q, "score": sc,
                "feedback": f"Answer captured ({wc} words). AI evaluation unavailable — scored by length heuristic.",
                "suggested_rephrasing": "",
                "key_points_missed": []
            })

        cat = round(total * 0.9)
        return {
            "success": True,
            "total_score": total,
            "category_scores": {
                "communication":       {"score": cat, "comment": "Scored by rule-based fallback (AI unavailable)."},
                "technical_knowledge": {"score": cat, "comment": "Scored by rule-based fallback (AI unavailable)."},
                "problem_solving":     {"score": cat, "comment": "Scored by rule-based fallback (AI unavailable)."},
                "confidence_clarity":  {"score": cat, "comment": "Scored by rule-based fallback (AI unavailable)."},
                "relevance":           {"score": cat, "comment": "Scored by rule-based fallback (AI unavailable)."},
            },
            "per_question_feedback": per_q,
            "strengths": f"Completed {answered}/{total_q} questions with an average answer length of {avg_len} words.",
            "areas_for_improvement": "AI evaluation was unavailable. Re-run the interview for a detailed Gemini analysis.",
            "skill_gaps": [],
            "final_assessment": f"Rule-based score: {total}/100 based on completion rate and answer length. Gemini evaluation failed — please retry.",
            "improvement_plan": "1. Retry the interview when Gemini API quota resets.\n2. Aim for 50+ word answers per question.\n3. Reduce filler words (um, uh, like).",
            "filler_word_count": filler_count,
            "avg_answer_length": avg_len,
        }

    def _empty_feedback(self):
        return {
            "success": False, "total_score": 0, "category_scores": {},
            "per_question_feedback": [], "strengths": "No data",
            "areas_for_improvement": "No data", "skill_gaps": [],
            "final_assessment": "Interview data insufficient.", "improvement_plan": "",
            "filler_word_count": 0, "avg_answer_length": 0,
        }

    @staticmethod
    def save_interview_session(user_id, job_role, difficulty, interview_type,
                               question_count, questions, expected_answers,
                               skills_to_test, job_description="", language="en"):
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO mock_interviews
                    (user_id, job_role, job_description, difficulty,
                     interview_type, language, question_count,
                     questions, expected_answers, skills_to_test, status)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'pending')
                    RETURNING id
                """, (
                    user_id, job_role, job_description, difficulty,
                    interview_type, language, question_count,
                    json.dumps(questions), json.dumps(expected_answers),
                    json.dumps(skills_to_test),
                ))
                interview_id = cursor.fetchone()[0]
                conn.commit()
                return interview_id
        except Exception as e:
            print(f"Error saving interview session: {e}")
            return None

    @staticmethod
    def save_transcript(interview_id: int, transcript: list) -> bool:
        """Save transcript to DB when interview completes on GitHub Pages.
        Streamlit polls for this and runs evaluation when found."""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE mock_interviews
                    SET status = 'transcript_ready',
                        questions = COALESCE(questions, questions)
                    WHERE id = %s
                """, (interview_id,))
                # Store transcript in a temp column or reuse interview_feedback with partial data
                cursor.execute("""
                    INSERT INTO interview_feedback
                    (interview_id, transcript, total_score, created_at)
                    VALUES (%s, %s, 0, NOW())
                    ON CONFLICT DO NOTHING
                """, (interview_id, json.dumps(transcript)))
                conn.commit()
                return True
        except Exception as e:
            # Fallback: just update status
            try:
                with get_database_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "UPDATE mock_interviews SET status='transcript_ready' WHERE id=%s",
                        (interview_id,)
                    )
                    conn.commit()
            except Exception:
                pass
            print(f"save_transcript error: {e}")
            return False

    @staticmethod
    def get_pending_transcript(interview_id: int):
        """Get transcript saved by save_transcript, if evaluation not yet done."""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT transcript FROM interview_feedback
                    WHERE interview_id = %s AND total_score = 0
                    ORDER BY created_at DESC LIMIT 1
                """, (interview_id,))
                row = cursor.fetchone()
                if row and row[0]:
                    t = row[0]
                    return t if isinstance(t, list) else json.loads(t)
                return None
        except Exception as e:
            print(f"get_pending_transcript error: {e}")
            return None

    @staticmethod
    def save_feedback(interview_id, user_id, transcript, feedback, pdf_path=None):
        try:
            cats = feedback.get("category_scores", {})
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO interview_feedback
                    (interview_id, user_id, transcript, total_score,
                     communication_score, technical_score, problem_solving_score,
                     confidence_score, relevance_score, category_scores,
                     strengths, areas_for_improvement, per_question_feedback,
                     skill_gaps, final_assessment, improvement_plan,
                     filler_word_count, avg_answer_length, pdf_path)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    RETURNING id
                """, (
                    interview_id, user_id,
                    json.dumps(transcript),
                    feedback.get("total_score", 0),
                    cats.get("communication", {}).get("score", 0),
                    cats.get("technical_knowledge", {}).get("score", 0),
                    cats.get("problem_solving", {}).get("score", 0),
                    cats.get("confidence_clarity", {}).get("score", 0),
                    cats.get("relevance", {}).get("score", 0),
                    json.dumps(cats),
                    feedback.get("strengths", ""),
                    feedback.get("areas_for_improvement", ""),
                    json.dumps(feedback.get("per_question_feedback", [])),
                    json.dumps(feedback.get("skill_gaps", [])),
                    feedback.get("final_assessment", ""),
                    feedback.get("improvement_plan", ""),
                    feedback.get("filler_word_count", 0),
                    feedback.get("avg_answer_length", 0),
                    pdf_path,
                ))
                feedback_id = cursor.fetchone()[0]
                cursor.execute(
                    "UPDATE mock_interviews SET status='completed' WHERE id=%s",
                    (interview_id,)
                )
                conn.commit()
                return feedback_id
        except Exception as e:
            print(f"Error saving feedback: {e}")
            return None

    @staticmethod
    def get_interview_by_id(interview_id):
        """Load a single interview session from DB — used for session-state recovery."""
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, job_role, difficulty, interview_type,
                           question_count, questions, expected_answers, skills_to_test,
                           status, created_at
                    FROM mock_interviews WHERE id = %s
                """, (interview_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                return {
                    "id": row[0], "user_id": row[1], "job_role": row[2],
                    "difficulty": row[3], "interview_type": row[4],
                    "question_count": row[5],
                    "questions": row[6] if isinstance(row[6], list) else json.loads(row[6] or "[]"),
                    "expected_answers": row[7] if isinstance(row[7], list) else json.loads(row[7] or "[]"),
                    "skills_to_test": row[8] if isinstance(row[8], list) else json.loads(row[8] or "[]"),
                    "status": row[9], "created_at": row[10],
                }
        except Exception as e:
            print(f"Error loading interview {interview_id}: {e}")
            return None

    @staticmethod
    def get_user_interviews(user_id):
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT mi.id, mi.job_role, mi.difficulty, mi.interview_type,
                           mi.question_count, mi.status, mi.created_at,
                           intf.total_score, intf.pdf_path, intf.id as feedback_id
                    FROM mock_interviews mi
                    LEFT JOIN interview_feedback intf ON intf.interview_id = mi.id
                    WHERE mi.user_id = %s
                    ORDER BY mi.created_at DESC
                """, (user_id,))
                rows = cursor.fetchall()
                return [
                    {
                        "id": r[0], "job_role": r[1], "difficulty": r[2],
                        "interview_type": r[3], "question_count": r[4],
                        "status": r[5], "created_at": r[6],
                        "total_score": r[7], "pdf_path": r[8],
                        "feedback_id": r[9],
                    }
                    for r in rows
                ]
        except Exception as e:
            print(f"Error getting interviews: {e}")
            return []

    @staticmethod
    def get_feedback_by_interview(interview_id):
        try:
            with get_database_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT intf.*, mi.job_role, mi.questions, mi.difficulty
                    FROM interview_feedback intf
                    JOIN mock_interviews mi ON mi.id = intf.interview_id
                    WHERE intf.interview_id = %s
                    ORDER BY intf.created_at DESC LIMIT 1
                """, (interview_id,))
                row = cursor.fetchone()
                if not row:
                    return None
                cols = [d[0] for d in cursor.description]
                return dict(zip(cols, row))
        except Exception as e:
            print(f"Error getting feedback: {e}")
            return None

    def generate_pdf_report(self, interview_data, feedback, candidate_name="Candidate"):
        if not REPORTLAB_AVAILABLE:
            return None

        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4,
                                rightMargin=50, leftMargin=50,
                                topMargin=50, bottomMargin=50)
        styles = getSampleStyleSheet()
        elements = []

        title_style = ParagraphStyle("CT", parent=styles["Title"],
            fontSize=22, textColor=colors.HexColor("#1a1a2e"),
            spaceAfter=6, alignment=TA_CENTER)
        section_style = ParagraphStyle("SH", parent=styles["Heading2"],
            fontSize=14, textColor=colors.HexColor("#4CAF50"),
            spaceBefore=16, spaceAfter=8)
        body_style = ParagraphStyle("BD", parent=styles["Normal"],
            fontSize=10, leading=15, textColor=colors.HexColor("#333333"),
            spaceAfter=6, alignment=TA_JUSTIFY)
        small_style = ParagraphStyle("SM", parent=styles["Normal"],
            fontSize=9, textColor=colors.HexColor("#666666"))

        elements.append(Paragraph("AI Mock Interview Report", title_style))
        elements.append(Paragraph(
            f"Candidate: <b>{candidate_name}</b> | Role: <b>{interview_data.get('job_role','N/A')}</b> | Date: <b>{datetime.now().strftime('%B %d, %Y')}</b>",
            ParagraphStyle("SH2", parent=styles["Normal"], fontSize=11,
                           alignment=TA_CENTER, textColor=colors.HexColor("#555555"), spaceAfter=4)
        ))
        elements.append(Paragraph(
            f"Difficulty: <b>{interview_data.get('difficulty','medium').capitalize()}</b> | Type: <b>{interview_data.get('interview_type','mixed').capitalize()}</b>",
            ParagraphStyle("SH3", parent=styles["Normal"], fontSize=10,
                           alignment=TA_CENTER, textColor=colors.HexColor("#777777"), spaceAfter=12)
        ))
        elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#4CAF50")))
        elements.append(Spacer(1, 12))

        total = feedback.get("total_score", 0)
        score_color = "#4CAF50" if total >= 75 else "#FF9800" if total >= 50 else "#F44336"
        score_data = [[
            Paragraph(f"<b>{total}/100</b>", ParagraphStyle("BS", parent=styles["Normal"],
                fontSize=32, textColor=colors.HexColor(score_color), alignment=TA_CENTER)),
            Paragraph(
                f"<b>Overall Score</b><br/><font color='{score_color}'>"
                f"{'Excellent' if total>=75 else 'Good' if total>=50 else 'Needs Work'}</font>"
                f"<br/><font size=8 color='#888888'>Filler words: {feedback.get('filler_word_count',0)} | "
                f"Avg answer: {feedback.get('avg_answer_length',0)} words</font>",
                ParagraphStyle("SD", parent=styles["Normal"], fontSize=12,
                               alignment=TA_LEFT, textColor=colors.HexColor("#333333"))
            )
        ]]
        score_table = Table(score_data, colWidths=[120, 350])
        score_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (0,0), colors.HexColor("#f8f9fa")),
            ("BOX", (0,0), (-1,-1), 1, colors.HexColor("#e0e0e0")),
            ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
            ("LEFTPADDING", (0,0), (-1,-1), 12),
            ("TOPPADDING", (0,0), (-1,-1), 12),
            ("BOTTOMPADDING", (0,0), (-1,-1), 12),
        ]))
        elements.append(score_table)
        elements.append(Spacer(1, 16))

        elements.append(Paragraph("Competency Breakdown", section_style))
        cats = feedback.get("category_scores", {})
        cat_map = [
            ("Communication", "communication"),
            ("Technical Knowledge", "technical_knowledge"),
            ("Problem Solving", "problem_solving"),
            ("Confidence & Clarity", "confidence_clarity"),
            ("Answer Relevance", "relevance"),
        ]
        cat_rows = [["Competency", "Score", "Feedback"]]
        for label, key in cat_map:
            c = cats.get(key, {})
            sc = c.get("score", 0)
            bar_color = "#4CAF50" if sc>=75 else "#FF9800" if sc>=50 else "#F44336"
            cat_rows.append([
                Paragraph(f"<b>{label}</b>", body_style),
                Paragraph(f"<font color='{bar_color}'><b>{sc}/100</b></font>", body_style),
                Paragraph(c.get("comment","N/A")[:200], small_style),
            ])
        cat_table = Table(cat_rows, colWidths=[130, 65, 285])
        cat_table.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f9f9f9"), colors.white]),
            ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#dddddd")),
            ("VALIGN", (0,0), (-1,-1), "TOP"),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        elements.append(cat_table)
        elements.append(Spacer(1, 16))

        elements.append(Paragraph("Strengths", section_style))
        elements.append(Paragraph(feedback.get("strengths", "N/A"), body_style))
        elements.append(Paragraph("Areas for Improvement", section_style))
        elements.append(Paragraph(feedback.get("areas_for_improvement", "N/A"), body_style))

        pqf = feedback.get("per_question_feedback", [])
        if pqf:
            elements.append(Paragraph("Per-Question Analysis", section_style))
            for i, qf in enumerate(pqf):
                qsc = qf.get("score", 0)
                qc = "#4CAF50" if qsc>=75 else "#FF9800" if qsc>=50 else "#F44336"
                missed = qf.get("key_points_missed", [])
                rows = [
                    [Paragraph(f"<b>Q{i+1}: {str(qf.get('question',''))[:100]}</b>", body_style),
                     Paragraph(f"<font color='{qc}'><b>{qsc}/100</b></font>", body_style)],
                    [Paragraph(f"<b>Feedback:</b> {qf.get('feedback','')}", small_style), ""],
                    [Paragraph(f"<b>Better answer:</b> <i>{str(qf.get('suggested_rephrasing',''))[:300]}</i>", small_style), ""],
                ]
                if missed:
                    rows.append([Paragraph(f"<b>Missed:</b> {', '.join(missed[:5])}", small_style), ""])
                qt = Table(rows, colWidths=[380, 100])
                qt.setStyle(TableStyle([
                    ("BOX", (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
                    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f0f4f8")),
                    ("SPAN", (0,1), (-1,1)), ("SPAN", (0,2), (-1,2)),
                    ("LEFTPADDING", (0,0), (-1,-1), 8),
                    ("TOPPADDING", (0,0), (-1,-1), 5),
                    ("BOTTOMPADDING", (0,0), (-1,-1), 5),
                    ("VALIGN", (0,0), (-1,-1), "TOP"),
                ]))
                elements.append(KeepTogether([qt, Spacer(1, 8)]))

        gaps = feedback.get("skill_gaps", [])
        if gaps:
            elements.append(Paragraph("Identified Skill Gaps", section_style))
            elements.append(Paragraph(
                f"<font color='#F44336'>{' | '.join(gaps[:10])}</font>", body_style))

        if feedback.get("improvement_plan"):
            elements.append(Paragraph("Personalized Improvement Plan", section_style))
            plan = feedback["improvement_plan"]
            if isinstance(plan, list):
                plan = "\n".join(str(p) for p in plan)
            elements.append(Paragraph(str(plan), body_style))

        elements.append(Paragraph("Final Assessment", section_style))
        final = feedback.get("final_assessment", "N/A")
        if isinstance(final, list):
            final = " ".join(str(f) for f in final)
        elements.append(Paragraph(str(final), body_style))

        elements.append(Spacer(1, 20))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#4CAF50")))
        elements.append(Paragraph(
            "Generated by Smart Resume AI · AI Mock Interview System",
            ParagraphStyle("Ftr", parent=styles["Normal"], fontSize=8,
                           alignment=TA_CENTER, textColor=colors.HexColor("#aaaaaa"), spaceBefore=6)
        ))

        doc.build(elements)
        buffer.seek(0)
        return buffer
