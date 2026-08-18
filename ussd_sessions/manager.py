from django.utils import timezone
from django.conf import settings
from .models import USSDSession
from institutions.models import Institution, Service
from workflows.models import WorkflowStep

class USSDSessionManager:
    @staticmethod
    def get_or_create_session(session_id: str, phone_number: str) -> USSDSession:
        timeout_seconds = getattr(settings, 'USSD_SESSION_TIMEOUT_SECONDS', 120)
        
        try:
            session = USSDSession.objects.get(session_id=session_id)
            
            # Check timeout based on updated_at
            now = timezone.now()
            time_difference = (now - session.updated_at).total_seconds()
            
            if time_difference > timeout_seconds or session.is_completed:
                # Session is expired or completed, start fresh
                session.delete()
                session = USSDSession.objects.create(
                    session_id=session_id,
                    phone_number=phone_number
                )
        except USSDSession.DoesNotExist:
            session = USSDSession.objects.create(
                session_id=session_id,
                phone_number=phone_number
            )
            
        return session

    @staticmethod
    def update_session(session: USSDSession, **kwargs) -> USSDSession:
        for key, value in kwargs.items():
            setattr(session, key, value)
        session.save()
        return session

    @staticmethod
    def save_input(session: USSDSession, variable_name: str, value: str) -> USSDSession:
        if not session.session_data:
            session.session_data = {}
        session.session_data[variable_name] = value
        session.save()
        return session

    @staticmethod
    def close_session(session: USSDSession) -> USSDSession:
        session.is_completed = True
        session.save()
        return session
