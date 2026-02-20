from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserProfile
from .serializers import UserSerializer
import logging

  # Ajouter pour logout
from .models import UserProfile
from .serializers import UserSerializer
import logging

logger = logging.getLogger(__name__)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    Inscription d'un nouvel utilisateur
    
    POST /api/auth/register/
    Body: {
        "username": "nom_utilisateur",
        "email": "email@exemple.com",  // optionnel
        "password": "mot_de_passe",
        "phone": "+226 70123456",       // optionnel
        "class_level": "cm1"            // optionnel
    }
    """
    username = request.data.get('username')
    email = request.data.get('email', '')
    password = request.data.get('password')
    phone = request.data.get('phone', '')
    class_level = request.data.get('class_level', '')
    
    # Validations
    if not username or not password:
        return Response(
            {'error': 'Nom d\'utilisateur et mot de passe requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if len(password) < 6:
        return Response(
            {'error': 'Le mot de passe doit contenir au moins 6 caractères'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Vérifier si l'utilisateur existe déjà
    if User.objects.filter(username=username).exists():
        return Response(
            {'error': 'Ce nom d\'utilisateur existe déjà'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if email and User.objects.filter(email=email).exists():
        return Response(
            {'error': 'Cet email existe déjà'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        
        # Créer le profil
        UserProfile.objects.create(
            user=user,
            phone=phone,
            class_level=class_level
        )
        
        # Générer les tokens JWT
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"Nouvel utilisateur inscrit: {username}")
        
        return Response({
            'message': 'Inscription réussie ! Bienvenue ! 🎉',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'class_level': class_level,
            },
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Erreur lors de l'inscription: {e}")
        return Response(
            {'error': 'Erreur lors de l\'inscription'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    """
    Connexion d'un utilisateur
    
    POST /api/auth/login/
    Body: {
        "username": "nom_utilisateur",
        "password": "mot_de_passe"
    }
    """
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response(
            {'error': 'Nom d\'utilisateur et mot de passe requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Authentifier l'utilisateur
    user = authenticate(username=username, password=password)
    
    if user is None:
        return Response(
            {'error': 'Nom d\'utilisateur ou mot de passe incorrect'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    # Générer les tokens JWT
    refresh = RefreshToken.for_user(user)
    
    # Récupérer le profil
    profile = None
    if hasattr(user, 'profile'):
        profile = {
            'phone': user.profile.phone,
            'class_level': user.profile.class_level,
            'avatar': user.profile.avatar,
        }
    
    logger.info(f"Utilisateur connecté: {username}")
    
    return Response({
        'message': 'Connexion réussie ! 👋',
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'profile': profile,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        }
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
def logout(request):
    """
    Déconnexion (blacklist du refresh token)
    
    POST /api/auth/logout/
    Headers: Authorization: Bearer <access_token>
    Body: {
        "refresh_token": "votre_refresh_token"
    }
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token requis'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        logger.info(f"Utilisateur déconnecté")
        
        return Response(
            {'message': 'Déconnexion réussie 👋'},
            status=status.HTTP_200_OK
        )
    except Exception as e:
        logger.error(f"Erreur lors de la déconnexion: {e}")
        return Response(
            {'error': 'Erreur lors de la déconnexion'},
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['GET'])
def get_profile(request):
    """
    Récupérer le profil de l'utilisateur connecté
    
    GET /api/auth/profile/
    Headers: Authorization: Bearer <access_token>
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Non authentifié'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

@api_view(['PUT'])
def update_profile(request):
    """
    Mettre à jour le profil de l'utilisateur
    
    PUT /api/auth/profile/update/
    Headers: Authorization: Bearer <access_token>
    Body: {
        "email": "nouveau@email.com",  // optionnel
        "phone": "+226 70123456",      // optionnel
        "class_level": "cm2"           // optionnel
    }
    """
    if not request.user.is_authenticated:
        return Response(
            {'error': 'Non authentifié'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = request.user
    
    # Mettre à jour l'email
    email = request.data.get('email')
    if email and email != user.email:
        if User.objects.filter(email=email).exclude(id=user.id).exists():
            return Response(
                {'error': 'Cet email est déjà utilisé'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user.email = email
        user.save()
    
    # Mettre à jour le profil
    profile = user.profile
    if request.data.get('phone'):
        profile.phone = request.data.get('phone')
    if request.data.get('class_level'):
        profile.class_level = request.data.get('class_level')
    if request.data.get('avatar'):
        profile.avatar = request.data.get('avatar')
    profile.save()
    
    serializer = UserSerializer(user)
    return Response({
        'message': 'Profil mis à jour avec succès ✅',
        'user': serializer.data
    })