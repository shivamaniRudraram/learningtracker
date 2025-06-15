import streamlit as st
import pandas as pd
import os
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns

# ---------- CONFIG ----------
DATA_FILE = "data.csv"
TASKS = [
    "Create Swecha GitLab Account",
    "Create Public Profile README",
    "System Setup & Tech Stack",
    "Install Jupyter + Extension in VSCode",
    "Complete Python Modules on LMS",
    "Creating Hugging Face Chat Assistant",
    "Creating Streamlit Application"
]
BADGE_PATH = "✅ Completed"

# ---------- INIT ----------
if not os.path.exists(DATA_FILE):
    df_init = pd.DataFrame(columns=["Swecha Username", "Email", *TASKS, "Submitted At"])
    df_init.to_csv(DATA_FILE, index=False)

def load_data():
    try:
        df = pd.read_csv(DATA_FILE)
    except Exception:
        df = pd.DataFrame(columns=["Swecha Username", "Email", *TASKS, "Submitted At"])
        df.to_csv(DATA_FILE, index=False)
    return df

def save_data(new_entry):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)

def is_all_tasks_completed(entry):
    return all(entry.get(task, "No") == "Yes" for task in TASKS)

# ---------- HEADER ----------
st.markdown(
    """
    <div style='text-align: center; padding: 20px; background-color: #f9f9ff; border-radius: 12px; margin-bottom: 20px;'>
        <h1 style='color: #6c63ff;'>🤖 Vishwam AI Internship 2025</h1>
        <p style='font-size: 1.2em; color: #333;'>Welcome to SoAI Learning Progress Tracker — Track, Improve, and Earn Badges!</p>
    </div>
    """, unsafe_allow_html=True
)

# ---------- IMAGE BANNER ----------
st.markdown(
    """
    <div style="max-width: 800px; margin: auto;">
        <p style="text-align: center; font-size: 16px; color: #555;">Empowering Interns with AI 🔬</p>
    </div>
    """,
    unsafe_allow_html=True
)

# ---------- SIDEBAR MENU ----------
menu = st.sidebar.selectbox("📌 Choose an option", ["📝 Submit Progress", "📊 View All Submissions", "🧼 Admin: Reset"])

# ---------- SUBMIT FORM ----------
if menu == "📝 Submit Progress":
    st.markdown("## ✍️ Submit Your Progress")
    st.markdown("Fill the form below to log your internship progress.")

    with st.form(key='progress_form'):
        swecha_username = st.text_input("👤 Swecha Username")
        email = st.text_input("📧 Email")

        task_completion = {}
        for task in TASKS:
            task_completion[task] = st.selectbox(f"✅ {task}?", ["No", "Yes"])

        submitted = st.form_submit_button("🚀 Submit")

    if submitted:
        if not swecha_username.strip() or not email.strip():
            st.error("❗ Please fill in all fields.")
        else:
            new_entry = {
                "Swecha Username": swecha_username.strip(),
                "Email": email.strip(),
                **task_completion,
                "Submitted At": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            try:
                save_data(new_entry)
                st.success("✅ Progress submitted successfully!")
                if is_all_tasks_completed(task_completion):
                    st.balloons()
                    st.success("🏅 Congrats! You earned the SoAI Onboarding Badge!")
            except Exception as e:
                st.error(f"❌ Error saving data: {e}")

# ---------- VIEW SUBMISSIONS ----------
elif menu == "📊 View All Submissions":
    st.markdown("## 📊 Intern Submissions & Progress Report")
    df = load_data()

    if df.empty:
        st.info("ℹ️ No submissions yet.")
    else:
        df_numeric = df.copy()
        for task in TASKS:
            df_numeric[task] = df_numeric[task].apply(lambda x: 1 if x == "Yes" else 0)

        df["Badge"] = df.apply(lambda row: BADGE_PATH if is_all_tasks_completed(row) else "❌ Incomplete", axis=1)

        search = st.text_input("🔎 Search by Swecha Username")
        if search:
            mask = df["Swecha Username"].str.contains(search, case=False, na=False)
            df = df.loc[mask]
            df_numeric = df_numeric.loc[mask]

        with st.expander("📅 Filter by Submission Date"):
            df["Submitted At"] = pd.to_datetime(df["Submitted At"], errors='coerce')
            if not df["Submitted At"].isnull().all():
                min_date = df["Submitted At"].min().date()
                max_date = df["Submitted At"].max().date()
                selected_range = st.date_input("Select Date Range", [min_date, max_date])
                if len(selected_range) == 2:
                    start, end = selected_range
                    mask = (df["Submitted At"].dt.date >= start) & (df["Submitted At"].dt.date <= end)
                    df = df.loc[mask]
                    df_numeric = df_numeric.loc[mask]

        st.success(f"👥 Total Submissions: {len(df)} | 🏅 Badges Earned: {(df['Badge'] == BADGE_PATH).sum()}")
        st.dataframe(df)
        st.download_button("⬇️ Download CSV", df.to_csv(index=False), "submissions.csv", "text/csv")

        # ---------- Charts ----------
        st.markdown("---")
        st.markdown("### 📊 Visual Analytics")

        st.markdown("#### ✅ Task Completion Count")
        task_completion_counts = df_numeric[TASKS].sum().sort_values(ascending=False)
        st.bar_chart(task_completion_counts)

        st.markdown("#### 🧭 Overall Progress")
        completed_all = df_numeric.apply(lambda row: all(row[task] == 1 for task in TASKS), axis=1)
        completed_counts = completed_all.value_counts()
        labels = ['🎉 Completed All Tasks', '🔧 Incomplete Tasks']
        sizes = [completed_counts.get(True, 0), completed_counts.get(False, 0)]

        if sum(sizes) == 0:
            st.info("No data to display the pie chart.")
        else:
            fig1, ax1 = plt.subplots()
            ax1.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=['#00C853', '#FF6D00'])
            ax1.axis('equal')
            st.pyplot(fig1)

        st.markdown("#### 🌡️ Task Completion Heatmap")
        if not df_numeric.empty:
            df_heatmap = df_numeric[["Swecha Username"] + TASKS].set_index("Swecha Username")
            fig2, ax2 = plt.subplots(figsize=(10, min(0.5 * len(df_heatmap), 15)))
            sns.heatmap(df_heatmap, cmap="YlGnBu", cbar=True, linewidths=0.5, linecolor='gray', ax=ax2)
            st.pyplot(fig2)

# ---------- RESET DATA (Admin Tool) ----------
elif menu == "🧼 Admin: Reset":
    st.warning("⚠️ This will clear all data!")
    if st.button("🔥 Reset Data File"):
        df_init = pd.DataFrame(columns=["Swecha Username", "Email", *TASKS, "Submitted At"])
        df_init.to_csv(DATA_FILE, index=False)
        st.success("✅ Data has been reset.")
