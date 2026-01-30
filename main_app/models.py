from django.db import models
from django.contrib.auth.models import User
import uuid

class LearningSession(models.Model):
    """Session d'apprentissage pour suivre la progression de l'utilisateur"""
    MODE_CHOICES = [
        ('video', 'Learn While You Watch'),
        ('problem', 'Visual Problem Solver'),
        ('document', 'Document Intelligence'),
        ('creative', 'Creative Workshop'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES)
    title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration_seconds = models.IntegerField(default=0)
    completed = models.BooleanField(default=False)
    
    # Statistiques
    questions_asked = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    hints_used = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_mode_display()} - {self.title}"
    
    @property
    def accuracy_rate(self):
        if self.questions_asked == 0:
            return 0
        return (self.correct_answers / self.questions_asked) * 100


class UploadedContent(models.Model):
    """Contenu uploadé par l'utilisateur (vidéos, images, documents)"""
    CONTENT_TYPE_CHOICES = [
        ('video', 'Video'),
        ('image', 'Image'),
        ('document', 'Document'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='uploads')
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES)
    file = models.FileField(upload_to='uploads/%Y/%m/%d/', null=True, blank=True)
    filename = models.CharField(max_length=255)
    file_size = models.BigIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # Analyse Gemini
    analysis_completed = models.BooleanField(default=False)
    analysis_summary = models.TextField(blank=True)
    key_concepts = models.JSONField(default=list, blank=True)
    
    def __str__(self):
        return f"{self.filename} - {self.content_type}"


class Interaction(models.Model):
    """Interaction entre l'utilisateur et Gemini"""
    INTERACTION_TYPE_CHOICES = [
        ('question', 'Question'),
        ('answer', 'Answer'),
        ('hint', 'Hint'),
        ('explanation', 'Explanation'),
        ('feedback', 'Feedback'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPE_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Contenu
    gemini_prompt = models.TextField()
    gemini_response = models.TextField()
    user_response = models.TextField(blank=True)
    is_correct = models.BooleanField(null=True, blank=True)
    
    # Contexte
    context_data = models.JSONField(default=dict, blank=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.get_interaction_type_display()} at {self.timestamp}"


class ConceptMap(models.Model):
    """Carte conceptuelle générée pour un document"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(LearningSession, on_delete=models.CASCADE, related_name='concept_maps')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Données de la carte
    nodes = models.JSONField(default=list)  # Liste des concepts
    edges = models.JSONField(default=list)  # Relations entre concepts
    
    def __str__(self):
        return f"Concept Map for {self.session.title}"


class UserProgress(models.Model):
    """Suivi de la progression globale de l'utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='progress')
    
    # Statistiques globales
    total_sessions = models.IntegerField(default=0)
    total_time_minutes = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    total_correct = models.IntegerField(default=0)
    
    # Niveaux par domaine (JSON pour flexibilité)
    subject_levels = models.JSONField(default=dict, blank=True)
    
    # Préférences d'apprentissage detectées
    learning_style = models.CharField(max_length=50, blank=True)
    preferred_difficulty = models.CharField(max_length=20, default='medium')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Progress for {self.user.username}"
    
    @property
    def overall_accuracy(self):
        if self.total_questions == 0:
            return 0
        return (self.total_correct / self.total_questions) * 100
