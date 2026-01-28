from django.contrib import admin
from .models import (
    LearningSession,
    UploadedContent,
    Interaction,
    ConceptMap,
    UserProgress
)


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'mode', 'user', 'created_at', 'duration_seconds', 'accuracy_rate', 'completed')
    list_filter = ('mode', 'completed', 'created_at')
    search_fields = ('title', 'user__username')
    readonly_fields = ('id', 'created_at', 'updated_at', 'accuracy_rate')
    
    fieldsets = (
        ('Session Info', {
            'fields': ('id', 'user', 'mode', 'title', 'completed')
        }),
        ('Statistics', {
            'fields': ('duration_seconds', 'questions_asked', 'correct_answers', 'hints_used', 'accuracy_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )


@admin.register(UploadedContent)
class UploadedContentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'content_type', 'session', 'file_size', 'analysis_completed', 'uploaded_at')
    list_filter = ('content_type', 'analysis_completed', 'uploaded_at')
    search_fields = ('filename', 'session__title')
    readonly_fields = ('id', 'uploaded_at', 'file_size')


@admin.register(Interaction)
class InteractionAdmin(admin.ModelAdmin):
    list_display = ('session', 'interaction_type', 'timestamp', 'is_correct')
    list_filter = ('interaction_type', 'is_correct', 'timestamp')
    search_fields = ('session__title', 'gemini_prompt', 'user_response')
    readonly_fields = ('id', 'timestamp')
    
    fieldsets = (
        ('Interaction Info', {
            'fields': ('id', 'session', 'interaction_type', 'timestamp', 'is_correct')
        }),
        ('Content', {
            'fields': ('gemini_prompt', 'gemini_response', 'user_response')
        }),
        ('Context', {
            'fields': ('context_data',)
        }),
    )


@admin.register(ConceptMap)
class ConceptMapAdmin(admin.ModelAdmin):
    list_display = ('session', 'created_at')
    search_fields = ('session__title',)
    readonly_fields = ('id', 'created_at')


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_sessions', 'total_time_minutes', 'overall_accuracy', 'learning_style')
    search_fields = ('user__username',)
    readonly_fields = ('created_at', 'updated_at', 'overall_accuracy')
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Global Statistics', {
            'fields': ('total_sessions', 'total_time_minutes', 'total_questions', 'total_correct', 'overall_accuracy')
        }),
        ('Learning Profile', {
            'fields': ('learning_style', 'preferred_difficulty', 'subject_levels')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
