from ussd_sessions.models import USSDSession
from institutions.models import Institution
from .connectors.bank_connector import BankConnector
from .connectors.wallet_connector import WalletConnector

class ConnectorDispatcher:
    @staticmethod
    def dispatch(session: USSDSession) -> dict:
        inst = session.current_institution
        srv = session.current_service
        
        if not inst or not srv:
            return {
                'api_success': 'False',
                'api_message': "Institution ou Service manquant pour l'appel API."
            }
            
        slug = inst.slug.lower()
        
        # Sélection du connecteur approprié selon le slug de l'institution
        if 'bank' in slug:
            connector = BankConnector(inst)
        elif 'wallet' in slug or 'money' in slug:
            connector = WalletConnector(inst)
        else:
            # Fallback vers BankConnector par défaut pour les autres types (ex: Microfinance)
            connector = BankConnector(inst)
            
        # Ajout de la langue dans les données pour la traduction des connecteurs
        connector_data = dict(session.session_data)
        connector_data['lang'] = session.preferred_language
        
        # Exécution de l'action de service
        return connector.execute(
            service_name=srv.name,
            phone_number=session.phone_number,
            data=connector_data
        )
