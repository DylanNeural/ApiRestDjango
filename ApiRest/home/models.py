# home/models.py
from django.db import models
from django.conf import settings





class Users(models.Model):
    account = models.OneToOneField(          # ← lien vers l’utilisateur d’auth
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile_user",
        null=True, blank=True,               # (null/blank le temps de migrer)
    )
    
    prenom = models.CharField(max_length=30)
    age = models.IntegerField()
    dateAnniversaire = models.DateField()

    def __str__(self):
        return f"{self.prenom} {self.nom}"

class DossierSante(models.Model):
    user = models.OneToOneField(
        Users,
        on_delete=models.CASCADE,
        related_name="dossier_sante"
    )
    groupe_sanguin = models.CharField(max_length=3, blank=True)
    allergies = models.TextField(blank=True)
    medecin_traitant = models.CharField(max_length=120, blank=True)
    department_medical = models.CharField(max_length=120, blank=True)
    

    def __str__(self):
        return f"Dossier santé de {self.user}"
