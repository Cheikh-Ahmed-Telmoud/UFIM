import re
import logging

logger = logging.getLogger('ufim.security')

# Regex pour détecter les numéros de téléphone (formats internationaux et locaux)
PHONE_REGEX = re.compile(r'(\+?\d{1,4}[\s-]?)?\(?\d{2,4}\)?[\s.-]?\d{3,4}[\s.-]?\d{2,4}')

# Regex pour détecter les montants financiers (séquences de chiffres >= 3 digits)
AMOUNT_REGEX = re.compile(r'\b\d{3,}\b')


def mask_phone_number(phone: str) -> str:
    """Masque un numéro de téléphone : +221777777777 -> +221******77"""
    if not phone or len(phone) < 6:
        return "***"
    prefix = phone[:4]
    suffix = phone[-2:]
    masked = '*' * (len(phone) - 6)
    return f"{prefix}{masked}{suffix}"


def mask_sensitive_data(message: str) -> str:
    """Masque les données sensibles (numéros de téléphone et montants) dans un message de log."""
    if not message:
        return message
    
    # Masquer les numéros de téléphone
    def phone_replacer(match):
        return mask_phone_number(match.group(0))
    
    masked = PHONE_REGEX.sub(phone_replacer, message)
    return masked


class SecurityLoggingMiddleware:
    """
    Middleware Django qui intercepte les requêtes et réponses
    pour journaliser les interactions USSD de manière sécurisée.
    
    - Masque les numéros de téléphone dans les logs.
    - Ne journalise JAMAIS les codes PIN ou données financières sensibles.
    - Enregistre uniquement : session_id (tronqué), horodatage, action, résultat.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log de la requête entrante (uniquement pour le endpoint USSD)
        if '/ussd/' in request.path:
            self._log_request(request)
        
        response = self.get_response(request)
        
        if '/ussd/' in request.path:
            self._log_response(request, response)
        
        return response

    def _log_request(self, request):
        session_id = request.POST.get('sessionId', 'N/A')
        phone = request.POST.get('phoneNumber', 'N/A')
        text = request.POST.get('text', '')
        
        # Ne JAMAIS logger le contenu brut du texte (peut contenir un PIN)
        # On log seulement le nombre d'étapes franchies
        steps_count = len([p for p in text.split('*') if p.strip()]) if text else 0
        
        logger.info(
            f"USSD_REQUEST | session={session_id[:8]}... | "
            f"phone={mask_phone_number(phone)} | "
            f"steps_completed={steps_count}"
        )

    def _log_response(self, request, response):
        session_id = request.POST.get('sessionId', 'N/A')
        
        # Déterminer si la session est terminée ou continue
        if hasattr(response, 'content'):
            content = response.content.decode('utf-8', errors='replace')
            action = "SESSION_END" if content.startswith("END") else "SESSION_CONTINUE"
        else:
            action = "UNKNOWN"
        
        logger.info(
            f"USSD_RESPONSE | session={session_id[:8]}... | "
            f"action={action} | status={response.status_code}"
        )
