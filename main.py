import streamlit as st
from src.agents.router_agent import run_router
from src.agents.coach_agent import run_coach_agent_with_tools
from src.agents.game_plan_agent import run_game_plan_agent
from src.agents.injury_agent import run_injury_agent
from src.database import (
    save_student_profile,
    view_all_rows,
)
from src.user_guide import USER_GUIDE_CONTENT

st.set_page_config(page_title="BJJ AI Agents", layout="wide")
st.title("🥋 BJJ AI Agents System")

# --- Sidebar: User Guide ---
with st.sidebar:
    st.markdown("## 📖 User Guide & Help")
    st.markdown(USER_GUIDE_CONTENT)

# --- Session State Initialization ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "profile" not in st.session_state:
    st.session_state.profile = {}

# --- Tabs ---
tabs = st.tabs(
    [
        "🤖 Enhanced AI Chat",
        "👤 Student Profile",
        "👨‍🏫 Coach Chat",
        "📋 Game Plan Generator",
        "📈 Progress Tracking",
        "🗃️ Database Viewer",
        "🥋 Training Examples",
        "📚 Resources",
    ]
)

# --- Enhanced AI Chat Tab ---
with tabs[0]:
    st.subheader("💬 Enhanced AI Chat with Agent Routing")
    st.markdown(
        "The AI will automatically route your query to the best agent (Coach, Game Plan, or Injury)."
    )
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state.chat_history:
            if msg["role"] == "user":
                st.markdown(f"**You:** {msg['content']}")
            else:
                st.markdown(f"**AI:** {msg['content']}")
        user_input = st.text_input(
            "Type your message and press Enter", key="ai_chat_input"
        )
        if st.button("Send", key="ai_chat_send") and user_input.strip():
            st.session_state.chat_history.append(
                {"role": "user", "content": user_input}
            )
            # Route to the correct agent
            agent_response = run_router(user_input)
            st.session_state.chat_history.append(
                {"role": "assistant", "content": agent_response}
            )
            st.experimental_rerun()

# --- Student Profile Tab ---
with tabs[1]:
    st.subheader("📝 Manage Your Profile")
    with st.form("profile_form"):
        name = st.text_input("Name", value=st.session_state.profile.get("name", ""))
        age = st.number_input(
            "Age",
            min_value=5,
            max_value=100,
            value=st.session_state.profile.get("age", 18),
        )
        weight = st.number_input(
            "Weight (lbs)",
            min_value=50,
            max_value=400,
            value=st.session_state.profile.get("weight", 150),
        )
        belt = st.selectbox(
            "Belt Color", ["White", "Blue", "Purple", "Brown", "Black"], index=0
        )
        gender = st.selectbox("Gender", ["Male", "Female"], index=0)
        no_gi_level = st.selectbox(
            "No-Gi Level", ["Beginner", "Intermediate", "Advanced"], index=0
        )
        submitted = st.form_submit_button("Save Profile")
        if submitted:
            profile = {
                "name": name,
                "age": age,
                "weight": int(round(weight)),
                "belt_color": belt,
                "gender": gender,
                "no_gi_level": no_gi_level,
            }
            st.session_state.profile = profile
            save_student_profile(profile)
            st.success("Profile saved!")

# --- Coach Chat Tab ---
with tabs[2]:
    st.subheader("💬 Chat with a Virtual BJJ Coach")
    coach_input = st.text_area("Ask your coach anything...")
    if st.button("Ask Coach") and coach_input.strip():
        response = run_coach_agent_with_tools(coach_input)
        st.markdown(f"**Coach:** {response}")

# --- Game Plan Generator Tab ---
with tabs[3]:
    st.subheader("🏆 Generate a Competition Game Plan")
    game_plan_input = st.text_area(
        "Enter tournament details, your style, opponent's style, etc."
    )
    if st.button("Generate Game Plan") and game_plan_input.strip():
        response = run_game_plan_agent(game_plan_input)
        st.markdown(f"**Game Plan:** {response}")

# --- Progress Tracking Tab ---
with tabs[4]:
    st.subheader("📊 Track Your BJJ Progress")
    with st.form("progress_form"):
        technique = st.text_input("Technique", "")
        level = st.selectbox(
            "Proficiency Level", ["Learning", "Practicing", "Mastered"]
        )
        no_gi_level = st.selectbox(
            "No-Gi Level", ["Beginner", "Intermediate", "Advanced"], index=0
        )
        notes = st.text_area("Notes", "")
        submitted = st.form_submit_button("Track Progress")
        if submitted:
            # You can implement saving to DB here
            st.success(f"Progress tracked for {technique} at {level} level.")

# --- Database Viewer Tab ---
with tabs[5]:
    st.subheader("🔍 View Database Tables")
    table = st.selectbox(
        "Select Table", ["students", "progress_tracking", "game_plans"]
    )
    if st.button("View Table"):
        data = view_all_rows(table)
        st.dataframe(data)

# --- Training Examples Tab ---
with tabs[6]:
    st.subheader("💡 Generate Training Scenarios")
    if st.button("Generate Examples"):
        # You can implement example generation here
        st.info("Example generation not yet implemented.")

# --- Resources Tab ---
with tabs[7]:
    st.subheader("📚 External Resources")
    st.text_area("YouTube Channels", "")
    st.text_area("Blog Articles", "")
    st.button("Save Resources")
    st.markdown(
        "### Future functionality: Web scraping and JSON management will be implemented here."
    )
