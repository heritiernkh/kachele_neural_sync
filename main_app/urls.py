from django.urls import path
from . import views

app_name = 'main_app'

urlpatterns = [
    # Pages principales
    path('', views.index, name='index'),
    path('demo/', views.demo, name='demo'),
    path('features/', views.features, name='features'),
    path('about/', views.about, name='about'),
    
    # API endpoints
    path('api/session/create/', views.create_session, name='create_session'),
    path('api/session/<uuid:session_id>/stats/', views.get_session_stats, name='session_stats'),
    path('api/upload/', views.upload_content, name='upload_content'),
    path('api/ask/', views.ask_question, name='ask_question'),
    path('api/answer/', views.submit_answer, name='submit_answer'),
    path('api/hint/', views.request_hint, name='request_hint'),
    path('api/practice/generate/', views.generate_practice, name='generate_practice'),
]
