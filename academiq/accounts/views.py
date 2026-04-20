from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import LoginForm, InscriptionForm


def accueil(request):
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    login_form = LoginForm(request.POST if request.method == 'POST' and 'login_submit' in request.POST else None)
    inscription_form = InscriptionForm(request.POST if request.method == 'POST' and 'inscription_submit' in request.POST else None)

    if request.method == 'POST':
        if 'login_submit' in request.POST and login_form.is_valid():
            email = login_form.cleaned_data['email']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=email, password=password)
            if user is None:
                messages.error(request, "Email ou mot de passe incorrect.")
            elif not user.actif:
                messages.error(request, "Ce compte est désactivé. Contactez l'administration.")
            else:
                login(request, user)
                return redirect('accounts:dashboard')

        elif 'inscription_submit' in request.POST and inscription_form.is_valid():
            personne = inscription_form.save(commit=False)
            personne.set_password(inscription_form.cleaned_data['password'])
            personne.actif = False
            personne.save()
            # Notifier tous les agents DIRECTION et SCOLARITE
            from core.models import Notification, Personne as P
            from django.contrib.auth.models import Group
            destinataires = P.objects.filter(
                groups__name__in=['DIRECTION', 'SCOLARITE'], actif=True
            ).distinct()
            for dest in destinataires:
                Notification.objects.create(
                    destinataire=dest,
                    message=f"Nouvelle demande d'inscription : {personne.get_full_name()} ({personne.email})",
                    type_notif='annonce',
                )
            messages.success(request, "Votre demande a été envoyée. L'administration vous contactera pour activer votre compte.")
            return redirect('accounts:accueil')

    return render(request, 'accounts/accueil.html', {
        'login_form': login_form,
        'inscription_form': inscription_form,
    })


def login_view(request):
    return redirect('accounts:accueil')


def logout_view(request):
    logout(request)
    return redirect('accounts:accueil')


@login_required
def dashboard(request):
    """Redirige l'utilisateur vers son espace selon son groupe Django."""
    groupes = request.user.groups.values_list('name', flat=True)

    if any(g in groupes for g in ['DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES']):
        return redirect('personnel:dashboard')
    elif 'ENSEIGNANT' in groupes:
        return redirect('enseignant:dashboard')
    elif 'ELEVE' in groupes:
        return redirect('eleve:dashboard')
    elif 'PARENT' in groupes:
        return redirect('parent:dashboard')

    # Superuser → admin Django
    if request.user.is_superuser:
        return redirect('/admin/')

    messages.warning(request, "Votre compte n'est associé à aucun rôle. Contactez l'administration.")
    return redirect('accounts:login')


def acces_refuse(request):
    return render(request, 'accounts/403.html', status=403)


@login_required
def mon_profil(request):
    user = request.user
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'photo':
            if 'photo_profil' in request.FILES:
                user.photo_profil = request.FILES['photo_profil']
                user.save()
                messages.success(request, "Photo de profil mise à jour.")
            else:
                messages.error(request, "Aucun fichier sélectionné.")

        elif action == 'password':
            ancien = request.POST.get('ancien_mdp', '')
            nouveau = request.POST.get('nouveau_mdp', '')
            confirm = request.POST.get('confirm_mdp', '')
            if not user.check_password(ancien):
                messages.error(request, "Mot de passe actuel incorrect.")
            elif len(nouveau) < 6:
                messages.error(request, "Le nouveau mot de passe doit contenir au moins 6 caractères.")
            elif nouveau != confirm:
                messages.error(request, "Les mots de passe ne correspondent pas.")
            else:
                user.set_password(nouveau)
                user.save()
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, user)
                messages.success(request, "Mot de passe modifié avec succès.")

        return redirect('accounts:mon_profil')

    groupes = list(user.groups.values_list('name', flat=True))
    return render(request, 'accounts/profil.html', {'groupes': groupes})
