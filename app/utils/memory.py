import threading
import time


SESSION_TTL_SECONDS = 60 * 60
MAX_MESSAGES_PER_SESSION = 50

sessions: dict = {}
_lock = threading.Lock()


def _now() -> float:
    return time.time()


def prune_expired_sessions() -> None:
    cutoff = _now() - SESSION_TTL_SECONDS
    with _lock:
        stale = [
            sid
            for sid, s in sessions.items()
            if s.get("last_active_at", 0) < cutoff
        ]
        for sid in stale:
            sessions.pop(sid, None)


def touch_session(session: dict) -> None:
    session["last_active_at"] = _now()
    msgs = session.get("messages")
    if msgs and len(msgs) > MAX_MESSAGES_PER_SESSION:
        del msgs[: len(msgs) - MAX_MESSAGES_PER_SESSION]
