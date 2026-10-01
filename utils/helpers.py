from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


def ist_now():
    return datetime.now(IST)


def ist_date(offset: int = 0) -> str:
    """IST calendar date string (offset = days ago)."""
    return (ist_now() - timedelta(days=offset)).strftime('%Y-%m-%d')


def ist_midnight(offset: int = 0) -> int:
    """Epoch of IST midnight for today+offset days."""
    d = ist_now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=offset)
    return int(d.timestamp())


def ist_str(ts: int, fmt: str = '%d %b %Y') -> str:
    return datetime.fromtimestamp(ts, IST).strftime(fmt)


def mask(value: str, keep: int = 4) -> str:
    if not value:
        return "not set"
    if len(value) <= keep:
        return "*" * len(value)
    return value[:keep] + "*" * min(8, len(value) - keep)


def clean_url(url: str) -> str:
    if not url:
        return ""
    url = url.strip("<>[]()\"' ")
    if not url:
        return ""
    if url.startswith("t.me/"):
        return "https://" + url
    if not (url.startswith("http://") or url.startswith("https://") or url.startswith("tg://")):
        return "https://" + url
    return url


def trial_info(user: dict, settings: dict) -> dict:
    """Pure calculation of a user's trial state (calendar days in IST)."""
    if not settings.get('trial_enabled', True):
        return {'phase': 'off'}
    days = int(settings.get('trial_days', 3) or 0)
    daily = int(settings.get('trial_daily', 5) or 0)
    if days <= 0 or daily <= 0:
        return {'phase': 'off'}
    start = (user or {}).get('trial_start')
    if not start:
        return {'phase': 'new', 'days': days, 'daily': daily}
    day = (ist_now().date() - datetime.fromtimestamp(start, IST).date()).days + 1
    if day > days:
        return {'phase': 'ended', 'days': days, 'daily': daily}
    used = user.get('trial_used', 0) if user.get('trial_date') == ist_date() else 0
    return {'phase': 'active', 'day': day, 'days': days, 'daily': daily,
            'used': used, 'left': max(daily - used, 0)}
