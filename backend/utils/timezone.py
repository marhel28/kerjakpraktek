"""Shared timezone helpers for dashboard periods and Midtrans timestamps."""

from datetime import date, datetime, time, timedelta, timezone
from typing import Optional, Tuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import Header

DEFAULT_TIMEZONE = "Asia/Jakarta"
MIDTRANS_TIMEZONE = ZoneInfo("Asia/Jakarta")


def get_timezone(name: Optional[str]) -> ZoneInfo:
    if name:
        try:
            return ZoneInfo(name)
        except (ZoneInfoNotFoundError, ValueError, TypeError):
            pass
    return ZoneInfo(DEFAULT_TIMEZONE)


def get_request_timezone(
    x_timezone: Optional[str] = Header(default=None, alias="X-Timezone"),
) -> ZoneInfo:
    """Trust the admin browser IANA zone, with a safe fallback."""
    return get_timezone(x_timezone)


def timezone_name(tz: ZoneInfo) -> str:
    return getattr(tz, "key", DEFAULT_TIMEZONE)


ZONE_LABELS = {
    "Asia/Jakarta": "WIB",
    "Asia/Makassar": "WITA",
    "Asia/Jayapura": "WIT",
}


def timezone_label(tz: ZoneInfo) -> str:
    name = timezone_name(tz)
    return ZONE_LABELS.get(name, name)


def day_bounds_utc(day: date, tz: ZoneInfo) -> Tuple[datetime, datetime]:
    """UTC bounds of a local calendar day, valid across DST changes."""
    start = datetime.combine(day, time.min, tzinfo=tz).astimezone(timezone.utc)
    end = datetime.combine(day + timedelta(days=1), time.min, tzinfo=tz).astimezone(timezone.utc)
    return start, end


def period_bounds_utc(period: str, tz: ZoneInfo, today: Optional[date] = None) -> Tuple[Optional[datetime], Optional[datetime]]:
    """UTC bounds for all | today | week | month. None means unbounded."""
    if period == "all":
        return None, None
    today = today or datetime.now(tz).date()
    if period == "today":
        return day_bounds_utc(today, tz)
    if period == "week":
        start, _ = day_bounds_utc(today - timedelta(days=6), tz)
        _, end = day_bounds_utc(today, tz)
        return start, end
    if period == "month":
        first = today.replace(day=1)
        start, _ = day_bounds_utc(first, tz)
        _, end = day_bounds_utc(today, tz)
        return start, end
    return None, None


def parse_midtrans_datetime(value) -> Optional[datetime]:
    """Midtrans sends 'YYYY-MM-DD HH:MM:SS' in GMT+7 without an offset."""
    if not value:
        return None
    dt = None
    if isinstance(value, datetime):
        dt = value
    else:
        text = str(value).strip().replace("Z", "+00:00")
        try:
            dt = datetime.fromisoformat(text)
        except ValueError:
            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
                try:
                    dt = datetime.strptime(text, fmt)
                    break
                except ValueError:
                    continue
    if dt is None:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=MIDTRANS_TIMEZONE)
    return dt.astimezone(timezone.utc)
