"""
Timezone utility functions - using IST (Indian Standard Time, UTC+5:30)
All times are stored and displayed in IST
"""

from datetime import datetime
import pytz

# IST timezone
IST = pytz.timezone('Asia/Kolkata')

def get_ist_now():
    """
    Get current time in IST (timezone-naive for SQLite compatibility)
    Returns timezone-naive datetime representing current IST time
    """
    return datetime.now(IST).replace(tzinfo=None)

def format_ist(ist_datetime, format_string='%Y-%m-%d %H:%M:%S'):
    """
    Format IST datetime as string
    Args:
        ist_datetime: timezone-naive datetime in IST
        format_string: strftime format string
    Returns:
        formatted string in IST
    """
    if ist_datetime is None:
        return None
    
    return ist_datetime.strftime(format_string)

def format_ist_iso(ist_datetime):
    """
    Format IST datetime as ISO string with +05:30 offset
    Args:
        ist_datetime: timezone-naive datetime in IST
    Returns:
        ISO formatted string in IST with +05:30 offset (e.g., '2025-11-29T12:30:00+05:30')
    """
    if ist_datetime is None:
        return None
    
    # Add timezone info and format with offset
    ist_aware = IST.localize(ist_datetime)
    return ist_aware.isoformat()

# Backward compatibility - keep get_utc_now as alias for get_ist_now
get_utc_now = get_ist_now

