from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Avg, Sum


SEUIL_ABSENCES_HEURES = 10  # RG-AB06: seuil déclenchant la notification


@receiver(post_save, sender='core.Note')
def recalculer_resultat_matiere(sender, instance, **kwargs):
    """RG-M01, RG-M03 : Recalcul automatique de la moyenne après saisie de note."""
    from .models import Note, ResultatMatiere, Notification, HistoriqueActions

    moyenne = Note.objects.filter(
        eleve=instance.eleve,
        cours=instance.cours,
        periode=instance.periode
    ).aggregate(Avg('valeur'))['valeur__avg']

    ResultatMatiere.objects.update_or_create(
        eleve=instance.eleve,
        cours=instance.cours,
        periode=instance.periode,
        defaults={'moyenne': moyenne}
    )

    Notification.objects.create(
        message=f"Nouvelle note en {instance.cours.matiere.nom_matiere} : {instance.valeur}/20",
        type_notif='note_saisie',
        destinataire=instance.eleve,
    )

    HistoriqueActions.objects.create(
        auteur=instance.cours.enseignant,
        action='Saisie note',
        table_cible='note',
        id_enreg=instance.pk,
    )


@receiver(post_save, sender='core.Absence')
def notifier_absence(sender, instance, created, **kwargs):
    """RG-AB06 : Notifie l'élève et ses parents lors d'une nouvelle absence + seuil."""
    if not created:
        return
    from .models import Notification, LienParentEleve, Absence

    Notification.objects.create(
        message=f"Absence enregistrée le {instance.date_absence} en {instance.cours.matiere.nom_matiere}.",
        type_notif='absence_enregistree',
        destinataire=instance.eleve,
    )

    for lien in LienParentEleve.objects.filter(eleve=instance.eleve):
        Notification.objects.create(
            message=f"Votre enfant {instance.eleve.get_full_name()} est absent(e) "
                    f"le {instance.date_absence} en {instance.cours.matiere.nom_matiere}.",
            type_notif='absence_enregistree',
            destinataire=lien.parent,
        )

    # Vérification seuil absences non justifiées (RG-AB06)
    total_heures = Absence.objects.filter(
        eleve=instance.eleve,
        periode=instance.periode,
        statut='non_justifiee',
    ).aggregate(total=Sum('nb_heures'))['total'] or 0

    if total_heures >= SEUIL_ABSENCES_HEURES:
        Notification.objects.create(
            message=f"{instance.eleve.get_full_name()} a dépassé le seuil de {SEUIL_ABSENCES_HEURES}h "
                    f"d'absences non justifiées pour la période {instance.periode}.",
            type_notif='depassement_absences',
            destinataire=instance.eleve,
        )
        for lien in LienParentEleve.objects.filter(eleve=instance.eleve):
            Notification.objects.create(
                message=f"Votre enfant {instance.eleve.get_full_name()} a dépassé {SEUIL_ABSENCES_HEURES}h "
                        f"d'absences non justifiées pour la période {instance.periode}.",
                type_notif='depassement_absences',
                destinataire=lien.parent,
            )


@receiver(post_save, sender='core.Bulletin')
def notifier_bulletin(sender, instance, created, **kwargs):
    """RG-B : Notifie l'élève et ses parents quand un bulletin est généré."""
    if not created:
        return
    from .models import Notification, LienParentEleve

    Notification.objects.create(
        message=f"Votre bulletin pour la période {instance.periode} est disponible.",
        type_notif='bulletin_disponible',
        destinataire=instance.eleve,
    )

    for lien in LienParentEleve.objects.filter(eleve=instance.eleve):
        Notification.objects.create(
            message=f"Le bulletin de {instance.eleve.get_full_name()} "
                    f"pour la période {instance.periode} est disponible.",
            type_notif='bulletin_disponible',
            destinataire=lien.parent,
        )


@receiver(pre_save, sender='core.AnneeScolaire')
def une_seule_annee_active(sender, instance, **kwargs):
    """RG-T02 : Désactive l'ancienne année active si on en active une nouvelle."""
    if instance.active:
        from .models import AnneeScolaire
        AnneeScolaire.objects.exclude(pk=instance.pk).update(active=False)
