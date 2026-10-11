from django.contrib.sessions.backends.db import SessionStore as DjangoSessionStore
from user_sessions.backends.db import SessionStore as UserSessionStore


class SessionStore(UserSessionStore):
    """Treat expired or revoked user sessions as anonymous sessions."""

    def _get_session_from_db(self):
        session = DjangoSessionStore._get_session_from_db(self)
        if session is not None:
            self.user_id = session.user_id
            if self.user_agent != session.user_agent or self.ip != session.ip:
                self.modified = True
        return session
