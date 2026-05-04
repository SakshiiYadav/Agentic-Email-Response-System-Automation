"""
SchedulerAgent — deterministic rule-based dispatcher
Assigns scheduled_time and delay_minutes based on priority:
  critical → 15 min
  high     → 30 min
  medium   → 60 min
  low      → 240 min (4 hours)
"""

from datetime import datetime, timedelta


DELAY_MAP = {
    "critical": 15,
    "high":     30,
    "medium":   60,
    "low":      240,
}


class SchedulerAgent:
    def schedule(self, email_data: dict) -> dict:
        priority    = email_data.get("priority", "medium")
        delay_min   = DELAY_MAP.get(priority, 60)
        dispatch_dt = datetime.now() + timedelta(minutes=delay_min)
        return {
            "delay_minutes":  delay_min,
            "scheduled_time": dispatch_dt.strftime("%Y-%m-%d %H:%M"),
        }
