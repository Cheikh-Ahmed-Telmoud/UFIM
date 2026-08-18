import uuid
from django.db import models
from institutions.models import Service

class Workflow(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    service = models.OneToOneField(Service, on_delete=models.CASCADE, related_name="workflow", verbose_name="Service")
    description = models.TextField(blank=True, verbose_name="Description du Workflow")
    start_step = models.ForeignKey(
        'WorkflowStep', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="started_workflows",
        verbose_name="Étape Initiale"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Workflow pour {self.service.name}"

    class Meta:
        verbose_name = "Workflow"
        verbose_name_plural = "Workflows"


class WorkflowStep(models.Model):
    STEP_TYPES = (
        ('INPUT', 'Saisie Libre (INPUT)'),
        ('SELECT', 'Sélection d\'Option (SELECT)'),
        ('API_CALL', 'Appel d\'API Externe (API_CALL)'),
        ('END', 'Écran de Fin (END)'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, related_name="steps", verbose_name="Workflow")
    name = models.CharField(max_length=50, verbose_name="Nom de l'étape (ex: enter_amount)")
    step_type = models.CharField(max_length=20, choices=STEP_TYPES, verbose_name="Type d'étape")
    
    # Stocké sous forme de dictionnaire JSON. Exemple:
    # {"fr": "Entrez le montant :", "en": "Enter amount:", "ar": "أدخل المبلغ:"}
    prompt_texts = models.JSONField(
        default=dict, 
        verbose_name="Textes d'invite (JSON - fr, en, ar)",
        help_text="Format: {'fr': '...', 'en': '...', 'ar': '...'}"
    )
    
    validation_regex = models.CharField(
        max_length=255, 
        blank=True, 
        verbose_name="Regex de Validation (ex: ^\\d+$)",
        help_text="Laisser vide si aucune validation n'est requise."
    )
    variable_name = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Nom de la variable en session (ex: amount)",
        help_text="Nom sous lequel la valeur saisie sera stockée en session."
    )
    next_step_default = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name="previous_steps",
        verbose_name="Étape Suivante par Défaut"
    )
    step_order = models.IntegerField(default=0, verbose_name="Ordre d'affichage/exécution")

    def __str__(self):
        return f"{self.workflow.service.name} - Step: {self.name} ({self.get_step_type_display()})"

    class Meta:
        verbose_name = "Étape de Workflow"
        verbose_name_plural = "Étapes de Workflows"
        ordering = ['step_order']


class WorkflowStepBranch(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    step = models.ForeignKey(WorkflowStep, on_delete=models.CASCADE, related_name="branches", verbose_name="Étape Source")
    condition_value = models.CharField(
        max_length=255, 
        verbose_name="Valeur de condition",
        help_text="La saisie utilisateur qui déclenche cette branche (ex: '1' ou 'oui')."
    )
    next_step = models.ForeignKey(
        WorkflowStep, 
        on_delete=models.CASCADE, 
        related_name="branch_sources", 
        verbose_name="Étape Suivante"
    )

    def __str__(self):
        return f"Branche de {self.step.name} si saisie='{self.condition_value}' -> {self.next_step.name}"

    class Meta:
        verbose_name = "Branche d'Étape"
        verbose_name_plural = "Branches d'Étapes"
        unique_together = ('step', 'condition_value')
