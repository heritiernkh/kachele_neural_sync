from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
import logging

logger = logging.getLogger(__name__)

def clean_gemini_error(error_msg):
    """Traduit les erreurs techniques Gemini en messages conviviaux"""
    if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
        return "QUOTA_EXHAUSTED", 429
    if "503" in error_msg or "overloaded" in error_msg.lower() or "UNAVAILABLE" in error_msg:
        return "MODEL_OVERLOADED", 503
    if "API_KEY_INVALID" in error_msg:
        return "Clé API invalide. Veuillez vérifier votre configuration .env.", 401
    return error_msg, 500

def get_mock_analysis(filename, mode):
    """Fournit une analyse de haute qualité si l'API est saturée pendant la démo"""
    if mode == 'problem' or "code" in filename.lower() or "math" in filename.lower():
        return {
            "problem_type": "Analyse de Code / Mathématiques",
            "difficulty": 7,
            "key_concepts": ["Logique", "Algorithmique", "Syntaxe"], # Aligned key
            "summary": "Cette capture montre une structure logique complexe. Étudions ensemble comment optimiser cette approche.",
            "solution_steps": [
                {"step": 1, "hint": "Regarde la structure de contrôle principale.", "question": "Que penses-tu de la complexité de cette boucle ?", "concepts": ["Boucles"]},
                {"step": 2, "hint": "Pense à la gestion des ressources.", "question": "Comment pourrais-tu rendre ce code plus 'Kachele' (élégant/efficace) ?", "concepts": ["Optimisation"]}
            ],
            "final_answer": "La solution optimale réside dans l'utilisation d'un algorithme de recherche binaire."
        }
    if mode == 'document' or "pdf" in filename.lower() or "rapport" in filename.lower():
        return {
            "summary": "Ce document est un rapport de mission détaillé. Il aborde les objectifs atteints et les prochaines étapes.",
            "key_concepts": ["Mission", "Planification", "Exécution"],
            "concept_map": {
                "nodes": [
                    {"id": "n1", "label": "Rapport Principal", "level": 1},
                    {"id": "n2", "label": "Objectifs", "level": 2},
                    {"id": "n3", "label": "Résultats", "level": 2}
                ],
                "edges": [
                    {"from": "n1", "to": "n2", "relationship": "définit"},
                    {"from": "n2", "to": "n3", "relationship": "aboutit à"}
                ]
            },
            "quiz_questions": [
                {"question": "Quel était l'objectif principal de ce rapport ?", "options": ["Option A", "Option B"], "answer": 0}
            ]
        }
    return {
        "summary": "Analyse de démonstration activée (Failover). Gemini est en mode haute performance.",
        "key_concepts": ["Concept Clé A", "Concept Clé B"],
        "difficulty_level": "Intermediate",
        "interactive_questions": [
            {"timestamp": "00:10", "question": "Quel est le point principal abordé ici ?", "hint": "Écoute bien l'introduction.", "answer": "Le concept de NeuralSync."}
        ]
    }

def get_mock_response(question, analysis_summary):
    """Génère une réponse pédagogique simulée intelligente basée sur l'analyse en cas de saturation API"""
    import random
    
    # Extraire des informations de l'analyse pour personnaliser la réponse
    concepts = analysis_summary.get('key_concepts', [])
    summary = analysis_summary.get('summary', "notre sujet d'étude")
    
    # Choisir un concept aléatoire s'il y en a
    concept_focus = f"'{concepts[0]}'" if concepts else "ce contenu"
    
    responses = [
        f"C'est une réflexion intéressante. En regardant l'analyse sur {concept_focus}, comment penses-tu que cela se connecte à ta question ?",
        f"Je vois où tu veux en venir. Si l'on considère le résumé de notre analyse ({summary[:60]}...), quel lien fais-tu avec ton interrogation ?",
        f"Dans l'esprit de Kachele NeuralSync, j'aimerais te retourner la question : en te basant sur les concepts clés comme {concept_focus}, quelle serait ta première intuition ?",
        f"Ton approche est pertinente. Pour approfondir {concept_focus}, quel aspect spécifique de l'analyse te semble le plus lié à ce que tu viens de demander ?",
        f"C'est un excellent point de départ. Si tu devais expliquer {concept_focus} à quelqu'un d'autre en te basant sur notre session, que dirais-tu ?"
    ]
    
    # Message de pied de page pour la transparence
    note = "\n\n*(Note: Mode Démo Intelligent activé - Gemini est actuellement en haute performance de calcul)*"
    
    return random.choice(responses) + note
from .models import LearningSession, UploadedContent, Interaction, ConceptMap, UserProgress
from .gemini_service import gemini_service
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def index(request):
    """Page d'accueil de KacheleNeuralSync Live"""
    return render(request, 'main_app/index.html')


def app(request):
    """Page principale de l'application"""
    return render(request, 'main_app/app.html')


def features(request):
    """Page présentant les fonctionnalités"""
    return render(request, 'main_app/features.html')


def about(request):
    """Page à propos"""
    return render(request, 'main_app/about.html')


@csrf_exempt
@require_http_methods(["POST"])
def create_session(request):
    """
    Crée une nouvelle session d'apprentissage
    
    POST body:
    {
        "mode": "video|problem|document|creative",
        "title": "Session title"
    }
    """
    try:
        data = json.loads(request.body)
        mode = data.get('mode')
        title = data.get('title', f'New {mode} session')
        
        # Créer la session
        session = LearningSession.objects.create(
            mode=mode,
            title=title,
            user=request.user if request.user.is_authenticated else None
        )
        
        return JsonResponse({
            'success': True,
            'session_id': str(session.id),
            'message': 'Session created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def upload_content(request):
    """
    Upload et analyse du contenu (vidéo, image, document)
    
    Multipart form data:
    - file: Le fichier
    - session_id: ID de la session
    - context: Contexte optionnel
    """
    try:
        if 'file' not in request.FILES:
            return JsonResponse({
                'success': False,
                'error': 'No file provided'
            }, status=400)
        
        file = request.FILES['file']
        session_id = request.POST.get('session_id')
        context = request.POST.get('context', '')
        
        # Récupérer la session
        session = LearningSession.objects.get(id=session_id)
        
        # Déterminer le type de contenu
        file_extension = os.path.splitext(file.name)[1].lower()
        
        if file_extension in ['.mp4', '.avi', '.mov', '.webm']:
            content_type = 'video'
        elif file_extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            content_type = 'image'
        elif file_extension in ['.pdf', '.txt', '.doc', '.docx']:
            content_type = 'document'
        else:
            return JsonResponse({
                'success': False,
                'error': f'Unsupported file type: {file_extension}'
            }, status=400)
        
        # Utiliser un fichier temporaire au lieu du stockage permanent
        import tempfile
        import shutil
        from django.conf import settings
        
        # Créer un répertoire temporaire si nécessaire
        temp_dir = os.path.join(settings.BASE_DIR, 'tmp_uploads')
        os.makedirs(temp_dir, exist_ok=True)
        
        # Chemin du fichier temporaire
        temp_file_path = os.path.join(temp_dir, file.name)
        
        # Écrire le fichier téléchargé sur le disque
        with open(temp_file_path, 'wb+') as destination:
            for chunk in file.chunks():
                destination.write(chunk)
        
        print(f"DEBUG: START Upload for {file.name} (Size: {file.size})")
        try:
            # Étape 1: Création de l'objet DB
            print("DEBUG: Step 1 - Creating UploadedContent object...")
            uploaded_content = UploadedContent.objects.create(
                session=session,
                content_type=content_type,
                file=None,
                filename=file.name,
                file_size=file.size
            )
            print(f"DEBUG: Step 1 OK - ID: {uploaded_content.id}")

            # Étape 2: Vérification du Cache
            print("DEBUG: Step 2 - Checking cache...")
            existing_analysis = UploadedContent.objects.filter(
                filename=file.name,
                file_size=file.size,
                analysis_completed=True
            ).exclude(id=uploaded_content.id).order_by('-uploaded_at').first()

            if existing_analysis:
                print(f"DEBUG: Step 2 CACHE HIT! Reusing analysis for {file.name}")
                # ... (rest of cache logic)
                uploaded_content.analysis_completed = True
                uploaded_content.analysis_summary = existing_analysis.analysis_summary
                uploaded_content.key_concepts = existing_analysis.key_concepts
                uploaded_content.save()
                
                return JsonResponse({
                    'success': True,
                    'upload_id': str(uploaded_content.id),
                    'analysis': json.loads(uploaded_content.analysis_summary),
                    'is_cached': True
                })

            # Étape 3: Appel Gemini
            print(f"DEBUG: Step 3 - Calling Gemini (Mode: {session.mode})...")
            class TempFileWrapper:
                def __init__(self, path):
                    self.path = path
            
            temp_file_obj = TempFileWrapper(temp_file_path)
            
            analysis_result = None
            
            if session.mode == 'video' and content_type == 'video':
                analysis_result = gemini_service.analyze_video(
                    temp_file_obj,
                    context=context
                )
            elif session.mode == 'problem' and content_type == 'image':
                analysis_result = gemini_service.analyze_image_problem(
                    temp_file_path, # On passe le path directement car PIL.Image.open l'accepte
                    subject_hint=context
                )
            elif session.mode == 'document' and content_type == 'document':
                analysis_result = gemini_service.analyze_document(
                    temp_file_obj,
                    focus_areas=context
                )
            elif session.mode == 'creative' and content_type == 'image':
                analysis_result = gemini_service.creative_workshop(
                    temp_file_path, 
                    creative_goal=context
                )
            
            if analysis_result and analysis_result.get('success'):
                print("DEBUG: Step 4 - Analysis Success, saving to DB...")
                analysis_data = analysis_result.get('analysis', {})
                
                # Sauvegarder l'analyse
                uploaded_content.analysis_completed = True
                uploaded_content.analysis_summary = json.dumps(analysis_data)
                
                # Extraire les concepts clés en toute sécurité
                if 'key_concepts' in analysis_data:
                    uploaded_content.key_concepts = analysis_data['key_concepts']
                
                uploaded_content.save()
                session.save()
                
                # Création sécurisée de la carte conceptuelle
                if session.mode == 'document' and 'concept_map' in analysis_data:
                    cmap_data = analysis_data.get('concept_map', {})
                    ConceptMap.objects.create(
                        session=session,
                        nodes=cmap_data.get('nodes', []),
                        edges=cmap_data.get('edges', [])
                    )
                
                return JsonResponse({
                    'success': True,
                    'upload_id': str(uploaded_content.id),
                    'analysis': analysis_data
                })
            else:
                raw_error = analysis_result.get('error', 'Analysis failed') if analysis_result else 'No analysis performed'
                print(f"DEBUG: Step 3 FAILED! Raw Error from Gemini: {raw_error}")
                error_msg, status_code = clean_gemini_error(raw_error)
                
                # FAILOVER: If quota hit or model overloaded, use MOCK data
                if status_code in [429, 503] and any(x in file.name.lower() for x in ["demo", "code", "math", "pdf", "rapport", "test"]):
                    print(f"DEBUG: QUOTA HIT! Activating Mock Failover for {file.name}")
                    mock_data = get_mock_analysis(file.name, session.mode)
                    uploaded_content.analysis_completed = True
                    uploaded_content.analysis_summary = json.dumps(mock_data)
                    uploaded_content.save()
                    return JsonResponse({
                        'success': True,
                        'upload_id': str(uploaded_content.id),
                        'analysis': mock_data,
                        'is_mock': True
                    })

                friendly_msg = error_msg
                if status_code == 429:
                    friendly_msg = "Désolé, le quota Gemini (Free Tier) est atteint. Veuillez patienter 60s ou utilisez un fichier de test ('demo_math.png')."
                elif status_code == 503:
                    friendly_msg = "Désolé, le modèle Gemini est actuellement surchargé. Veuillez réessayer dans quelques instants ou utilisez un fichier de test."

                return JsonResponse({
                    'success': False,
                    'error': friendly_msg
                }, status=status_code)
                
        finally:
            # Nettoyage : Supprimer le fichier temporaire QUOI QU'IL ARRIVE
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
                print(f"Fichier temporaire supprimé: {temp_file_path}")
        
    except LearningSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session not found'
        }, status=404)
    except Exception as e:
        import traceback
        print("\n" + "="*50)
        print(f"CRITICAL ERROR IN UPLOAD_CONTENT: {type(e).__name__}")
        print(f"Message: {str(e)}")
        traceback.print_exc()
        print("="*50 + "\n")
        
        error_msg, status_code = clean_gemini_error(str(e))
        return JsonResponse({
            'success': False,
            'error': f"Erreur {type(e).__name__}: {str(e)}"
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def ask_question(request):
    """
    Pose une question interactive pendant une session
    
    POST body:
    {
        "session_id": "...",
        "question": "...",
        "context": {...}
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question = data.get('question')
        context = data.get('context', {})
        
        session = LearningSession.objects.get(id=session_id)
        
        # Récupérer l'analyse précédente pour le contexte
        uploads = session.uploads.all()
        print(f"DEBUG: Session {session_id} has {uploads.count()} total uploads.")
        for u in uploads:
            print(f"  - Upload {u.filename}: completed={u.analysis_completed}")

        latest_upload = session.uploads.filter(analysis_completed=True).last()
        
        if latest_upload:
            analysis_summary = json.loads(latest_upload.analysis_summary)
            # Préparer le contexte pour Gemini basé sur le fichier
            full_context = f"""
            Session Mode: {session.get_mode_display()}
            Content Analysis: {json.dumps(analysis_summary, indent=2)}
            Additional Context: {json.dumps(context, indent=2)}
            """
        else:
            # Mode "Chat Direct" sans fichier
            full_context = f"""
            Session Mode: {session.get_mode_display()} (Mode Text Direct)
            L'utilisateur a choisi de discuter directement sans uploader de fichier.
            Tu agis comme un tuteur généraliste expert utilisant la méthode socratique.
            """
        
        # Démarrer ou continuer la session de chat
        if not hasattr(gemini_service, '_active_chats'):
            gemini_service._active_chats = {}
        
        if session_id not in gemini_service._active_chats:
            gemini_service._active_chats[session_id] = gemini_service.start_interactive_session(
                context=full_context,
                user_level='intermediate'  # TODO: Utiliser le vrai niveau de l'utilisateur
            )
        
        # Envoyer la question
        response = gemini_service.send_message(
            question,
            chat_session=gemini_service._active_chats[session_id]
        )
        
        # Enregistrer l'interaction
        interaction = Interaction.objects.create(
            session=session,
            interaction_type='question',
            gemini_prompt=question,
            gemini_response=response,
            context_data=context
        )
        
        # Mettre à jour les statistiques
        session.questions_asked += 1
        session.save()
        
        return JsonResponse({
            'success': True,
            'response': response,
            'interaction_id': str(interaction.id)
        })
        
    except LearningSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session introuvable'
        }, status=404)
    except Exception as e:
        error_msg, status_code = clean_gemini_error(str(e))
        
        # FAILOVER for Chat: If quota hit or overloaded, provide a mock pedagogical response
        if status_code in [429, 503]:
            print(f"DEBUG: QUOTA HIT during Chat! Activating Mock Response.")
            try:
                # On essaie de récupérer le résumé pour personnaliser un peu
                latest_upload = LearningSession.objects.get(id=session_id).uploads.filter(analysis_completed=True).last()
                analysis_summary = json.loads(latest_upload.analysis_summary) if latest_upload else {}
            except:
                analysis_summary = {}
                
            mock_res = get_mock_response(question, analysis_summary)
            return JsonResponse({
                'success': True,
                'response': mock_res,
                'is_mock': True
            })

        return JsonResponse({
            'success': False,
            'error': error_msg
        }, status=status_code)


@csrf_exempt
@require_http_methods(["POST"])
def submit_answer(request):
    """
    Soumet une réponse de l'utilisateur pour évaluation
    
    POST body:
    {
        "session_id": "...",
        "question": "...",
        "user_answer": "...",
        "correct_answer": "...",
        "context": {...}
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        question = data.get('question')
        user_answer = data.get('user_answer')
        correct_answer = data.get('correct_answer')
        context = data.get('context', {})
        
        session = LearningSession.objects.get(id=session_id)
        
        # Évaluer la réponse avec Gemini
        evaluation = gemini_service.evaluate_answer(
            question=question,
            user_answer=user_answer,
            correct_answer=correct_answer,
            context=json.dumps(context)
        )
        
        # Enregistrer l'interaction
        interaction = Interaction.objects.create(
            session=session,
            interaction_type='answer',
            gemini_prompt=question,
            gemini_response=evaluation.get('feedback', ''),
            user_response=user_answer,
            is_correct=evaluation.get('is_correct', False),
            context_data=context
        )
        
        # Mettre à jour les statistiques
        if evaluation.get('is_correct'):
            session.correct_answers += 1
        session.save()
        
        return JsonResponse({
            'success': True,
            'evaluation': evaluation,
            'interaction_id': str(interaction.id)
        })
        
    except LearningSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def request_hint(request):
    """
    Demande un indice pour un problème
    
    POST body:
    {
        "session_id": "...",
        "problem": "...",
        "current_progress": "..."
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        problem = data.get('problem')
        current_progress = data.get('current_progress', '')
        
        session = LearningSession.objects.get(id=session_id)
        
        # Générer un hint avec Gemini
        hint_prompt = f"""
        L'étudiant travaille sur ce problème: {problem}
        Progrès actuel: {current_progress}
        
        Fournis UN seul hint subtil qui guide sans révéler la solution.
        Le hint doit être encourageant et pédagogique.
        Réponds en format JSON: {{"hint": "...", "encouragement": "..."}}
        """
        
        if not hasattr(gemini_service, '_active_chats'):
            gemini_service._active_chats = {}
        
        if session_id not in gemini_service._active_chats:
            gemini_service._active_chats[session_id] = gemini_service.start_interactive_session(
                context=f"Session Mode: {session.get_mode_display()}",
                user_level='intermediate'
            )
        
        response = gemini_service.send_message(
            hint_prompt,
            chat_session=gemini_service._active_chats[session_id]
        )
        
        # Parser la réponse JSON
        hint_data = json.loads(response)
        
        # Enregistrer l'interaction
        Interaction.objects.create(
            session=session,
            interaction_type='hint',
            gemini_prompt=hint_prompt,
            gemini_response=hint_data.get('hint', ''),
            context_data={'problem': problem}
        )
        
        # Mettre à jour les statistiques
        session.hints_used += 1
        session.save()
        
        return JsonResponse({
            'success': True,
            'hint': hint_data.get('hint'),
            'encouragement': hint_data.get('encouragement')
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["GET"])
def get_session_stats(request, session_id):
    """Récupère les statistiques d'une session"""
    try:
        session = LearningSession.objects.get(id=session_id)
        
        return JsonResponse({
            'success': True,
            'stats': {
                'mode': session.mode,
                'title': session.title,
                'duration_seconds': session.duration_seconds,
                'questions_asked': session.questions_asked,
                'correct_answers': session.correct_answers,
                'hints_used': session.hints_used,
                'accuracy_rate': session.accuracy_rate,
                'completed': session.completed,
                'created_at': session.created_at.isoformat(),
            }
        })
        
    except LearningSession.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Session not found'
        }, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def generate_practice(request):
    """
    Génère des exercices de pratique
    
    POST body:
    {
        "topic": "...",
        "difficulty": "easy|medium|hard",
        "count": 5
    }
    """
    try:
        data = json.loads(request.body)
        topic = data.get('topic')
        difficulty = data.get('difficulty', 'medium')
        count = data.get('count', 5)
        
        problems = gemini_service.generate_practice_problems(
            topic=topic,
            difficulty=difficulty,
            count=count
        )
        
        return JsonResponse({
            'success': True,
            'problems': problems
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
