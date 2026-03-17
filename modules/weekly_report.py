"""
weekly_report.py — Page 6: Weekly Health & Fitness Report
Loads 7 days of logs from Data Lake, sends to GPT-4 for analysis,
shows Plotly charts, colored achievement/improvement cards and report PDF.
"""

import json
import streamlit as st
import sys
import os
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta, date

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.azure_config import get_openai_client, get_deployment_name
from utils.datalake_helper import read_silver_daily_logs, write_gold_weekly_report

SYSTEM_PROMPT = (
    "You are a health coach. Analyze this 7-day health log and provide: "
    "overall performance score out of 100, top 3 achievements, top 3 areas to improve, "
    "personalized advice for next week, and a motivational message. "
    "Return ONLY structured JSON with keys: performance_score (number), "
    "achievements (array of 3 strings), improvements (array of 3 strings), "
    "advice (string), motivational_message (string)."
)


def _get_last_7_dates() -> list[str]:
    """Return a list of ISO date strings for the past 7 days."""
    return [(date.today() - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]


def _generate_report(logs: list[dict]) -> dict | None:
    """Send logs to GPT-4 for weekly analysis."""
    try:
        client = get_openai_client()
        deployment = get_deployment_name()

        log_str = json.dumps(logs, indent=2)
        response = client.chat.completions.create(
            model=deployment,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here are my 7 days of health logs:\n{log_str}"},
            ],
            temperature=0.6,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        return json.loads(raw)
    except Exception as e:
        st.error(f"❌ OpenAI API error: {e}")
        return None


def _make_demo_logs(n: int = 7) -> list[dict]:
    """Generate demo logs when no real data is available."""
    import random
    logs = []
    for i in range(n):
        day = date.today() - timedelta(days=n - 1 - i)
        logs.append({
            "date": day.isoformat(),
            "calories_consumed": random.randint(1600, 2400),
            "calories_burned": random.randint(200, 600),
            "water_glasses": random.randint(4, 10),
            "mood": random.choice(["good", "energized", "neutral", "tired"]),
            "goal_pct": random.randint(65, 110),
        })
    return logs


def _calorie_trend_chart(logs: list[dict]) -> go.Figure:
    """Build a Plotly line chart for daily calorie trend."""
    dates = [l.get("date", "")[-5:] for l in logs]
    consumed = [l.get("calories_consumed", 0) for l in logs]
    burned = [l.get("calories_burned", 0) for l in logs]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dates, y=consumed, mode="lines+markers", name="Consumed",
        line=dict(color="#ef4444", width=2), marker=dict(size=8),
    ))
    fig.add_trace(go.Scatter(
        x=dates, y=burned, mode="lines+markers", name="Burned",
        line=dict(color="#00ff88", width=2), marker=dict(size=8),
    ))
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=0, r=0, t=20, b=0),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        height=280,
    )
    return fig


def _workout_bar_chart(logs: list[dict]) -> go.Figure:
    """Build a Plotly bar chart for workout adherence (goal% per day)."""
    dates = [l.get("date", "")[-5:] for l in logs]
    goal_pcts = [l.get("goal_pct", 0) for l in logs]
    colors = ["#00ff88" if g >= 80 else "#f59e0b" if g >= 50 else "#ef4444" for g in goal_pcts]

    fig = go.Figure(go.Bar(
        x=dates, y=goal_pcts, marker_color=colors, name="Goal %", text=goal_pcts,
        texttemplate="%{text}%", textposition="outside",
    ))
    fig.add_hline(y=80, line_dash="dash", line_color="rgba(0,255,136,0.4)", annotation_text="80% target")
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e0e0e0"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", range=[0, 120]),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)"),
        margin=dict(l=0, r=0, t=20, b=0),
        height=280,
    )
    return fig


def show_weekly_report_page():
    """Render the Weekly Report page."""
    st.markdown("""
    <div class="hero-banner">
        <h2>📊 Weekly Report</h2>
        <p>AI-powered analysis of your past 7 days of health & fitness data</p>
    </div>
    """, unsafe_allow_html=True)

    profile = st.session_state.get("user_profile") or {}

    # Load last 7 days of logs from Data Lake
    dates = _get_last_7_dates()
    logs = []
    if profile:
        username_key = profile.get("name", "user").lower().replace(" ", "_")
        with st.spinner("📂 Loading your weekly data from Azure Data Lake..."):
            logs = read_silver_daily_logs(username_key, dates)

    if not logs:
        st.info("💡 No data found in Azure — using demo data to show how the report looks.")
        logs = _make_demo_logs()

    # ── Charts ─────────────────────────────────────
    st.markdown("### 📈 Calorie Trend — Last 7 Days")
    st.plotly_chart(_calorie_trend_chart(logs), use_container_width=True)

    st.markdown("### 📊 Daily Goal Achievement")
    st.plotly_chart(_workout_bar_chart(logs), use_container_width=True)

    # ── Quick Metrics ─────────────────────────────
    avg_consumed = int(sum(l.get("calories_consumed", 0) for l in logs) / len(logs))
    avg_burned = int(sum(l.get("calories_burned", 0) for l in logs) / len(logs))
    avg_water = round(sum(l.get("water_glasses", 0) for l in logs) / len(logs), 1)

    m1, m2, m3 = st.columns(3)
    for col, label, value, unit, color in [
        (m1, "🍽️ Avg Calories/Day", avg_consumed, "kcal", "#ef4444"),
        (m2, "🔥 Avg Burned/Day", avg_burned, "kcal", "#00ff88"),
        (m3, "💧 Avg Water/Day", avg_water, "glasses", "#00d4ff"),
    ]:
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <div style="color:#aaaaaa; font-size:13px;">{label}</div>
                <div style="font-size:36px; font-weight:800; color:{color};">{value}</div>
                <div style="color:#888; font-size:12px;">{unit}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── AI Analysis ───────────────────────────────
    st.markdown("---")
    st.markdown("### 🤖 AI Health Coach Analysis")

    if "weekly_report_analysis" not in st.session_state:
        if st.button("✨ Generate AI Analysis", use_container_width=True):
            with st.spinner("🤖 GPT-5 is analyzing your health data..."):
                report = _generate_report(logs)
            if report:
                st.session_state["weekly_report_analysis"] = report
                if profile:
                    username_key = profile.get("name", "user").lower().replace(" ", "_")
                    write_gold_weekly_report(username_key, date.today().isoformat(), report)
                st.success("✅ Analysis complete and saved to Azure Data Lake!")
                st.rerun()
    else:
        report = st.session_state["weekly_report_analysis"]

        # Performance Score
        score = report.get("performance_score", 0)
        score_color = "#00ff88" if score >= 80 else "#f59e0b" if score >= 50 else "#ef4444"
        st.markdown(f"""
        <div class="glass-card" style="text-align:center; padding:24px;">
            <div style="color:#aaaaaa; font-size:14px; margin-bottom:4px;">🏆 Overall Performance Score</div>
            <div style="font-size:64px; font-weight:900; color:{score_color};">{score}</div>
            <div style="color:#888;">/100</div>
        </div>
        """, unsafe_allow_html=True)

        col_a, col_i = st.columns(2)
        with col_a:
            st.markdown("#### ✅ Top Achievements")
            for ach in report.get("achievements", []):
                st.markdown(f"""
                <div style="padding:12px 16px; margin:6px 0; border-radius:10px;
                            background:rgba(0,255,136,0.1); border:1px solid rgba(0,255,136,0.4);
                            color:#00ff88;">
                    🌟 {ach}
                </div>
                """, unsafe_allow_html=True)
        with col_i:
            st.markdown("#### ⚠️ Areas to Improve")
            for imp in report.get("improvements", []):
                st.markdown(f"""
                <div style="padding:12px 16px; margin:6px 0; border-radius:10px;
                            background:rgba(245,158,11,0.1); border:1px solid rgba(245,158,11,0.4);
                            color:#f59e0b;">
                    📌 {imp}
                </div>
                """, unsafe_allow_html=True)

        # Advice
        st.markdown(f"""
        <div class="glass-card" style="margin-top:16px;">
            <div style="color:#00d4ff; font-weight:700; margin-bottom:8px;">💡 Advice for Next Week</div>
            <div style="color:#cccccc; line-height:1.7;">{report.get("advice", "")}</div>
        </div>
        """, unsafe_allow_html=True)

        # Motivational message
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,rgba(0,255,136,0.15),rgba(0,212,255,0.15));
                    border:1px solid rgba(0,255,136,0.4); border-radius:16px; padding:24px;
                    text-align:center; margin-top:16px;">
            <div style="font-size:28px; margin-bottom:8px;">🌟</div>
            <div style="font-size:18px; font-style:italic; color:#ffffff; line-height:1.6;">
                "{report.get('motivational_message', 'Keep up the great work!')}"
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Downloads
        st.markdown("<br/>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            if st.button("🔄 Regenerate Analysis", use_container_width=True):
                del st.session_state["weekly_report_analysis"]
                st.rerun()
        with col2:
            try:
                from modules.pdf_generator import generate_weekly_report_pdf
                pdf_bytes = generate_weekly_report_pdf(profile, report)
                st.download_button(
                    "⬇️ Download PDF",
                    data=pdf_bytes,
                    file_name=f"weekly_report_{date.today().isoformat()}.pdf",
                    mime="application/pdf",
                    use_container_width=True,
                )
            except Exception as e:
                st.error(f"PDF error: {e}")
        with col3:
            if st.button("📧 Email Report", use_container_width=True):
                email = profile.get("email", "")
                if not email:
                    st.error("No email in profile.")
                else:
                    with st.spinner("📤 Sending..."):
                        try:
                            from modules.pdf_generator import generate_weekly_report_pdf
                            from modules.email_sender import send_plan_email
                            pdf_bytes = generate_weekly_report_pdf(profile, report)
                            ok = send_plan_email(email, profile.get("name", "User"), "Weekly", pdf_bytes)
                            if ok:
                                st.success(f"✅ Report emailed to {email}!")
                            else:
                                st.error("❌ Email failed.")
                        except Exception as e:
                            st.error(f"Email error: {e}")
