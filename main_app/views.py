from django.shortcuts import render
from django.http import JsonResponse, StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import json
import os
from .models import LearningSession, UploadedContent, Interaction, ConceptMap, UserProgress
from .gemini_service import gemini_service
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


def index(request):
    """Page d'accueil de NeuralSync Live"""
    return render(request, 'main_app/index.html')


def demo(request):
    """Page de démonstration principale"""
    return render(request, 'main_app/demo.html')


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
        
        try:
            # Créer l'objet UploadedContent (sans fichier physique permanent pour l'instant)
            # On stocke juste le nom pour référence
            uploaded_content = UploadedContent.objects.create(
                session=session,
                content_type=content_type,
                file=None, # Pas de stockage permanent Django
                filename=file.name,
                file_size=file.size
            )
            
            # Analyser avec Gemini selon le mode (en passant le chemin temporaire)
            # Note: Il faut adapter GeminiService pour accepter un path str
            
            # Objet simulant un File Django pour compatibilité si nécessaire, 
            # mais mieux vaut passer le path direct si le service est adapté.
            # Pour l'instant on garde la logique d'appel mais on passera un objet qui a un attribut .path
            
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
                # Sauvegarder l'analyse
                uploaded_content.analysis_completed = True
                uploaded_content.analysis_summary = json.dumps(analysis_result['analysis'])
                
                # Extraire les concepts clés si disponibles
                if 'key_concepts' in analysis_result['analysis']:
                    uploaded_content.key_concepts = analysis_result['analysis']['key_concepts']
                
                uploaded_content.save()
                
                # Si c'est un document, créer la carte conceptuelle
                if session.mode == 'document' and 'concept_map' in analysis_result['analysis']:
                    ConceptMap.objects.create(
                        session=session,
                        nodes=analysis_result['analysis']['concept_map'].get('nodes', []),
                        edges=analysis_result['analysis']['concept_map'].get('edges', [])
                    )
                
                return JsonResponse({
                    'success': True,
                    'upload_id': str(uploaded_content.id),
                    'analysis': analysis_result['analysis']
                })
            else:
                error_msg = analysis_result.get('error', 'Analysis failed') if analysis_result else 'No analysis performed'
                return JsonResponse({
                    'success': False,
                    'error': error_msg
                }, status=500)
                
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
        traceback.print_exc()  # Affiche l'erreur complète dans la console serveur
        print(f"Error in upload_content: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
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
        latest_upload = session.uploads.filter(analysis_completed=True).last()
        
        if not latest_upload:
            return JsonResponse({
                'success': False,
                'error': 'No analyzed content found for this session'
            }, status=400)
        
        analysis_summary = json.loads(latest_upload.analysis_summary)
        
        # Préparer le contexte pour Gemini
        full_context = f"""
        Session Mode: {session.get_mode_display()}
        Content Analysis: {json.dumps(analysis_summary, indent=2)}
        Additional Context: {json.dumps(context, indent=2)}
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
            'error': 'Session not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


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
