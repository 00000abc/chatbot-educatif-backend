from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserProfile, Conversation, Message

class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer pour le profil utilisateur"""
    class Meta:
        model = UserProfile
        fields = ['phone', 'class_level', 'avatar', 'created_at']

class UserSerializer(serializers.ModelSerializer):
    """Serializer pour l'utilisateur"""
    profile = UserProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'profile']

class MessageSerializer(serializers.ModelSerializer):
    """Serializer pour les messages"""
    class Meta:
        model = Message
        fields = ['id', 'content', 'is_user', 'timestamp', 'class_level', 'subject']

class ConversationSerializer(serializers.ModelSerializer):
    """Serializer pour les conversations"""
    messages = MessageSerializer(many=True, read_only=True)
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'user', 'created_at', 'updated_at', 'messages']

class ChatRequestSerializer(serializers.Serializer):
    """Serializer pour les requêtes de chat"""
    message = serializers.CharField(required=True)
    class_level = serializers.CharField(required=False, allow_blank=True)
    subject = serializers.CharField(required=False, allow_blank=True)
    conversation_id = serializers.IntegerField(required=False, allow_null=True)

class ChatResponseSerializer(serializers.Serializer):
    """Serializer pour les réponses de chat"""
    response = serializers.CharField()
    conversation_id = serializers.IntegerField()
    message_id = serializers.IntegerField()