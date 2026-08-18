import time
import random
from .base import BaseConnector

class WalletConnector(BaseConnector):
    def execute(self, service_name: str, phone_number: str, data: dict) -> dict:
        time.sleep(0.4)
        srv = service_name.lower()
        
        lang = data.get("lang", "fr")
        
        if "solde" in srv or "balance" in srv:
            pin = data.get("pin", "")
            if pin == "1234":
                balance = random.randint(5000, 75000)
                msg = {
                    'fr': f"Solde Wallet : {balance} MRU",
                    'en': f"Wallet Balance : {balance} MRU",
                    'ar': f"رصيد المحفظة : {balance} أوقية"
                }.get(lang, f"Solde Wallet : {balance} MRU")
                return {
                    'api_success': 'True',
                    'api_message': msg,
                    'balance': str(balance)
                }
            else:
                msg = {'fr': "Code PIN Wallet incorrect.", 'en': "Incorrect Wallet PIN.", 'ar': "الرمز السري للمحفظة غير صحيح."}.get(lang, "Code PIN Wallet incorrect.")
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
                msg = {'fr': "Code PIN Wallet incorrect.", 'en': "Incorrect Wallet PIN.", 'ar': "الرمز السري للمحفظة غير صحيح."}.get(lang, "Code PIN Wallet incorrect.")
                return {'api_success': 'False', 'api_message': msg}
            if amount <= 0:
                msg = {'fr': "Montant invalide.", 'en': "Invalid amount.", 'ar': "مبلغ غير صحيح."}.get(lang, "Montant invalide.")
                return {'api_success': 'False', 'api_message': msg}
                
            tx_id = f"WLT{random.randint(100000, 999999)}"
            msg = {
                'fr': f"Transfert Wallet de {amount} MRU vers {recipient} réussi. Réf: {tx_id}",
                'en': f"Wallet Transfer of {amount} MRU to {recipient} successful. Ref: {tx_id}",
                'ar': f"نجح تحويل المحفظة بمبلغ {amount} أوقية إلى {recipient}. المرجع: {tx_id}"
            }.get(lang, f"Transfert Wallet de {amount} MRU vers {recipient} réussi. Réf: {tx_id}")
            return {
                'api_success': 'True',
                'api_message': msg,
                'transaction_id': tx_id
            }
            
        else:
            return {
                'api_success': 'True',
                'api_message': "Opération Wallet réussie.",
                'transaction_id': f"WLT{random.randint(100000, 999999)}"
            }
