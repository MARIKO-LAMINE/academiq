from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group


class Command(BaseCommand):
    help = "Crée les groupes Django requis par ACADEMIQ V3."

    def handle(self, *args, **kwargs):
        groupes = [
            'DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES',
            'ENSEIGNANT', 'ELEVE', 'PARENT',
        ]
        for nom in groupes:
            _, created = Group.objects.get_or_create(name=nom)
            status = 'créé' if created else 'déjà existant'
            self.stdout.write(f"  [{status}] {nom}")
        self.stdout.write(self.style.SUCCESS("Groupes initialisés avec succès."))
