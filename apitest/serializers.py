from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task  # si tu as un modèle Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'completed', 'created_at']


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User(
            username=validated_data['username'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user
    
    # class RegisterSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(
    #     required=True,
    #     validators=[UniqueValidator(queryset=User.objects.all())]
    # )
    # password = serializers.CharField(write_only=True)

    # class Meta:
    #     model = User
    #     fields = ['id', 'username', 'email', 'password']


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # tu peux enlever first_name / last_name si tu ne les utilises pas
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
