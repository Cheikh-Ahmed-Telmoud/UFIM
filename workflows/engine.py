import re
from django.utils.translation import gettext as _
from ussd_sessions.models import USSDSession
from ussd_sessions.manager import USSDSessionManager
from institutions.models import Institution, Service
from workflows.models import WorkflowStep, WorkflowStepBranch
from django.conf import settings

class WorkflowEngine:
    @staticmethod
    def get_prompt_text(step: WorkflowStep, lang: str) -> str:
        """Récupère le texte de l'étape dans la langue spécifiée ou en français par défaut."""
        texts = step.prompt_texts or {}
        return texts.get(lang, texts.get('fr', f"Step: {step.name}"))

    @staticmethod
    def interpolate_variables(text: str, session: USSDSession) -> str:
        """Remplace les variables entre accolades {nom_variable} par leur valeur en session."""
        if not text:
            return ""
        
        # Inject standard session variables
        data = {
            'phone_number': session.phone_number,
            'session_id': session.session_id,
        }
        # Inject collected data
        if session.session_data:
            data.update(session.session_data)
            
        try:
            return text.format(**data)
        except Exception:
            return text

    @classmethod
    def execute(cls, session: USSDSession, user_input: str) -> str:
        # Normalize input
        user_input = user_input.strip() if user_input else ""
        
        # --- Étape 0: Sélection de la Langue ---
        if not session.session_data or not session.session_data.get('language_selected'):
            if not user_input:
                # Premier appel de la session
                return "UFIM\n\n Veuillez choisir la langue:\n1. Français\n2. English\n3. العربية"
            else:
                if user_input == '1':
                    session.preferred_language = 'fr'
                elif user_input == '2':
                    session.preferred_language = 'en'
                elif user_input == '3':
                    session.preferred_language = 'ar'
                else:
                    return "Saisie invalide. Réessayez :\n1. Français\n2. English\n3. العربية"
                
                # Enregistrer le choix de langue
                session.session_data['language_selected'] = True
                session.save()
                # On réinitialise user_input pour afficher le menu principal
                user_input = ""

        lang = session.preferred_language

        # Traduction des messages système de base
        welcome_msg = {
            'fr': "Sélectionnez votre institution :",
            'en': "Select your institution:",
            'ar': "اختر المؤسسة:"
        }.get(lang, "Sélectionnez votre institution :")

        invalid_choice_msg = {
            'fr': "Choix invalide. Veuillez réessayer :",
            'en': "Invalid choice. Please try again:",
            'ar': "اختيار غير صالح. يرجى المحاولة مرة أخرى:"
        }.get(lang, "Choix invalide. Veuillez réessayer :")

        validation_failed_msg = {
            'fr': "Format incorrect. Veuillez réessayer :",
            'en': "Incorrect format. Please try again:",
            'ar': "صيغة غير صحيحة. يرجى المحاولة مرة أخرى:"
        }.get(lang, "Format incorrect. Veuillez réessayer :")

        # --- Étape 1: Choix de l'Institution ---
        if not session.current_institution:
            institutions = list(Institution.objects.filter(is_active=True))
            
            if not user_input:
                menu = f"{welcome_msg}\n"
                for idx, inst in enumerate(institutions, 1):
                    menu += f"{idx}. {inst.name}\n"
                return menu.strip()
            else:
                try:
                    idx = int(user_input) - 1
                    if 0 <= idx < len(institutions):
                        selected_inst = institutions[idx]
                        session.current_institution = selected_inst
                        session.save()
                        user_input = ""  # Reset user_input for next screen (service selection)
                    else:
                        raise ValueError
                except (ValueError, IndexError):
                    menu = f"{invalid_choice_msg}\n"
                    for idx, inst in enumerate(institutions, 1):
                        menu += f"{idx}. {inst.name}\n"
                    return menu.strip()

        # --- Étape 2: Choix du Service ---
        if not session.current_service:
            services = list(Service.objects.filter(institution=session.current_institution, is_active=True))
            
            if not user_input:
                menu_title = {
                    'fr': "Services de",
                    'en': "Services of",
                    'ar': "خدمات"
                }.get(lang, "Services de")
                
                menu = f"{menu_title} {session.current_institution.name} :\n"
                for idx, srv in enumerate(services, 1):
                    srv_name = srv.name
                    if lang == 'en':
                        if srv_name == "Consultation du solde": srv_name = "Balance Inquiry"
                        elif srv_name == "Transfert": srv_name = "Transfer"
                        elif srv_name == "Paiement marchand": srv_name = "Merchant Payment"
                    elif lang == 'ar':
                        if srv_name == "Consultation du solde": srv_name = "الاستعلام عن الرصيد"
                        elif srv_name == "Transfert": srv_name = "تحويل"
                        elif srv_name == "Paiement marchand": srv_name = "دفع للتاجر"
                    menu += f"{idx}. {srv_name}\n"
                return menu.strip()
            else:
                try:
                    idx = int(user_input) - 1
                    if 0 <= idx < len(services):
                        selected_srv = services[idx]
                        session.current_service = selected_srv
                        
                        # Récupérer le workflow associé
                        if hasattr(selected_srv, 'workflow') and selected_srv.workflow.start_step:
                            session.current_step = selected_srv.workflow.start_step
                        else:
                            # Pas de workflow configuré pour ce service
                            error_no_wf = {
                                'fr': "Service non disponible actuellement.",
                                'en': "Service currently unavailable.",
                                'ar': "الخدمة غير متوفرة حاليا."
                            }.get(lang, "Service non disponible actuellement.")
                            USSDSessionManager.close_session(session)
                            return f"END {error_no_wf}"
                            
                        session.save()
                        user_input = ""  # Reset user_input for starting step
                    else:
                        raise ValueError
                except (ValueError, IndexError):
                    menu_title = {
                        'fr': "Services de",
                        'en': "Services of",
                        'ar': "خدمات"
                    }.get(lang, "Services de")
                    
                    menu = f"{invalid_choice_msg}\n"
                    for idx, srv in enumerate(services, 1):
                        srv_name = srv.name
                        if lang == 'en':
                            if srv_name == "Consultation du solde": srv_name = "Balance Inquiry"
                            elif srv_name == "Transfert": srv_name = "Transfer"
                            elif srv_name == "Paiement marchand": srv_name = "Merchant Payment"
                        elif lang == 'ar':
                            if srv_name == "Consultation du solde": srv_name = "الاستعلام عن الرصيد"
                            elif srv_name == "Transfert": srv_name = "تحويل"
                            elif srv_name == "Paiement marchand": srv_name = "دفع للتاجر"
                        menu += f"{idx}. {srv_name}\n"
                    return menu.strip()

        # --- Étape 3: Exécution des Étapes du Workflow ---
        current_step = session.current_step
        
        while current_step:
            # Si nous avons de l'input utilisateur à traiter pour l'étape courante
            if user_input:
                # 1. Validation de l'input (pour les étapes INPUT)
                if current_step.step_type == 'INPUT' and current_step.validation_regex:
                    if not re.match(current_step.validation_regex, user_input):
                        prompt = cls.get_prompt_text(current_step, lang)
                        prompt = cls.interpolate_variables(prompt, session)
                        return f"{validation_failed_msg}\n{prompt}"
                
                # 2. Sauvegarde de la variable
                if current_step.variable_name:
                    USSDSessionManager.save_input(session, current_step.variable_name, user_input)
                
                # 3. Détermination de l'étape suivante (Transition)
                next_step = None
                
                # Vérifier s'il y a une branche conditionnelle (surtout pour SELECT)
                branch = WorkflowStepBranch.objects.filter(step=current_step, condition_value=user_input).first()
                if branch:
                    next_step = branch.next_step
                else:
                    # Si c'était un SELECT et qu'on ne trouve pas la branche, c'est un choix invalide
                    if current_step.step_type == 'SELECT':
                        prompt = cls.get_prompt_text(current_step, lang)
                        prompt = cls.interpolate_variables(prompt, session)
                        return f"{invalid_choice_msg}\n{prompt}"
                    
                    # Sinon, utiliser l'étape par défaut
                    next_step = current_step.next_step_default
                
                # Mettre à jour l'étape courante en base
                session.current_step = next_step
                session.save()
                current_step = next_step
                user_input = ""  # Consommé
                
            # Si pas d'input (on vient d'entrer dans l'étape ou on fait un traitement interne)
            if current_step:
                if current_step.step_type in ['INPUT', 'SELECT']:
                    prompt = cls.get_prompt_text(current_step, lang)
                    prompt = cls.interpolate_variables(prompt, session)
                    return f"{prompt}"
                
                elif current_step.step_type == 'API_CALL':
                    # L'appel d'API se fait silencieusement.
                    # Pour l'instant, on prépare un bouchon de routage vers les connecteurs (Phase 4).
                    # On exécute l'intégration
                    from routing.dispatcher import ConnectorDispatcher
                    try:
                        result = ConnectorDispatcher.dispatch(session)
                        # Injecter le résultat de l'API dans les données de session
                        for key, val in result.items():
                            USSDSessionManager.save_input(session, key, val)
                    except Exception as e:
                        USSDSessionManager.save_input(session, 'api_success', 'False')
                        USSDSessionManager.save_input(session, 'api_error', str(e))
                    
                    # Passer directement à l'étape suivante
                    next_step = current_step.next_step_default
                    session.current_step = next_step
                    session.save()
                    current_step = next_step
                
                elif current_step.step_type == 'END':
                    prompt = cls.get_prompt_text(current_step, lang)
                    prompt = cls.interpolate_variables(prompt, session)
                    USSDSessionManager.close_session(session)
                    return f"END {prompt}"

        # Écran de secours si le workflow s'arrête de manière inattendue
        fallback_msg = {
            'fr': "Une erreur est survenue. Session fermée.",
            'en': "An error occurred. Session closed.",
            'ar': "حدث خطأ. تم إغلاق الجلسة."
        }.get(lang, "Une erreur est survenue. Session fermée.")
        USSDSessionManager.close_session(session)
        return f"END {fallback_msg}"
