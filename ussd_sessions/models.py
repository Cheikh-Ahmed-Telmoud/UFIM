from django.db import models
from institutions.models import Institution, Service
from workflows.models import WorkflowStep

class USSDSession(models.Model):
    session_id = models.CharField(max_length=255, primary_key=True, verbose_name="ID de session Africa's Talking")
    phone_number = models.CharField(max_length=30, verbose_name="Numéro de téléphone")
    preferred_language = models.CharField(
        max_length=5, 
        choices=(('fr', 'Français'), ('en', 'English'), ('ar', 'العربية')), 
        default='fr',
        verbose_name="Langue préférée"
    )
    current_institution = models.ForeignKey(
        Institution, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Institution active"
    )
    current_service = models.ForeignKey(
        Service, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Service actif"
    )
    current_step = models.ForeignKey(
        WorkflowStep, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Étape courante"
    )
    session_data = models.JSONField(default=dict, verbose_name="Données collectées")
    is_completed = models.BooleanField(default=False, verbose_name="Terminée ?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        status = "Terminée" if self.is_completed else "Active"
        return f"Session {self.session_id} - {self.phone_number} ({status})"

    class Meta:
        verbose_name = "Session USSD"
        verbose_name_plural = "Sessions USSD"
