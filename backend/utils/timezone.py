"""
Timezone utility functions - using UTC only (no timezone conversions)
All times are stored and displayed in UTC
"""

from datetime import datetime

def get_utc_now():
    """
    Get current time in UTC (timezone-naive for SQLite compatibility)
    """
    return datetime.utcnow()

def format_utc(utc_datetime, format_string='%Y-%m-%d %H:%M:%S'):
    """
    Format UTC datetime as string
    Args:
        utc_datetime: timezone-naive datetime in UTC
        format_string: strftime format string
    Returns:
        formatted string in UTC
    """
    if utc_datetime is None:
        return None
    
    return utc_datetime.strftime(format_string)

def format_ist_iso(utc_datetime):
    """
    Format UTC datetime as ISO string (kept for backward compatibility)
    Args:
        utc_datetime: timezone-naive datetime in UTC
    Returns:
        ISO formatted string in UTC
    """
    if utc_datetime is None:
        return None
    
    return utc_datetime.isoformat()

