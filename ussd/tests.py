from django.test import TestCase, Client
from django.urls import reverse
from institutions.models import Institution, Service
from workflows.models import Workflow, WorkflowStep


class USSDGatewayTest(TestCase):
    """
    Tests automatisés du point d'entrée USSD (Webhook Gateway).
    
    Ces tests vérifient que le middleware UFIM fonctionne correctement
    de bout en bout, en simulant les requêtes HTTP POST qu'enverrait
    un agrégateur USSD (Africa's Talking) au serveur Django.
    
    Ce qui est testé :
    1. L'initialisation d'une session USSD (premier appel)
    2. Le flux complet d'un workflow : Langue → Institution → Service → Saisie → Résultat
    3. La gestion des saisies invalides (mauvais choix, format incorrect)
    4. Le support multilingue (français, anglais, arabe)
    5. La gestion de paramètres manquants dans la requête
    """

    def setUp(self):
        """Prépare les données de test : 1 institution, 1 service, 1 workflow avec 2 étapes."""
        self.client = Client()
        self.url = reverse('ussd_gateway')
        
        # Créer une institution de test
        self.inst = Institution.objects.create(
            name="Test Bank", slug="test-bank", ussd_code="1",
            is_active=True, api_base_url="https://api.test.example.com/v1"
        )
        # Créer un service de test
        self.service = Service.objects.create(
            institution=self.inst, name="Balance", service_code="1", is_active=True
        )
        # Créer un workflow de test avec 2 étapes
        self.workflow = Workflow.objects.create(service=self.service, description="Test Workflow")
        
        self.step1 = WorkflowStep.objects.create(
            workflow=self.workflow, name="enter_pin", step_type="INPUT",
            prompt_texts={'fr': 'Entrez votre code PIN :', 'en': 'Enter your PIN code:', 'ar': 'أدخل الرمز السري:'},
            validation_regex=r'^\d{4}$',
            variable_name='pin',
            step_order=1
        )
        self.step2 = WorkflowStep.objects.create(
            workflow=self.workflow, name="end_balance", step_type="END",
            prompt_texts={'fr': 'Solde : 1000 MRU', 'en': 'Balance: 1000 MRU', 'ar': 'الرصيد: 1000 أوقية'},
            step_order=2
        )
        self.step1.next_step_default = self.step2
        self.step1.save()
        
        self.workflow.start_step = self.step1
        self.workflow.save()

    # ================================================================
    # Test 1 : Vérifier que le premier appel affiche le menu de langues
    # ================================================================
    def test_initial_ussd_call(self):
        """
        Simule le tout premier appel USSD (text vide).
        Doit retourner l'écran de sélection de la langue.
        """
        response = self.client.post(self.url, {
            'sessionId': 'test_session_123',
            'phoneNumber': '+22243455259',
            'text': ''
        })
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('Choisir la langue', content)
        self.assertIn('1. Fran', content)  # Français
        self.assertIn('2. English', content)
        self.assertIn('3.', content)  # العربية

    # ================================================================
    # Test 2 : Flux complet Langue → Institution → Service → PIN → Fin
    # ================================================================
    def test_full_workflow_flow_french(self):
        """
        Simule un parcours complet en français :
        1 (Français) → 1 (Test Bank) → 1 (Balance) → 1234 (PIN) → Résultat final (END)
        """
        sid = 'test_session_flow_fr'
        phone = '+22243455259'

        # Étape 1 : Sélectionner le Français (option 1)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '1'
        })
        self.assertIn('institution', res.content.decode().lower())

        # Étape 2 : Sélectionner l'institution Test Bank (option 1)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '1*1'
        })
        self.assertIn('Services de Test Bank', res.content.decode())

        # Étape 3 : Sélectionner le service Balance (option 1)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '1*1*1'
        })
        self.assertIn('PIN', res.content.decode())

        # Étape 4 : Entrer le code PIN
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '1*1*1*1234'
        })
        content = res.content.decode()
        self.assertIn('END', content)
        self.assertIn('1000 MRU', content)

    # ================================================================
    # Test 3 : Flux complet en anglais
    # ================================================================
    def test_full_workflow_flow_english(self):
        """
        Simule un parcours complet en anglais :
        2 (English) → 1 (Test Bank) → 1 (Balance) → 1234 (PIN) → Result (END)
        """
        sid = 'test_session_flow_en'
        phone = '+22243455259'

        # Étape 1 : Sélectionner l'anglais (option 2)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '2'
        })
        self.assertIn('Select your institution', res.content.decode())

        # Étape 2 : Sélectionner l'institution Test Bank (option 1)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '2*1'
        })
        self.assertIn('Services of Test Bank', res.content.decode())

        # Étape 3 : Sélectionner le service Balance (option 1)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '2*1*1'
        })
        self.assertIn('Enter your PIN code', res.content.decode())

        # Étape 4 : Entrer le code PIN
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '2*1*1*1234'
        })
        content = res.content.decode()
        self.assertIn('END', content)
        self.assertIn('Balance: 1000 MRU', content)

    # ================================================================
    # Test 4 : Flux complet en arabe
    # ================================================================
    def test_full_workflow_flow_arabic(self):
        """
        Simule un parcours complet en arabe :
        3 (العربية) → 1 (Test Bank) → 1 (Balance) → 1234 (PIN) → Résultat (END)
        """
        sid = 'test_session_flow_ar'
        phone = '+22243455259'

        # Étape 1 : Sélectionner l'arabe (option 3)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '3'
        })
        self.assertIn('اختر المؤسسة', res.content.decode())

        # Étape 2 : Sélectionner l'institution Test Bank (option 1)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '3*1'
        })
        self.assertIn('Test Bank', res.content.decode())

        # Étape 3 : Sélectionner le service Balance (option 1)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '3*1*1'
        })
        self.assertIn('أدخل الرمز السري', res.content.decode())

        # Étape 4 : Entrer le code PIN
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '3*1*1*1234'
        })
        content = res.content.decode()
        self.assertIn('END', content)
        self.assertIn('أوقية', content)

    # ================================================================
    # Test 5 : Saisie de langue invalide
    # ================================================================
    def test_invalid_language_choice(self):
        """
        Vérifie qu'un choix de langue invalide (ex: '9') affiche
        un message d'erreur et redemande le choix.
        """
        res = self.client.post(self.url, {
            'sessionId': 'test_invalid_lang',
            'phoneNumber': '+22243455259',
            'text': '9'
        })
        content = res.content.decode()
        self.assertIn('invalide', content.lower())
        self.assertIn('1. Fran', content)

    # ================================================================
    # Test 6 : Format de PIN invalide (ne correspond pas au regex)
    # ================================================================
    def test_invalid_pin_format(self):
        """
        Vérifie qu'un PIN de mauvais format (ex: 'abc') est rejeté
        par la validation regex et que le prompt est ré-affiché.
        """
        sid = 'test_invalid_pin'
        phone = '+22243455259'

        # Sélection langue + institution + service
        self.client.post(self.url, {'sessionId': sid, 'phoneNumber': phone, 'text': '1'})
        self.client.post(self.url, {'sessionId': sid, 'phoneNumber': phone, 'text': '1*1'})
        self.client.post(self.url, {'sessionId': sid, 'phoneNumber': phone, 'text': '1*1*1'})

        # Entrer un PIN invalide (lettres au lieu de 4 chiffres)
        res = self.client.post(self.url, {
            'sessionId': sid, 'phoneNumber': phone, 'text': '1*1*1*abcd'
        })
        content = res.content.decode()
        self.assertIn('incorrect', content.lower())
        self.assertIn('PIN', content)

    # ================================================================
    # Test 7 : Paramètres manquants dans la requête
    # ================================================================
    def test_missing_parameters(self):
        """
        Vérifie qu'une requête sans sessionId ou phoneNumber
        retourne un message d'erreur END.
        """
        # Sans sessionId
        res = self.client.post(self.url, {
            'phoneNumber': '+22243455259', 'text': ''
        })
        self.assertIn('END', res.content.decode())

        # Sans phoneNumber
        res = self.client.post(self.url, {
            'sessionId': 'test_no_phone', 'text': ''
        })
        self.assertIn('END', res.content.decode())
