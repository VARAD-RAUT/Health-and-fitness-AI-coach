"""
blob_helper.py — High-level helper functions for Azure Blob Storage operations.
Uses a single container (health-fitness-data) for all app storage.
"""

import json
import sys
import os

# Allow imports from project root
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from config.azure_config import upload_to_blob, download_from_blob, list_blobs
from dotenv import load_dotenv

load_dotenv()

# Get container name from environment, default to health-fitness-data
BLOB_CONTAINER = os.getenv("BLOB_CONTAINER_NAME", "health-fitness-data")


def list_saved_profiles() -> list[str]:
    """
    List all saved profile names from Blob Storage (users/ folder).
    Extracts profile names by removing the .json extension.
    Returns a sorted list of profile names, empty list on failure.
    """
    try:
        blob_names = list_blobs(BLOB_CONTAINER, prefix="users/")
        profile_names = []
        for blob_name in blob_names:
            # Extract name from users/{name}.json
            if blob_name.endswith(".json"):
                name = blob_name.replace("users/", "").replace(".json", "")
                if name:
                    profile_names.append(name)
        return sorted(profile_names)
    except Exception as e:
        print(f"[list_saved_profiles] Error: {e}")
        return []


def save_profile(username: str, profile_data: dict) -> bool:
    """
    Save a user profile to Blob Storage: users/{username}.json
    Returns True on success, False on failure.
    """
    try:
        blob_name = f"users/{username}.json"
        data = json.dumps(profile_data, indent=2)
        return upload_to_blob(BLOB_CONTAINER, blob_name, data)
    except Exception as e:
        print(f"[save_profile] Error: {e}")
        return False


def load_profile(username: str) -> dict | None:
    """
    Load a user profile from Blob Storage.
    Returns a dict on success, None if not found or on failure.
    """
    try:
        blob_name = f"users/{username}.json"
        raw = download_from_blob(BLOB_CONTAINER, blob_name)
        if raw is None:
            return None
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        print(f"[load_profile] Error: {e}")
        return None


def save_food_image(username: str, datetime_str: str, image_bytes: bytes) -> bool:
    """
    Upload a food photo to Blob Storage: food-images/{username}/{datetime}.jpg
    Returns True on success.
    """
    try:
        blob_name = f"food-images/{username}/{datetime_str}.jpg"
        return upload_to_blob(BLOB_CONTAINER, blob_name, image_bytes)
    except Exception as e:
        print(f"[save_food_image] Error: {e}")
        return False


def save_diet_plan(username: str, plan: dict) -> bool:
    """
    Save a diet plan to Blob Storage: diet-plans/{username}.json
    Returns True on success.
    """
    try:
        blob_name = f"diet-plans/{username}.json"
        data = json.dumps(plan, indent=2)
        return upload_to_blob(BLOB_CONTAINER, blob_name, data)
    except Exception as e:
        print(f"[save_diet_plan] Error: {e}")
        return False


def save_workout_plan(username: str, plan: dict) -> bool:
    """
    Save a workout plan to Blob Storage: workout-plans/{username}.json
    Returns True on success.
    """
    try:
        blob_name = f"workout-plans/{username}.json"
        data = json.dumps(plan, indent=2)
        return upload_to_blob(BLOB_CONTAINER, blob_name, data)
    except Exception as e:
        print(f"[save_workout_plan] Error: {e}")
        return False


def save_daily_log(username: str, date_str: str, log_data: dict) -> bool:
    """
    Save a daily log to Blob Storage: daily-logs/{username}/{date}.json
    Returns True on success.
    """
    try:
        blob_name = f"daily-logs/{username}/{date_str}.json"
        data = json.dumps(log_data, indent=2)
        return upload_to_blob(BLOB_CONTAINER, blob_name, data)
    except Exception as e:
        print(f"[save_daily_log] Error: {e}")
        return False


def load_daily_log(username: str, date_str: str) -> dict | None:
    """
    Load a daily log from Blob Storage.
    Returns a dict on success, None if not found or on failure.
    """
    try:
        blob_name = f"daily-logs/{username}/{date_str}.json"
        raw = download_from_blob(BLOB_CONTAINER, blob_name)
        if raw is None:
            return None
        return json.loads(raw.decode("utf-8"))
    except Exception as e:
        print(f"[load_daily_log] Error: {e}")
        return None


def load_daily_logs(username: str, dates: list) -> list:
    """
    Load multiple daily logs from Blob Storage for given dates.
    Returns a list of dicts (skips missing entries).
    """
    logs = []
    for date_str in dates:
        try:
            log = load_daily_log(username, date_str)
            if log:
                logs.append(log)
        except Exception as e:
            print(f"[load_daily_logs] Skipping {date_str}: {e}")
    return logs


def save_food_analysis(username: str, datetime_str: str, analysis: dict) -> bool:
    """
    Save food analysis to Blob Storage: food-analysis/{username}/{datetime}.json
    Returns True on success.
    """
    try:
        blob_name = f"food-analysis/{username}/{datetime_str}.json"
        data = json.dumps(analysis, indent=2)
        return upload_to_blob(BLOB_CONTAINER, blob_name, data)
    except Exception as e:
        print(f"[save_food_analysis] Error: {e}")
        return False


def save_weekly_report(username: str, report: dict) -> bool:
    """
    Save a weekly report to Blob Storage: reports/{username}.json
    Returns True on success.
    """
    try:
        blob_name = f"reports/{username}.json"
        data = json.dumps(report, indent=2)
        return upload_to_blob(BLOB_CONTAINER, blob_name, data)
    except Exception as e:
        print(f"[save_weekly_report] Error: {e}")
        return False
