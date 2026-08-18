from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from ussd_sessions.manager import USSDSessionManager
from workflows.engine import WorkflowEngine

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def ussd_gateway_view(request):
    """
    Point d'entrée du Webhook USSD compatible avec le format d'Africa's Talking.
    Paramètres POST attendus :
    - sessionId : ID unique de la session
    - phoneNumber : Numéro de téléphone de l'appelant
    - text : Saisie cumulative de l'utilisateur séparée par des '*' (ex: '1*2*5000')
    - serviceCode : Code USSD composé (ex: '*123#')
    """
    session_id = request.data.get("sessionId") or request.POST.get("sessionId")
    phone_number = request.data.get("phoneNumber") or request.POST.get("phoneNumber")
    text = request.data.get("text") or request.POST.get("text") or ""

    if not session_id or not phone_number:
        return HttpResponse("END Requête invalide. Paramètres manquants.", content_type="text/plain")

    # Extraire la dernière saisie de l'utilisateur (après la dernière étoile)
    parts = [p.strip() for p in text.split('*') if p.strip()]
    latest_input = parts[-1] if parts else ""

    # Charger ou créer la session USSD correspondante
    session = USSDSessionManager.get_or_create_session(session_id, phone_number)

    # Si c'est la toute première interaction (text vide)
    if not text:
        # Forcer la réinitialisation de l'input pour afficher le premier écran (choix de langue)
        latest_input = ""

    # Exécuter le moteur de workflow
    response_text = WorkflowEngine.execute(session, latest_input)

    # Africa's Talking exige que la réponse commence par 'CON ' ou 'END '
    if not response_text.startswith("CON ") and not response_text.startswith("END "):
        response_text = "CON " + response_text

    return HttpResponse(response_text, content_type="text/plain")
