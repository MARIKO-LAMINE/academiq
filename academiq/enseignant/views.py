from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.paginator import Paginator

from core.permissions import role_required
from core.models import (
    Cours, Note, Absence, AnneeScolaire, Inscription,
    ResultatMatiere, Notification,
)
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
        absence.save()
        messages.success(request, f"Absence enregistrée pour {absence.eleve.get_full_name()}.")
        return redirect('enseignant:absences_cours', cours_id=cours.pk)

    return render(request, 'enseignant/absences/form.html', {
        'form': form,
        'cours': cours,
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
    from core.models import Personne
    eleve = get_object_or_404(Personne, pk=eleve_id)
    notes = Note.objects.filter(cours=cours, eleve=eleve).select_related('periode').order_by('periode__date_debut', '-date_saisie')
    resultats = ResultatMatiere.objects.filter(cours=cours, eleve=eleve).select_related('periode')
    return render(request, 'enseignant/notes/par_eleve.html', {
        'cours': cours,
        'eleve': eleve,
        'notes': notes,
        'resultats': resultats,
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
