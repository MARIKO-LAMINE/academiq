from .models import Notification, Absence, Personne, Message, LienParentEleve


def notifications_context(request):
    if not request.user.is_authenticated:
        return {}
    nb_notifs = Notification.objects.filter(destinataire=request.user, lu=False).count()
    nb_messages_non_lus = Message.objects.filter(destinataire=request.user, lu=False).count()
    groupes = list(request.user.groups.values_list('name', flat=True))
    context = {
        'nb_notifs': nb_notifs,
        'nb_messages_non_lus': nb_messages_non_lus,
        'groupes_user': groupes,
    }
    if any(g in groupes for g in ['DIRECTION', 'SCOLARITE']):
        context['absences_attente'] = Absence.objects.filter(statut='en_attente').count()
        context['inscrits_en_attente'] = Personne.objects.filter(
            groups__isnull=True, actif=False, is_superuser=False
        ).count()
    if 'PARENT' in groupes:
        context['enfants_liens'] = LienParentEleve.objects.filter(
            parent=request.user
        ).select_related('eleve')
    return context
