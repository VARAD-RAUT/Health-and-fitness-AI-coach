"""
app.py — Main Streamlit entry point for the AI Health & Fitness Assistant.
Provides the dark-themed UI, sidebar navigation, CSS injection, and routes
to all 7 feature pages.
"""

import streamlit as st
import os
import sys

# Ensure project root is on the path for all module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

# ─────────────────────────────────────────────
# Page configuration (MUST be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AI Health & Fitness Assistant",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
)

# All custom CSS removed - using default Streamlit theme


# ─────────────────────────────────────────────
# Session state initialisation
# ─────────────────────────────────────────────
def _init_session_state():
    """Initialise all required session state keys with defaults."""
    defaults = {
        "user_profile": None,
        "diet_plan": None,
        "workout_plan": None,
        "last_food_analysis": None,
        "daily_meals_log": [],
        "daily_water": 0,
        "daily_mood": "😊 Good",
        "chat_history": [],
        "calories_burned_today": 0,
        "current_page": "👤 User Profile",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


_init_session_state()


# ─────────────────────────────────────────────
# Profile Loading Helper
# ─────────────────────────────────────────────
def _load_profile_by_username(username: str) -> dict | None:
    """Attempt to load a saved profile from Azure Blob Storage."""
    try:
        from utils.blob_helper import load_profile
        profile = load_profile(username.lower().replace(" ", "_"))
        if profile:
            st.session_state["user_profile"] = profile
            return profile
    except Exception as e:
        # Silently fail — Azure storage may not be configured
        pass
    return None


# ─────────────────────────────────────────────
# Sidebar
# ─────────────────────────────────────────────
def _render_sidebar():
    """Render the sidebar with navigation and user badge."""
    with st.sidebar:
        # Logo / App Title
        st.markdown("""
        <div class="sidebar-logo">
            <div style="font-size:40px;">💪</div>
            <div class="sidebar-title">AI Health Assistant</div>
            <div class="sidebar-subtitle">Powered by Azure OpenAI GPT-5</div>
        </div>
        """, unsafe_allow_html=True)

        # User badge (shows only when profile exists)
        profile = st.session_state.get("user_profile")
        if profile:
            avatar = profile.get("avatar", "🏋️")
            name = profile.get("name", "User")
            goal = profile.get("goal", "Fitness")
            st.markdown(f"""
            <div class="user-badge">
                <div class="avatar">{avatar}</div>
                <div class="user-name">{name}</div>
                <div class="goal-chip">{goal}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="text-align:center; color:#555; font-size:13px; margin:12px 0;">
                👆 Set up your profile to get started
            </div>
            """, unsafe_allow_html=True)

        # Profile Loading
        with st.expander("📂 Load Saved Profile", expanded=False):
            try:
                from utils.blob_helper import list_saved_profiles
                saved_profiles = list_saved_profiles()
                
                if saved_profiles:
                    selected_profile = st.selectbox(
                        "Select Profile",
                        saved_profiles,
                        key="load_profile_select",
                        label_visibility="collapsed"
                    )
                    if st.button("🔄 Load", use_container_width=True):
                        loaded = _load_profile_by_username(selected_profile)
                        if loaded:
                            st.success("✅ Profile loaded!")
                            st.rerun()
                        else:
                            st.info("ℹ️ Profile not found or Azure storage unavailable.")
                else:
                    st.info("ℹ️ No saved profiles found. Save a profile first!")
            except Exception as e:
                st.info("ℹ️ Unable to fetch saved profiles (Azure storage unavailable).")

        st.markdown("---")
        st.markdown("<div style='color:#555; font-size:11px; margin-bottom:8px;'>NAVIGATION</div>", unsafe_allow_html=True)

        pages = [
            ("👤 User Profile", "Profile"),
            ("🥗 AI Diet Plan", "Diet Plan"),
            ("🏋️ AI Workout Plan", "Workout Plan"),
            ("📸 Food Analyzer", "Food Analyzer"),
            ("📓 Daily Log", "Daily Log"),
            ("📊 Weekly Report", "Weekly Report"),
            ("💬 Chat with AI", "Chat"),
        ]

        for label, _ in pages:
            if st.button(label, key=f"nav_{label}"):
                st.session_state["current_page"] = label

        st.markdown("---")
        st.markdown("""
        <div style="text-align:center; color:#333; font-size:11px; padding:8px 0;">
            Built with Azure OpenAI + Streamlit<br/>
            <span style="color:#00ff88;">💚</span> Stay healthy!
        </div>
        """, unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Chat Page (inline — no separate module needed)
# ─────────────────────────────────────────────
def _show_chat_page():
    """Render the Chat with AI page with history, suggestions, and typing indicator."""
    st.markdown("""
    <div class="hero-banner">
        <h2>💬 Chat with AI Health Coach</h2>
        <p>Ask anything about diet, fitness, nutrition and healthy living</p>
    </div>
    """, unsafe_allow_html=True)

    profile = st.session_state.get("user_profile") or {}

    # Quick suggestion chips
    suggestions = [
        "What should I eat before workout?",
        "How much protein do I need?",
        "Give me a 10 min home workout",
        "Is my BMI healthy?",
    ]
    st.markdown("**💡 Quick Questions:**")
    cols = st.columns(len(suggestions))
    for col, suggestion in zip(cols, suggestions):
        with col:
            if st.button(suggestion, key=f"suggest_{suggestion[:20]}"):
                st.session_state["chat_history"].append({"role": "user", "content": suggestion})
                safe_profile = profile or {}
                _get_ai_response(suggestion, safe_profile)
                st.rerun()

    st.markdown("---")

    # Chat history display
    chat_container = st.container()
    with chat_container:
        for msg in st.session_state["chat_history"]:
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-user">
                    <div class="bubble">{msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-ai">
                    <div class="bubble">🤖 {msg["content"]}</div>
                </div>
                """, unsafe_allow_html=True)

    # Input area
    st.markdown("<br/>", unsafe_allow_html=True)
    col_input, col_send, col_clear = st.columns([7, 1, 1])
    with col_input:
        user_input = st.text_input(
            "Type your message...",
            key="chat_input",
            placeholder="Ask me anything about health, fitness or nutrition...",
            label_visibility="collapsed",
        )
    with col_send:
        send_clicked = st.button("➤ Send", use_container_width=True)
    with col_clear:
        if st.button("🗑️ Clear", use_container_width=True):
            st.session_state["chat_history"] = []
            st.rerun()

    if send_clicked and user_input.strip():
        st.session_state["chat_history"].append({"role": "user", "content": user_input.strip()})
        with st.spinner("🤖 AI is thinking..."):
            safe_profile = profile or {}
            _get_ai_response(user_input.strip(), safe_profile)
        st.rerun()


def _get_ai_response(user_message: str, profile: dict):
    """Call Azure OpenAI and append AI response to chat history."""
    try:
        from config.azure_config import get_openai_client, get_deployment_name

        client = get_openai_client()
        deployment = get_deployment_name()

        system_prompt = (
            "You are a friendly certified nutritionist and personal trainer. "
            "Answer questions about diet, fitness, workouts, nutrition and healthy lifestyle. "
            "Be specific, practical and encouraging. Use the user's profile data to personalize answers."
        )
        # Ensure profile is never None
        profile = profile or {}
        if profile:
            system_prompt += (
                f"\n\nUser Profile: Name={profile.get('name')}, Age={profile.get('age')}, "
                f"Weight={profile.get('weight')}kg, Height={profile.get('height')}cm, "
                f"Goal={profile.get('goal')}, BMI={profile.get('bmi')}, "
                f"Diet={profile.get('diet_preference')}, Activity={profile.get('activity_level')}."
            )

        messages = [{"role": "system", "content": system_prompt}]
        for msg in st.session_state["chat_history"][-10:]:  # Last 10 messages for context
            messages.append({"role": msg["role"], "content": msg["content"]})

        response = client.chat.completions.create(
            model=deployment,
            messages=messages,
            temperature=0.75,
            max_tokens=600,
        )
        ai_reply = response.choices[0].message.content
        st.session_state["chat_history"].append({"role": "assistant", "content": ai_reply})

    except Exception as e:
        st.session_state["chat_history"].append({
            "role": "assistant",
            "content": f"⚠️ Sorry, I ran into an error: {e}. Please check your Azure OpenAI credentials in `.env`.",
        })


# ─────────────────────────────────────────────
# Main App Router
# ─────────────────────────────────────────────
def main():
    """Main entry point — render sidebar and route to the active page."""
    _render_sidebar()

    page = st.session_state.get("current_page", "👤 User Profile")

    # ── App Title ───────────────────────────────
    st.markdown("""
    <h1 style="
        text-align: center;
        font-size: 36px;
        font-weight: 900;
        background: linear-gradient(90deg, #00ff88, #00d4ff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 4px;
        padding-top: 8px;
    ">💪 AI Health & Fitness Assistant</h1>
    <p style="text-align:center; color:#555; font-size:14px; margin-bottom:24px;">
        Personalized nutrition & fitness powered by Azure OpenAI GPT-5
    </p>
    """, unsafe_allow_html=True)

    # Route to the selected page
    try:
        if page == "👤 User Profile":
            from modules.profile import show_profile_page
            show_profile_page()

        elif page == "🥗 AI Diet Plan":
            from modules.diet_plan import show_diet_plan_page
            show_diet_plan_page()

        elif page == "🏋️ AI Workout Plan":
            from modules.workout_plan import show_workout_plan_page
            show_workout_plan_page()

        elif page == "📸 Food Analyzer":
            from modules.food_analyzer import show_food_analyzer_page
            show_food_analyzer_page()

        elif page == "📓 Daily Log":
            from modules.daily_log import show_daily_log_page
            show_daily_log_page()

        elif page == "📊 Weekly Report":
            from modules.weekly_report import show_weekly_report_page
            show_weekly_report_page()

        elif page == "💬 Chat with AI":
            _show_chat_page()

    except Exception as e:
        st.error(f"❌ Page error: {e}")
        st.exception(e)


if __name__ == "__main__":
    main()
