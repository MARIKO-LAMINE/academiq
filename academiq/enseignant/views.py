from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator

from core.permissions import role_required
from core.models import (
    Cours, Note, Absence, AnneeScolaire, Inscription,
    ResultatMatiere, Notification, EmploiDuTemps, Periode,
    Message, Personne, EvenementScolaire,
)
from core.edt_utils import construire_grille
from .forms import NoteForm, AbsenceForm


# ─── Dashboard ────────────────────────────────────────────────────────────────

@role_required('ENSEIGNANT')
def dashboard(request):
    import json
    from django.db.models import Avg, Count
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    mes_cours = Cours.objects.filter(
        enseignant=request.user, annee=annee_active
    ).select_related('matiere', 'classe') if annee_active else Cours.objects.none()

    nb_notes    = Note.objects.filter(cours__enseignant=request.user).count()
    nb_absences = Absence.objects.filter(cours__enseignant=request.user).count()
    nb_notifs   = Notification.objects.filter(destinataire=request.user, lu=False).count()

    # Graphique : moyenne par cours
    chart_labels, chart_data = [], []
    for cours in mes_cours:
        moy = Note.objects.filter(cours=cours).aggregate(m=Avg('valeur'))['m']
        if moy is not None:
            chart_labels.append(f"{cours.matiere.nom_matiere[:15]} / {cours.classe.nom}")
            chart_data.append(round(float(moy), 2))

    # Graphique : répartition des notes (tranches)
    notes_qs = Note.objects.filter(cours__enseignant=request.user)
    tranches = [0, 0, 0, 0]  # <8, 8-10, 10-14, >=14
    for n in notes_qs.values_list('valeur', flat=True):
        v = float(n)
        if v < 8:        tranches[0] += 1
        elif v < 10:     tranches[1] += 1
        elif v < 14:     tranches[2] += 1
        else:            tranches[3] += 1

    return render(request, 'enseignant/dashboard.html', {
        'annee_active':  annee_active,
        'mes_cours':     mes_cours,
        'nb_notes':      nb_notes,
        'nb_absences':   nb_absences,
        'nb_notifs':     nb_notifs,
        'chart_cours_labels': json.dumps(chart_labels),
        'chart_cours_data':   json.dumps(chart_data),
        'chart_tranches_data': json.dumps(tranches),
    })


# ─── Mes cours ────────────────────────────────────────────────────────────────

@role_required('ENSEIGNANT')
def mes_cours(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    cours_qs = Cours.objects.filter(
        enseignant=request.user, annee=annee_active
    ).select_related('matiere', 'classe') if annee_active else Cours.objects.none()
    return render(request, 'enseignant/cours/liste.html', {
        'cours_list': cours_qs,
        'annee_active': annee_active,
    })


# ─── Détail d'un cours (élèves + notes) ──────────────────────────────────────

@role_required('ENSEIGNANT')
def detail_cours(request, cours_id):
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)

    inscriptions = Inscription.objects.filter(
        classe=cours.classe, annee=cours.annee, statut='actif'
    ).select_related('eleve')

    notes = Note.objects.filter(cours=cours).select_related('eleve', 'periode').order_by('-date_saisie')

    return render(request, 'enseignant/cours/detail.html', {
        'cours': cours,
        'inscriptions': inscriptions,
        'notes': notes,
    })


# ─── Saisir une note ──────────────────────────────────────────────────────────

@role_required('ENSEIGNANT')
def saisir_note(request, cours_id):
    from datetime import date
    from core.models import Periode
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)
    form = NoteForm(cours, request.POST or None)

    if request.method == 'POST':
        # RG-N06: bloquer si la période sélectionnée est clôturée ou terminée
        periode_id = request.POST.get('periode')
        if periode_id:
            try:
                periode = Periode.objects.get(pk=periode_id)
                if periode.cloturee or periode.date_fin < date.today():
                    messages.error(request, f"La période '{periode.nom}' est clôturée. Saisie de note impossible.")
                    return render(request, 'enseignant/notes/form.html', {'form': form, 'cours': cours})
            except Periode.DoesNotExist:
                pass

        if form.is_valid():
            note = form.save(commit=False)
            note.cours = cours
            note.save()
            messages.success(request, f"Note {note.valeur}/20 enregistrée pour {note.eleve.get_full_name()}.")
            return redirect('enseignant:detail_cours', cours_id=cours.pk)

    return render(request, 'enseignant/notes/form.html', {
        'form': form,
        'cours': cours,
    })


# ─── Saisie des notes en liste (toute la classe) ─────────────────────────────

@role_required('ENSEIGNANT')
def saisie_notes(request, cours_id):
    """Saisie groupée : l'enseignant choisit UNE fois la période et le type
    d'évaluation, puis la liste des élèves apparaît pour attribuer les notes."""
    from datetime import date
    from decimal import Decimal, InvalidOperation
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)

    periodes = Periode.objects.filter(annee=cours.annee).order_by('date_debut')
    types_eval = Note.TYPES_EVAL

    periode_id = request.GET.get('periode') or request.POST.get('periode')
    type_eval  = request.GET.get('type_eval') or request.POST.get('type_eval')

    periode_sel = periodes.filter(pk=periode_id).first() if periode_id else None
    type_valide = any(type_eval == t[0] for t in types_eval)

    inscriptions = Inscription.objects.filter(
        classe=cours.classe, annee=cours.annee, statut='actif'
    ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom')

    if request.method == 'POST':
        if not periode_sel or not type_valide:
            messages.error(request, "Veuillez choisir une période et un type d'évaluation.")
        elif periode_sel.cloturee or periode_sel.date_fin < date.today():
            messages.error(request, f"La période '{periode_sel.nom}' est clôturée. Saisie impossible.")
        else:
            nb_ok, erreurs = 0, []
            for insc in inscriptions:
                brut = (request.POST.get(f"note_{insc.eleve_id}") or '').strip().replace(',', '.')
                if not brut:
                    continue
                try:
                    valeur = Decimal(brut)
                except InvalidOperation:
                    erreurs.append(insc.eleve.get_full_name())
                    continue
                if valeur < 0 or valeur > 20:
                    erreurs.append(insc.eleve.get_full_name())
                    continue
                Note.objects.update_or_create(
                    cours=cours, eleve=insc.eleve,
                    periode=periode_sel, type_eval=type_eval,
                    defaults={'valeur': valeur},
                )
                nb_ok += 1
            if nb_ok:
                messages.success(request, f"{nb_ok} note(s) enregistrée(s).")
            if erreurs:
                messages.error(request, "Notes ignorées (valeur invalide) : " + ", ".join(erreurs))
            from django.urls import reverse
            return redirect(f"{reverse('enseignant:saisie_notes', args=[cours.pk])}?periode={periode_sel.pk}&type_eval={type_eval}")

    # Pré-remplissage des notes déjà saisies pour ce couple (période, type)
    notes_existantes = {}
    if periode_sel and type_valide:
        for n in Note.objects.filter(cours=cours, periode=periode_sel, type_eval=type_eval):
            notes_existantes[n.eleve_id] = n.valeur

    eleves = [{
        'eleve': insc.eleve,
        'valeur': notes_existantes.get(insc.eleve_id, ''),
    } for insc in inscriptions]

    return render(request, 'enseignant/notes/saisie.html', {
        'cours': cours,
        'periodes': periodes,
        'types_eval': types_eval,
        'periode_sel': periode_sel,
        'type_eval_sel': type_eval if type_valide else None,
        'eleves': eleves,
        'pret': bool(periode_sel and type_valide),
    })


# ─── Modifier une note ────────────────────────────────────────────────────────

@role_required('ENSEIGNANT')
def modifier_note(request, note_id):
    note = get_object_or_404(Note, pk=note_id, cours__enseignant=request.user)
    cours = note.cours
    form = NoteForm(cours, request.POST or None, instance=note)

    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Note modifiée.")
        return redirect('enseignant:detail_cours', cours_id=cours.pk)

    return render(request, 'enseignant/notes/form.html', {
        'form': form,
        'cours': cours,
        'note': note,
        'titre': 'Modifier la note',
    })


# ─── Saisir une absence ───────────────────────────────────────────────────────

@role_required('ENSEIGNANT')
def saisir_absence(request, cours_id):
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)
    form = AbsenceForm(cours, request.POST or None)

    if request.method == 'POST' and form.is_valid():
        absence = form.save(commit=False)
        absence.cours = cours
        absence.statut = 'non_justifiee'
        absence.save()
        messages.success(request, f"Absence enregistrée pour {absence.eleve.get_full_name()}.")
        return redirect('enseignant:absences_cours', cours_id=cours.pk)

    return render(request, 'enseignant/absences/form.html', {
        'form': form,
        'cours': cours,
    })


# ─── Faire l'appel (feuille de présence) ─────────────────────────────────────

@role_required('ENSEIGNANT')
def faire_appel(request, cours_id):
    """L'enseignant choisit la période (et la date, par défaut aujourd'hui) ;
    la liste de la classe s'affiche avec présent / absent par élève."""
    from datetime import date as date_cls, datetime
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)

    periodes = Periode.objects.filter(annee=cours.annee).order_by('date_debut')
    periode_id = request.GET.get('periode') or request.POST.get('periode')
    periode_sel = periodes.filter(pk=periode_id).first() if periode_id else None

    date_str = request.GET.get('date') or request.POST.get('date')
    try:
        date_appel = datetime.strptime(date_str, '%Y-%m-%d').date() if date_str else date_cls.today()
    except ValueError:
        date_appel = date_cls.today()

    inscriptions = Inscription.objects.filter(
        classe=cours.classe, annee=cours.annee, statut='actif'
    ).select_related('eleve').order_by('eleve__nom', 'eleve__prenom')

    if request.method == 'POST':
        if not periode_sel:
            messages.error(request, "Veuillez choisir une période.")
        else:
            nb_abs, nb_present = 0, 0
            for insc in inscriptions:
                statut = request.POST.get(f"presence_{insc.eleve_id}", 'present')
                existante = Absence.objects.filter(
                    cours=cours, eleve=insc.eleve, periode=periode_sel, date_absence=date_appel,
                )
                if statut == 'absent':
                    if not existante.exists():
                        Absence.objects.create(
                            cours=cours, eleve=insc.eleve, periode=periode_sel,
                            date_absence=date_appel, nb_heures=1, statut='non_justifiee',
                        )
                    nb_abs += 1
                else:
                    # Présent : on retire une éventuelle absence saisie par erreur ce jour-là
                    existante.delete()
                    nb_present += 1
            messages.success(
                request,
                f"Appel enregistré ({date_appel:%d/%m/%Y}) : {nb_present} présent(s), {nb_abs} absent(s).",
            )
            from django.urls import reverse
            return redirect(
                f"{reverse('enseignant:faire_appel', args=[cours.pk])}"
                f"?periode={periode_sel.pk}&date={date_appel:%Y-%m-%d}"
            )

    # Pré-remplissage : élèves déjà marqués absents ce jour-là
    absents_ids = set()
    if periode_sel:
        absents_ids = set(Absence.objects.filter(
            cours=cours, periode=periode_sel, date_absence=date_appel,
        ).values_list('eleve_id', flat=True))

    eleves = [{
        'eleve': insc.eleve,
        'absent': insc.eleve_id in absents_ids,
    } for insc in inscriptions]

    return render(request, 'enseignant/absences/appel.html', {
        'cours': cours,
        'periodes': periodes,
        'periode_sel': periode_sel,
        'date_appel': date_appel,
        'eleves': eleves,
        'pret': bool(periode_sel),
    })


# ─── Absences d'un cours ──────────────────────────────────────────────────────

@role_required('ENSEIGNANT')
def absences_cours(request, cours_id):
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)
    absences = Absence.objects.filter(cours=cours).select_related('eleve', 'periode').order_by('-date_absence')
    paginator = Paginator(absences, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'enseignant/absences/liste.html', {
        'cours': cours,
        'page_obj': page_obj,
    })


# ─── Notes par élève (vue résultats) ─────────────────────────────────────────

@role_required('ENSEIGNANT')
def notes_eleve(request, cours_id, eleve_id):
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)
    from core.models import Personne, Inscription
    eleve = get_object_or_404(Personne, pk=eleve_id)
    get_object_or_404(Inscription, eleve=eleve, classe=cours.classe, annee=cours.annee, statut='actif')
    notes = Note.objects.filter(cours=cours, eleve=eleve).select_related('periode').order_by('periode__date_debut', '-date_saisie')
    resultats = ResultatMatiere.objects.filter(cours=cours, eleve=eleve).select_related('periode')
    return render(request, 'enseignant/notes/par_eleve.html', {
        'cours': cours,
        'eleve': eleve,
        'notes': notes,
        'resultats': resultats,
    })


# ─── Mon emploi du temps ─────────────────────────────────────────────────────

JOURS_ORDER = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
JOURS_LABELS = {
    'lundi': 'Lundi', 'mardi': 'Mardi', 'mercredi': 'Mercredi',
    'jeudi': 'Jeudi', 'vendredi': 'Vendredi', 'samedi': 'Samedi',
}


@role_required('ENSEIGNANT')
def mon_edt(request):
    from datetime import date
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    periodes = Periode.objects.filter(annee=annee_active).order_by('date_debut') if annee_active else Periode.objects.none()

    periode_id = request.GET.get('periode')
    periode_sel = None
    creneaux_par_jour = {}
    grille = None

    if annee_active:
        if periode_id:
            periode_sel = Periode.objects.filter(pk=periode_id, annee=annee_active).first()
        else:
            periode_sel = periodes.filter(date_debut__lte=date.today(), date_fin__gte=date.today()).first() or periodes.first()

        if periode_sel:
            creneaux = EmploiDuTemps.objects.filter(
                cours__enseignant=request.user, periode=periode_sel,
            ).select_related('cours__matiere', 'cours__classe', 'salle').order_by('heure_debut')
            for jour in JOURS_ORDER:
                slots = [c for c in creneaux if c.jour == jour]
                if slots:
                    creneaux_par_jour[jour] = slots
            grille = construire_grille(creneaux)

    return render(request, 'enseignant/edt.html', {
        'annee_active': annee_active,
        'periodes': periodes,
        'periode_sel': periode_sel,
        'creneaux_par_jour': creneaux_par_jour,
        'jours_labels': JOURS_LABELS,
        'grille': grille,
        'edt_mode': 'enseignant',
    })


# ─── Messagerie ───────────────────────────────────────────────────────────────

@role_required('ENSEIGNANT')
def messagerie(request):
    recus   = Message.objects.filter(destinataire=request.user).order_by('-date_envoi')
    envoyes = Message.objects.filter(expediteur=request.user).order_by('-date_envoi')
    nb_non_lus = recus.filter(lu=False).count()
    return render(request, 'enseignant/messagerie/liste.html', {
        'recus': recus[:20], 'envoyes': envoyes[:20],
        'nb_non_lus': nb_non_lus,
    })


@role_required('ENSEIGNANT')
def envoyer_message(request):
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
                    return redirect('enseignant:envoyer_message')
                msg_obj = Message(expediteur=request.user, destinataire=dest, sujet=sujet, corps=corps)
                if piece:
                    msg_obj.piece_jointe = piece
                msg_obj.save()
                messages.success(request, f"Message envoyé à {dest.get_full_name()}.")
            except Personne.DoesNotExist:
                messages.error(request, "Destinataire introuvable.")
        else:
            messages.error(request, "Veuillez remplir tous les champs.")
        return redirect('enseignant:messagerie')
    qs = Personne.objects.filter(actif=True).exclude(pk=request.user.pk)
    ORDRE_ROLES = ['DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES', 'ENSEIGNANT', 'PARENT', 'ELEVE']
    groupes_dest = {}
    for role in ORDRE_ROLES:
        membres = list(qs.filter(groups__name=role).order_by('nom', 'prenom'))
        if membres:
            groupes_dest[role] = membres
    return render(request, 'enseignant/messagerie/nouveau.html', {'groupes_dest': groupes_dest})


@role_required('ENSEIGNANT')
def lire_message(request, pk):
    from django.db.models import Q
    from django.core.exceptions import PermissionDenied
    msg = Message.objects.filter(
        Q(destinataire=request.user) | Q(expediteur=request.user), pk=pk
    ).first()
    if not msg:
        messages.error(request, "Ce message est introuvable ou ne vous appartient pas.")
        return redirect('enseignant:messagerie')
    if msg.destinataire == request.user and not msg.lu:
        msg.lu = True
        msg.save(update_fields=['lu'])
    return render(request, 'enseignant/messagerie/detail.html', {'msg': msg})


# ─── Calendrier scolaire ──────────────────────────────────────────────────────

@role_required('ENSEIGNANT')
def mon_calendrier(request):
    import json
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    evenements = EvenementScolaire.objects.filter(
        annee=annee_active
    ).order_by('date_debut') if annee_active else EvenementScolaire.objects.none()

    couleurs = {
        'vacances': '#D97706', 'examen': '#dc2626',
        'reunion': '#2563eb', 'ferie': '#16a34a', 'autre': '#6b7280',
    }
    events_json = json.dumps([{
        'title': e.titre,
        'start': e.date_debut.isoformat(),
        'end':   e.date_fin.isoformat(),
        'color': couleurs.get(e.type_event, '#6b7280'),
        'description': e.description,
    } for e in evenements])

    return render(request, 'enseignant/calendrier.html', {
        'evenements': evenements,
        'annee_active': annee_active,
        'events_json': events_json,
    })


# ─── Notifications ────────────────────────────────────────────────────────────

@role_required('ENSEIGNANT')
def mes_notifications(request):
    notifs = Notification.objects.filter(destinataire=request.user).order_by('-date_envoi')
    paginator = Paginator(notifs, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    # Marquer toutes comme lues
    Notification.objects.filter(destinataire=request.user, lu=False).update(lu=True)
    return render(request, 'enseignant/notifications.html', {'page_obj': page_obj})
