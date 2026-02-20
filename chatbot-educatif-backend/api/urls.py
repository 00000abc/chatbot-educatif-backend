# api/urls.py - CORRIGEZ CE FICHIER
from django.urls import path
from . import views
from .authentication import register, login, logout, get_profile, update_profile

urlpatterns = [
    # Authentication
    path('auth/register/', register, name='register'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/profile/', get_profile, name='get_profile'),
    path('auth/profile/update/', update_profile, name='update_profile'),
    
    # Chat
    path('chat/', views.chat, name='chat'),
    path('conversation/<int:conversation_id>/', views.get_conversation, name='get_conversation'),
    path('conversations/', views.get_user_conversations, name='get_user_conversations'),
    path('conversation/<int:conversation_id>/delete/', views.delete_conversation, name='delete_conversation'),
    
    # Health check
    path('health/', views.health_check, name='health_check'),
]