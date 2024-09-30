# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
import secrets

class Licence(models.Model):
    DUREE_CHOICES = (
        ('6M', '6 mois'),
        ('1Y', '1 an'),
    )
    
    duree = models.CharField(max_length=2, choices=DUREE_CHOICES)
    nombre_employes = models.IntegerField()
    nombre_boutiques = models.IntegerField()
    date_debut = models.DateField(default=timezone.now)
    date_fin = models.DateField(blank=True, null=True)
    cle_activation = models.CharField(max_length=100, blank=True, unique=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # vérifie si l'instance est nouvelle (pas encore enregistrée en base de données)
            # Générer la clé d'activation avec des informations spécifiques
            info_cle = f"{self.duree}-{self.date_fin}-{secrets.token_urlsafe(30)}"
            self.cle_activation = info_cle[:100]  # limiter à 100 caractères comme défini dans le modèle
        
        if self.duree == '6M':
            self.date_fin = self.date_debut + timedelta(days=180)  # 6 mois
        elif self.duree == '1Y':
            self.date_fin = self.date_debut + timedelta(days=365)  # 1 an
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Licence - {self.duree}"

class Entreprise(models.Model):
    nom = models.CharField(max_length=100)
    adresse = models.TextField()
    email = models.EmailField(max_length=254)
    telephone = models.CharField(max_length=20)
    licence = models.ForeignKey(Licence, on_delete=models.CASCADE, null=True, blank=True)
    cle_activation = models.CharField(max_length=100, blank=True, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    status = models.BooleanField(default=False)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)  # Ajout du champ logo

    def save(self, *args, **kwargs):
        if not self.pk and self.licence:
            info_cle = f"{self.licence.duree}-{self.licence.date_fin}-{self.nom}-{secrets.token_urlsafe(30)}"
            self.cle_activation = info_cle[:100]
        
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nom

class CustomUser(AbstractUser):
    entreprise = models.ForeignKey(Entreprise, on_delete=models.CASCADE, null=True, blank=True)
    is_patron = models.BooleanField(default=False)
    is_employe = models.BooleanField(default=False)
    password = models.CharField(max_length=128)

    def __str__(self):
        return self.username
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Employe(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    nom_employe = models.CharField(max_length=255)
    numero_employe = models.CharField(max_length=20)
    mot_de_passe_employe = models.CharField(max_length=128)
    boutique_index = models.IntegerField()
    photo_de_profile = models.ImageField(upload_to='employe_photos/', null=True, blank=True)
    salaire = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Ajout du champ salaire

    def __str__(self):
        return f"{self.user.username} - {self.nom_employe} - Boutique {self.boutique_index}"

# Signal pour créer automatiquement l'habilitation après la création de l'employé
@receiver(post_save, sender=Employe)
def create_habilitation_for_employe(sender, instance, created, **kwargs):
    if created:
        # Créer une habilitation par défaut pour l'employé s'il est créé
        Habilitation.objects.get_or_create(user=instance.user)



class Produit(models.Model):
    nom = models.CharField(max_length=255)
    product_image = models.ImageField(upload_to='product_image/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    entreprise = models.ForeignKey('Entreprise', on_delete=models.CASCADE, related_name='produits')

    def __str__(self):
        return f"{self.nom} - {self.entreprise.nom}"

class ServiceDerive(models.Model):
    nom = models.CharField(max_length=255)
    sderive_image = models.ImageField(upload_to='sderive_image/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    entreprise = models.ForeignKey('Entreprise', on_delete=models.CASCADE, related_name='services_derives')

    def __str__(self):
        return f"{self.nom} - {self.entreprise.nom}"

# models.py
from django.db import models

class Vente(models.Model):
    client_nom = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='ventes_images/', null=True, blank=True)
    produits = models.ManyToManyField('Produit', blank=True)
    services = models.ManyToManyField('ServiceDerive', blank=True)
    entreprise = models.ForeignKey('Entreprise', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Vente de {self.client_nom} - {self.date}"




class Depense(models.Model):
    entreprise = models.ForeignKey('Entreprise', on_delete=models.CASCADE, related_name='depenses')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='depenses_images/', null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Depense de {self.montant} - {self.entreprise.nom}"

class Facture(models.Model):
    entreprise = models.ForeignKey('Entreprise', on_delete=models.CASCADE, related_name='factures')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image = models.ImageField(upload_to='factures_images/', null=True, blank=True)
    date_emission = models.DateField(default=timezone.now)
    date_paiement = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"Facture de {self.montant} - {self.entreprise.nom}"


class Stock(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE, related_name='stocks')
    longueur = models.CharField(max_length=255)
    specificite = models.TextField()
    quantite_en_cours = models.PositiveIntegerField()
    quantite_restant = models.PositiveIntegerField()
    heure_date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Stock de {self.produit.nom} - {self.heure_date}"




from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

class Prestation(models.Model):
    description = models.CharField(max_length=255)
    prix = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.description






from django.db import models
from django.utils import timezone

class FactureClient(models.Model):
    client_nom = models.CharField(max_length=255)
    client_prenom = models.CharField(max_length=255)
    client_telephone = models.CharField(max_length=20)
    prestations = models.ManyToManyField('Prestation', related_name='factures')
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    entreprise = models.ForeignKey('Entreprise', on_delete=models.CASCADE, null=True, blank=True)  # Peut être vide
    date_creation = models.DateTimeField(default=timezone.now)

    def calculer_total(self):
        total = sum(prestation.prix for prestation in self.prestations.all())
        self.total = total
        self.save()

    def __str__(self):
        return f"Facture pour {self.client_nom} {self.client_prenom}"


class Habilitation(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    peut_creer_produit = models.BooleanField(default=False)
    peut_creer_service = models.BooleanField(default=False)
    peut_enregistrer_vente = models.BooleanField(default=True)
    peut_enregistrer_depense = models.BooleanField(default=False)
    peut_creer_facture = models.BooleanField(default=False)
    peut_telecharger_pdf = models.BooleanField(default=False)
    peut_consulter_bilan = models.BooleanField(default=False)

    def __str__(self):
        return f"Habilitation for {self.user.username}"


class SalairePaye(models.Model):
    employe = models.ForeignKey(Employe, on_delete=models.CASCADE)
    date_paiement = models.DateTimeField(auto_now_add=True)
    montant = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Paiement de {self.montant} à {self.employe.nom_employe} le {self.date_paiement}"
