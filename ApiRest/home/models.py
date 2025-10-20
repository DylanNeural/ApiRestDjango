# home/models.py
from django.db import models

class Users(models.Model):
    id = models.CharField(primary_key=True, max_length=120)
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
    

    def __str__(self):
        return f"Dossier santé de {self.user}"
