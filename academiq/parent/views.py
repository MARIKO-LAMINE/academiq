from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator

from core.permissions import role_required
from core.edt_utils import construire_grille
from core.models import (
    AnneeScolaire, LienParentEleve, Inscription, Note,
    Absence, Bulletin, Notification, ResultatMatiere, Cours, Personne,
    EmploiDuTemps, Periode, Message, FraisScolarite,
)


def _get_enfants(user):
    """Retourne la liste des enfants liés au parent connecté."""
    return LienParentEleve.objects.filter(parent=user).select_related('eleve')


def _get_eleve_or_403(user, eleve_id):
    """Vérifie que l'élève appartient bien au parent connecté."""
    lien = get_object_or_404(LienParentEleve, parent=user, eleve_id=eleve_id)
    return lien.eleve


# ─── Dashboard ────────────────────────────────────────────────────────────────

@role_required('PARENT')
def dashboard(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    liens = _get_enfants(request.user)
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()

    enfants_data = []
    for lien in liens:
        enfant = lien.eleve
        inscription = Inscription.objects.filter(
            eleve=enfant, annee=annee_active, statut='actif'
        ).select_related('classe').first() if annee_active else None
        cours_ids = []
        if inscription and annee_active:
            cours_ids = list(Cours.objects.filter(
                classe=inscription.classe, annee=annee_active
            ).values_list('pk', flat=True))

        enfants_data.append({
            'enfant': enfant,
            'lien': lien.get_lien_display(),
            'inscription': inscription,
            'nb_notes': Note.objects.filter(eleve=enfant, cours__in=cours_ids).count(),
            'nb_absences': Absence.objects.filter(eleve=enfant, cours__in=cours_ids).count(),
            'derniere_note': Note.objects.filter(eleve=enfant).order_by('-date_saisie').first(),
        })

    return render(request, 'parent/dashboard.html', {
        'annee_active': annee_active,
        'enfants_data': enfants_data,
        'nb_notifs': nb_notifs,
    })


# ─── Suivi d'un enfant ────────────────────────────────────────────────────────

@role_required('PARENT')
def suivi_enfant(request, eleve_id):
    enfant = _get_eleve_or_403(request.user, eleve_id)
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()

    inscription = Inscription.objects.filter(
        eleve=enfant, annee=annee_active, statut='actif'
    ).select_related('classe').first() if annee_active else None

    cours_ids = []
    if inscription and annee_active:
        cours_ids = list(Cours.objects.filter(
            classe=inscription.classe, annee=annee_active
        ).values_list('pk', flat=True))

    notes = Note.objects.filter(
        eleve=enfant, cours__in=cours_ids
    ).select_related('cours__matiere', 'periode').order_by('-date_saisie')[:20]

    absences = Absence.objects.filter(
        eleve=enfant, cours__in=cours_ids
    ).select_related('cours__matiere', 'periode').order_by('-date_absence')[:10]

    resultats = ResultatMatiere.objects.filter(
        eleve=enfant, cours__annee=annee_active
    ).select_related('cours__matiere', 'periode') if annee_active else ResultatMatiere.objects.none()

    bulletins = Bulletin.objects.filter(eleve=enfant).select_related('periode').order_by('-periode__date_debut')

    return render(request, 'parent/suivi_enfant.html', {
        'enfant': enfant,
        'inscription': inscription,
        'annee_active': annee_active,
        'notes': notes,
        'absences': absences,
        'resultats': resultats,
        'bulletins': bulletins,
        'nb_notifs': nb_notifs,
    })


# ─── Détail bulletin (lecture seule) ─────────────────────────────────────────

@role_required('PARENT')
def detail_bulletin(request, eleve_id, bulletin_id):
    enfant = _get_eleve_or_403(request.user, eleve_id)
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id, eleve=enfant)
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()

    resultats = ResultatMatiere.objects.filter(
        eleve=enfant, periode=bulletin.periode
    ).select_related('cours__matiere').order_by('cours__matiere__nom_matiere')

    return render(request, 'parent/bulletin_detail.html', {
        'enfant': enfant,
        'bulletin': bulletin,
        'resultats': resultats,
        'annee_active': annee_active,
        'nb_notifs': nb_notifs,
    })


# ─── Emploi du temps d'un enfant ─────────────────────────────────────────────

JOURS_ORDER = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
JOURS_LABELS = {
    'lundi': 'Lundi', 'mardi': 'Mardi', 'mercredi': 'Mercredi',
    'jeudi': 'Jeudi', 'vendredi': 'Vendredi', 'samedi': 'Samedi',
}


@role_required('PARENT')
def edt_enfant(request, eleve_id):
    enfant = _get_eleve_or_403(request.user, eleve_id)
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()

    inscription = Inscription.objects.filter(
        eleve=enfant, annee=annee_active, statut='actif'
    ).select_related('classe').first() if annee_active else None

    periodes = Periode.objects.filter(annee=annee_active).order_by('date_debut') if annee_active else Periode.objects.none()
    periode_id = request.GET.get('periode')
    periode_sel = None
    creneaux_par_jour = {}
    grille = None

    if inscription and annee_active:
        if periode_id:
            periode_sel = get_object_or_404(Periode, pk=periode_id, annee=annee_active)
        else:
            from datetime import date
            periode_sel = periodes.filter(date_debut__lte=date.today(), date_fin__gte=date.today()).first() or periodes.first()

        if periode_sel:
            creneaux = EmploiDuTemps.objects.filter(
                cours__classe=inscription.classe,
                periode=periode_sel,
            ).select_related('cours__matiere', 'cours__enseignant', 'salle').order_by('heure_debut')

            for jour in JOURS_ORDER:
                slots = [c for c in creneaux if c.jour == jour]
                if slots:
                    creneaux_par_jour[jour] = slots
            grille = construire_grille(creneaux)

    return render(request, 'parent/edt_enfant.html', {
        'enfant': enfant,
        'inscription': inscription,
        'annee_active': annee_active,
        'periodes': periodes,
        'periode_sel': periode_sel,
        'creneaux_par_jour': creneaux_par_jour,
        'jours_labels': JOURS_LABELS,
        'grille': grille,
        'edt_mode': 'classe',
        'nb_notifs': nb_notifs,
    })


# ─── Scolarité / Paiements ───────────────────────────────────────────────────

@role_required('PARENT')
def mes_paiements(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()
    liens = _get_enfants(request.user)

    enfants_frais = []
    for lien in liens:
        try:
            frais = FraisScolarite.objects.get(eleve=lien.eleve, annee=annee_active) if annee_active else None
        except FraisScolarite.DoesNotExist:
            frais = None
        paiements = frais.paiements.order_by('-date_paiement') if frais else []
        enfants_frais.append({'lien': lien, 'frais': frais, 'paiements': paiements})

    return render(request, 'parent/paiements.html', {
        'enfants_frais': enfants_frais,
        'annee_active': annee_active,
        'nb_notifs': nb_notifs,
    })



# ─── Annonces ────────────────────────────────────────────────────────────────

@role_required('PARENT')
def mes_annonces(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()
    liens = _get_enfants(request.user)

    # Collecter les classes de tous les enfants inscrits cette année
    classes_enfants = []
    for lien in liens:
        insc = Inscription.objects.filter(
            eleve=lien.eleve, annee=annee_active, statut='actif'
        ).select_related('classe').first() if annee_active else None
        if insc:
            classes_enfants.append(insc.classe)

    annonces = Notification.objects.filter(
        type_notif='annonce',
        classe__in=classes_enfants,
    ).order_by('-date_envoi') if classes_enfants else Notification.objects.none()

    return render(request, 'parent/annonces.html', {
        'annonces': annonces,
        'annee_active': annee_active,
        'nb_notifs': nb_notifs,
        'classes_enfants': classes_enfants,
    })


# ─── Messagerie ───────────────────────────────────────────────────────────────

@role_required('PARENT')
def messagerie(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()
    recus   = Message.objects.filter(destinataire=request.user).order_by('-date_envoi')
    envoyes = Message.objects.filter(expediteur=request.user).order_by('-date_envoi')
    nb_non_lus = recus.filter(lu=False).count()
    return render(request, 'parent/messagerie/liste.html', {
        'recus': recus[:20], 'envoyes': envoyes[:20],
        'nb_non_lus': nb_non_lus,
        'annee_active': annee_active, 'nb_notifs': nb_notifs,
    })


@role_required('PARENT')
def envoyer_message(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()
    if request.method == 'POST':
        dest_id = request.POST.get('destinataire')
        sujet   = request.POST.get('sujet', '').strip()
        corps   = request.POST.get('corps', '').strip()
        if dest_id and sujet and corps:
            try:
                dest = Personne.objects.get(pk=dest_id, actif=True)
                piece = request.FILES.get('piece_jointe')
                if piece and not piece.name.lower().endswith('.pdf'):
                    messages.error(request, "Seuls les fichiers PDF sont acceptés.")
                    return redirect('parent:envoyer_message')
                msg_obj = Message(expediteur=request.user, destinataire=dest, sujet=sujet, corps=corps)
                if piece:
                    msg_obj.piece_jointe = piece
                msg_obj.save()
                messages.success(request, f"Message envoyé à {dest.get_full_name()}.")
            except Personne.DoesNotExist:
                messages.error(request, "Destinataire introuvable.")
        else:
            messages.error(request, "Veuillez remplir tous les champs.")
        return redirect('parent:messagerie')
    destinataires = Personne.objects.filter(
        actif=True, groups__name__in=['DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES', 'ENSEIGNANT']
    ).exclude(pk=request.user.pk).distinct().order_by('nom')
    return render(request, 'parent/messagerie/nouveau.html', {
        'destinataires': destinataires,
        'annee_active': annee_active, 'nb_notifs': nb_notifs,
    })


@role_required('PARENT')
def lire_message(request, pk):
    from django.db.models import Q
    from django.core.exceptions import PermissionDenied
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()
    msg = Message.objects.filter(
        Q(destinataire=request.user) | Q(expediteur=request.user), pk=pk
    ).first()
    if not msg:
        messages.error(request, "Ce message est introuvable ou ne vous appartient pas.")
        return redirect('parent:messagerie')
    if msg.destinataire == request.user and not msg.lu:
        msg.lu = True
        msg.save(update_fields=['lu'])
    return render(request, 'parent/messagerie/detail.html', {
        'msg': msg,
        'annee_active': annee_active, 'nb_notifs': nb_notifs,
    })


# ─── Notifications ────────────────────────────────────────────────────────────

@role_required('PARENT')
def mes_notifications(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()
    notifs = Notification.objects.filter(destinataire=request.user).order_by('-date_envoi')
    Notification.objects.filter(destinataire=request.user, lu=False).update(lu=True)
    paginator = Paginator(notifs, 20)
    return render(request, 'parent/notifications.html', {
        'page_obj': paginator.get_page(request.GET.get('page')),
        'annee_active': annee_active,
        'nb_notifs': nb_notifs,
    })
