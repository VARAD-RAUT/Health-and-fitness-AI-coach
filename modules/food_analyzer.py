"""
food_analyzer.py — Page 4: Food Photo Analyzer
Upload a food photo → encode to base64 → send to GPT-5 Vision → display nutrition results.
Saves photo to Blob Storage and analysis to Data Lake silver zone.
"""

import json
import base64
import streamlit as st
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.azure_config import get_openai_client, get_deployment_name
from utils.blob_helper import save_food_image
from utils.datalake_helper import write_silver_food_analysis

VISION_PROMPT = (
    "Analyze this food image. Identify all food items visible, estimate portion sizes, "
    "and calculate approximate calories, protein, carbs and fats. "
    "Return ONLY valid structured JSON with keys: "
    "food_items (array of objects with name and calories), "
    "total_calories (number), protein_g (number), carbs_g (number), fats_g (number), "
    "health_score (number out of 10), health_notes (string)."
)


def _analyze_food_image(image_bytes: bytes) -> dict | None:
    """Send image to GPT-5 Vision and parse the nutrition JSON response."""
    try:
        client = get_openai_client()
        deployment = get_deployment_name()

        b64_image = base64.b64encode(image_bytes).decode("utf-8")

        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_PROMPT},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{b64_image}",
                                "detail": "high",
                            },
                        },
                    ],
                }
            ],
            max_tokens=800,
        )
        raw = response.choices[0].message.content
        # Strip markdown code fences if present
        if "```" in raw:
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw.strip())
    except Exception as e:
        st.error(f"❌ Vision API error: {e}")
        return None


def _health_score_display(score: float):
    """Display a styled health score card."""
    if score >= 8:
        color, label = "#00ff88", "Excellent 🌟"
    elif score >= 6:
        color, label = "#f59e0b", "Good 👍"
    elif score >= 4:
        color, label = "#f97316", "Fair ⚠️"
    else:
        color, label = "#ef4444", "Poor 🚨"

    pct = int((score / 10) * 100)
    st.markdown(f"""
    <div class="glass-card" style="text-align:center; padding:24px;">
        <div style="font-size:14px; color:#aaaaaa; margin-bottom:8px;">Health Score</div>
        <div style="font-size:52px; font-weight:800; color:{color};">{score}</div>
        <div style="font-size:13px; color:#ffffff;">/10</div>
        <div style="margin-top:10px;">
            <div style="background:rgba(255,255,255,0.1); border-radius:50px; height:10px; overflow:hidden;">
                <div style="background:{color}; width:{pct}%; height:100%; border-radius:50px;
                            transition:width 0.8s ease;"></div>
            </div>
        </div>
        <div style="margin-top:8px; color:{color}; font-weight:600;">{label}</div>
    </div>
    """, unsafe_allow_html=True)


def show_food_analyzer_page():
    """Render the Food Photo Analyzer page."""
    st.markdown("""
    <div class="hero-banner">
        <h2>📸 Food Photo Analyzer</h2>
        <p>Upload a food photo and get instant AI-powered nutrition analysis</p>
    </div>
    """, unsafe_allow_html=True)

    profile = st.session_state.get("user_profile") or {}

    # Styled upload area
    st.markdown("""
    <div style="border: 2px dashed rgba(0,255,136,0.4); border-radius:16px; padding:20px;
                text-align:center; margin-bottom:16px; background:rgba(0,255,136,0.03);">
        <div style="font-size:36px;">📷</div>
        <div style="color:#aaaaaa; font-size:14px; margin-top:8px;">
            Drag & drop your food photo or click to browse<br/>
            <span style="color:#00ff88;">Supported: JPG, JPEG, PNG, WEBP</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(
        "Choose a food image",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
    )

    if uploaded_file:
        img_bytes = uploaded_file.read()
        col_img, col_btn = st.columns([3, 1])
        with col_img:
            st.image(img_bytes, caption="Uploaded Food Photo", width="stretch")
        with col_btn:
            analyze_clicked = st.button("🔍 Analyze Food", use_container_width=True)

        if analyze_clicked:
            with st.spinner("🤖 GPT-5 Vision is analyzing your food..."):
                result = _analyze_food_image(img_bytes)

            if result:
                st.session_state["last_food_analysis"] = result
                datetime_str = datetime.now().strftime("%Y%m%d_%H%M%S")

                # Save photo and analysis to Azure
                if profile:
                    username_key = profile.get("name", "user").lower().replace(" ", "_")
                    with st.spinner("☁️ Uploading to Azure..."):
                        save_food_image(username_key, datetime_str, img_bytes)
                        write_silver_food_analysis(username_key, datetime_str, result)

                st.success("✅ Analysis complete!")
                st.rerun()

    # ── Display Results ──────────────────────────────
    result = st.session_state.get("last_food_analysis")
    if result:
        st.markdown("---")
        st.markdown("### 📊 Nutrition Analysis Results")

        # Metric cards
        col1, col2, col3, col4 = st.columns(4)
        metrics = [
            (col1, "🔥 Total Calories", f"{result.get('total_calories', 0)}", "kcal", "#ef4444"),
            (col2, "💪 Protein", f"{result.get('protein_g', 0)}", "grams", "#3b82f6"),
            (col3, "🌾 Carbs", f"{result.get('carbs_g', 0)}", "grams", "#f59e0b"),
            (col4, "🥑 Fats", f"{result.get('fats_g', 0)}", "grams", "#a855f7"),
        ]
        for col, label, value, unit, color in metrics:
            with col:
                st.markdown(f"""
                <div class="glass-card" style="text-align:center; padding:16px;">
                    <div style="font-size:12px; color:#aaaaaa;">{label}</div>
                    <div style="font-size:36px; font-weight:800; color:{color};">{value}</div>
                    <div style="font-size:12px; color:#888;">{unit}</div>
                </div>
                """, unsafe_allow_html=True)

        col_items, col_score = st.columns([3, 2])

        with col_items:
            st.markdown("#### 🍽️ Detected Food Items")
            food_items = result.get("food_items", [])
            for item in food_items:
                if isinstance(item, dict):
                    name = item.get("name", "Unknown")
                    cals = item.get("calories", 0)
                    st.markdown(f"""
                    <div style="display:flex; justify-content:space-between; align-items:center;
                                padding:8px 12px; margin:4px 0; background:rgba(255,255,255,0.05);
                                border-radius:8px; border-left:3px solid #00ff88;">
                        <span style="color:#e0e0e0;">🍴 {name}</span>
                        <span style="color:#00ff88; font-weight:600;">~{cals} kcal</span>
                    </div>
                    """, unsafe_allow_html=True)

            notes = result.get("health_notes", "")
            if notes:
                st.markdown(f"""
                <div class="glass-card" style="margin-top:12px;">
                    <div style="color:#00d4ff; font-weight:600; margin-bottom:4px;">💡 Nutritionist Notes</div>
                    <div style="color:#cccccc; font-size:14px;">{notes}</div>
                </div>
                """, unsafe_allow_html=True)

        with col_score:
            _health_score_display(result.get("health_score", 5))

        # Add to log button
        st.markdown("<br/>", unsafe_allow_html=True)
        if st.button("➕ Add to Today's Log", use_container_width=True):
            log = st.session_state.get("daily_meals_log", [])
            log.append({
                "source": "Food Analyzer",
                "description": ", ".join(
                    [i.get("name", "") for i in result.get("food_items", []) if isinstance(i, dict)]
                ),
                "calories": result.get("total_calories", 0),
                "protein_g": result.get("protein_g", 0),
                "carbs_g": result.get("carbs_g", 0),
                "fats_g": result.get("fats_g", 0),
                "time": datetime.now().strftime("%H:%M"),
            })
            st.session_state["daily_meals_log"] = log
            st.success("✅ Added to today's Daily Log!")
