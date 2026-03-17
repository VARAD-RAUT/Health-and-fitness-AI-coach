"""
workout_plan.py — Page 3: AI Workout Plan
Generates a 7-day personalized workout plan via Azure OpenAI GPT-4.
Displays exercises with sets/reps badges, rest days, PDF/email options.
"""

import json
import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.azure_config import get_openai_client, get_deployment_name
from utils.datalake_helper import write_gold_workout_plan


SYSTEM_PROMPT = (
    "You are a certified personal trainer. Create a 7-day workout plan based on the user's goal, "
    "fitness level and available equipment (bodyweight only). Include exercise name, sets, reps, "
    "rest time and calories burned. Format as structured JSON with this schema: "
    '{"days": {"Day 1": {"focus": "Upper Body", "rest_day": false, "exercises": ['
    '{"name": "Push-Ups", "sets": 3, "reps": "12-15", "rest": "60s", "muscle_group": "Chest", "calories_burned": 50}]}, '
    '"Day 2": {"rest_day": true, "focus": "Rest & Recovery", "exercises": []}, ...}}'
)

MUSCLE_GROUP_COLORS = {
    "Chest": "#ef4444",
    "Back": "#3b82f6",
    "Legs": "#a855f7",
    "Shoulders": "#f59e0b",
    "Arms": "#10b981",
    "Core": "#00d4ff",
    "Full Body": "#00ff88",
    "Cardio": "#f97316",
}


def _get_muscle_color(muscle_group: str) -> str:
    """Return hex color for a muscle group."""
    for key, color in MUSCLE_GROUP_COLORS.items():
        if key.lower() in muscle_group.lower():
            return color
    return "#888888"


def _generate_workout_plan(profile: dict) -> dict | None:
    """Call Azure OpenAI to generate a 7-day workout plan."""
    try:
        client = get_openai_client()
        deployment = get_deployment_name()

        user_msg = (
            f"User Profile:\n"
            f"- Age: {profile.get('age')}, Gender: {profile.get('gender')}\n"
            f"- Weight: {profile.get('weight')} kg, Height: {profile.get('height')} cm\n"
            f"- Goal: {profile.get('goal')}\n"
            f"- Activity Level: {profile.get('activity_level')}\n"
            f"- Health Conditions: {profile.get('health_conditions', 'None')}"
        )

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except Exception as e:
        st.error(f"❌ OpenAI API error: {e}")
        return None


def _render_day_card(day_name: str, day_info: dict):
    """Render a workout day card."""
    is_rest = day_info.get("rest_day", False)
    focus = day_info.get("focus", "Training")
    exercises = day_info.get("exercises", [])

    if is_rest:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:24px;">
            <div style="font-size:48px;">😴</div>
            <div style="font-size:18px; color:#00ff88; font-weight:700; margin:8px 0;">{day_name}</div>
            <div style="color:#aaaaaa;">Rest & Recovery Day</div>
            <div style="color:#cccccc; font-size:13px; margin-top:8px;">
                🚰 Stay hydrated &nbsp;|&nbsp; 🧘 Light stretching &nbsp;|&nbsp; 😴 Sleep 7–9 hours
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        completed = st.session_state.get(f"workout_done_{day_name}", set())
        total = len(exercises)
        done_count = len(completed)
        pct = int((done_count / total) * 100) if total else 0

        st.markdown(f"""
        <div class="glass-card">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
                <div>
                    <div style="font-size:16px; font-weight:700; color:#00ff88;">🏋️ {day_name}</div>
                    <div style="color:#00d4ff; font-size:13px;">{focus}</div>
                </div>
                <div style="color:#aaaaaa; font-size:13px;">{done_count}/{total} exercises</div>
            </div>
        """, unsafe_allow_html=True)

        # Progress bar for workout completion
        st.progress(pct / 100, text=f"{pct}% complete")

        for ex in exercises:
            if not isinstance(ex, dict):
                continue
            ex_name = ex.get("name", "Exercise")
            muscle = ex.get("muscle_group", "")
            muscle_color = _get_muscle_color(muscle)
            ex_done = st.checkbox(
                f"✅ {ex_name}",
                key=f"ex_{day_name}_{ex_name}",
                value=ex_name in completed,
            )
            if ex_done:
                completed.add(ex_name)
            else:
                completed.discard(ex_name)
            st.session_state[f"workout_done_{day_name}"] = completed

            st.markdown(f"""
            <div style="display:flex; flex-wrap:wrap; gap:8px; margin:4px 0 10px 24px;">
                <span class="macro-badge" style="background:rgba(0,255,136,0.15);border:1px solid #00ff88;color:#00ff88;">
                    🔢 {ex.get("sets")} × {ex.get("reps")}
                </span>
                <span class="macro-badge" style="background:rgba(0,212,255,0.15);border:1px solid #00d4ff;color:#00d4ff;">
                    ⏱️ Rest: {ex.get("rest", "60s")}
                </span>
                <span class="macro-badge" style="background:rgba(0,0,0,0.3);border:1px solid {muscle_color};color:{muscle_color};">
                    💪 {muscle}
                </span>
                <span class="macro-badge" style="background:rgba(239,68,68,0.15);border:1px solid #ef4444;color:#ef4444;">
                    🔥 ~{ex.get("calories_burned", 0)} kcal
                </span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)


def show_workout_plan_page():
    """Render the AI Workout Plan page."""
    st.markdown("""
    <div class="hero-banner">
        <h2>🏋️ AI Workout Plan</h2>
        <p>Your personalized 7-day bodyweight training plan powered by GPT-4</p>
    </div>
    """, unsafe_allow_html=True)

    profile = st.session_state.get("user_profile") or {}
    if not profile:
        st.warning("⚠️ Please complete your profile first on the **User Profile** page.")
        return

    st.markdown(f"""
    <div class="glass-card" style="display:flex; gap:20px; flex-wrap:wrap; margin-bottom:16px;">
        <div>👤 <b style="color:#00d4ff;">{profile.get("name")}</b></div>
        <div>🎯 <b style="color:#00ff88;">{profile.get("goal")}</b></div>
        <div>⚡ <b style="color:#f59e0b;">{profile.get("activity_level")}</b></div>
    </div>
    """, unsafe_allow_html=True)

    # Get current plan
    plan = st.session_state.get("workout_plan") or {}
    
    # Button to generate plan - always visible
    if st.button("✨ Generate 7-Day Workout Plan", use_container_width=True):
        with st.spinner("🤖 GPT-5 is designing your workout program..."):
            plan = _generate_workout_plan(profile)
        if plan:
            st.session_state["workout_plan"] = plan
            username_key = profile.get("name", "user").lower().replace(" ", "_")
            write_gold_workout_plan(username_key, datetime.now().strftime("%Y-%m-%d"), plan)
            st.success("✅ Workout plan generated and saved!")
            st.rerun()
        else:
            st.error("❌ Failed to generate plan. Check your Azure OpenAI credentials.")

    # Display plan if it exists
    if not plan:
        st.info("💡 Click the button above to generate your personalized 7-day workout plan!")
    else:
        days = plan.get("days", {})
        if not days:
            st.warning("⚠️ Plan data incomplete. Try regenerating.")
        else:
            st.markdown("### 📅 Your 7-Day Workout Schedule")
            # Display in 2 columns
            day_items = list(days.items())
            for i in range(0, len(day_items), 2):
                c1, c2 = st.columns(2)
                with c1:
                    _render_day_card(day_items[i][0], day_items[i][1])
                if i + 1 < len(day_items):
                    with c2:
                        _render_day_card(day_items[i+1][0], day_items[i+1][1])

            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button("🔄 Regenerate Plan", use_container_width=True):
                    st.session_state["workout_plan"] = None
                    st.rerun()
            with col2:
                try:
                    from modules.pdf_generator import generate_workout_plan_pdf
                    pdf_bytes = generate_workout_plan_pdf(profile, plan)
                    st.download_button(
                        "⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"workout_plan_{profile.get('name', 'user').replace(' ', '_')}.pdf",
                        mime="application/pdf",
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"PDF error: {e}")
            with col3:
                if st.button("📧 Email My Plan", use_container_width=True):
                    email = profile.get("email", "")
                    if not email:
                        st.error("No email in profile.")
                    else:
                        with st.spinner("📤 Sending email..."):
                            try:
                                from modules.pdf_generator import generate_workout_plan_pdf
                                from modules.email_sender import send_plan_email
                                pdf_bytes = generate_workout_plan_pdf(profile, plan)
                                ok = send_plan_email(email, profile.get("name", "User"), "Workout", pdf_bytes)
                                if ok:
                                    st.success(f"✅ Plan emailed to {email}!")
                                else:
                                    st.error("❌ Email sending failed.")
                            except Exception as e:
                                st.error(f"Email error: {e}")
