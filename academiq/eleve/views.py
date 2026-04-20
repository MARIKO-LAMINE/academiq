from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from core.permissions import role_required
from core.models import (
    AnneeScolaire, Inscription, Note, Absence,
    Bulletin, Notification, ResultatMatiere, Cours,
)


def _get_eleve_context(user, annee_active):
    """Données communes à toutes les vues élève."""
    inscription = Inscription.objects.filter(
        eleve=user, annee=annee_active, statut='actif'
    ).select_related('classe').first() if annee_active else None

    nb_notifs = Notification.objects.filter(destinataire=user, lu=False).count()
    return {'inscription': inscription, 'annee_active': annee_active, 'nb_notifs': nb_notifs}


# ─── Dashboard ────────────────────────────────────────────────────────────────

@role_required('ELEVE')
def dashboard(request):
    import json
    from django.db.models import Avg
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    ctx = _get_eleve_context(request.user, annee_active)

    if ctx['inscription']:
        classe = ctx['inscription'].classe
        cours_ids = Cours.objects.filter(classe=classe, annee=annee_active).values_list('pk', flat=True)
        ctx['dernieres_notes'] = Note.objects.filter(
            eleve=request.user, cours__in=cours_ids
        ).select_related('cours__matiere', 'periode').order_by('-date_saisie')[:5]
        ctx['nb_absences'] = Absence.objects.filter(
            eleve=request.user, cours__in=cours_ids
        ).count()
        ctx['nb_bulletins'] = Bulletin.objects.filter(eleve=request.user).count()

        # Graphique : moyennes par matière
        resultats = ResultatMatiere.objects.filter(
            eleve=request.user, cours__in=cours_ids
        ).select_related('cours__matiere').order_by('cours__matiere__nom_matiere')
        chart_labels = [r.cours.matiere.nom_matiere[:18] for r in resultats]
        chart_data   = [round(float(r.moyenne), 2) if r.moyenne else 0 for r in resultats]
        ctx['chart_labels'] = json.dumps(chart_labels)
        ctx['chart_data']   = json.dumps(chart_data)
    else:
        ctx['chart_labels'] = json.dumps([])
        ctx['chart_data']   = json.dumps([])

    return render(request, 'eleve/dashboard.html', ctx)


# ─── Notes ────────────────────────────────────────────────────────────────────

@role_required('ELEVE')
def mes_notes(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    ctx = _get_eleve_context(request.user, annee_active)

    periode_id = request.GET.get('periode')
    notes_qs = Note.objects.filter(eleve=request.user).select_related(
        'cours__matiere', 'periode'
    ).order_by('cours__matiere__nom_matiere', 'periode__date_debut')

    if periode_id:
        notes_qs = notes_qs.filter(periode_id=periode_id)

    # Moyennes par matière/période
    if annee_active:
        resultats = ResultatMatiere.objects.filter(
            eleve=request.user, cours__annee=annee_active
        ).select_related('cours__matiere', 'periode').order_by('cours__matiere__nom_matiere')
    else:
        resultats = ResultatMatiere.objects.none()

    from core.models import Periode
    periodes = Periode.objects.filter(annee=annee_active) if annee_active else Periode.objects.none()

    ctx.update({'notes': notes_qs, 'resultats': resultats, 'periodes': periodes, 'periode_id': periode_id})
    return render(request, 'eleve/notes.html', ctx)


# ─── Absences ─────────────────────────────────────────────────────────────────

@role_required('ELEVE')
def mes_absences(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    ctx = _get_eleve_context(request.user, annee_active)

    absences = Absence.objects.filter(eleve=request.user).select_related(
        'cours__matiere', 'periode'
    ).order_by('-date_absence')
    paginator = Paginator(absences, 20)
    ctx['page_obj'] = paginator.get_page(request.GET.get('page'))
    ctx['total_heures'] = sum(a.nb_heures for a in absences)
    ctx['nb_justifiees'] = absences.filter(statut='justifiee').count()
    ctx['nb_non_justifiees'] = absences.filter(statut='non_justifiee').count()
    return render(request, 'eleve/absences.html', ctx)


# ─── Bulletins ────────────────────────────────────────────────────────────────

@role_required('ELEVE')
def mes_bulletins(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    ctx = _get_eleve_context(request.user, annee_active)

    bulletins = Bulletin.objects.filter(eleve=request.user).select_related(
        'periode__annee'
    ).order_by('-periode__date_debut')
    ctx['bulletins'] = bulletins
    return render(request, 'eleve/bulletins.html', ctx)


@role_required('ELEVE')
def detail_bulletin(request, bulletin_id):
    bulletin = get_object_or_404(Bulletin, pk=bulletin_id, eleve=request.user)
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    ctx = _get_eleve_context(request.user, annee_active)

    resultats = ResultatMatiere.objects.filter(
        eleve=request.user, periode=bulletin.periode
    ).select_related('cours__matiere').order_by('cours__matiere__nom_matiere')

    ctx.update({'bulletin': bulletin, 'resultats': resultats})
    return render(request, 'eleve/bulletin_detail.html', ctx)


# ─── Notifications ────────────────────────────────────────────────────────────

@role_required('ELEVE')
def mes_notifications(request):
    annee_active = AnneeScolaire.objects.filter(active=True).first()
    ctx = _get_eleve_context(request.user, annee_active)

    notifs = Notification.objects.filter(destinataire=request.user).order_by('-date_envoi')
    Notification.objects.filter(destinataire=request.user, lu=False).update(lu=True)
    paginator = Paginator(notifs, 20)
    ctx['page_obj'] = paginator.get_page(request.GET.get('page'))
    return render(request, 'eleve/notifications.html', ctx)
