from django.contrib.auth.models import User
import requests
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Task
from .serializers import TaskSerializer, RegisterSerializer, UserSerializer


@api_view(['GET'])
@permission_classes([AllowAny])  # ou IsAuthenticated si tu veux protéger
def external_tasks(request):
    """
    Récupère des tâches depuis une API tierce (JSONPlaceholder).
    GET /api/external-tasks/?userId=1
    """
    user_id = request.query_params.get("userId")

    url = "https://jsonplaceholder.typicode.com/todos"
    params = {}
    if user_id:
        params["userId"] = user_id

    try:
        resp = requests.get(url, params=params, timeout=5)
        resp.raise_for_status()
    except requests.RequestException as e:
        return Response(
            {"detail": "Erreur lors de l'appel à l'API externe", "error": str(e)},
            status=status.HTTP_502_BAD_GATEWAY,
        )

    data = resp.json()

    # 
    tasks = [
        {
            "id": t["id"],
            "title": t["title"],
            "completed": t["completed"],
            "external_user_id": t["userId"],
        }
        for t in data
    ]

    return Response(tasks, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def task_list_create(request):
    if request.method == 'GET':
        tasks = Task.objects.all()
        serializer = TaskSerializer(tasks, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
def task_detail(request, pk):
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response({'detail': 'Not found'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TaskSerializer(task)
        return Response(serializer.data)

    elif request.method == 'PUT' or request.method == 'PATCH':
        serializer = TaskSerializer(task, data=request.data, partial=(request.method == 'PATCH'))
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    
    elif request.method == 'DELETE':
        #  Seuls les admins peuvent supprimer
        if not request.user.is_superuser:  # ou request.user.is_superuser
            return Response(
                {"detail": "Vous n'avez pas la permission de supprimer cette tâche."},
                status=status.HTTP_403_FORBIDDEN
            )

        task.delete()
        return Response({'detail': 'Supprimé avec succès'},status=status.HTTP_204_NO_CONTENT)
    
    
    
@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"message": "Utilisateur créé"}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Utilisateur Déconnecté"},status=status.HTTP_205_RESET_CONTENT)
    except Exception:
        return Response({"detail": "Token invalide"}, status=status.HTTP_400_BAD_REQUEST)




