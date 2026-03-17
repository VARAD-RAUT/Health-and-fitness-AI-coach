"""
datalake_helper.py — Simplified data persistence wrappers.

Previously used Data Lake bronze/silver/gold zones. Now uses single Blob container.
Functions maintain same interface for backward compatibility.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from utils.blob_helper import (
    save_profile,
    save_daily_log,
    load_daily_logs,
    save_food_analysis,
    save_diet_plan,
    save_workout_plan,
    save_weekly_report,
)


# ─────────── Profile Functions ───────────

def write_bronze_profile(username: str, profile_data: dict) -> bool:
    """
    Save user profile to Blob Storage.
    Maps to: users/{username}.json
    """
    return save_profile(username, profile_data)


# ─────────── Daily Log Functions ───────────

def write_bronze_daily_log(username: str, date_str: str, log_data: dict) -> bool:
    """
    Save daily log to Blob Storage.
    Maps to: daily-logs/{username}/{date}.json
    """
    return save_daily_log(username, date_str, log_data)


def write_silver_daily_log(username: str, date_str: str, log_data: dict) -> bool:
    """
    Save cleaned daily log to Blob Storage.
    Maps to: daily-logs/{username}/{date}.json
    """
    return save_daily_log(username, date_str, log_data)


def read_silver_daily_logs(username: str, dates: list) -> list:
    """
    Read multiple daily logs from Blob Storage for given dates.
    Returns a list of dicts (skips missing entries).
    """
    return load_daily_logs(username, dates)


# ─────────── Food Analysis Functions ───────────

def write_silver_food_analysis(username: str, datetime_str: str, analysis: dict) -> bool:
    """
    Save food analysis to Blob Storage.
    Maps to: food-analysis/{username}/{datetime}.json
    """
    return save_food_analysis(username, datetime_str, analysis)


# ─────────── Diet Plan Functions ───────────

def write_gold_diet_plan(username: str, date_str: str, plan: dict) -> bool:
    """
    Save diet plan to Blob Storage.
    Maps to: diet-plans/{username}.json
    """
    return save_diet_plan(username, plan)


# ─────────── Workout Plan Functions ───────────

def write_gold_workout_plan(username: str, date_str: str, plan: dict) -> bool:
    """
    Save workout plan to Blob Storage.
    Maps to: workout-plans/{username}.json
    """
    return save_workout_plan(username, plan)


# ─────────── Weekly Report Functions ───────────

def write_gold_weekly_report(username: str, date_str: str, report: dict) -> bool:
    """
    Save weekly report to Blob Storage.
    Maps to: reports/{username}.json
    """
    return save_weekly_report(username, report)
