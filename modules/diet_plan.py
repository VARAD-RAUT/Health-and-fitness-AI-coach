"""
diet_plan.py — Page 2: AI Diet Plan
Calls Azure OpenAI GPT-4 to generate a 7-day meal plan, displays it with tabs and cards,
and supports PDF download and email delivery.
"""

import json
import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.azure_config import get_openai_client, get_deployment_name
from utils.datalake_helper import write_gold_diet_plan


SYSTEM_PROMPT = (
    "You are a certified nutritionist. Create a detailed 7-day meal plan with breakfast, "
    "lunch, dinner and 2 snacks per day. Include calories and macros (protein, carbs, fats) "
    "for each meal. Format as structured JSON with this schema: "
    '{"days": {"Day 1": {"Breakfast": {"items": "...", "calories": 400, "protein_g": 20, "carbs_g": 50, "fats_g": 10}, '
    '"Lunch": {...}, "Dinner": {...}, "Snack 1": {...}, "Snack 2": {...}}, "Day 2": {...}, ...}}'
)

MEAL_ICONS = {
    "Breakfast": "🌅",
    "Lunch": "🍽️",
    "Dinner": "🌙",
    "Snack 1": "🍎",
    "Snack 2": "🥜",
}


def _generate_diet_plan(profile: dict) -> dict | None:
    """Call Azure OpenAI to generate a 7-day diet plan JSON from the user profile."""
    try:
        client = get_openai_client()
        deployment = get_deployment_name()

        user_msg = (
            f"User Profile:\n"
            f"- Age: {profile.get('age')}, Gender: {profile.get('gender')}\n"
            f"- Weight: {profile.get('weight')} kg, Height: {profile.get('height')} cm\n"
            f"- Goal: {profile.get('goal')}\n"
            f"- Dietary Preference: {profile.get('diet_preference')}\n"
            f"- Activity Level: {profile.get('activity_level')}\n"
            f"- Daily Calorie Target: {profile.get('daily_calories', 2000)} kcal\n"
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


def _render_day_tab(day_name: str, meals: dict, daily_cal_target: int):
    """Render a single day's meals as styled cards."""
    total_calories = sum(
        m.get("calories", 0) for m in meals.values() if isinstance(m, dict)
    )
    pct = min(int((total_calories / daily_cal_target) * 100), 100) if daily_cal_target else 0

    st.markdown(f"""
    <div style="display:flex; align-items:center; gap:12px; margin-bottom:12px;">
        <span style="color:#aaaaaa; font-size:14px;">Daily Calories: <b style="color:#fff;">{total_calories} kcal</b></span>
        <span style="color:#aaaaaa; font-size:14px;">Target: <b style="color:#00d4ff;">{daily_cal_target} kcal</b></span>
    </div>
    """, unsafe_allow_html=True)

    # Calorie progress bar
    st.progress(pct / 100, text=f"{pct}% of daily target")

    # Meal cards in columns
    cols = st.columns(2)
    for idx, (meal_name, meal_info) in enumerate(meals.items()):
        if not isinstance(meal_info, dict):
            continue
        icon = MEAL_ICONS.get(meal_name, "🍴")
        with cols[idx % 2]:
            st.markdown(f"""
            <div class="glass-card" style="margin-bottom:12px;">
                <div style="font-size:18px; font-weight:700; color:#00ff88; margin-bottom:8px;">
                    {icon} {meal_name}
                </div>
                <div style="color:#e0e0e0; font-size:14px; margin-bottom:10px;">
                    {meal_info.get("items", meal_info.get("food_items", "N/A"))}
                </div>
                <div style="display:flex; gap:10px; flex-wrap:wrap;">
                    <span class="macro-badge" style="background:rgba(239,68,68,0.2);border:1px solid #ef4444;color:#ef4444;">
                        🔥 {meal_info.get("calories", 0)} kcal
                    </span>
                    <span class="macro-badge" style="background:rgba(59,130,246,0.2);border:1px solid #3b82f6;color:#3b82f6;">
                        💪 P: {meal_info.get("protein_g", meal_info.get("protein", 0))}g
                    </span>
                    <span class="macro-badge" style="background:rgba(245,158,11,0.2);border:1px solid #f59e0b;color:#f59e0b;">
                        🌾 C: {meal_info.get("carbs_g", meal_info.get("carbs", 0))}g
                    </span>
                    <span class="macro-badge" style="background:rgba(168,85,247,0.2);border:1px solid #a855f7;color:#a855f7;">
                        🥑 F: {meal_info.get("fats_g", meal_info.get("fats", 0))}g
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)


def show_diet_plan_page():
    """Render the AI Diet Plan page."""
    st.markdown("""
    <div class="hero-banner">
        <h2>🥗 AI Diet Plan</h2>
        <p>Your personalized 7-day meal plan powered by GPT-4</p>
    </div>
    """, unsafe_allow_html=True)

    profile = st.session_state.get("user_profile") or {}
    if not profile:
        st.warning("⚠️ No profile found. Please complete your profile on the **User Profile** page first.")
        return

    # Summary card
    st.markdown(f"""
    <div class="glass-card" style="display:flex; gap:20px; flex-wrap:wrap; margin-bottom:16px;">
        <div>👤 <b style="color:#00d4ff;">{profile.get("name")}</b></div>
        <div>🎯 <b style="color:#00ff88;">{profile.get("goal")}</b></div>
        <div>🥦 <b style="color:#a855f7;">{profile.get("diet_preference")}</b></div>
        <div>🔥 Target: <b style="color:#f59e0b;">{profile.get("daily_calories", 2000)} kcal/day</b></div>
    </div>
    """, unsafe_allow_html=True)

    # Get current plan
    plan = st.session_state.get("diet_plan") or {}
    
    # Button to generate plan - always visible
    if st.button("✨ Generate 7-Day Diet Plan", use_container_width=True):
        with st.spinner("🤖 GPT-5 is crafting your personalized meal plan..."):
            plan = _generate_diet_plan(profile)
        if plan:
            st.session_state["diet_plan"] = plan
            # Save to Data Lake gold zone
            username_key = profile.get("name", "user").lower().replace(" ", "_")
            write_gold_diet_plan(username_key, datetime.now().strftime("%Y-%m-%d"), plan)
            st.success("✅ Diet plan generated and saved!")
            st.rerun()
        else:
            st.error("❌ Failed to generate plan. Check your Azure OpenAI credentials.")

    # Display plan if it exists
    if not plan:
        st.info("💡 Click the button above to generate your personalized 7-day meal plan!")
    else:
        days = plan.get("days", {})
        if not days:
            st.warning("⚠️ Plan data incomplete. Try regenerating.")
        else:
            st.markdown("### 📅 Your 7-Day Meal Plan")
            day_tabs = st.tabs([f"📅 {d}" for d in days.keys()])
            daily_cal = profile.get("daily_calories", 2000)
            for tab, (day_name, meals) in zip(day_tabs, days.items()):
                with tab:
                    _render_day_tab(day_name, meals, daily_cal)

            st.markdown("---")
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                if st.button("🔄 Regenerate Plan", use_container_width=True):
                    st.session_state["diet_plan"] = None
                    st.rerun()
            with col2:
                # PDF Download
                try:
                    from modules.pdf_generator import generate_diet_plan_pdf
                    pdf_bytes = generate_diet_plan_pdf(profile, plan)
                    st.download_button(
                        "⬇️ Download PDF",
                        data=pdf_bytes,
                        file_name=f"diet_plan_{profile.get('name', 'user').replace(' ', '_')}.pdf",
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
                                from modules.pdf_generator import generate_diet_plan_pdf
                                from modules.email_sender import send_plan_email
                                pdf_bytes = generate_diet_plan_pdf(profile, plan)
                                ok = send_plan_email(email, profile.get("name", "User"), "Diet", pdf_bytes)
                                if ok:
                                    st.success(f"✅ Plan emailed to {email}!")
                                else:
                                    st.error("❌ Email sending failed.")
                            except Exception as e:
                                st.error(f"Email error: {e}")
