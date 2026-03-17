"""
daily_log.py — Page 5: Daily Log
Track daily meals and workouts. Shows calorie totals, water intake, and mood.
Saves to Azure Data Lake bronze and silver zones.
"""

import json
import streamlit as st
import sys
import os
from datetime import datetime, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.datalake_helper import write_bronze_daily_log, write_silver_daily_log


MOOD_OPTIONS = {
    "😴 Tired": "tired",
    "😐 Neutral": "neutral",
    "😊 Good": "good",
    "💪 Energized": "energized",
}

WATER_GLASS_EMOJI = "🥤"


def _save_log_to_lake(profile: dict, log_data: dict):
    """Persist daily log to bronze and silver zones in Data Lake."""
    try:
        username_key = profile.get("name", "user").lower().replace(" ", "_")
        date_str = date.today().isoformat()
        write_bronze_daily_log(username_key, date_str, log_data)
        write_silver_daily_log(username_key, date_str, log_data)
    except Exception as e:
        print(f"[_save_log_to_lake] Error: {e}")


def show_daily_log_page():
    """Render the Daily Log page."""
    st.markdown("""
    <div class="hero-banner">
        <h2>📓 Daily Log</h2>
        <p>Track your meals, workouts, water intake and mood for today</p>
    </div>
    """, unsafe_allow_html=True)

    profile = st.session_state.get("user_profile") or {}
    daily_cal_target = profile.get("daily_calories", 2000)
    today_str = datetime.now().strftime("%A, %d %B %Y")

    st.markdown(f"<div style='color:#aaaaaa; margin-bottom:16px;'>📅 {today_str}</div>", unsafe_allow_html=True)

    # ── Initialize session state ────────────────────
    if "daily_meals_log" not in st.session_state:
        st.session_state["daily_meals_log"] = []
    if "daily_water" not in st.session_state:
        st.session_state["daily_water"] = 0
    if "daily_mood" not in st.session_state:
        st.session_state["daily_mood"] = "😊 Good"

    meals_log = st.session_state["daily_meals_log"]

    # ══════════════════════════════════════════════════
    # SECTION 1: MEALS LOG
    # ══════════════════════════════════════════════════
    st.markdown("## 🍽️ Meals Log")
    col_form, col_list = st.columns([1, 2])

    with col_form:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("#### ➕ Add Meal Entry")
        food_desc = st.text_input("Food / Meal Name", placeholder="e.g. Grilled chicken salad")
        meal_cals = st.number_input("Calories (kcal)", min_value=0, max_value=5000, step=10)
        meal_protein = st.number_input("Protein (g)", min_value=0.0, max_value=200.0, step=0.5)
        meal_carbs = st.number_input("Carbs (g)", min_value=0.0, max_value=500.0, step=0.5)
        meal_fats = st.number_input("Fats (g)", min_value=0.0, max_value=200.0, step=0.5)

        if st.button("➕ Add Meal", use_container_width=True):
            if food_desc.strip():
                meals_log.append({
                    "description": food_desc.strip(),
                    "calories": meal_cals,
                    "protein_g": meal_protein,
                    "carbs_g": meal_carbs,
                    "fats_g": meal_fats,
                    "time": datetime.now().strftime("%H:%M"),
                    "source": "Manual",
                })
                st.session_state["daily_meals_log"] = meals_log
                st.success("✅ Meal added!")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_list:
        if meals_log:
            for idx, entry in enumerate(meals_log):
                col_entry, col_del = st.columns([9, 1])
                with col_entry:
                    src_badge = "📸" if entry.get("source") == "Food Analyzer" else "✏️"
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center;
                                padding:10px 14px; margin:4px 0; background:rgba(255,255,255,0.04);
                                border-radius:10px; border-left:3px solid #00ff88;">
                        <span style="color:#e0e0e0;">{src_badge} {entry.get('description', '')}</span>
                        <span style="color:#aaaaaa; font-size:12px;">{entry.get('time', '')}</span>
                        <span style="color:#00ff88; font-weight:600;">{entry.get('calories', 0)} kcal</span>
                    </div>
                    """, unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑️", key=f"del_meal_{idx}"):
                        meals_log.pop(idx)
                        st.session_state["daily_meals_log"] = meals_log
                        st.rerun()
        else:
            st.markdown("""
            <div style="text-align:center; color:#555; padding:30px;">
                No meals logged yet. Add your first meal! 🍽️
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════
    # SECTION 2: WORKOUT LOG
    # ══════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("## 🏋️ Workout Log")

    workout_plan = st.session_state.get("workout_plan", {})
    today_weekday = datetime.now().strftime("%A")
    day_map = {
        "Monday": "Day 1", "Tuesday": "Day 2", "Wednesday": "Day 3",
        "Thursday": "Day 4", "Friday": "Day 5", "Saturday": "Day 6", "Sunday": "Day 7"
    }
    day_key = day_map.get(today_weekday, "Day 1")
    days = workout_plan.get("days", {})
    today_workout = days.get(day_key, {})

    if today_workout and not today_workout.get("rest_day"):
        exercises = today_workout.get("exercises", [])
        completed_set = st.session_state.get("workout_completed_today", set())
        st.markdown(f"**Today's plan: {today_workout.get('focus', 'Training')}**")

        total_cals_burned = 0
        for ex in exercises:
            if not isinstance(ex, dict):
                continue
            ex_name = ex.get("name", "Exercise")
            done = st.checkbox(
                f"✅ {ex_name}  — {ex.get('sets')}×{ex.get('reps')}  |  ⏱️ {ex.get('rest', '60s')}  |  🔥 ~{ex.get('calories_burned', 0)} kcal",
                key=f"log_ex_{ex_name}",
                value=ex_name in completed_set,
            )
            if done:
                completed_set.add(ex_name)
                total_cals_burned += ex.get("calories_burned", 0)
            else:
                completed_set.discard(ex_name)
        st.session_state["workout_completed_today"] = completed_set
        st.session_state["calories_burned_today"] = total_cals_burned
    elif today_workout.get("rest_day"):
        st.info("😴 Today is your planned Rest Day. Focus on recovery!")
    else:
        st.info("💡 No workout plan found. Generate one on the **Workout Plan** page.")

    # ══════════════════════════════════════════════════
    # SECTION 3: DAILY SUMMARY
    # ══════════════════════════════════════════════════
    st.markdown("---")
    st.markdown("## 📊 Daily Summary")

    total_consumed = sum(m.get("calories", 0) for m in meals_log)
    cal_burned = st.session_state.get("calories_burned_today", 0)
    net_calories = total_consumed - cal_burned
    goal_pct = min(int((total_consumed / daily_cal_target) * 100), 100) if daily_cal_target else 0

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div style="color:#aaaaaa; font-size:13px;">🔥 Calories Consumed</div>
            <div style="font-size:36px; font-weight:800; color:#ef4444;">{total_consumed}</div>
            <div style="color:#888; font-size:12px;">of {daily_cal_target} kcal target</div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div style="color:#aaaaaa; font-size:13px;">💪 Calories Burned</div>
            <div style="font-size:36px; font-weight:800; color:#00ff88;">{cal_burned}</div>
            <div style="color:#888; font-size:12px;">from tracked exercises</div>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        net_color = "#00ff88" if net_calories <= daily_cal_target else "#ef4444"
        st.markdown(f"""
        <div class="glass-card" style="text-align:center;">
            <div style="color:#aaaaaa; font-size:13px;">⚖️ Net Calories</div>
            <div style="font-size:36px; font-weight:800; color:{net_color};">{net_calories}</div>
            <div style="color:#888; font-size:12px;">consumed – burned</div>
        </div>
        """, unsafe_allow_html=True)

    # Calorie goal progress ring (via progress bar)
    st.markdown(f"**📈 Daily Calorie Goal Progress: {goal_pct}%**")
    st.progress(goal_pct / 100)

    # Water tracker
    st.markdown("---")
    st.markdown("#### 💧 Water Intake Tracker")
    water_col1, water_col2 = st.columns([3, 1])
    with water_col1:
        water_glasses = st.slider(
            "Glasses of water (250ml each)",
            min_value=0,
            max_value=15,
            value=st.session_state["daily_water"],
            step=1,
        )
        st.session_state["daily_water"] = water_glasses
        water_display = WATER_GLASS_EMOJI * water_glasses + ("⬜" * (8 - min(water_glasses, 8)))
        st.markdown(f"<div style='font-size:24px; margin-top:8px;'>{water_display}</div>", unsafe_allow_html=True)
        st.caption(f"{water_glasses} / 8 recommended glasses")
    with water_col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:16px;">
            <div style="font-size:32px;">{water_glasses * 250}ml</div>
            <div style="color:#aaaaaa; font-size:12px;">total today</div>
        </div>
        """, unsafe_allow_html=True)

    # Mood selector
    st.markdown("---")
    st.markdown("#### 😊 How are you feeling today?")
    mood = st.radio(
        "Mood",
        list(MOOD_OPTIONS.keys()),
        index=list(MOOD_OPTIONS.keys()).index(st.session_state["daily_mood"]),
        horizontal=True,
        label_visibility="collapsed",
    )
    st.session_state["daily_mood"] = mood

    # Save button
    st.markdown("<br/>", unsafe_allow_html=True)
    if st.button("💾 Save Today's Log to Azure", use_container_width=True):
        log_data = {
            "date": date.today().isoformat(),
            "meals": meals_log,
            "calories_consumed": total_consumed,
            "calories_burned": cal_burned,
            "net_calories": net_calories,
            "water_glasses": water_glasses,
            "mood": MOOD_OPTIONS.get(mood, "good"),
            "goal_pct": goal_pct,
        }
        if profile:
            with st.spinner("☁️ Saving to Azure Data Lake..."):
                _save_log_to_lake(profile, log_data)
            st.success("✅ Daily log saved to Azure Data Lake!")
        else:
            st.info("💡 Set up your profile first to save logs to Azure.")
