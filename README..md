# API Django — Users & Dossier Santé

Mini-API en Django  qui expose des endpoints pour :

Task (CRUD basique)

conf des token et + dans settings.py 

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
}

L'API permet permet a un utilisateur d'utiliser le CRUD des task (todoList) excepté le delete qui est reservé aux superusers
elle permet également de créer un compte (création login me logout refreshtoken) géré par rest_framework_simplejwt 

Login -> TokenObtainPairView()
    - récupere un username et un mot de passe si il est bon : retourne un un access token et un refresh token appairé a l'utilisateur

Refresh -> TokenRefreshView()dfsd
    - récupere un refreshToken, si le refresh token est pas encore expiré ET non blacklisté: retourne un nouveau refresh token 

Signup -> utlise le RegisterSerializer dans serializers.py -> récupere le model User(créé par django) de l'ORM (model = User) vérifié la validité des données sur l'username et l'email grace aux field présent dans la page de model (ORM)
qui pointe vers des validator distinc 
Email : 
(C:\Users\Dylan\AppData\Roaming\Python\Python314\site-packages\django\core\validators.py)

L'username :

C:\Users\Dylan\AppData\Roaming\Python\Python314\site-packages\django\contrib\auth\validators.py

Password : 
Aucune validation sur le password (création d'un validator custom en cours)
Le password est hashé dans le registerSerializer ave user.set_password() en pkfb SHA258



Logout : Black list le refresh Token 



(éxplication uniquement du delete car pas de controle sur les autres)
CRUD des task 

CREATE 

GET 

UPDATE

DELETE
    - seul un superUser peut delete une task grace a 
    ```
     elif request.method == 'DELETE':
        #  Seuls les admins peuvent supprimer
        if not ***request.user.is_superuser***:  
            return Response(
                {"detail": "Vous n'avez pas la permission de supprimer cette tâche."},
                status=status.HTTP_403_FORBIDDEN
            )

        task.delete()
        return Response({'detail': 'Supprimé avec succès'},status=status.HTTP_204_NO_CONTENT)
    ```


le décorateur *** @permission_classes([IsAuthenticated]) ***
```
class IsAuthenticated(BasePermission):
    """
    Allows access only to authenticated users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)
```

# Prérequis

Python 3.10+ (idéalement 3.11+)

pip

# Installation
1) cloner ou ouvrir le dossier

git clone https://github.com/DylanNeural/ApiRestDjango.git

cd ApiRest

2) environnement virtuel
   
python -m venv .venv

.\.venv\Scripts\activate     # Windows

3) installer les deps
   
pip install django

4) migrations DB # a initialiser lorsque la BDD est modifié et préférable également avant premier lancement dezzipage
   
python manage.py makemigrations

python manage.py migrate

5) 
python manage.py runserver

- http://127.0.0.1:8000/ La collection POSTMAN EST RÉGLÉ SUR LE PORT 8020

- Commande qui modifie le port en cas de conflit avec une autre application

- python manage.py runserver 8001


# Modèles

from django.db import models

class Task(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



# Endpoints

* Auth
POST /api/signup/
Inscription d’un utilisateur.

POST /api/token/
Login : obtention du couple access + refresh JWT.

POST /api/token/refresh/
Rafraîchir le token d’accès à partir du refresh.

GET /api/auth/me/
Récupérer le profil de l’utilisateur connecté.

POST /api/logout/
Logout : blacklist du refresh token.

* Task
GET /api/tasks/
Lister toutes les tâches de l’utilisateur.

POST /api/tasks/
Créer une nouvelle tâche.

GET /api/tasks/<id>/
Récupérer une tâche par son ID.

PUT /api/tasks/<id>/
Mettre à jour complètement une tâche.

PATCH /api/tasks/<id>/
Mettre à jour partiellement une tâche.

DELETE /api/tasks/<id>/
Supprimer une tâche (d’après ton commentaire : admin only côté API).



Une collection de test POSTMAN est disponible a la racine[text](postman.json)


# Reste a faire

- Ajouter des données (plus tard)
- ne renvoyer que le access token et garder le refresh
gestion d'erreur api tierce c'est fait -> try catch
expliquer les fonction auth
Utiliser seulement le access Token


  
Auteur: @DylanNeural



