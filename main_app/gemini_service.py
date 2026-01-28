"""
Service d'intégration avec l'API Gemini 3
Gère toutes les interactions avec le modèle d'IA
"""
import google.generativeai as genai
from django.conf import settings
import json
import base64
from PIL import Image
import io

# Configuration de l'API
genai.configure(api_key=settings.GOOGLE_API_KEY)


class GeminiService:
    """Service principal pour interagir avec Gemini 3"""
    
    def __init__(self, model_name="gemini-2.0-flash-exp"):
        """
        Initialise le service Gemini
        Utilise gemini-2.0-flash-exp pour la vitesse et les capacités multimodales
        """
        self.model = genai.GenerativeModel(model_name)
        self.chat = None
    
    def analyze_video(self, video_file, context=""):
        """
        Analyse une vidéo et extrait les concepts clés
        
        Args:
            video_file: Fichier vidéo uploadé
            context: Contexte additionnel fourni par l'utilisateur
        
        Returns:
            dict: Analyse complète avec concepts, timestamps, questions
        """
        try:
            # Upload de la vidéo vers Gemini
            video_data = genai.upload_file(video_file.path)
            
            prompt = f"""
            Analyse cette vidéo éducative en profondeur. {context}
            
            Fournis une réponse structurée en JSON avec:
            1. "summary": Un résumé complet du contenu
            2. "key_concepts": Liste des concepts principaux abordés
            3. "difficulty_level": Niveau estimé (beginner/intermediate/advanced)
            4. "timestamps": Moments clés avec description
            5. "interactive_questions": 5-7 questions à poser pendant le visionnage
               Format: [{{"timestamp": "MM:SS", "question": "...", "hint": "...", "answer": "..."}}]
            6. "prerequisites": Connaissances préalables recommandées
            """
            
            response = self.model.generate_content([video_data, prompt])
            
            # Parse la réponse JSON
            analysis = json.loads(response.text)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_image_problem(self, image_file, subject_hint=""):
        """
        Analyse une image d'un problème (math, physique, code, etc.)
        
        Args:
            image_file: Image du problème
            subject_hint: Indice sur le domaine (optionnel)
        
        Returns:
            dict: Analyse du problème avec guidance pas-à-pas
        """
        try:
            # Lire l'image
            img = Image.open(image_file)
            
            prompt = f"""
            Tu es un tuteur expert utilisant la méthode socratique.
            Analyse ce problème {subject_hint} et fournis une réponse JSON avec:
            
            1. "problem_type": Type de problème identifié
            2. "difficulty": Niveau de difficulté (1-10)
            3. "concepts_needed": Liste des concepts requis
            4. "solution_steps": Liste d'étapes (sans révéler la solution complète)
               Format: [{{"step": 1, "hint": "...", "question": "...", "concepts": [...]}}]
            5. "final_answer": La solution complète (sera cachée initialement)
            6. "similar_problems": 3 problèmes similaires pour pratiquer
            
            IMPORTANT: Guide l'étudiant, ne donne pas directement la réponse!
            """
            
            response = self.model.generate_content([img, prompt])
            
            analysis = json.loads(response.text)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_document(self, document_file, focus_areas=""):
        """
        Analyse un document et crée une carte conceptuelle
        
        Args:
            document_file: Document PDF/texte
            focus_areas: Domaines d'intérêt spécifiques
        
        Returns:
            dict: Carte conceptuelle et quiz adaptatif
        """
        try:
            # Upload du document
            doc_data = genai.upload_file(document_file.path)
            
            prompt = f"""
            Analyse ce document académique/technique en profondeur.
            {f"Focus sur: {focus_areas}" if focus_areas else ""}
            
            Fournis une réponse JSON avec:
            1. "summary": Résumé exécutif du document
            2. "main_topics": Liste des sujets principaux
            3. "concept_map": 
               - "nodes": [{{"id": "unique_id", "label": "Concept", "level": 1-3, "description": "..."}}]
               - "edges": [{{"from": "id1", "to": "id2", "relationship": "..."}}]
            4. "key_definitions": Dictionnaire des termes importants
            5. "quiz_questions": 10 questions adaptatives de différents niveaux
               Format: [{{"level": "easy/medium/hard", "question": "...", "options": [...], "correct": 0, "explanation": "..."}}]
            6. "analogies": Analogies pour simplifier les concepts complexes
            7. "further_reading": Suggestions de lectures complémentaires
            """
            
            response = self.model.generate_content([doc_data, prompt])
            
            analysis = json.loads(response.text)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def creative_workshop(self, image_file, creative_goal=""):
        """
        Atelier créatif: analyse un design/esquisse et propose des améliorations
        
        Args:
            image_file: Image de l'esquisse/design
            creative_goal: Objectif créatif de l'utilisateur
        
        Returns:
            dict: Feedback créatif avec suggestions
        """
        try:
            img = Image.open(image_file)
            
            prompt = f"""
            Tu es un mentor créatif expert en design, architecture, et arts visuels.
            Analyse cette création/esquisse. {creative_goal}
            
            Fournis une réponse JSON avec:
            1. "analysis": Analyse détaillée de ce qui est présenté
            2. "strengths": Points forts du design (3-5 éléments)
            3. "improvements": Suggestions d'amélioration (5-7 éléments)
               Format: [{{"aspect": "...", "suggestion": "...", "why": "...", "priority": "high/medium/low"}}]
            4. "design_principles": Principes de design applicables
            5. "variations": 3 variations/alternatives à explorer
            6. "technique_tips": Conseils techniques spécifiques
            7. "inspiration": Références/artistes similaires
            8. "next_steps": Plan d'action pour développer le projet
            """
            
            response = self.model.generate_content([img, prompt])
            
            analysis = json.loads(response.text)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def start_interactive_session(self, context, user_level="intermediate"):
        """
        Démarre une session de chat interactive
        
        Args:
            context: Contexte de la session (résumé de l'analyse précédente)
            user_level: Niveau de l'utilisateur
        
        Returns:
            chat: Session de chat Gemini
        """
        system_instruction = f"""
        Tu es NeuralSync AI, un tuteur adaptatif expert.
        
        Contexte de la session: {context}
        Niveau de l'utilisateur: {user_level}
        
        Principes:
        1. Utilise la méthode socratique - guide avec des questions
        2. Adapte ton langage au niveau de l'utilisateur
        3. Fournis des exemples concrets et des analogies
        4. Encourage et célèbre les progrès
        5. Détecte les lacunes de compréhension et ajuste
        6. Sois enthousiaste et engageant
        
        Format de réponse:
        - Concis mais complet
        - Structure claire
        - Emojis pour l'engagement (modérément)
        """
        
        self.chat = self.model.start_chat(history=[])
        
        # Message initial du système
        initial_response = self.chat.send_message(system_instruction)
        
        return self.chat
    
    def send_message(self, message, chat_session=None):
        """
        Envoie un message dans une session interactive
        
        Args:
            message: Message de l'utilisateur
            chat_session: Session de chat (optionnel, utilise self.chat si None)
        
        Returns:
            str: Réponse de Gemini
        """
        chat = chat_session or self.chat
        
        if not chat:
            raise ValueError("No active chat session. Call start_interactive_session first.")
        
        response = chat.send_message(message)
        
        return response.text
    
    def evaluate_answer(self, question, user_answer, correct_answer, context=""):
        """
        Évalue la réponse d'un utilisateur et fournis un feedback détaillé
        
        Args:
            question: La question posée
            user_answer: Réponse de l'utilisateur
            correct_answer: Réponse correcte
            context: Contexte additionnel
        
        Returns:
            dict: Évaluation avec feedback
        """
        prompt = f"""
        Évalue cette réponse d'étudiant avec bienveillance et pédagogie.
        {context}
        
        Question: {question}
        Réponse de l'étudiant: {user_answer}
        Réponse attendue: {correct_answer}
        
        Fournis une réponse JSON avec:
        1. "is_correct": true/false
        2. "correctness_percentage": 0-100 (peut être partiel)
        3. "feedback": Feedback constructif et encourageant
        4. "what_was_good": Ce qui était bien dans la réponse
        5. "what_to_improve": Points d'amélioration spécifiques
        6. "hint_for_next_time": Conseil pour des questions similaires
        7. "encouragement": Message motivant personnalisé
        """
        
        response = self.model.generate_content(prompt)
        
        evaluation = json.loads(response.text)
        
        return evaluation
    
    def generate_practice_problems(self, topic, difficulty, count=5):
        """
        Génère des problèmes de pratique sur un sujet
        
        Args:
            topic: Sujet/concept
            difficulty: Niveau de difficulté
            count: Nombre de problèmes à générer
        
        Returns:
            list: Liste de problèmes
        """
        prompt = f"""
        Génère {count} problèmes de pratique sur: {topic}
        Niveau de difficulté: {difficulty}
        
        Fournis une réponse JSON avec:
        "problems": [
            {{
                "id": 1,
                "problem": "Énoncé du problème",
                "type": "multiple_choice/open_ended/true_false",
                "options": [...] (si applicable),
                "solution": "Solution détaillée",
                "hints": ["hint1", "hint2", ...],
                "learning_objective": "Ce que ce problème enseigne"
            }},
            ...
        ]
        """
        
        response = self.model.generate_content(prompt)
        
        result = json.loads(response.text)
        
        return result.get("problems", [])
    
    def adaptive_difficulty_suggestion(self, user_stats):
        """
        Suggère le niveau de difficulté optimal basé sur les performances
        
        Args:
            user_stats: Statistiques de l'utilisateur (dict)
        
        Returns:
            dict: Recommandations de difficulté
        """
        prompt = f"""
        Analyse ces statistiques d'apprentissage et recommande le niveau optimal:
        
        {json.dumps(user_stats, indent=2)}
        
        Fournis une réponse JSON avec:
        1. "recommended_level": Level recommandé
        2. "reasoning": Explication de la recommandation
        3. "strengths": Domaines de force identifiés
        4. "areas_to_focus": Domaines à travailler
        5. "learning_pace": Rythme d'apprentissage (slow/medium/fast)
        6. "motivation_message": Message personnalisé motivant
        """
        
        response = self.model.generate_content(prompt)
        
        recommendation = json.loads(response.text)
        
        return recommendation


# Instance singleton du service
gemini_service = GeminiService()
