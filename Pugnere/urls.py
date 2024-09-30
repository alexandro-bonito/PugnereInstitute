

from django.urls import path
from . import views

app_name = 'Pugnere'

urlpatterns = [
    path('', views.index, name='index'),
    path('signup/', views.signup, name='signup'),
    path('signin/', views.signin, name='signin'),
    path('add_employe/', views.add_employe, name='add_employe'),
    path('download_pdf/', views.download_pdf, name='download_pdf'),

    path('is_employe/', views.is_employe, name='is_employe'),
    path('creer_produit/', views.creer_produit, name='creer_produit'),
    path('creer_service_derive/', views.creer_service_derive, name='creer_service_derive'),
    path('enregistrer_vente/', views.enregistrer_vente, name='enregistrer_vente'),
    path('enregistrer-depense/', views.enregistrer_depense, name='enregistrer_depense'),
    path('passerelle/', views.passerelle, name='passerelle'),
    path('enregistrer-facture/', views.enregistrer_facture, name='enregistrer_facture'),
    path('bilan/', views.bilan_view, name='bilan'),
    path('stock/', views.stock_view, name='stock_view'),  # URL pour la gestion des stocks
    path('marketplace/', views.marketplace, name='marketplace'),
    path('payer-a-nouveau/<int:salaire_paye_id>/', views.payer_a_nouveau, name='payer_a_nouveau'),    path('equipe/', views.equipe_view, name='equipe'),
    path('mettre_a_jour_habilitation/<int:employe_id>/', views.mettre_a_jour_habilitation, name='mettre_a_jour_habilitation'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('habilitation/', views.habilitation, name='habilitation'),  # URL pour exécuter la fonction d'habilitation
    path('facture/creer/', views.facture_client_view, name='creer_facture'),  # Créer une facture
    path('facture/telecharger/<int:facture_id>/', views.telecharger_pdf, name='telecharger_pdf'),    #path('facture/<int:pk>/pdf/', views.facture_pdf, name='facture_pdf'),  # Télécharger la facture en PDF


]