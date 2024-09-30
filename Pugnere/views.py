from django.shortcuts import render

# Create your views here.

# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Entreprise, CustomUser, Licence
from django.utils import timezone
from datetime import timedelta
import secrets
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .models import Entreprise, CustomUser, Licence
from django.utils import timezone
from datetime import timedelta
import secrets

def signup(request):
    licences = Licence.objects.all()
    
    if request.method == 'POST':
        nom = request.POST.get('nom')
        adresse = request.POST.get('adresse')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        licence_id = request.POST.get('licence_id')
        username = request.POST.get('username')
        password = request.POST.get('password')
        logo = request.FILES.get('logo')

        if not (nom and adresse and email and telephone and licence_id and username and password):
            return render(request, 'signup.html', {'error': 'Tous les champs sont requis', 'licences': licences})

        if CustomUser.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Ce nom d\'utilisateur est déjà pris', 'licences': licences})

        try:
            licence = Licence.objects.get(id=licence_id)
            
            entreprise = Entreprise.objects.create(
                nom=nom,
                adresse=adresse,
                email=email,
                telephone=telephone,
                licence=licence,
                logo=logo
            )
            
            CustomUser.objects.create_user(username=username, password=password, entreprise=entreprise, is_patron=True)
            
            return redirect('Pugnere:index')
        except Licence.DoesNotExist:
            return render(request, 'signup.html', {'error': 'Licence invalide', 'licences': licences})
        except Exception as e:
            return render(request, 'signup.html', {'error': str(e), 'licences': licences})

    return render(request, 'signup.html', {'licences': licences})


# views.py
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Entreprise, CustomUser, Licence
from django.utils import timezone
from datetime import timedelta

def signin(request):
    if request.method == 'POST':
        cle_activation = request.POST.get('cle_activation')
        password = request.POST.get('password')
        
        if not (cle_activation and password):
            return render(request, 'signin.html', {'error': 'Tous les champs sont requis'})

        try:
            entreprise = Entreprise.objects.get(cle_activation=cle_activation)
            user = authenticate(request, username=entreprise.customuser_set.first().username, password=password)
            
            if user is not None:
                if not entreprise.status:
                    entreprise.status = True
                    entreprise.licence.date_debut = timezone.now().date()
                    if entreprise.licence.duree == '6M':
                        entreprise.licence.date_fin = entreprise.licence.date_debut + timedelta(days=180)
                    elif entreprise.licence.duree == '1Y':
                        entreprise.licence.date_fin = entreprise.licence.date_debut + timedelta(days=365)
                    entreprise.licence.save()
                    entreprise.save()
                
                login(request, user)
                return redirect('Pugnere:index')
            else:
                return render(request, 'signin.html', {'error': 'Clé de licence ou mot de passe incorrect'})
        except Entreprise.DoesNotExist:
            return render(request, 'signin.html', {'error': 'Clé de licence invalide'})
    
    return render(request, 'signin.html')



from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Employe, Entreprise, CustomUser
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Employe, Entreprise, CustomUser, Licence
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password
from .models import Employe, CustomUser, Entreprise, Licence
@login_required
def add_employe(request):
    if request.method == 'POST':
        nom_employe = request.POST.get('nom_employe')
        numero_employe = request.POST.get('numero_employe')
        salaire = request.POST.get('salaire')
        mot_de_passe_employe = request.POST.get('mot_de_passe_employe')
        boutique_index = request.POST.get('boutique_index')
        photo_de_profile = request.FILES.get('photo_de_profile')

        if not (nom_employe and numero_employe and mot_de_passe_employe and boutique_index):
            return render(request, 'add_employe.html', {'error': 'Tous les champs sont requis'})

        try:
            entreprise = request.user.entreprise
            licence = entreprise.licence

            if int(boutique_index) > licence.nombre_boutiques:
                return render(request, 'add_employe.html', {'error': 'L\'index de la boutique dépasse le nombre de boutiques autorisé par la licence'})

            username = f"{entreprise.nom}_{numero_employe}"

            if CustomUser.objects.filter(username=username).exists():
                return render(request, 'add_employe.html', {'error': 'Cet employé existe déjà'})

            user = CustomUser.objects.create_user(
                username=username,
                password=mot_de_passe_employe,
                entreprise=entreprise
            )

            employe = Employe.objects.create(
                user=user,
                nom_employe=nom_employe,
                numero_employe=numero_employe,
                salaire=salaire,
                mot_de_passe_employe=make_password(mot_de_passe_employe),
                boutique_index=boutique_index,
                photo_de_profile=photo_de_profile
            )

            return redirect('Pugnere:index')
        except Exception as e:
            return render(request, 'add_employe.html', {'error': str(e)})

    return render(request, 'add_employe.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .models import Employe

def is_employe(request):
    if request.method == 'POST':
        numero_employe = request.POST.get('numero_employe')
        mot_de_passe_employe = request.POST.get('mot_de_passe_employe')

        if not (numero_employe and mot_de_passe_employe):
            return render(request, 'is_employe.html', {'error': 'Tous les champs sont requis'})
            
        try:
            employe = Employe.objects.get(numero_employe=numero_employe)
            user = authenticate(username=employe.user.username, password=mot_de_passe_employe)

            if user is not None:
                login(request, user)
                return redirect('Pugnere:index')  # Rediriger vers la page d'index sans paramètre
            else:
                return render(request, 'is_employe.html', {'error': 'Numéro d\'employé ou mot de passe incorrect'})
        except Employe.DoesNotExist:
            return render(request, 'is_employe.html', {'error': 'Numéro d\'employé invalide'})

    return render(request, 'is_employe.html')








from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, ServiceDerive

@login_required
def creer_produit(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        prix = request.POST.get('prix')
        product_image = request.FILES.get('product_image')

        entreprise = request.user.entreprise

        produit = Produit(
            nom=nom,
            description=description,
            prix=prix,
            product_image=product_image,
            entreprise=entreprise
        )
        produit.save()
        messages.success(request, 'Produit créé avec succès')
        return redirect('Pugnere:index')  # Redirige vers l'index après création

    return render(request, 'index.html')  # Affiche le formulaire de création


@login_required
def creer_service_derive(request):
    if request.method == 'POST':
        nom = request.POST.get('nom')
        description = request.POST.get('description')
        prix = request.POST.get('prix')
        sderive_image = request.FILES.get('sderive_image')

        entreprise = request.user.entreprise

        service_derive = ServiceDerive(
            nom=nom,
            description=description,
            prix=prix,
            sderive_image=sderive_image,
            entreprise=entreprise
        )
        service_derive.save()
        messages.success(request, 'Service dérivé créé avec succès')
        return redirect('Pugnere:index')  # Redirige vers l'index après création

    return render(request, 'index.html')  # Affiche le formulaire de création


@login_required
def afficher_produits_et_services(request):
    entreprise = request.user.entreprise

    if entreprise is None:
        messages.error(request, 'Aucune entreprise associée à cet utilisateur.')
        return redirect('Pugnere:index')

    produits = Produit.objects.filter(entreprise=entreprise)
    services_derives = ServiceDerive.objects.filter(entreprise=entreprise)

    context = {
        'produits': produits,
        'services_derives': services_derives,
    }

    return context



# views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, ServiceDerive, Vente, Entreprise
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Produit, ServiceDerive, Vente

@login_required
def enregistrer_vente(request):
    if request.method == 'POST':
        client_nom = request.POST['clientNom']
        prix = float(request.POST['prix'])
        entreprise = request.user.entreprise
        image = request.FILES.get('image')

        produits_ids = request.POST.getlist('produitDérivé')
        services_ids = request.POST.getlist('serviceDérivé')

        total_produits = 0.0
        total_services = 0.0
        produits_obj = []
        services_obj = []

        # Ajoutez une vérification pour les produits dérivés
        if produits_ids:
            for produit_id in produits_ids:
                if produit_id:  # Assurez-vous que l'ID n'est pas une chaîne vide
                    try:
                        produit = Produit.objects.get(id=produit_id)
                        produits_obj.append(produit)
                        total_produits += float(produit.prix)  # Convert Decimal to float
                    except Produit.DoesNotExist:
                        messages.error(request, f"Produit avec ID {produit_id} n'existe pas.")
                        return redirect('Pugnere:index')

        # Ajoutez une vérification pour les services dérivés
        if services_ids:
            for service_id in services_ids:
                if service_id:  # Assurez-vous que l'ID n'est pas une chaîne vide
                    try:
                        service = ServiceDerive.objects.get(id=service_id)
                        services_obj.append(service)
                        total_services += float(service.prix)  # Convert Decimal to float
                    except ServiceDerive.DoesNotExist:
                        messages.error(request, f"Service dérivé avec ID {service_id} n'existe pas.")
                        return redirect('Pugnere:index')

        total = prix + total_produits + total_services

        vente = Vente(client_nom=client_nom, prix=prix, total=total, entreprise=entreprise, image=image)
        vente.save()
        vente.produits.set(produits_obj)
        vente.services.set(services_obj)
        vente.save()

        messages.success(request, 'Vente enregistrée avec succès')
        return redirect('Pugnere:index')  # Assurez-vous que 'Pugnere:index' est le nom correct de votre route

    produits = Produit.objects.all()
    services = ServiceDerive.objects.all()
    return render(request, 'index.html', {'services': services,'produits': produits})


@login_required
def afficher_ventes(request):
    ventes = Vente.objects.filter(entreprise=request.user.entreprise).order_by('-date')
    return {'ventes': ventes}

  
from datetime import date

from datetime import date
from django.contrib.auth.decorators import login_required
from .models import Vente

@login_required
def compter_ventes_journee(request):
    aujourd_hui = date.today()
    ventes_journee = Vente.objects.filter(date__date=aujourd_hui, entreprise=request.user.entreprise)
    
    nombre_ventes_journee = ventes_journee.count()
    total_ventes_journee = sum(vente.total for vente in ventes_journee)
    
    return {
        'nombre_ventes_journee': nombre_ventes_journee,
        'total_ventes_journee': total_ventes_journee
    }





from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from .models import Depense


@login_required
def enregistrer_depense(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        description = request.POST.get('description')
        image = request.FILES.get('image')

        if montant and description:
            # Création de la dépense
            depense = Depense(
                entreprise=request.user.entreprise,  # Associer l'entreprise de l'utilisateur connecté
                montant=montant,
                description=description
            )
            
            if image:
                # Sauvegarder l'image
                depense.image = image
            
            depense.save()

            messages.success(request, 'Dépense enregistrée avec succès.')
            return redirect('Pugnere:index')  # Redirection vers la page listant les dépenses
        else:
            messages.error(request, 'Veuillez remplir tous les champs requis.')

    return render(request, 'index.html')



from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from .models import Facture


@login_required
def enregistrer_facture(request):
    if request.method == 'POST':
        montant = request.POST.get('montant')
        description = request.POST.get('description')
        image = request.FILES.get('image')
        date_emission = request.POST.get('date_emission', timezone.now().date())  # Utilise la date actuelle si aucune date n'est fournie

        if montant and description:
            # Création de la facture
            facture = Facture(
                entreprise=request.user.entreprise,  # Associer l'entreprise de l'utilisateur connecté
                montant=montant,
                description=description,
                date_emission=date_emission
            )
            
            if image:
                # Sauvegarder l'image
                facture.image = image

            facture.save()

            messages.success(request, 'Facture enregistrée avec succès.')
            return redirect('Pugnere:index')  # Redirection vers la page listant les factures
        else:
            messages.error(request, 'Veuillez remplir tous les champs requis.')

    return render(request, 'index.html')



def marketplace(request):
    entreprise = request.user.entreprise

    if entreprise is None:
        messages.error(request, 'Aucune entreprise associée à cet utilisateur.')
        return redirect('Pugnere:index')

    produits = Produit.objects.filter(entreprise=entreprise)
    services_derives = ServiceDerive.objects.filter(entreprise=entreprise)

    context = {
        'produits': produits,
        'services_derives': services_derives,
    }
    return render(request, 'marketplace.html', context)


from .models import Facture, Depense

def afficher_factures(request):
    factures = Facture.objects.filter(entreprise=request.user.entreprise).order_by('-date_emission')
    return {'factures': factures}

def afficher_depenses(request):
    depenses = Depense.objects.filter(entreprise=request.user.entreprise).order_by('-date')
    return {'depenses': depenses}



from datetime import date
from django.contrib.auth.decorators import login_required
from .models import Facture, Depense

@login_required
def compter_depenses_et_factures_journee(request):
    aujourd_hui = date.today()
    
    # Filtrer les factures de la journée sans utiliser __date
    factures_journee = Facture.objects.filter(date_emission=aujourd_hui, entreprise=request.user.entreprise)
    
    # Filtrer les dépenses de la journée sans utiliser __date
    depenses_journee = Depense.objects.filter(date=aujourd_hui, entreprise=request.user.entreprise)
    
    # Calculer le nombre total
    nombre_factures_journee = factures_journee.count()
    nombre_depenses_journee = depenses_journee.count()
    
    # Calculer le total des montants
    total_factures_journee = sum(facture.montant for facture in factures_journee)
    total_depenses_journee = sum(depense.montant for depense in depenses_journee)
    
    return {
        'nombre_factures_journee': nombre_factures_journee,
        'total_factures_journee': total_factures_journee,
        'nombre_depenses_journee': nombre_depenses_journee,
        'total_depenses_journee': total_depenses_journee
    }







from django.db.models import Sum
from django.shortcuts import render
from .models import Vente, Depense, Facture

def bilan_view(request):
    user = request.user
    entreprise = user.entreprise

    if entreprise is None:
        return render(request, 'error.html', {'message': 'Aucune entreprise associée à votre profil.'})

    ventes_data = Vente.objects.filter(entreprise=entreprise).values('date__date').annotate(total_ventes=Sum('total'))
    depenses_data = Depense.objects.filter(entreprise=entreprise).values('date__date').annotate(total_depenses=Sum('montant'))
    factures_data = FactureClient.objects.filter(entreprise=entreprise)
    factures_simples_data = Facture.objects.filter(entreprise=entreprise)

    ventes_labels = [item['date__date'].strftime('%Y-%m-%d') for item in ventes_data]
    ventes_totals = [item['total_ventes'] for item in ventes_data]

    depenses_labels = [item['date__date'].strftime('%Y-%m-%d') for item in depenses_data]
    depenses_totals = [item['total_depenses'] for item in depenses_data]

    factures_labels = [facture.date_creation.strftime('%Y-%m-%d') for facture in factures_data]
    factures_totals = [facture.total for facture in factures_data]

    factures_simples_labels = [facture.date_emission.strftime('%Y-%m-%d') for facture in factures_simples_data]
    factures_simples_totals = [facture.montant for facture in factures_simples_data]

    context = {
        'ventes_data': dict(zip(ventes_labels, ventes_totals)),
        'depenses_data': dict(zip(depenses_labels, depenses_totals)),
        'factures_simples_data': dict(zip(factures_simples_labels, factures_simples_totals)),
        'factures_simples': factures_simples_data,
        'factures_data': dict(zip(factures_labels, factures_totals)),
        'factures': factures_data,  # Ajout des factures
    }

    return render(request, 'bilan.html', context)




from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Produit, Stock

@receiver(post_save, sender=Produit)
def create_stock(sender, instance, created, **kwargs):
    if created:
        Stock.objects.create(produit=instance, quantite_en_cours=0, quantite_restant=0)
def stock_view(request):
    produits = Produit.objects.all()
    stocks = Stock.objects.select_related('produit')

    if request.method == 'POST':
        produit_id = request.POST.get('produit_id')
        quantite_vendue = request.POST.get('quantite_vendue')
        quantite_en_cours = request.POST.get('quantite_en_cours')

        # Debugging: afficher les valeurs envoyées
        print(f"Produit ID: {produit_id}, Quantité vendue: {quantite_vendue}, Quantité en cours: {quantite_en_cours}")

        # Récupérer le produit et son stock
        produit = get_object_or_404(Produit, id=produit_id)
        stock = Stock.objects.get(produit=produit)

        # Cas 1 : Si "quantité vendue" est remplie, on la soustrait de "quantité en cours"
        if quantite_vendue:
            quantite_vendue = int(quantite_vendue)
            if quantite_vendue > stock.quantite_en_cours:
                return JsonResponse({'error': 'Quantité vendue dépasse la quantité disponible.'})

            stock.quantite_en_cours -= quantite_vendue
            stock.quantite_restant = stock.quantite_en_cours

        # Cas 2 : Si "quantité en cours" est modifiée
        if quantite_en_cours:
            quantite_en_cours = int(quantite_en_cours)
            stock.quantite_en_cours = quantite_en_cours
            stock.quantite_restant = quantite_en_cours

        # Mise à jour du stock
        stock.heure_date = timezone.now()
        stock.save()

        # Afficher le stock mis à jour
        updated_stock = {
            'message': f"Stock de {stock.produit.nom} modifié le {stock.heure_date.strftime('%Y-%m-%d %H:%M:%S')}",
            'stock': {
                'produit': stock.produit.nom,
                'quantite_en_cours': stock.quantite_en_cours,
                'quantite_restant': stock.quantite_restant,
                'heure_date': stock.heure_date.strftime('%Y-%m-%d %H:%M:%S')
            }
        }
        return JsonResponse(updated_stock)

    context = {
        'stocks': stocks,
        'produits': produits
    }
    return render(request, 'stock.html', context)




from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import FactureClient, Prestation, Entreprise,Habilitation
from django.contrib.auth.decorators import login_required






from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from .models import FactureClient, Prestation, Entreprise
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .models import FactureClient, Prestation, SalairePaye

@login_required
def facture_client_view(request):
    permissions = habilitation(request.user)
    user = request.user
    entreprise = user.entreprise
    if not permissions['peut_creer_facture']:
        return JsonResponse({'error': 'Vous n\'avez pas les autorisations nécessaires pour créer une facture.'})

    if request.method == 'POST':
        client_nom = request.POST.get('client_nom')
        client_prenom = request.POST.get('client_prenom')
        client_telephone = request.POST.get('client_telephone')
        
        # Création de la facture
        facture = FactureClient.objects.create(
            client_nom=client_nom,
            client_prenom=client_prenom,
            client_telephone=client_telephone,
            entreprise=entreprise,
            date_creation=timezone.now()
        )

        # Ajout des prestations à la facture
        prestations_desc = request.POST.getlist('prestations[]')
        prestations_prix = request.POST.getlist('prix[]')

        for desc, prix in zip(prestations_desc, prestations_prix):
            prestation = Prestation.objects.create(description=desc, prix=prix)
            facture.prestations.add(prestation)
        
        # Calcul du total
        facture.calculer_total()

        return JsonResponse({'message': 'Facture créée avec succès.', 'facture_id': facture.id})

    factures = FactureClient.objects.filter(entreprise=entreprise).select_related('entreprise')
    
    return render(request, 'facture_client.html', {'factures': factures, 'entreprise': entreprise})





from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

def telecharger_pdf(request, facture_id):
    facture = get_object_or_404(FactureClient, id=facture_id)
    html_string = render_to_string('facture_pdf.html', {'facture': facture})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="Facture_{facture.id}.pdf"'

    HTML(string=html_string).write_pdf(response)
    return response





def habilitation(user):
    entreprise = user.entreprise  # Récupérer l'entreprise de l'utilisateur

    if user.is_patron:
        return {
            'peut_creer_produit': True,
            'peut_creer_service': True,
            'peut_enregistrer_vente': True,
            'peut_enregistrer_depense': True,
            'peut_creer_facture': True,
            'peut_telecharger_pdf': True,
            'peut_consulter_bilan': True,
        }

    try:
        habilitation = Habilitation.objects.get(user=user, user__entreprise=entreprise)
        return {
            'peut_creer_produit': habilitation.peut_creer_produit,
            'peut_creer_service': habilitation.peut_creer_service,
            'peut_enregistrer_vente': habilitation.peut_enregistrer_vente,
            'peut_enregistrer_depense': habilitation.peut_enregistrer_depense,
            'peut_creer_facture': habilitation.peut_creer_facture,
            'peut_telecharger_pdf': habilitation.peut_telecharger_pdf,
            'peut_consulter_bilan': habilitation.peut_consulter_bilan,
        }
    except Habilitation.DoesNotExist:
        return {
            'peut_creer_produit': False,
            'peut_creer_service': False,
            'peut_enregistrer_vente': True,
            'peut_enregistrer_depense': False,
            'peut_creer_facture': False,
            'peut_telecharger_pdf': False,
            'peut_consulter_bilan': False,
        }


"""""
def habilitation(user):
    entreprise = user.entreprise  # Récupérer l'entreprise de l'utilisateur

    if user.is_patron:
        return {
            'peut_creer_produit': True,
            'peut_creer_service': True,
            'peut_enregistrer_vente': True,
            'peut_enregistrer_depense': True,
            'peut_creer_facture': True,
            'peut_telecharger_pdf': True,
            'peut_consulter_bilan': True,
        }

    try:
        habilitation = Habilitation.objects.get(user=user, user__entreprise=entreprise)
        return {
            'peut_creer_produit': habilitation.peut_creer_produit,
            'peut_creer_service': habilitation.peut_creer_service,
            'peut_enregistrer_vente': habilitation.peut_enregistrer_vente,
            'peut_enregistrer_depense': habilitation.peut_enregistrer_depense,
            'peut_creer_facture': habilitation.peut_creer_facture,
            'peut_telecharger_pdf': habilitation.peut_telecharger_pdf,
            'peut_consulter_bilan': habilitation.peut_consulter_bilan,
        }
    except Habilitation.DoesNotExist:
        return {
            'peut_creer_produit': False,
            'peut_creer_service': False,
            'peut_enregistrer_vente': True,
            'peut_enregistrer_depense': False,
            'peut_creer_facture': False,
            'peut_telecharger_pdf': False,
            'peut_consulter_bilan': False,
        }
 """

from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import CustomUser, Habilitation
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Habilitation
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import CustomUser, Employe
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from django.http import HttpResponse
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Sum
from .models import Vente, Depense, FactureClient  # Assurez-vous d'importer vos modèles

def download_pdf(request):
    user = request.user
    entreprise = user.entreprise

    if entreprise is None:
        return HttpResponse("Aucune entreprise associée à votre profil.", status=400)

    # Récupérer les données pour le PDF
    ventes_data = Vente.objects.filter(entreprise=entreprise).values('date__date').annotate(total_ventes=Sum('total'))
    depenses_data = Depense.objects.filter(entreprise=entreprise).values('date__date').annotate(total_depenses=Sum('montant'))
    factures_data = FactureClient.objects.filter(entreprise=entreprise)

    ventes_labels = [item['date__date'].strftime('%Y-%m-%d') for item in ventes_data]
    ventes_totals = [item['total_ventes'] for item in ventes_data]

    depenses_labels = [item['date__date'].strftime('%Y-%m-%d') for item in depenses_data]
    depenses_totals = [item['total_depenses'] for item in depenses_data]

    factures_labels = [facture.date_creation.strftime('%Y-%m-%d') for facture in factures_data]
    factures_totals = [facture.total for facture in factures_data]

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="bilan.pdf"'

    # Créer un PDF
    buffer = SimpleDocTemplate(response, pagesize=A4)
    elements = []

    # Styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']

    # Titre
    title = Paragraph("Bilan des Ventes, Dépenses et Factures", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2 * inch))

    # Table des ventes
    elements.append(Paragraph("Ventes:", normal_style))
    ventes_table_data = [["Date", "Total"]]
    ventes_table_data += [[date, total] for date, total in zip(ventes_labels, ventes_totals)]
    
    ventes_table = Table(ventes_table_data)
    ventes_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(ventes_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Table des dépenses
    elements.append(Paragraph("Dépenses:", normal_style))
    depenses_table_data = [["Date", "Total"]]
    depenses_table_data += [[date, total] for date, total in zip(depenses_labels, depenses_totals)]
    
    depenses_table = Table(depenses_table_data)
    depenses_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(depenses_table)
    elements.append(Spacer(1, 0.2 * inch))

    # Table des factures
    elements.append(Paragraph("Factures:", normal_style))
    factures_table_data = [["Date", "Total"]]
    factures_table_data += [[date, total] for date, total in zip(factures_labels, factures_totals)]
    
    factures_table = Table(factures_table_data)
    factures_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    
    elements.append(factures_table)

    # Finaliser le PDF
    buffer.build(elements)

    return response

@login_required
def equipe_view(request):
    user = request.user
    entreprise = user.entreprise

    if not user.is_patron:
        return JsonResponse({'error': 'Vous n\'avez pas les autorisations nécessaires pour accéder à cette page.'}, status=403)

    employes = Employe.objects.filter(user__entreprise=entreprise)

    if request.method == 'POST':
        employe_id = request.POST.get('employe_id')
        employe = Employe.objects.get(id=employe_id)
        montant = employe.salaire

        # Créer une entrée dans SalairePaye
        SalairePaye.objects.create(employe=employe, montant=montant)
        messages.success(request, f"Le salaire de {employe.nom_employe} a été payé avec succès.")

        return redirect('Pugnere:equipe_view')

    # Récupérer tous les paiements de salaires pour afficher dans le tableau
    salaires_payes = SalairePaye.objects.filter(employe__user__entreprise=entreprise)

    return render(request, 'equipe.html', {'employes': employes, 'salaires_payes': salaires_payes})

from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Employe, Habilitation

from django.contrib import messages

@login_required
def mettre_a_jour_habilitation(request, employe_id):
    user = request.user
    entreprise = user.entreprise

    if not user.is_patron:
        return JsonResponse({'error': 'Vous n\'avez pas les autorisations nécessaires pour accéder à cette page.'}, status=403)

    employe = get_object_or_404(Employe, id=employe_id)
    
    habilitation, created = Habilitation.objects.get_or_create(user=employe.user)

    # Mise à jour des habilitations
    habilitation.peut_creer_produit = request.POST.get('peut_creer_produit') == 'on'
    habilitation.peut_creer_service = request.POST.get('peut_creer_service') == 'on'
    habilitation.peut_enregistrer_vente = request.POST.get('peut_enregistrer_vente') == 'on'
    habilitation.peut_enregistrer_depense = request.POST.get('peut_enregistrer_depense') == 'on'
    habilitation.peut_creer_facture = request.POST.get('peut_creer_facture') == 'on'
    habilitation.peut_telecharger_pdf = request.POST.get('peut_telecharger_pdf') == 'on'
    habilitation.peut_consulter_bilan = request.POST.get('peut_consulter_bilan') == 'on'

    habilitation.save()

    messages.success(request, 'Les habilitations ont été mises à jour avec succès.')
    
    return redirect('Pugnere:equipe')

from django.shortcuts import redirect

def index(request):
    # Vérifier si l'utilisateur est connecté
    if not request.user.is_authenticated:
        return redirect('Pugnere:passerelle')  # Rediriger vers la passerelle si l'utilisateur n'est pas connecté

    context = afficher_produits_et_services(request)
    context.update(afficher_ventes(request))
    context.update(compter_ventes_journee(request))
    
    # Ajouter les factures et les dépenses
    context.update(afficher_factures(request))
    context.update(afficher_depenses(request))
    
    # Ajouter les factures et les dépenses de la journée
    context.update(compter_depenses_et_factures_journee(request))
    context.update(habilitation(request.user))  # Passer l'utilisateur ici
    
    return render(request, 'index.html', context)



from django.contrib.auth import logout
from django.shortcuts import redirect

def deconnexion(request):
    logout(request)  # Cette ligne désauthentifie l'utilisateur
    return redirect('Pugnere:passerelle')  # Redirige vers la page du marketplace


from django.shortcuts import render

# Vue simple pour passerelle
def passerelle(request):
    # Vous pouvez ajouter des variables ou des données supplémentaires ici si nécessaire
    return render(request, 'pass.html')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import SalairePaye, Employe
from django.utils import timezone

def payer_a_nouveau(request, salaire_paye_id):
    if request.method == "POST":
        # Obtenez l'objet SalairePaye correspondant à l'ID
        salaire_paye = get_object_or_404(SalairePaye, id=salaire_paye_id)
        employe = salaire_paye.employe

        # Logique de paiement ici
        montant = salaire_paye.montant  # Vous pouvez aussi définir un nouveau montant si nécessaire
        date_paiement = timezone.now()  # Date de paiement actuelle

        # Créez un nouvel enregistrement de SalairePaye
        SalairePaye.objects.create(employe=employe, montant=montant, date_paiement=date_paiement)

        messages.success(request, f"Le salaire de {employe.nom_employe} a été payé avec succès.")
        return redirect('Pugnere:equipe')  # Redirigez vers la page de l'équipe ou une autre page appropriée

    return redirect('Pugnere:equipe')  # Redirection si la méthode n'est pas POST
