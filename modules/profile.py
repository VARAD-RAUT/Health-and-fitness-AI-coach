"""
profile.py — Page 1: User Profile
Handles user profile form, BMI calculation, saving to Blob Storage and Data Lake.
"""

import json
import streamlit as st
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.blob_helper import save_profile, load_profile
from utils.datalake_helper import write_bronze_profile


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight in kg and height in cm."""
    height_m = height_cm / 100
    return round(weight_kg / (height_m ** 2), 1)


def get_bmi_category(bmi: float) -> tuple[str, str]:
    """Return (category label, hex color) based on BMI value."""
    if bmi < 18.5:
        return "Underweight", "#3b82f6"
    elif bmi < 25.0:
        return "Normal", "#00ff88"
    elif bmi < 30.0:
        return "Overweight", "#f59e0b"
    else:
        return "Obese", "#ef4444"


def get_avatar_emoji(goal: str) -> str:
    """Return an appropriate emoji avatar based on fitness goal."""
    avatars = {
        "Weight Loss": "🏃",
        "Muscle Gain": "💪",
        "Maintain Fitness": "🧘",
    }
    return avatars.get(goal, "🏋️")


def get_daily_calories(weight_kg: float, height_cm: float, age: int, gender: str, activity_level: str, goal: str) -> int:
    """
    Estimate daily calorie target using Mifflin-St Jeor equation
    adjusted for activity level and goal.
    """
    # BMR
    if gender == "Male":
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + 5
    else:
        bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age - 161

    # Activity multipliers
    multipliers = {
        "Sedentary": 1.2,
        "Moderate": 1.55,
        "Very Active": 1.725,
    }
    tdee = bmr * multipliers.get(activity_level, 1.4)

    # Goal adjustments
    if goal == "Weight Loss":
        return int(tdee - 400)
    elif goal == "Muscle Gain":
        return int(tdee + 300)
    return int(tdee)


def show_profile_page():
    """Render the User Profile page."""

    # Hero banner
    st.markdown("""
    <div class="hero-banner">
        <h2>👤 User Profile</h2>
        <p>Set up your personal health profile to get AI-powered recommendations</p>
    </div>
    """, unsafe_allow_html=True)

    # ── Load existing session profile ──────────────────
    existing = st.session_state.get("user_profile") or {}

    with st.form("profile_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name", value=existing.get("name", ""))
            age = st.number_input("Age", min_value=10, max_value=100, value=existing.get("age", 25))
            weight = st.number_input("Weight (kg)", min_value=20.0, max_value=300.0, value=float(existing.get("weight", 70.0)), step=0.5)
            height = st.number_input("Height (cm)", min_value=100.0, max_value=250.0, value=float(existing.get("height", 170.0)), step=0.5)
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], index=["Male", "Female", "Other"].index(existing.get("gender", "Male")))

        with col2:
            goal = st.selectbox(
                "Fitness Goal",
                ["Weight Loss", "Muscle Gain", "Maintain Fitness"],
                index=["Weight Loss", "Muscle Gain", "Maintain Fitness"].index(existing.get("goal", "Weight Loss"))
            )
            diet_pref = st.selectbox(
                "Dietary Preference",
                ["Vegetarian", "Non-Vegetarian", "Vegan"],
                index=["Vegetarian", "Non-Vegetarian", "Vegan"].index(existing.get("diet_preference", "Non-Vegetarian"))
            )
            activity = st.selectbox(
                "Activity Level",
                ["Sedentary", "Moderate", "Very Active"],
                index=["Sedentary", "Moderate", "Very Active"].index(existing.get("activity_level", "Moderate"))
            )
            email = st.text_input("Email Address", value=existing.get("email", ""))

        health_conditions = st.text_area(
            "Health Conditions (optional — e.g. diabetes, hypertension)",
            value=existing.get("health_conditions", ""),
            placeholder="Leave blank if none"
        )

        submitted = st.form_submit_button("💾 Save Profile", use_container_width=True)

    if submitted:
        if not name.strip():
            st.error("⚠️ Please enter your full name.")
            return

        bmi = calculate_bmi(weight, height)
        bmi_category, bmi_color = get_bmi_category(bmi)
        daily_calories = get_daily_calories(weight, height, age, gender, activity, goal)

        profile = {
            "name": name.strip(),
            "age": age,
            "weight": weight,
            "height": height,
            "gender": gender,
            "goal": goal,
            "diet_preference": diet_pref,
            "activity_level": activity,
            "email": email.strip(),
            "health_conditions": health_conditions.strip(),
            "bmi": bmi,
            "bmi_category": bmi_category,
            "daily_calories": daily_calories,
            "avatar": get_avatar_emoji(goal),
        }

        # Save to session state
        st.session_state["user_profile"] = profile

        with st.spinner("☁️ Saving profile to Azure..."):
            username_key = name.strip().lower().replace(" ", "_")
            save_ok = save_profile(username_key, profile)

        # ── BMI Display ────────────────────────────────
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:24px;">
            <h3 style="color:#00d4ff; margin:0 0 8px;">Your BMI Results</h3>
            <div style="font-size:48px; font-weight:700; color:#ffffff;">{bmi}</div>
            <div style="
                display:inline-block;
                padding:6px 20px;
                border-radius:50px;
                background:{bmi_color};
                color:#ffffff;
                font-weight:600;
                font-size:16px;
                margin-top:8px;
            ">{bmi_category}</div>
            <div style="margin-top:16px; color:#aaaaaa;">
                Daily Calorie Target: <span style="color:#00ff88; font-weight:bold;">{daily_calories} kcal</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Storage status
        if save_ok:
            st.success("✅ Profile saved to Azure Blob Storage!")
        else:
            st.info("💡 Profile saved to session only (Azure storage unavailable — check your .env credentials).")

        st.balloons()

    # ── Show current profile if it exists ─────────────
    elif existing:
        bmi = existing.get("bmi", 0)
        bmi_category = existing.get("bmi_category", "Unknown")
        bmi_color = get_bmi_category(bmi)[1] if bmi else "#555"
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:24px;">
            <h3 style="color:#00d4ff; margin:0 0 4px;">Current Profile — {existing.get("name", "")}</h3>
            <p style="color:#aaaaaa; margin:0 0 16px;">BMI: <span style="font-size:28px;font-weight:700;color:#fff;">{bmi}</span>
            &nbsp;<span style="padding:4px 14px;border-radius:50px;background:{bmi_color};color:#fff;font-size:13px;">{bmi_category}</span></p>
            <p style="color:#aaaaaa;">Daily Target: <b style="color:#00ff88;">{existing.get('daily_calories', 'N/A')} kcal</b>
            &nbsp;|&nbsp; Goal: <b style="color:#00d4ff;">{existing.get('goal', 'N/A')}</b></p>
        </div>
        """, unsafe_allow_html=True)
