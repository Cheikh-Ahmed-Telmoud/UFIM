"""
Script de peuplement initial de la base de données UFIM.
Crée les institutions, services et workflows de démonstration.

Usage :
    python manage.py shell < seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from institutions.models import Institution, Service
from workflows.models import Workflow, WorkflowStep, WorkflowStepBranch

print("=== Peuplement UFIM ===")

# --- 1. Institutions ---
bank_a, _ = Institution.objects.get_or_create(
    slug='bank-a',
    defaults={
        'name': 'Bank A',
        'ussd_code': '1',
        'is_active': True,
        'api_base_url': 'https://api.bank-a.example.com/v1',
    }
)
print(f"  Institution: {bank_a}")

wallet_b, _ = Institution.objects.get_or_create(
    slug='wallet-b',
    defaults={
        'name': 'Wallet B',
        'ussd_code': '2',
        'is_active': True,
        'api_base_url': 'https://api.wallet-b.example.com/v1',
    }
)
print(f"  Institution: {wallet_b}")

micro_c, _ = Institution.objects.get_or_create(
    slug='microfinance-c',
    defaults={
        'name': 'Microfinance C',
        'ussd_code': '3',
        'is_active': True,
        'api_base_url': 'https://api.microfinance-c.example.com/v1',
    }
)
print(f"  Institution: {micro_c}")

# --- 2. Services pour Bank A ---
srv_solde, _ = Service.objects.get_or_create(
    institution=bank_a, service_code='1',
    defaults={'name': 'Consultation du solde', 'is_active': True}
)
srv_transfert, _ = Service.objects.get_or_create(
    institution=bank_a, service_code='2',
    defaults={'name': 'Transfert', 'is_active': True}
)
srv_paiement, _ = Service.objects.get_or_create(
    institution=bank_a, service_code='3',
    defaults={'name': 'Paiement marchand', 'is_active': True}
)
print(f"  Services Bank A: {srv_solde.name}, {srv_transfert.name}, {srv_paiement.name}")

# --- 3. Services pour Wallet B ---
srv_solde_w, _ = Service.objects.get_or_create(
    institution=wallet_b, service_code='1',
    defaults={'name': 'Consultation du solde', 'is_active': True}
)
srv_transfert_w, _ = Service.objects.get_or_create(
    institution=wallet_b, service_code='2',
    defaults={'name': 'Transfert', 'is_active': True}
)
print(f"  Services Wallet B: {srv_solde_w.name}, {srv_transfert_w.name}")

# --- 4. Services pour Microfinance C ---
srv_solde_m, _ = Service.objects.get_or_create(
    institution=micro_c, service_code='1',
    defaults={'name': 'Consultation du solde', 'is_active': True}
)
print(f"  Services Microfinance C: {srv_solde_m.name}")

# =====================================================================
# WORKFLOWS
# =====================================================================

# --- 5. Workflow : Consultation du Solde (Bank A) ---
wf_solde, _ = Workflow.objects.get_or_create(
    service=srv_solde,
    defaults={'description': 'Workflow de consultation du solde Bank A'}
)

step_pin = WorkflowStep.objects.get_or_create(
    workflow=wf_solde, name='enter_pin',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez votre code PIN :',
            'en': 'Enter your PIN code:',
            'ar': 'أدخل الرمز السري:'
        },
        'validation_regex': r'^\d{4}$',
        'variable_name': 'pin',
        'step_order': 1,
    }
)[0]

step_api_solde = WorkflowStep.objects.get_or_create(
    workflow=wf_solde, name='api_check_balance',
    defaults={
        'step_type': 'API_CALL',
        'prompt_texts': {},
        'variable_name': '',
        'step_order': 2,
    }
)[0]

step_end_solde = WorkflowStep.objects.get_or_create(
    workflow=wf_solde, name='display_balance',
    defaults={
        'step_type': 'END',
        'prompt_texts': {
            'fr': '{api_message}',
            'en': '{api_message}',
            'ar': '{api_message}'
        },
        'step_order': 3,
    }
)[0]

# Chaîner les étapes
step_pin.next_step_default = step_api_solde
step_pin.save()
step_api_solde.next_step_default = step_end_solde
step_api_solde.save()
wf_solde.start_step = step_pin
wf_solde.save()
print(f"  Workflow Solde Bank A : {step_pin.name} -> {step_api_solde.name} -> {step_end_solde.name}")

# --- 6. Workflow : Transfert (Bank A) ---
wf_transfert, _ = Workflow.objects.get_or_create(
    service=srv_transfert,
    defaults={'description': 'Workflow de transfert Bank A'}
)

step_recipient = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert, name='enter_recipient',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez le numéro du bénéficiaire :',
            'en': 'Enter the recipient number:',
            'ar': 'أدخل رقم المستفيد:'
        },
        'validation_regex': r'^\+?\d{8,15}$',
        'variable_name': 'recipient',
        'step_order': 1,
    }
)[0]

step_amount = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert, name='enter_amount',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez le montant (MRU) :',
            'en': 'Enter the amount (MRU):',
            'ar': 'أدخل المبلغ (أوقية):'
        },
        'validation_regex': r'^\d+$',
        'variable_name': 'amount',
        'step_order': 2,
    }
)[0]

step_pin_transfer = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert, name='enter_pin_transfer',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez votre code PIN de validation :',
            'en': 'Enter your validation PIN:',
            'ar': 'أدخل الرمز السري للتأكيد:'
        },
        'validation_regex': r'^\d{4}$',
        'variable_name': 'pin',
        'step_order': 3,
    }
)[0]

step_api_transfer = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert, name='api_execute_transfer',
    defaults={
        'step_type': 'API_CALL',
        'prompt_texts': {},
        'step_order': 4,
    }
)[0]

step_end_transfer = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert, name='display_transfer_result',
    defaults={
        'step_type': 'END',
        'prompt_texts': {
            'fr': '{api_message}',
            'en': '{api_message}',
            'ar': '{api_message}'
        },
        'step_order': 5,
    }
)[0]

# Chaîner les étapes du transfert
step_recipient.next_step_default = step_amount
step_recipient.save()
step_amount.next_step_default = step_pin_transfer
step_amount.save()
step_pin_transfer.next_step_default = step_api_transfer
step_pin_transfer.save()
step_api_transfer.next_step_default = step_end_transfer
step_api_transfer.save()
wf_transfert.start_step = step_recipient
wf_transfert.save()
print(f"  Workflow Transfert Bank A : {step_recipient.name} -> {step_amount.name} -> {step_pin_transfer.name} -> {step_api_transfer.name} -> {step_end_transfer.name}")

# --- 7. Workflow : Paiement Marchand (Bank A) ---
wf_paiement, _ = Workflow.objects.get_or_create(
    service=srv_paiement,
    defaults={'description': 'Workflow de paiement marchand Bank A'}
)

step_merchant_code = WorkflowStep.objects.get_or_create(
    workflow=wf_paiement, name='enter_merchant_code',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez le code du marchand :',
            'en': 'Enter the merchant code:',
            'ar': 'أدخل رمز التاجر:'
        },
        'validation_regex': r'^\d{3,10}$',
        'variable_name': 'merchant_code',
        'step_order': 1,
    }
)[0]

step_amount_pay = WorkflowStep.objects.get_or_create(
    workflow=wf_paiement, name='enter_amount_payment',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez le montant à payer (MRU) :',
            'en': 'Enter the amount to pay (MRU):',
            'ar': 'أدخل المبلغ المراد دفعه (أوقية):'
        },
        'validation_regex': r'^\d+$',
        'variable_name': 'amount',
        'step_order': 2,
    }
)[0]

step_pin_pay = WorkflowStep.objects.get_or_create(
    workflow=wf_paiement, name='enter_pin_payment',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez votre code PIN de validation :',
            'en': 'Enter your validation PIN:',
            'ar': 'أدخل الرمز السري للتأكيد:'
        },
        'validation_regex': r'^\d{4}$',
        'variable_name': 'pin',
        'step_order': 3,
    }
)[0]

step_api_pay = WorkflowStep.objects.get_or_create(
    workflow=wf_paiement, name='api_execute_payment',
    defaults={
        'step_type': 'API_CALL',
        'prompt_texts': {},
        'step_order': 4,
    }
)[0]

step_end_pay = WorkflowStep.objects.get_or_create(
    workflow=wf_paiement, name='display_payment_result',
    defaults={
        'step_type': 'END',
        'prompt_texts': {
            'fr': '{api_message}',
            'en': '{api_message}',
            'ar': '{api_message}'
        },
        'step_order': 5,
    }
)[0]

# Chaîner les étapes du paiement
step_merchant_code.next_step_default = step_amount_pay
step_merchant_code.save()
step_amount_pay.next_step_default = step_pin_pay
step_amount_pay.save()
step_pin_pay.next_step_default = step_api_pay
step_pin_pay.save()
step_api_pay.next_step_default = step_end_pay
step_api_pay.save()
wf_paiement.start_step = step_merchant_code
wf_paiement.save()
print(f"  Workflow Paiement Bank A : {step_merchant_code.name} -> {step_amount_pay.name} -> {step_pin_pay.name} -> {step_api_pay.name} -> {step_end_pay.name}")

# --- 8. Workflow : Consultation du Solde (Wallet B) ---
wf_solde_w, _ = Workflow.objects.get_or_create(
    service=srv_solde_w,
    defaults={'description': 'Workflow de consultation du solde Wallet B'}
)

step_pin_w = WorkflowStep.objects.get_or_create(
    workflow=wf_solde_w, name='enter_pin_wallet',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez votre code PIN Wallet :',
            'en': 'Enter your Wallet PIN:',
            'ar': 'أدخل الرمز السري للمحفظة:'
        },
        'validation_regex': r'^\d{4}$',
        'variable_name': 'pin',
        'step_order': 1,
    }
)[0]

step_api_w = WorkflowStep.objects.get_or_create(
    workflow=wf_solde_w, name='api_check_wallet_balance',
    defaults={
        'step_type': 'API_CALL',
        'prompt_texts': {},
        'step_order': 2,
    }
)[0]

step_end_w = WorkflowStep.objects.get_or_create(
    workflow=wf_solde_w, name='display_wallet_balance',
    defaults={
        'step_type': 'END',
        'prompt_texts': {
            'fr': '{api_message}',
            'en': '{api_message}',
            'ar': '{api_message}'
        },
        'step_order': 3,
    }
)[0]

step_pin_w.next_step_default = step_api_w
step_pin_w.save()
step_api_w.next_step_default = step_end_w
step_api_w.save()
wf_solde_w.start_step = step_pin_w
wf_solde_w.save()
print(f"  Workflow Solde Wallet B : {step_pin_w.name} -> {step_api_w.name} -> {step_end_w.name}")

# --- 9. Workflow : Transfert (Wallet B) ---
wf_transfert_w, _ = Workflow.objects.get_or_create(
    service=srv_transfert_w,
    defaults={'description': 'Workflow de transfert Wallet B'}
)

step_recipient_w = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert_w, name='enter_recipient_wallet',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez le numéro du bénéficiaire :',
            'en': 'Enter the recipient number:',
            'ar': 'أدخل رقم المستفيد:'
        },
        'validation_regex': r'^\+?\d{8,15}$',
        'variable_name': 'recipient',
        'step_order': 1,
    }
)[0]

step_amount_w = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert_w, name='enter_amount_wallet',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez le montant (MRU) :',
            'en': 'Enter the amount (MRU):',
            'ar': 'أدخل المبلغ (أوقية):'
        },
        'validation_regex': r'^\d+$',
        'variable_name': 'amount',
        'step_order': 2,
    }
)[0]

step_pin_transfer_w = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert_w, name='enter_pin_transfer_wallet',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez votre code PIN de validation :',
            'en': 'Enter your validation PIN:',
            'ar': 'أدخل الرمز السري للتأكيد:'
        },
        'validation_regex': r'^\d{4}$',
        'variable_name': 'pin',
        'step_order': 3,
    }
)[0]

step_api_transfer_w = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert_w, name='api_execute_wallet_transfer',
    defaults={
        'step_type': 'API_CALL',
        'prompt_texts': {},
        'step_order': 4,
    }
)[0]

step_end_transfer_w = WorkflowStep.objects.get_or_create(
    workflow=wf_transfert_w, name='display_wallet_transfer_result',
    defaults={
        'step_type': 'END',
        'prompt_texts': {
            'fr': '{api_message}',
            'en': '{api_message}',
            'ar': '{api_message}'
        },
        'step_order': 5,
    }
)[0]

# Chaîner les étapes du transfert Wallet B
step_recipient_w.next_step_default = step_amount_w
step_recipient_w.save()
step_amount_w.next_step_default = step_pin_transfer_w
step_amount_w.save()
step_pin_transfer_w.next_step_default = step_api_transfer_w
step_pin_transfer_w.save()
step_api_transfer_w.next_step_default = step_end_transfer_w
step_api_transfer_w.save()
wf_transfert_w.start_step = step_recipient_w
wf_transfert_w.save()
print(f"  Workflow Transfert Wallet B : {step_recipient_w.name} -> {step_amount_w.name} -> {step_pin_transfer_w.name} -> {step_api_transfer_w.name} -> {step_end_transfer_w.name}")

# --- 10. Workflow : Consultation du Solde (Microfinance C) ---
wf_solde_m, _ = Workflow.objects.get_or_create(
    service=srv_solde_m,
    defaults={'description': 'Workflow de consultation du solde Microfinance C'}
)

step_pin_m = WorkflowStep.objects.get_or_create(
    workflow=wf_solde_m, name='enter_pin_micro',
    defaults={
        'step_type': 'INPUT',
        'prompt_texts': {
            'fr': 'Entrez votre code PIN :',
            'en': 'Enter your PIN code:',
            'ar': 'أدخل الرمز السري:'
        },
        'validation_regex': r'^\d{4}$',
        'variable_name': 'pin',
        'step_order': 1,
    }
)[0]

step_api_m = WorkflowStep.objects.get_or_create(
    workflow=wf_solde_m, name='api_check_micro_balance',
    defaults={
        'step_type': 'API_CALL',
        'prompt_texts': {},
        'step_order': 2,
    }
)[0]

step_end_m = WorkflowStep.objects.get_or_create(
    workflow=wf_solde_m, name='display_micro_balance',
    defaults={
        'step_type': 'END',
        'prompt_texts': {
            'fr': '{api_message}',
            'en': '{api_message}',
            'ar': '{api_message}'
        },
        'step_order': 3,
    }
)[0]

step_pin_m.next_step_default = step_api_m
step_pin_m.save()
step_api_m.next_step_default = step_end_m
step_api_m.save()
wf_solde_m.start_step = step_pin_m
wf_solde_m.save()
print(f"  Workflow Solde Microfinance C : {step_pin_m.name} -> {step_api_m.name} -> {step_end_m.name}")

print("\n=== Peuplement terminé avec succès ! ===")
