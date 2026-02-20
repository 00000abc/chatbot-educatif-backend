from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging

from .models import Conversation, Message
from .serializers import (
    ChatRequestSerializer,
    ChatResponseSerializer,
    ConversationSerializer
)
from .gemini_service import get_gemini_service

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def chat(request):
    """
    Envoyer un message et recevoir une réponse de l'IA
    
    POST /api/chat/
    Headers: Authorization: Bearer <access_token>
    Body: {
        "message": "Comment fait-on une addition ?",
        "class_level": "cp1",           // optionnel
        "subject": "mathematiques",     // optionnel
        "conversation_id": 1            // optionnel
    }
    """
    serializer = ChatRequestSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    data = serializer.validated_data
    message = data['message']
    class_level = data.get('class_level')
    subject = data.get('subject')
    conversation_id = data.get('conversation_id')
    
    user = request.user
    
    try:
        # Récupérer ou créer la conversation
        if conversation_id:
            conversation = Conversation.objects.get(id=conversation_id, user=user)
        else:
            conversation = Conversation.objects.create(user=user)
        
        # Sauvegarder le message de l'utilisateur
        user_message = Message.objects.create(
            conversation=conversation,
            content=message,
            is_user=True,
            class_level=class_level,
            subject=subject
        )
        
        logger.info(f"Message reçu de {user.username}: {message}")
        
        # Générer la réponse avec Gemini
        gemini_service = get_gemini_service()
        context = {
            'class_level': class_level,
            'subject': subject,
        }
        ai_response = gemini_service.generate_response(message, context)
        
        logger.info(f"Réponse IA générée pour {user.username}")
        
        # Sauvegarder la réponse de l'IA
        ai_message = Message.objects.create(
            conversation=conversation,
            content=ai_response,
            is_user=False,
            class_level=class_level,
            subject=subject
        )
        
        # Retourner la réponse
        response_data = {
            'response': ai_response,
            'conversation_id': conversation.id,
            'message_id': ai_message.id
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Erreur lors du traitement du message: {e}", exc_info=True)
        return Response(
            {'error': 'Erreur lors du traitement de votre message'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation(request, conversation_id):
    """
    Récupérer une conversation avec tous ses messages
    
    GET /api/conversation/<id>/
    Headers: Authorization: Bearer <access_token>
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_conversations(request):
    """
    Récupérer toutes les conversations de l'utilisateur
    
    GET /api/conversations/
    Headers: Authorization: Bearer <access_token>
    """
    conversations = Conversation.objects.filter(user=request.user)
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_conversation(request, conversation_id):
    """
    Supprimer une conversation
    
    DELETE /api/conversation/<id>/
    Headers: Authorization: Bearer <access_token>
    """
    try:
        conversation = Conversation.objects.get(id=conversation_id, user=request.user)
        conversation.delete()
        return Response(
            {'message': 'Conversation supprimée avec succès'},
            status=status.HTTP_200_OK
        )
    except Conversation.DoesNotExist:
        return Response(
            {'error': 'Conversation introuvable'},
            status=status.HTTP_404_NOT_FOUND
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Vérifier que l'API fonctionne
    
    GET /api/health/
    """
    gemini_service = get_gemini_service()
    gemini_configured = gemini_service.model is not None
    
    return Response({
        'status': 'ok',
        'message': 'API Django fonctionne correctement',
        'gemini_configured': gemini_configured,
        'database': 'MySQL',
    })