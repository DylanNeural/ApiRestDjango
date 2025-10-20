# API Django — Users & Dossier Santé

Mini-API en Django (sans DRF) qui expose des endpoints JSON pour :

Users (CRUD basique)

DossierSante (relation 1–1 avec un user & CRUD classique)


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

-http://127.0.0.1:8000/

-Commande qui modifie le port en cas de conflit avec une autre application

-python manage.py runserver 8001


# Modèles

#home/models.py

class Users(models.Model):

    - nom = models.CharField(max_length=120)
    - prenom = models.CharField(max_length=30)
    - age = models.IntegerField()
    - dateAnniversaire = models.DateField()
    - adresse = models.CharField(max_length=255)

class DossierSante(models.Model):

    - user = models.OneToOneField(Users, on_delete=models.CASCADE, related_name="dossier_sante")
    - groupe_sanguin = models.CharField(max_length=3, blank=True)
    - allergies = models.TextField(blank=True)
    - medecin_traitant = models.CharField(max_length=120, blank=True)

# Routes

#Endpoints

GET    /api/users/                    → liste des users

POST   /api/users/                    → créer un user

GET    /api/users/<int:pk>/           → détail user

PATCH  /api/users/<int:pk>/           → modifier partiellement un user

DELETE /api/users/<int:pk>/           → supprimer un user

GET    /api/users/<int:pk>/dossier/    → récupérer dossier santé

POST   /api/users/<int:pk>/dossier/    → créer dossier santé (si absent)

PATCH  /api/users/<int:pk>/dossier/    → modifier dossier santé

DELETE /api/users/<int:pk>/dossier/    → supprimer dossier santé

Une collection de test POSTMAN sera bientot Disponible : POSTMAN KO :( 


Attention l'endpoint doit bien terminer par un "/"


# Reste a faire
- Documenter le code
- Ajouter un systeme d'authentification
- Ajouter des données

  
Auteur: @DylanNeural
