import uuid
from django.db import models
from security.crypto import encrypt_value, decrypt_value

class Institution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="Nom de l'Institution")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug (URL/Routage)")
    ussd_code = models.CharField(max_length=10, unique=True, verbose_name="Code USSD (ex: 1)")
    is_active = models.BooleanField(default=True, verbose_name="Actif ?")
    api_base_url = models.URLField(verbose_name="URL de base de l'API")
    encrypted_api_credentials = models.TextField(blank=True, verbose_name="Identifiants API Chiffrés")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def api_credentials(self) -> str:
        return decrypt_value(self.encrypted_api_credentials)

    @api_credentials.setter
    def api_credentials(self, value: str):
        self.encrypted_api_credentials = encrypt_value(value)

    def __str__(self):
        return f"{self.name} (Code: {self.ussd_code})"

    class Meta:
        verbose_name = "Institution"
        verbose_name_plural = "Institutions"


class Service(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    institution = models.ForeignKey(Institution, on_delete=models.CASCADE, related_name="services", verbose_name="Institution")
    name = models.CharField(max_length=100, verbose_name="Nom du Service (ex: Transfert)")
    service_code = models.CharField(max_length=10, verbose_name="Code Service (ex: 2)")
    is_active = models.BooleanField(default=True, verbose_name="Actif ?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.institution.name} - {self.name} (Code: {self.service_code})"

    class Meta:
        verbose_name = "Service Financier"
        verbose_name_plural = "Services Financiers"
        unique_together = ('institution', 'service_code')
