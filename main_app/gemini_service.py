"""
Service d'intégration avec l'API Gemini 3 (SDK v1.0+)
Gère toutes les interactions avec le modèle d'IA
"""
from google import genai
from google.genai import types
from django.conf import settings
import json
import base64
from PIL import Image
import io
import os

class GeminiService:
    """Service principal pour interagir avec Gemini 3 (Nouveau SDK)"""
    
    def __init__(self, model_name="gemini-3-flash-preview"):
        """
        Initialise le client Gemini
        """
        self.api_key = settings.GOOGLE_API_KEY
        self.model_name = model_name
        self.client = None
        self.chat = None
        self._active_chats = {}  # Pour gérer plusieurs sessions
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"Error initializing Gemini client: {e}")
    
    def _check_config(self):
        """Vérifie si le service est prêt"""
        if not self.api_key:
            return {
                "success": False,
                "error": "API Key not configured. Please add GOOGLE_API_KEY to your .env file."
            }
        if not self.client:
            return {
                "success": False,
                "error": "Client not initialized. Check your API key and internet connection."
            }
        return None

    def analyze_video(self, video_file, context=""):
        """Analyse une vidéo et extrait les concepts clés"""
        config_error = self._check_config()
        if config_error:
            return config_error

        try:
            print(f"DEBUG: SDK Uploading video from {video_file.path}...")
            upload_result = self.client.files.upload(file=video_file.path)
            
            # Attendre que le fichier soit prêt (si nécessaire, le SDK gère souvent ça mieux)
            # Mais pour la vidéo, c'est mieux d'attendre l'état ACTIVE
            import time
            while upload_result.state.name == "PROCESSING":
                time.sleep(2)
                upload_result = self.client.files.get(name=upload_result.name)
                
            if upload_result.state.name == "FAILED":
                raise ValueError("Video processing failed")

            prompt = f"""
            Analyse cette vidéo en profondeur. {context}
            
            Fournis une réponse structurée en JSON avec:
            1. "summary": Un résumé complet du contenu
            2. "key_concepts": Liste des concepts principaux abordés
            3. "difficulty_level": Niveau estimé (beginner/intermediate/advanced)
            4. "timestamps": Moments clés avec description
            5. "interactive_questions": 5-7 questions à poser pendant le visionnage
               Format: [{{"timestamp": "MM:SS", "question": "...", "hint": "...", "answer": "..."}}]
            6. "prerequisites": Connaissances préalables recommandées
            
            Réponds uniquement par le JSON.
            """
            
            # Utilisation de config de génération pour forcer le JSON
            generate_config = types.GenerateContentConfig(
                response_mime_type="application/json"
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[upload_result, prompt],
                config=generate_config
            )
            
            # Parse la réponse JSON
            # Avec le nouveau SDK et response_mime_type, response.text est déjà du JSON propre
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
        """Analyse une image d'un problème"""
        config_error = self._check_config()
        if config_error:
            return config_error

        try:
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
            Réponds uniquement par le JSON.
            """
            
            generate_config = types.GenerateContentConfig(
                response_mime_type="application/json"
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[img, prompt],
                config=generate_config
            )
            
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
        """Analyse un document et crée une carte conceptuelle"""
        config_error = self._check_config()
        if config_error:
            return config_error

        try:
            print(f"DEBUG: SDK Uploading document from {document_file.path}...")
            upload_result = self.client.files.upload(file=document_file.path)
            
            # Attente active si nécessaire pour les gros PDF
            import time
            while upload_result.state.name == "PROCESSING":
                time.sleep(1)
                upload_result = self.client.files.get(name=upload_result.name)
            
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
            
            Réponds uniquement par le JSON.
            """
            
            generate_config = types.GenerateContentConfig(
                response_mime_type="application/json"
            )
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[upload_result, prompt],
                config=generate_config
            )
            
            analysis = json.loads(response.text)
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            print(f"!!! GEMINI SERVICE ERROR in analyze_document: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def creative_workshop(self, image_file, creative_goal=""):
        """Atelier créatif: analyse un design/esquisse"""
        config_error = self._check_config()
        if config_error:
            return config_error

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
            
            Réponds uniquement par le JSON.
            """
            
            generate_config = types.GenerateContentConfig(
                response_mime_type="application/json"
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[img, prompt],
                config=generate_config
            )
            
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
        """Démarre une session de chat interactive"""
        config_error = self._check_config()
        if config_error:
            raise ValueError(config_error['error'])

        system_instruction = f"""
        Tu es Kachele NeuralSync AI, un tuteur adaptatif expert.
        Contexte de la session: {context}
        Niveau de l'utilisateur: {user_level}
        Principes: Socratique, Adaptatif, Enthousiaste.
        """
        
        # Nouveau SDK: client.chats.create
        chat = self.client.chats.create(
            model=self.model_name,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        
        return chat
    
    def send_message(self, message, chat_session=None):
        """Envoie un message dans une session interactive"""
        config_error = self._check_config()
        if config_error:
            return f"Error: {config_error['error']}"

        chat = chat_session or self.chat
        
        if not chat:
            # Fallback si pas de chat session fournie, on en crée une éphémère
            # Mais idéalement views.py doit gérer les sessions
            raise ValueError("No active chat session provided.")
        
        response = chat.send_message(message)
        return response.text
    
    def evaluate_answer(self, question, user_answer, correct_answer, context=""):
        """Évalue la réponse d'un utilisateur"""
        config_error = self._check_config()
        if config_error:
            return {"error": config_error['error']}

        prompt = f"""
        Évalue cette réponse d'étudiant avec bienveillance et pédagogie.
        {context}
        
        Question: {question}
        Réponse de l'étudiant: {user_answer}
        Réponse attendue: {correct_answer}
        
        Fournis une réponse JSON, incluant pourcentage, feedback, what_was_good, what_to_improve.
        """
        
        generate_config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=generate_config
        )
        
        return json.loads(response.text)
    
    def generate_practice_problems(self, topic, difficulty, count=5):
        """Génère des problèmes de pratique"""
        config_error = self._check_config()
        if config_error:
            return []

        prompt = f"""
        Génère {count} problèmes de pratique sur: {topic}
        Niveau de difficulté: {difficulty}
        Format JSON requis: list under key "problems".
        """
        
        generate_config = types.GenerateContentConfig(
            response_mime_type="application/json"
        )
        
        response = self.client.models.generate_content(
            model=self.model_name,
            contents=prompt,
            config=generate_config
        )
        
        result = json.loads(response.text)
        return result.get("problems", [])


# Instance singleton du service
gemini_service = GeminiService()
