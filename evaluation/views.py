

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login ,logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os

from django.utils import timezone
# Create your views here.

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from django.core.files.base import ContentFile


from .models import EvaluationMultQ
from .models import QuestionType
from .models import ProfileUser



def accueil(request):
    return render(request, 'Acceuil.html')


def guidage_page(request):
    return render(request, 'user_page/Guidage.html')

from django.core.cache import cache

def evaluation_page(request):
    # Récupérer les évaluations pour chaque module
    evaluations_generalites = EvaluationMultQ.objects.filter(additional_module='generalites',user=request.user)
    print(evaluations_generalites)
    evaluations_logiciels = EvaluationMultQ.objects.filter(additional_module='logiciels',user=request.user)
    evaluations_algorithmique = EvaluationMultQ.objects.filter(additional_module='algorithmique',user=request.user)
    evaluations_reseaux = EvaluationMultQ.objects.filter(additional_module='reseaux',user=request.user)
    
    try:
        # Récupérer le profil de l'utilisateur s'il existe
        Profile_user = ProfileUser.objects.get(user=request.user)
    except ProfileUser.DoesNotExist:
        Profile_user = None  #

    # Passer les évaluations au template
    context = {
        'evaluations_generalites': evaluations_generalites,
        'evaluations_logiciels': evaluations_logiciels,
        'evaluations_algorithmique': evaluations_algorithmique,
        'evaluations_reseaux': evaluations_reseaux,
        'user':request.user,
        'profile_user':Profile_user,
    }
    return render(request, 'user_page/Evaluation.html', context)

def evaluation_discussion(request):
    return render(request, 'user_page/Discussion.html')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Count, Q


@csrf_exempt
def evalution_search_construit(request):
    if request.method == 'POST':
        module = request.POST.get('module')
        type_item = 'constructed'  # Type d'item recherché

         # Mapper les valeurs de modules aux noms complets
        module_map = {
            'generalites': 'Généralités sur les systèmes informatiques',
            'logiciels': 'Logiciels',
            'algorithmique': 'Algorithmique et Programmation',
            'réseaux': 'Réseaux et Internet'
        }

        # Récupérer les évaluations basées sur le module et les questions de type 'constructed'
        evaluations = EvaluationMultQ.objects.annotate(num_question_types=Count('question_types')).filter(
            num_question_types=1,  # Il y a exactement un objet dans question_types
            question_types__name=type_item,  # Le nom de l'objet est 'single'
            additional_module=module,
        )

        # Liste pour stocker les URLs des fichiers téléchargés
        evaluations_urls = []

        # Boucler à travers les évaluations et récupérer les URLs des fichiers
        for evaluation in evaluations:
            evaluations_urls.append(evaluation.uploaded_files.url)

        # Réponse JSON avec les URLs des fichiers téléchargés
        response_data = {
            'module': module_map.get(module, 'Module non trouvé'),
            'type_item': "construite",
            'evaluations_urls': evaluations_urls,
            'message': 'Recherche effectuée avec succès'
        }

        return JsonResponse(response_data)
    return JsonResponse({'message': 'Méthode non autorisée'}, status=405)


@csrf_exempt
def modal_search_view(request):
    if request.method == 'POST':
        module = request.POST.get('module')
        type_item = request.POST.get('type_item')

         # Mapper les valeurs de modules aux noms complets
        module_map = {
            'generalites': 'Généralités sur les systèmes informatiques',
            'logiciels': 'Logiciels',
            'algorithmique': 'Algorithmique et Programmation',
            'réseaux': 'Réseaux et Internet'
        }

         # Mapper les valeurs de type_item aux noms complets
        type_item_map = {
            'multiple': 'Choix multiple',
            'single': 'Choix simple ',
        }

        # Récupérer les évaluations basées sur le module et les questions de type 'constructed'
        evaluations = EvaluationMultQ.objects.annotate(num_question_types=Count('question_types')).filter(
            num_question_types=1,  # Il y a exactement un objet dans question_types
            question_types__name=type_item , # Le nom de l'objet est 'single',
            additional_module=module,
            
        )
        

        

        # Liste pour stocker les URLs des fichiers téléchargés
        evaluations_urls = []

        # Boucler à travers les évaluations et récupérer les URLs des fichiers
        for evaluation in evaluations:
            evaluations_urls.append(evaluation.uploaded_files.url)

        # Réponse JSON avec les URLs des fichiers téléchargés
        response_data = {
            'module':  module_map.get(module, 'Module non trouvé'),
            'type_item': type_item_map.get(type_item, 'Type d\'item non trouvé'),
            'evaluations_urls': evaluations_urls,
            'message': 'Recherche effectuée avec succès'
        }
        print(response_data)
        return JsonResponse(response_data)
    return JsonResponse({'message': 'Méthode non autorisée'}, status=405)

from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404


@csrf_exempt
def submit_evaluation_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        evaluation_data = data.get('evaluationData', [])

        # Vérifier si l'utilisateur avec ID 1 existe, sinon la créer (à adapter selon vos besoins)


        # Créer une nouvelle instance d'évaluation pour l'utilisateur
        evaluation_instance = EvaluationMultQ.objects.create(user=request.user)

        # Génération du PDF
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="evaluation.pdf"'

        # Création du canvas PDF
        c = canvas.Canvas(response, pagesize='A4')
        c.setFont("Helvetica-Bold", 12)

        # Position de départ pour l'écriture
        y_start = 700

        # Déterminer le type d'évaluation et ajuster le titre en conséquence
        evaluation_type = evaluation_data[0].get('evaluationType', 'generalites')
        evaluation_instance.additional_module = evaluation_type  # Attribuer la valeur de evaluation_type
        evaluation_instance.save()  # Sauvegarder l'instance modifiée

        title = "Évaluation"

        if evaluation_type == 'generalites':
            title += " Généralités sur les systèmes informatiques"
        elif evaluation_type == 'logiciels':
            title += " Logiciels"
        elif evaluation_type == 'algorithmique':
            title += " Algorithmique et Programmation"
        elif evaluation_type == 'reseaux':
            title += " Réseaux et Internet"

        # Écrire le titre centré
        c.drawCentredString(300, y_start, title)
        y_start -= 20  # Descendre de 20 points

        c.setFont("Helvetica", 10)

        for evaluation_item in evaluation_data:
            question_number = evaluation_item.get('questionNumber', '')
            question_type = evaluation_item.get('type', '')
            question = evaluation_item.get('question', '')
            answers = evaluation_item.get('answers', [])

            question_type_instance, _ = QuestionType.objects.get_or_create(name=question_type)
            evaluation_instance.question_types.add(question_type_instance)
            evaluation_instance.save()

            # Écrire la question
            c.drawString(50, y_start, f"Question {question_number}: {question}")
            y_start -= 20  # Descendre de 20 points

            if question_type == 'multiple':
                # Pour les choix multiples, écrire chaque réponse avec un carré de coche
                for index, answer in enumerate(answers):
                    # Dessiner un carré à cocher
                    c.rect(70, y_start - 3, 10, 10)  # Position x, y, largeur, hauteur
                    c.drawString(90, y_start, f" {answer}")
                    y_start -= 15  # Descendre de 15 points
            elif question_type == 'single':
                # Pour le choix unique, écrire les choix vrai ou faux
                c.rect(70, y_start - 3, 10, 10)  # Dessiner un carré à cocher
                c.drawString(90, y_start, "Vrai")
                y_start -= 15  # Descendre de 15 points
                c.rect(70, y_start - 3, 10, 10)  # Dessiner un carré à cocher
                c.drawString(90, y_start, "Faux")
                y_start -= 15  # Descendre de 15 points

            # Sauter 20 points avant la prochaine question
            y_start -= 20

        # Sauvegarder le PDF dans le stockage par défaut (MEDIA_ROOT)
        file_name = f'evaluation_{evaluation_instance.id}.pdf'
        c.save()

        # Enregistrer le fichier PDF dans le champ uploaded_files de l'instance d'évaluation
        pdf_file_content = response.content
        pdf_file = ContentFile(pdf_file_content)
        evaluation_instance.uploaded_files.save(file_name, pdf_file)

        # Récupérer l'URL du fichier PDF sauvegardé
        pdf_url = evaluation_instance.uploaded_files.url

        # Retourner la réponse JSON avec l'URL du fichier PDF
        return JsonResponse({'evaluationType': evaluation_type, 'pdf_url': pdf_url})

    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)



def submit_evaluation_with_pdf(request):
    if request.method == 'POST':
        # Récupérer l'objet Evaluation de l'utilisateur connecté s'il existe, sinon le créer
        evaluation = EvaluationMultQ.objects.create(user=request.user)
        
        # Récupérer les données du formulaire
        evaluation_type = request.POST.get('evaluationType')
        evaluation.additional_module = evaluation_type  # Attribuer la valeur de evaluation_type
        evaluation.save()  # Sauvegarder l'instance modifiée

        pdf_upload = request.FILES.get('pdfUpload')
        print(evaluation_type)
        
        # Vérifier si un fichier PDF a été téléchargé
        if pdf_upload:
            evaluation.uploaded_files = pdf_upload
            evaluation.save()
            
            # Récupérer l'URL du fichier PDF ajouté
            pdf_url = evaluation.uploaded_files.url
            question_type = request.POST.get('questionType')
            if question_type:
                question_type_instance, created = QuestionType.objects.get_or_create(name=question_type)
                evaluation.question_types.add(question_type_instance)
           
            evaluation.save()

            return JsonResponse({'success': True, 'pdf_url': pdf_url, 'evaluation_type': evaluation_type})
        else:
            return JsonResponse({'success': False, 'error': 'Aucun fichier PDF n\'a été téléchargé.'})
    else:
        return JsonResponse({'success': False, 'error': 'Méthode de requête invalide.'})
    

def modify_profile(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire POST
        new_name = request.POST.get('new_name', None)
        new_email = request.POST.get('new_email', None)
        new_image = request.FILES.get('new_image', None)

        # Récupérer le profil utilisateur ou le créer s'il n'existe pas
        profile, created = ProfileUser.objects.get_or_create(user=request.user)

        # Exemple de traitement des données (vous pouvez adapter selon vos besoins)
        if new_name:
            request.user.username = new_name
            request.user.save()

        if new_email:
            request.user.email = new_email
            request.user.save()

        if new_image:
            profile.profile_image = new_image
            profile.save()

        # Réponse JSON pour indiquer que la modification a réussi
        return JsonResponse({'message': 'Profil modifié avec succès.'})

    # Gérer le cas où la méthode n'est pas POST (par exemple, rediriger ou afficher un message d'erreur)
    return JsonResponse({'error': 'Méthode non autorisée.'}, status=405)




@login_required
def admin_page(request):
    # Vérifiez si l'utilisateur est le premier utilisateur (ID = 1)
    if request.user.id == 1:
        # Obtenez l'année en cours
        current_year = timezone.now().year

        # Initialisez un dictionnaire pour stocker le nombre d'évaluations par mois
        evaluations_per_month = {}

        # Boucle sur les douze mois de l'année
        for month in range(1, 13):
            # Filtrez les évaluations pour le mois et l'année spécifiés
            count = EvaluationMultQ.objects.filter(
                created_at__year=current_year,
                created_at__month=month
            ).count()
            evaluations_per_month[month] = count

        # Convertissez le dictionnaire en JSON pour le passage au template
        evaluations_per_month_json = json.dumps(evaluations_per_month)

        # Calculer le nombre d'évaluations par type de question
        question_types_count = {}
        question_types = QuestionType.objects.all()

        for question_type in question_types:
            count = EvaluationMultQ.objects.filter(
                question_types=question_type,
                created_at__year=current_year
            ).count()
            question_types_count[question_type.name] = count

        # Préparer les données pour le pie chart
        labels = json.dumps(list(question_types_count.keys()))
        data = json.dumps(list(question_types_count.values()))

        module_counts = {}

        modules = ['generalites', 'logiciels', 'algorithmique','reseaux']  # Remplacez par vos modules réels

        for module in modules:
            count = EvaluationMultQ.objects.filter(
                additional_module=module,
                created_at__year=current_year
            ).count()
            module_counts[module] = count

        # Préparer les données pour le nouveau chart (par module)
        module_chart_labels = json.dumps(list(module_counts.keys()))
        module_chart_data = json.dumps(list(module_counts.values()))
        

        print(module_chart_data)
        print(module_chart_labels)

        # Liste pour stocker les résultats
        results = []

        for module in modules:
             # Compter les évaluations pour ce module avec exactement un type de question 'Single'
               count_single = EvaluationMultQ.objects.filter(
                   user=request.user,  # Remplacez par votre logique d'utilisateur
                   additional_module=module,
                   question_types__name='single'
                ).annotate(num_questions=Count('question_types')).filter(num_questions=1).count()

             # Compter les évaluations pour ce module avec exactement un type de question 'Constructed'
               count_constructed = EvaluationMultQ.objects.filter(
                user=request.user,  # Remplacez par votre logique d'utilisateur
                additional_module=module,
                question_types__name='constructed'
               ).annotate(num_questions=Count('question_types')).filter(num_questions=1).count()

             # Compter les évaluations pour ce module avec exactement un type de question 'Multiple'
               count_multiple = EvaluationMultQ.objects.filter(
                   user=request.user,  # Remplacez par votre logique d'utilisateur
                   additional_module=module,
                    question_types__name='multiple'
                  ).annotate(num_questions=Count('question_types')).filter(num_questions=1).count()

             # Ajouter le résultat à la liste des résultats
               results.append({
                 'module': module,
                 'count_single': count_single,
                 'count_constructed': count_constructed,
                 'count_multiple': count_multiple
              })

        print(results)

        context = {
            'user': request.user,
            'evaluations_per_month_json': evaluations_per_month_json,
            'pie_chart_labels': labels,
            'pie_chart_data': data,
            'module_chart_labels': module_chart_labels,
            'module_chart_data': module_chart_data,
        }

        return render(request, 'admin_page.html', context)
    else:
        # Redirigez les utilisateurs non autorisés vers la page d'accueil ou une autre page
        return redirect('accueil')
    



def utilisateurs_view(request):
    # Récupérer tous les utilisateurs avec la date d'ajout
    utilisateurs = User.objects.all().order_by('-date_joined')

    # Liste pour stocker les données à afficher dans le template
    users_data = []

    # Boucler à travers chaque utilisateur pour récupérer les données nécessaires
    for user in utilisateurs:
        # Récupérer le nombre total d'évaluations pour cet utilisateur
        evaluations_count = EvaluationMultQ.objects.filter(user=user).count()

        # Récupérer le profil utilisateur s'il existe
        try:
            profile = ProfileUser.objects.get(user=user)
            profile_image_url = profile.profile_image.url if profile.profile_image else ''
        except ProfileUser.DoesNotExist:
            profile_image_url = ''

        # Préparer les données à ajouter à la liste
        user_data = {
            'id':user.id,
            'username': user.username,
            'address': user.email,
            'image_url': profile_image_url,
            'evaluations_count': evaluations_count,
            'date_joined': user.date_joined.strftime('%d/%m/%Y %H:%M')  # Formatage de la date d'ajout
        }

        users_data.append(user_data)

    # Rendre le template avec les données des utilisateurs
    return render(request, 'admin_page_utilisateurs.html', {'users_data': users_data})



from django.core.mail import send_mail
from django.conf import settings

def send_welcome_email(username, email, password):
    subject = 'Bienvenue sur LearnEva'
    plain_message = f'Bonjour {username},\n\nBienvenue sur LearnEva ! Votre compte a été créé avec succès.\n\nVoici vos informations de connexion :\n\nNom d\'utilisateur : {username}\nMot de passe : {password}\n\nConnectez-vous à LearnEva dès maintenant et commencez à utiliser notre plateforme !'
    
    html_message = f'''
    <html>
        <body>
            <p>Bonjour <strong>{username}</strong>,</p>
            <p>Bienvenue sur <strong>LearnEva</strong> ! Votre compte a été créé avec succès.</p>
            <p>Voici vos informations de connexion :</p>
            <ul>
                <li><strong>Nom d'utilisateur :</strong> {username}</li>
                <li><strong>Email :</strong> {email}</li>
                <li><strong>Mot de passe :</strong> {password}</li>
            </ul>
            <p>Connectez-vous à <strong>LearnEva</strong> dès maintenant et commencez à utiliser notre plateforme !</p>
            <p>Cordialement,<br>L'équipe LearnEva</p>
        </body>
    </html>
    '''
    
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [email]

    send_mail(subject, plain_message, from_email, recipient_list, html_message=html_message)


import secrets
import string

def generate_password(length=8):
    alphabet = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(secrets.choice(alphabet) for i in range(length))
    return password


@csrf_exempt  # Pour désactiver la vérification CSRF lors de l'utilisation de fetch
def add_user_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')

        # Générer un mot de passe aléatoire
        password = generate_password()

        # Créer un nouvel utilisateur Django
        new_user = User.objects.create_user(username=name, email=email, password=password)

        # Envoyer un email à l'utilisateur avec ses informations de connexion
        send_welcome_email(name, email, password)

        # Exemple de réponse JSON pour indiquer le succès
        return JsonResponse({'success': True, 'message': 'Utilisateur ajouté avec succès.'})
    



def delete_user(request, user_id):
    if request.method == 'DELETE':
        user = get_object_or_404(User, id=user_id)
        user.delete()
        return JsonResponse({'message': 'Utilisateur supprimé avec succès.'})
    return JsonResponse({'error': 'Requête invalide.'}, status=400)




@csrf_exempt
def login_view(request):
    # Récupérer les données du formulaire de la requête POST
    email = request.POST.get('email')
    password = request.POST.get('password')

    # Vérifier si l'email existe dans la base de données
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Email ou mot de passe incorrect.'})

    # Authentifier l'utilisateur par le nom d'utilisateur et le mot de passe
    user = authenticate(username=user.username, password=password)
    print(user)

    if user is not None:
        # Authentification réussie, connecter l'utilisateur
        login(request, user)
        return JsonResponse({'success': True, 'redirect_url': '/evaluation_user/evaluation/'})
    else:
        # Authentification échouée
        return JsonResponse({'success': False, 'message': 'Email ou mot de passe incorrect.'})
    
def logout_view(request):
    logout(request)
    # Redirection vers la page d'accueil après la déconnexion
    return redirect('accueil')




def search_users(request):
    if request.method == "GET" and 'q' in request.GET:
        query = request.GET.get('q')
        users = User.objects.filter(username__icontains=query)
        user_list = []
        for user in users:
            profile = ProfileUser.objects.filter(user=user).first()
            if profile and profile.profile_image:
                profile_image_url = profile.profile_image.url
            else:
                profile_image_url = '/media/user_png.png'
            user_list.append({
                'id': user.id,
                'username': user.username,
                'profile_image': profile_image_url,
            })
        return JsonResponse({'users': user_list})
    return JsonResponse({'users': []})