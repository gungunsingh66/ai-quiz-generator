import streamlit as st
from quiz_generator import generate_quiz
import time
import pandas as pd
from streamlit_autorefresh import st_autorefresh
from report_generator import generate_pdf
from certificate_generator import generate_certificate
from database import (
    init_db,
    save_result,
    get_results,
    get_leaderboard,
    create_user,
    verify_user
)

st.set_page_config(
    page_title="AI Quiz Platform",
    page_icon="🧠",
    layout="wide"
)

#load css
def load_css():
    with open("styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize database
init_db()

# -------------------------
# HERO BANNER
# -------------------------

st.markdown(
"""
<div style="
padding:30px;
border-radius:15px;
background:linear-gradient(90deg,#2563eb,#38bdf8);
color:white;
text-align:center;
margin-bottom:25px;
">

<h1>🧠 AI Quiz Platform</h1>

<p>Generate AI-powered quizzes and test your knowledge instantly.</p>

</div>
""",
unsafe_allow_html=True
)

# -------------------------
# SESSION STATE INITIALIZATION
# -------------------------

if "user" not in st.session_state:
    st.session_state.user = None

# -------------------------
# DASHBOARD METRICS
# -------------------------

col1, col2, col3 = st.columns(3)

# Quiz count
with col1:

    if st.session_state.user:
        results = get_results(st.session_state.user)
        quizzes_taken = len(results)
    else:
        quizzes_taken = 0

    st.metric("📚 Quizzes Taken", quizzes_taken)

# Average accuracy
with col2:

    if st.session_state.user and quizzes_taken > 0:

        avg_accuracy = round(
            sum(r[2] / r[3] for r in results) / quizzes_taken * 100,
            2
        )

    else:
        avg_accuracy = 0

    st.metric("🎯 Avg Accuracy", f"{avg_accuracy}%")

# Leaderboard size
with col3:

    leaders = get_leaderboard()

    st.metric("🏆 Leaderboard Entries", len(leaders))

st.divider()

# -------------------------
# LOGIN SYSTEM (SIDEBAR)
# -------------------------

st.sidebar.title("🔐 Account")

if not st.session_state.user:

    st.sidebar.info("🔒 Not logged in")

    login_tab, signup_tab = st.sidebar.tabs(["Login", "Signup"])

    # LOGIN
    with login_tab:

        username = st.text_input("Username", key="login_user")
        password = st.text_input("Password", type="password", key="login_pass")

        if st.button("Login"):

            user = verify_user(username, password)

            if user:
                st.session_state.user = username
                st.success("Login successful")
                st.rerun()
            else:
                st.error("Invalid username or password")

    # SIGNUP
    with signup_tab:

        new_user = st.text_input("Create Username", key="signup_user")
        new_pass = st.text_input("Create Password", type="password", key="signup_pass")

        if st.button("Create Account"):

            success = create_user(new_user, new_pass)

            if success:
                st.success("Account created. Please login.")
            else:
                st.error("Username already exists")

else:

    st.sidebar.success(f"👤 Logged in as: {st.session_state.user}")

    if st.sidebar.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# -------------------------
# MAIN TABS
# -------------------------

quiz_tab, history_tab, leaderboard_tab = st.tabs(
    ["🧠 Take Quiz", "📊 History", "🏆 Leaderboard"]
)

# =========================
# QUIZ TAB
# =========================

with quiz_tab:

    topic = st.text_input("Enter quiz topic")

    num_questions = st.number_input(
        "Number of questions",
        min_value=1,
        max_value=10,
        step=1
    )

    difficulty = st.selectbox(
        "Select difficulty",
        ["Easy", "Medium", "Hard"]
    )

    # -------------------------
    # TIMER CALCULATION
    # -------------------------

    if difficulty == "Easy":
        time_per_question = 60
        warning_time = 20
    elif difficulty == "Medium":
        time_per_question = 40
        warning_time = 15
    else:
        time_per_question = 25
        warning_time = 10

    QUIZ_TIME = num_questions * time_per_question

    minutes = QUIZ_TIME // 60
    seconds = QUIZ_TIME % 60

    st.info(f"⏱ Quiz Time: {minutes} min {seconds} sec")

    # -------------------------
    # GENERATE QUIZ
    # -------------------------

    if st.button("Generate Quiz"):

        if topic:

            quiz = generate_quiz(topic, num_questions, difficulty)

            st.session_state.quiz = quiz
            st.session_state.answers = {}
            st.session_state.submitted = False

            st.session_state.start_time = time.time()
            st.session_state.quiz_time = QUIZ_TIME

        else:
            st.warning("Please enter a topic")

    # -------------------------
    # DISPLAY QUIZ
    # -------------------------

    if "quiz" in st.session_state:

        # refresh timer only if quiz not submitted
        if not st.session_state.get("submitted", False):
            st_autorefresh(interval=1000, key="timer")

        elapsed = time.time() - st.session_state.start_time
        remaining = int(st.session_state.quiz_time - elapsed)

        minutes = remaining // 60
        seconds = remaining % 60

        # -------------------------
        # TIMER DISPLAY
        # -------------------------

        if remaining <= 0:
            st.warning("⏰ Time is up!")

        elif remaining <= warning_time:
            st.error(f"⏰ Hurry! Time Remaining: {minutes:02d}:{seconds:02d}")
            st.error("⚠ Final seconds! Submit soon.")

        else:
            st.info(f"⏳ Time Remaining: {minutes:02d}:{seconds:02d}")

        progress = max(remaining / st.session_state.quiz_time, 0)
        st.progress(progress)

        st.subheader("Answer the following questions")

        for i, q in enumerate(st.session_state.quiz):

            st.write(f"**Q{i+1}. {q['question']}**")

            user_answer = st.radio(
                "Choose an option:",
                q["options"],
                key=f"q{i}",
                index=None
            )

            st.session_state.answers[i] = user_answer

        # -------------------------
        # SUBMIT LOGIC
        # -------------------------

        if "submitted" not in st.session_state:
            st.session_state.submitted = False

        submit = st.button(
            "Submit Quiz",
            key="submit_quiz",
            disabled=st.session_state.submitted
        )

        if submit:
            st.session_state.submitted = True

        # auto submit when time ends
        if remaining <= 0:
            st.session_state.submitted = True

        if st.session_state.submitted:

            if None in st.session_state.answers.values():
                st.warning("Please answer all questions before submitting.")

            else:

                score = 0
                total = len(st.session_state.quiz)

                for i, q in enumerate(st.session_state.quiz):
                    if st.session_state.answers[i] == q["answer"]:
                        score += 1

                st.success(f"Your Score: {score} / {total}")

                username = st.session_state.user if st.session_state.user else "Guest User"
                if st.session_state.user:
                    file_path = generate_pdf(
                        st.session_state.user,
                        topic,
                        difficulty,
                        score,
                        total
                    )

                    with open(file_path, "rb") as file:
                        st.download_button(
                            label="📄 Download Quiz Report",
                            data=file,
                            file_name="quiz_report.pdf",
                            mime="application/pdf"
                        )
                else:
                    st.warning("🔒 Login to download your quiz certificate")
                
                if st.session_state.user:
                    file_path = generate_certificate(
                        st.session_state.user,
                        topic,
                        score,
                        total
                    )

                    with open(file_path, "rb") as file:
                        st.download_button(
                            label="🏅 Download Certificate",
                            data=file,
                            file_name="quiz_certificate.pdf",
                            mime="application/pdf"
                        )

                else:
                    st.warning("🔒 Login to download your quiz certificate")

                save_result(
                    st.session_state.user,
                    topic,
                    difficulty,
                    score,
                    total
                )

                st.subheader("Quiz Review")

                for i, q in enumerate(st.session_state.quiz):

                    st.write(f"**Q{i+1}. {q['question']}**")

                    user_answer = st.session_state.answers.get(i)
                    correct_answer = q["answer"]

                    st.write(f"Your answer: {user_answer}")

                    if user_answer == correct_answer:
                        st.success("Correct ✅")
                    else:
                        st.error(f"Incorrect ❌ | Correct answer: {correct_answer}")

                    st.info(f"Explanation: {q['explanation']}")

        # -------------------------
        # RESET QUIZ
        # -------------------------

        if st.button("🔄 Start New Quiz"):

            for key in ["quiz", "answers", "start_time", "quiz_time", "submitted"]:
                if key in st.session_state:
                    del st.session_state[key]

            st.rerun()

# =========================
# HISTORY TAB
# =========================

with history_tab:

    st.header("📊 Your Quiz History")

    results = get_results(st.session_state.user)

    if results:

        df = pd.DataFrame(
            results,
            columns=["Topic", "Difficulty", "Score", "Total", "Date"]
        )

        df["Accuracy %"] = (
            (df["Score"] / df["Total"]) * 100
        ).round(2).astype(str) + "%"

        st.dataframe(df)

    else:
        st.write("No quizzes taken yet.")

# =========================
# LEADERBOARD TAB
# =========================

with leaderboard_tab:

    st.subheader("🏆 Leaderboard")

    leaders = get_leaderboard()

    if leaders:
        for i, row in enumerate(leaders, 1):
            username, topic, score, total = row

            if i == 1:
                st.write(f"🥇 {username} — {topic} ({score}/{total})")
            elif i == 2:
                st.write(f"🥈 {username} — {topic} ({score}/{total})")
            elif i == 3:
                st.write(f"🥉 {username} — {topic} ({score}/{total})")
            else:
                st.write(f"{i}. {username} — {topic} ({score}/{total})")
    else:
        st.write("No scores yet.")

st.markdown(
    '<div class="footer">Built with ❤️ using Python, Streamlit and Groq AI</div>',
    unsafe_allow_html=True
)