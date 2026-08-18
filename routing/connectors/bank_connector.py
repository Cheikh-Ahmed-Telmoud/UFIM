import time
import random
from .base import BaseConnector

class BankConnector(BaseConnector):
    def execute(self, service_name: str, phone_number: str, data: dict) -> dict:
        # Simulation d'un délai réseau API
        time.sleep(0.5)
        
        # Normalisation du nom de service (ex: "solde", "transfert")
        srv = service_name.lower()
        
        lang = data.get("lang", "fr")
        
        if "solde" in srv or "balance" in srv:
            pin = data.get("pin", "")
            if pin == "1234":
                # Solde fictif
                balance = random.randint(15000, 250000)
                msg = {
                    'fr': f"Solde : {balance} MRU",
                    'en': f"Balance : {balance} MRU",
                    'ar': f"الرصيد : {balance} أوقية"
                }.get(lang, f"Solde : {balance} MRU")
                return {
                    'api_success': 'True',
                    'api_message': msg,
                    'balance': str(balance)
                }
            else:
                msg = {'fr': "Code PIN incorrect.", 'en': "Incorrect PIN.", 'ar': "الرمز السري غير صحيح."}.get(lang, "Code PIN incorrect.")
                return {'api_success': 'False', 'api_message': msg}
                
        elif "transfert" in srv or "transfer" in srv:
            recipient = data.get("recipient", "")
            amount_str = data.get("amount", "0")
            pin = data.get("pin", "")
            
            try:
                amount = int(amount_str)
            except ValueError:
                amount = 0
                
            if pin != "1234":
                msg = {'fr': "Code PIN incorrect.", 'en': "Incorrect PIN.", 'ar': "الرمز السري غير صحيح."}.get(lang, "Code PIN incorrect.")
                return {'api_success': 'False', 'api_message': msg}
            if amount <= 0:
                msg = {'fr': "Montant invalide.", 'en': "Invalid amount.", 'ar': "مبلغ غير صحيح."}.get(lang, "Montant invalide.")
                return {'api_success': 'False', 'api_message': msg}
                
            tx_id = f"BNK{random.randint(100000, 999999)}"
            msg = {
                'fr': f"Transfert de {amount} MRU vers {recipient} réussi. Réf: {tx_id}",
                'en': f"Transfer of {amount} MRU to {recipient} successful. Ref: {tx_id}",
                'ar': f"نجح تحويل {amount} أوقية إلى {recipient}. المرجع: {tx_id}"
            }.get(lang, f"Transfert de {amount} MRU vers {recipient} réussi. Réf: {tx_id}")
            return {
                'api_success': 'True',
                'api_message': msg,
                'transaction_id': tx_id
            }
            
        elif "paiement" in srv or "payment" in srv:
            merchant_code = data.get("merchant_code", "")
            amount_str = data.get("amount", "0")
            pin = data.get("pin", "")
            
            try:
                amount = int(amount_str)
            except ValueError:
                amount = 0
                
            if pin != "1234":
                msg = {'fr': "Code PIN incorrect.", 'en': "Incorrect PIN.", 'ar': "الرمز السري غير صحيح."}.get(lang, "Code PIN incorrect.")
                return {'api_success': 'False', 'api_message': msg}
            if amount <= 0:
                msg = {'fr': "Montant invalide.", 'en': "Invalid amount.", 'ar': "مبلغ غير صحيح."}.get(lang, "Montant invalide.")
                return {'api_success': 'False', 'api_message': msg}
                
            tx_id = f"PAY{random.randint(100000, 999999)}"
            msg = {
                'fr': f"Paiement de {amount} MRU au marchand {merchant_code} réussi. Réf: {tx_id}",
                'en': f"Payment of {amount} MRU to merchant {merchant_code} successful. Ref: {tx_id}",
                'ar': f"نجح دفع {amount} أوقية للتاجر {merchant_code}. المرجع: {tx_id}"
            }.get(lang, f"Paiement de {amount} MRU au marchand {merchant_code} réussi. Réf: {tx_id}")
            return {
                'api_success': 'True',
                'api_message': msg,
                'transaction_id': tx_id
            }
            
        else:
            # Autres services génériques
            return {
                'api_success': 'True',
                'api_message': "Opération effectuée avec succès.",
                'transaction_id': f"GEN{random.randint(100000, 999999)}"
            }
