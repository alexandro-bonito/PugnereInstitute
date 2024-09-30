from django.contrib import admin
from .models import Licence, Entreprise, CustomUser, Employe, Produit, ServiceDerive, Vente
@admin.register(Licence)
class LicenceAdmin(admin.ModelAdmin):
    list_display = ('duree', 'nombre_employes', 'nombre_boutiques', 'date_debut', 'date_fin', 'cle_activation')

@admin.register(Entreprise)
class EntrepriseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'adresse', 'email', 'telephone', 'licence', 'cle_activation', 'date_creation', 'status', 'logo')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active', 'is_patron', 'entreprise')

@admin.register(Employe)
class EmployeAdmin(admin.ModelAdmin):
    list_display = ('user', 'nom_employe', 'numero_employe', 'mot_de_passe_employe', 'boutique_index', 'photo_de_profile')

@admin.register(Produit)
class ProduitAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'prix', 'entreprise')
    search_fields = ('nom', 'description', 'entreprise__nom')

@admin.register(ServiceDerive)
class ServiceDeriveAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description', 'prix', 'entreprise')
    search_fields = ('nom', 'description', 'entreprise__nom')

@admin.register(Vente)
class VenteAdmin(admin.ModelAdmin):
    list_display = ('client_nom', 'prix', 'total', 'entreprise','date')
    search_fields = ('client_nom', 'entreprise__nom')
    list_filter = ('entreprise', 'date')
    date_hierarchy = 'date'
    filter_horizontal = ('produits', 'services')







from .models import Depense, Facture, Licence, Entreprise, CustomUser, Employe, Produit, ServiceDerive, Vente

class DepenseAdmin(admin.ModelAdmin):
    list_display = ['entreprise', 'montant', 'description', 'date']
    search_fields = ['entreprise__nom', 'description']
    
class FactureAdmin(admin.ModelAdmin):
    list_display = ['entreprise', 'montant', 'description', 'date_emission', 'date_paiement']
    search_fields = ['entreprise__nom', 'description']

admin.site.register(Depense, DepenseAdmin)
admin.site.register(Facture, FactureAdmin)



from .models import Produit, Stock, Vente

class StockAdmin(admin.ModelAdmin):
    list_display = ('produit', 'longueur', 'specificite', 'quantite_en_cours', 'quantite_restant', 'heure_date')
    search_fields = ('produit__nom',)
    list_filter = ('produit',)
admin.site.register(Stock, StockAdmin)



from django.contrib import admin
from .models import Habilitation

class HabilitationAdmin(admin.ModelAdmin):
    list_display = ('user', 'peut_creer_produit', 'peut_creer_service', 
                    'peut_enregistrer_vente', 'peut_enregistrer_depense', 
                    'peut_creer_facture', 'peut_telecharger_pdf', 
                    'peut_consulter_bilan')
    search_fields = ('user__username',)  # Permet de rechercher par nom d'utilisateur

    # Pour faciliter la modification, on peut ajouter les habilitations en tant que champs 
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        ('Permissions', {
            'fields': (
                'peut_creer_produit',
                'peut_creer_service',
                'peut_enregistrer_vente',
                'peut_enregistrer_depense',
                'peut_creer_facture',
                'peut_telecharger_pdf',
                'peut_consulter_bilan',
            ),
        }),
    )

# Enregistrer le modèle et l'administration
admin.site.register(Habilitation, HabilitationAdmin)
