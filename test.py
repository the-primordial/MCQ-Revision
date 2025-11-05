import streamlit as st
import pandas as pd
import os
import random

DATA_FILE = "questions.csv"

# ------------------------------
# DATA MANAGEMENT
# ------------------------------
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    else:
        return pd.DataFrame(columns=["Subject", "Chapter", "Question", "A", "B", "C", "D", "Answer"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)


# ------------------------------
# INITIAL SETUP
# ------------------------------
if "menu" not in st.session_state:
    st.session_state.menu = "main"
if "sub_menu" not in st.session_state:
    st.session_state.sub_menu = None
if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None
if "current_q" not in st.session_state:
    st.session_state.current_q = 0
if "answers" not in st.session_state:
    st.session_state.answers = {}
if "quiz_started" not in st.session_state:
    st.session_state.quiz_started = False

st.set_page_config(page_title="Smart MCQ Builder", page_icon="🧠", layout="centered")


# ------------------------------
# MAIN MENU
# ------------------------------
if st.session_state.menu == "main":
    st.subheader("Main Menu")

    if st.button("✏️ Modify Questions"):
        st.session_state.menu = "modify"
        st.rerun()

    if st.button("🧪 Attempt Quiz"):
        st.session_state.menu = "quiz"
        st.rerun()

# ------------------------------
# MODIFY QUESTIONS SECTION (IMPROVED NAVIGATION)
# ------------------------------
elif st.session_state.menu == "modify":
    st.subheader("✏️ Modify Questions")

    data = load_data()

    # --- State tracking ---
    if "selected_subject" not in st.session_state:
        st.session_state.selected_subject = None
    if "selected_chapter" not in st.session_state:
        st.session_state.selected_chapter = None
    if "edit_mode" not in st.session_state:
        st.session_state.edit_mode = None

    # --- Subject Selection ---
    if st.session_state.selected_subject is None:
        st.markdown("### 📘 Select a Subject")
        subjects = sorted(data["Subject"].unique().tolist())

        for sub in subjects:
            if st.button(f"📗 {sub}", key=f"sub_{sub}"):
                st.session_state.selected_subject = sub
                st.rerun()

        st.markdown("---")
        new_subject = st.text_input("➕ Add New Subject:")
        if st.button("Add Subject") and new_subject.strip():
            st.session_state.selected_subject = new_subject.strip()
            st.rerun()

        if st.button("⬅️ Back to Main Menu"):
            st.session_state.menu = "main"
            st.rerun()

    # --- Chapter Selection ---
    elif st.session_state.selected_chapter is None:
        st.markdown(f"### 📘 Subject: {st.session_state.selected_subject}")
        chapters = sorted(data[data["Subject"] == st.session_state.selected_subject]["Chapter"].unique().tolist())

        for chap in chapters:
            if st.button(f"📙 {chap}", key=f"chap_{chap}"):
                st.session_state.selected_chapter = chap
                st.rerun()

        st.markdown("---")
        new_chapter = st.text_input("➕ Add New Chapter:")
        if st.button("Add Chapter") and new_chapter.strip():
            st.session_state.selected_chapter = new_chapter.strip()
            st.rerun()

        if st.button("⬅️ Back to Subjects"):
            st.session_state.selected_subject = None
            st.rerun()

    # --- Question List + Add/Edit/Delete ---
    else:
        subject = st.session_state.selected_subject
        chapter = st.session_state.selected_chapter
        st.markdown(f"### 📘 {subject} → 📙 {chapter}")

        chapter_data = data[(data["Subject"] == subject) & (data["Chapter"] == chapter)]

        st.markdown("#### ✳️ Add New Question")
        q_text = st.text_area("Question:")
        optA = st.text_input("Option A:")
        optB = st.text_input("Option B:")
        optC = st.text_input("Option C:")
        optD = st.text_input("Option D:")
        answer = st.selectbox("Correct Answer:", ["A", "B", "C", "D"])

        if st.button("➕ Add Question"):
            if q_text.strip() and optA and optB and optC and optD:
                new_row = {
                    "Subject": subject,
                    "Chapter": chapter,
                    "Question": q_text.strip(),
                    "OptionA": optA.strip(),
                    "OptionB": optB.strip(),
                    "OptionC": optC.strip(),
                    "OptionD": optD.strip(),
                    "Answer": answer,
                }
                data = data._append(new_row, ignore_index=True)
                save_data(data)
                st.success("✅ Question added successfully!")
                st.rerun()
            else:
                st.warning("Please fill all fields before adding.")

        st.markdown("---")
        st.markdown("#### 🧾 Existing Questions")

        if chapter_data.empty:
            st.info("No questions added yet.")
        else:
            for idx, row in chapter_data.iterrows():
                with st.expander(f"Q{idx+1}: {row['Question']}"):
                    st.write(f"**A)** {row['OptionA']}")
                    st.write(f"**B)** {row['OptionB']}")
                    st.write(f"**C)** {row['OptionC']}")
                    st.write(f"**D)** {row['OptionD']}")
                    st.write(f"✅ **Correct Answer:** {row['Answer']}")
                    col1, col2 = st.columns([1, 1])
                    with col1:
                        if st.button(f"🗑️ Delete Q{idx+1}", key=f"del_{idx}"):
                            data.drop(index=idx, inplace=True)
                            save_data(data)
                            st.warning("Question deleted.")
                            st.rerun()
                    with col2:
                        if st.button(f"✏️ Edit Q{idx+1}", key=f"edit_{idx}"):
                            st.session_state.edit_mode = idx
                            st.rerun()

        # --- Edit mode ---
        if st.session_state.edit_mode is not None:
            idx = st.session_state.edit_mode
            row = data.loc[idx]
            st.markdown("### ✏️ Edit Question")
            new_q = st.text_area("Question:", row["Question"])
            new_A = st.text_input("Option A:", row["OptionA"])
            new_B = st.text_input("Option B:", row["OptionB"])
            new_C = st.text_input("Option C:", row["OptionC"])
            new_D = st.text_input("Option D:", row["OptionD"])
            new_ans = st.selectbox("Correct Answer:", ["A", "B", "C", "D"], index=["A","B","C","D"].index(row["Answer"]))

            if st.button("💾 Save Changes"):
                data.loc[idx, ["Question", "OptionA", "OptionB", "OptionC", "OptionD", "Answer"]] = [
                    new_q, new_A, new_B, new_C, new_D, new_ans
                ]
                save_data(data)
                st.success("✅ Changes saved!")
                st.session_state.edit_mode = None
                st.rerun()

        st.markdown("---")
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("⬅️ Back to Chapters"):
                st.session_state.selected_chapter = None
                st.rerun()
        with col2:
            if st.button("🏠 Back to Main Menu"):
                st.session_state.selected_subject = None
                st.session_state.selected_chapter = None
                st.session_state.menu = "main"
                st.rerun()
# ------------------------------
# ATTEMPT QUIZ SECTION (IMPROVED UI)
# ------------------------------
elif st.session_state.menu == "quiz":
    st.subheader("🧪 Attempt Quiz")

    data = load_data()
    subjects = sorted(data["Subject"].unique().tolist())

    if not subjects:
        st.warning("No subjects found. Please add some questions first.")
        if st.button("⬅️ Back to Main Menu"):
            st.session_state.menu = "main"
            st.rerun()
    else:
        # Select subject & chapter
        subject = st.selectbox("Select Subject:", subjects)
        chapters = sorted(data[data["Subject"] == subject]["Chapter"].unique().tolist())
        chapter = st.selectbox("Select Chapter:", chapters)

        chapter_data = data[(data["Subject"] == subject) & (data["Chapter"] == chapter)]
        total_questions = len(chapter_data)

        if total_questions > 0:
            num_questions = st.number_input(
                f"Select number of questions (1–{total_questions}):",
                min_value=1,
                max_value=total_questions,
                value=min(5, total_questions),
                step=1
            )

            if st.button("▶️ Start Quiz"):
                selected_data = chapter_data.sample(n=num_questions).reset_index(drop=True)
                st.session_state.quiz_data = selected_data
                st.session_state.quiz_started = True
                st.session_state.answers = {}
                st.session_state.current_q = 0
                st.rerun()
        else:
            st.info("No questions available for this chapter.")

        if st.session_state.get("quiz_started", False):
            quiz_data = st.session_state.quiz_data
            total = len(quiz_data)
            q_index = st.session_state.current_q
            q_data = quiz_data.iloc[q_index]

            # --- Progress UI ---
            st.markdown(f"### 📖 {subject} > {chapter}")
            st.write(f"**Question {q_index + 1} of {total}**")
            st.progress((q_index + 1) / total)

            # --- Question display ---
            st.markdown(f"#### {q_data['Question']}")
            options = ["A", "B", "C", "D"]
            prev_answer = st.session_state.answers.get(q_index)
            index = options.index(prev_answer) if prev_answer in options else 0

            choice = st.radio(
                "Your Answer:",
                options,
                index=index,
                key=f"q_{q_index}_radio",
                horizontal=True
            )
            st.session_state.answers[q_index] = choice

            # --- Navigation buttons ---
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                if st.button("⬅️ Previous", disabled=(q_index == 0)):
                    st.session_state.current_q -= 1
                    st.rerun()
            with col3:
                if st.button("➡️ Next", disabled=(q_index == total - 1)):
                    st.session_state.current_q += 1
                    st.rerun()

            # --- Submit button (only on last question) ---
            if q_index == total - 1:
                st.markdown("---")
                if st.button("✅ Submit Quiz"):
                    score = 0
                    for i, row in quiz_data.iterrows():
                        if st.session_state.answers.get(i) == row["Answer"]:
                            score += 1
                    st.success(f"🎯 Your Score: {score}/{total}")
                    st.session_state.quiz_started = False

        if st.button("⬅️ Back to Main Menu"):
            st.session_state.menu = "main"
            st.session_state.quiz_started = False
            st.rerun()
