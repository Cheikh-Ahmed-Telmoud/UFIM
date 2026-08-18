from abc import ABC, abstractmethod
from institutions.models import Institution

class BaseConnector(ABC):
    def __init__(self, institution: Institution):
        self.institution = institution

    @abstractmethod
    def execute(self, service_name: str, phone_number: str, data: dict) -> dict:
        """
        Exécute la transaction financière auprès du partenaire.
        Retourne un dictionnaire contenant au moins:
        - 'api_success': str ('True' ou 'False')
        - 'api_message': str (Message d'explication)
        - 'transaction_id': str (Référence de transaction générée)
        """
        pass

    def generate_hmac_signature(self, payload: str) -> str:
        """
        Génère une signature HMAC-SHA256 pour sécuriser les appels vers l'institution.
        Utilise la clé d'API chiffrée de l'institution comme secret.
        """
        import hmac
        import hashlib
        
        api_secret = self.institution.api_key or 'default-secret-key'
        secret_bytes = api_secret.encode('utf-8')
        payload_bytes = payload.encode('utf-8')
        
        signature = hmac.new(secret_bytes, payload_bytes, hashlib.sha256).hexdigest()
        return signature
