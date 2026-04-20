"""
Commande de démonstration — ACADEMIQ
Charge un jeu de données complet et cohérent pour la soutenance.

Usage : python manage.py charger_demo
        python manage.py charger_demo --reset  (supprime les données demo avant)
"""

from datetime import date, time
from decimal import Decimal

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    AnneeScolaire, Periode, Salle, Matiere, Personne,
    Personnel, Enseignant, Eleve, Parent, Classe, Cours,
    EmploiDuTemps, Inscription, LienParentEleve, Note,
    ResultatMatiere, Absence, Bulletin, Notification,
)


class Command(BaseCommand):
    help = "Charge les données de démonstration pour la soutenance"

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset', action='store_true',
            help='Supprime les données demo avant de recharger'
        )

    def handle(self, *args, **options):
        if options['reset']:
            self._reset()

        with transaction.atomic():
            self._charger()

        self.stdout.write(self.style.SUCCESS(
            "\nOK - Donnees de demonstration chargees !\n"
            "----------------------------------------\n"
            "  DIRECTION     : direction@academiq.ci  / demo1234\n"
            "  ADMINISTRATION: admin.sec@academiq.ci  / demo1234\n"
            "  SCOLARITE     : scolarite@academiq.ci  / demo1234\n"
            "  FINANCES      : finances@academiq.ci   / demo1234\n"
            "  ENSEIGNANT 1  : prof.maths@academiq.ci / demo1234\n"
            "  ENSEIGNANT 2  : prof.phys@academiq.ci  / demo1234\n"
            "  ENSEIGNANT 3  : prof.svt@academiq.ci   / demo1234\n"
            "  ENSEIGNANT 4  : prof.fr@academiq.ci    / demo1234\n"
            "  ELEVE 1       : eleve1@academiq.ci     / demo1234\n"
            "  ELEVE 2       : eleve2@academiq.ci     / demo1234\n"
            "  ELEVE 3       : eleve3@academiq.ci     / demo1234\n"
            "  PARENT 1      : parent1@academiq.ci    / demo1234\n"
            "----------------------------------------\n"
        ))

    # ──────────────────────────────────────────────────────────────────────────
    def _reset(self):
        self.stdout.write("  Suppression des données demo...")
        emails_demo = [
            'direction@academiq.ci', 'admin.sec@academiq.ci',
            'scolarite@academiq.ci', 'finances@academiq.ci',
            'prof.maths@academiq.ci', 'prof.phys@academiq.ci',
            'prof.svt@academiq.ci', 'prof.fr@academiq.ci',
            'eleve1@academiq.ci', 'eleve2@academiq.ci', 'eleve3@academiq.ci',
            'parent1@academiq.ci',
        ]
        Personne.objects.filter(email__in=emails_demo).delete()

    # ──────────────────────────────────────────────────────────────────────────
    def _charger(self):
        self.stdout.write("  Chargement en cours...")

        # ── Groupes ──────────────────────────────────────────────────────────
        groupes = {}
        for nom in ['DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES',
                    'ENSEIGNANT', 'ELEVE', 'PARENT']:
            g, _ = Group.objects.get_or_create(name=nom)
            groupes[nom] = g

        # ── Année scolaire ────────────────────────────────────────────────────
        annee, _ = AnneeScolaire.objects.get_or_create(
            libelle='2025-2026',
            defaults={'date_debut': date(2025, 9, 8), 'date_fin': date(2026, 7, 4), 'active': True}
        )
        AnneeScolaire.objects.exclude(pk=annee.pk).update(active=False)

        # ── Périodes ─────────────────────────────────────────────────────────
        sem1, _ = Periode.objects.get_or_create(
            nom='SEMESTRE 1', annee=annee,
            defaults={
                'type_periode': 'semestre',
                'date_debut': date(2025, 9, 8),
                'date_fin': date(2026, 1, 24),
                'cloturee': True,
            }
        )
        sem2, _ = Periode.objects.get_or_create(
            nom='SEMESTRE 2', annee=annee,
            defaults={
                'type_periode': 'semestre',
                'date_debut': date(2026, 1, 26),
                'date_fin': date(2026, 5, 15),
                'cloturee': False,
            }
        )

        # ── Salles ───────────────────────────────────────────────────────────
        salle_a, _ = Salle.objects.get_or_create(
            numero='A101',
            defaults={'batiment': 'Bâtiment A', 'capacite': 45, 'type_salle': 'salle_de_cours'}
        )
        salle_b, _ = Salle.objects.get_or_create(
            numero='B202',
            defaults={'batiment': 'Bâtiment B', 'capacite': 40, 'type_salle': 'salle_de_cours'}
        )
        labo, _ = Salle.objects.get_or_create(
            numero='LABO1',
            defaults={'batiment': 'Bâtiment Sciences', 'capacite': 30, 'type_salle': 'laboratoire'}
        )

        # ── Matières ─────────────────────────────────────────────────────────
        def get_or_create_matiere(nom, coef):
            m, _ = Matiere.objects.get_or_create(
                nom_matiere=nom,
                defaults={'coefficient': Decimal(str(coef))}
            )
            return m

        mat_maths = get_or_create_matiere('MATHEMATIQUES', 5.0)
        mat_phys  = get_or_create_matiere('PHYSIQUE-CHIMIE', 4.0)
        mat_svt   = get_or_create_matiere('SCIENCES DE LA VIE ET DE LA TERRE', 3.0)
        mat_fr    = get_or_create_matiere('FRANÇAIS', 3.0)
        mat_hg    = get_or_create_matiere('HISTOIRE-GEOGRAPHIE', 2.0)
        mat_ang   = get_or_create_matiere('ANGLAIS', 2.0)
        mat_info  = get_or_create_matiere('INFORMATIQUE', 2.0)
        mat_eps   = get_or_create_matiere('EDUCATION PHYSIQUE ET SPORTIVE', 1.0)

        # ── Comptes utilisateurs ──────────────────────────────────────────────
        def creer_personne(email, nom, prenom, role_group, password='demo1234', **kwargs):
            p, created = Personne.objects.get_or_create(
                email=email,
                defaults={'nom': nom, 'prenom': prenom, 'actif': True, **kwargs}
            )
            # Toujours forcer le mot de passe demo (meme si compte existant)
            p.set_password(password)
            p.actif = True
            p.save()
            p.groups.add(groupes[role_group])
            return p, created

        # Direction
        p_dir, _ = creer_personne(
            'direction@academiq.ci', 'COULIBALY', 'Adama', 'DIRECTION'
        )
        Personnel.objects.get_or_create(
            personne=p_dir,
            defaults={'fonction': 'direction'}
        )

        # Administration
        p_adm, _ = creer_personne(
            'admin.sec@academiq.ci', 'SYLLA', 'Hamed', 'ADMINISTRATION'
        )
        Personnel.objects.get_or_create(
            personne=p_adm,
            defaults={'fonction': 'administration'}
        )

        # Scolarité
        p_sco, _ = creer_personne(
            'scolarite@academiq.ci', 'TRAORE', 'Fatoumata', 'SCOLARITE'
        )
        Personnel.objects.get_or_create(
            personne=p_sco,
            defaults={'fonction': 'scolarite'}
        )

        # Finances
        p_fin, _ = creer_personne(
            'finances@academiq.ci', 'BALLO', 'Mariam', 'FINANCES'
        )
        Personnel.objects.get_or_create(
            personne=p_fin,
            defaults={'fonction': 'finances'}
        )

        # Enseignants
        p_ens1, _ = creer_personne(
            'prof.maths@academiq.ci', 'DIABATE', 'Moussa', 'ENSEIGNANT'
        )
        Enseignant.objects.get_or_create(
            personne=p_ens1,
            defaults={'specialite': 'Mathématiques', 'grade': 'PLEG', 'date_embauche': date(2018, 9, 1)}
        )

        p_ens2, _ = creer_personne(
            'prof.phys@academiq.ci', 'KONE', 'Aminata', 'ENSEIGNANT'
        )
        Enseignant.objects.get_or_create(
            personne=p_ens2,
            defaults={'specialite': 'Physique-Chimie', 'grade': 'PLEG', 'date_embauche': date(2019, 9, 1)}
        )

        p_ens3, _ = creer_personne(
            'prof.svt@academiq.ci', 'TOURE', 'Mamadou', 'ENSEIGNANT'
        )
        Enseignant.objects.get_or_create(
            personne=p_ens3,
            defaults={'specialite': 'Sciences Naturelles', 'grade': 'PLEG', 'date_embauche': date(2020, 9, 1)}
        )

        p_ens4, _ = creer_personne(
            'prof.fr@academiq.ci', 'OUEDRAOGO', 'Awa', 'ENSEIGNANT'
        )
        Enseignant.objects.get_or_create(
            personne=p_ens4,
            defaults={'specialite': 'Lettres Modernes', 'grade': 'PLEG', 'date_embauche': date(2021, 9, 1)}
        )

        # Élèves
        p_el1, _ = creer_personne(
            'eleve1@academiq.ci', 'BAMBA', 'Youssouf', 'ELEVE'
        )
        Eleve.objects.get_or_create(
            personne=p_el1,
            defaults={
                'date_naissance': date(2007, 3, 15),
                'lieu_naissance': 'Abidjan',
                'matricule': 'EL-2025-001',
            }
        )

        p_el2, _ = creer_personne(
            'eleve2@academiq.ci', 'OUATTARA', 'Mariam', 'ELEVE'
        )
        Eleve.objects.get_or_create(
            personne=p_el2,
            defaults={
                'date_naissance': date(2007, 7, 22),
                'lieu_naissance': 'Bouaké',
                'matricule': 'EL-2025-002',
            }
        )

        p_el3, _ = creer_personne(
            'eleve3@academiq.ci', 'DOUMBIA', 'Ibrahim', 'ELEVE'
        )
        Eleve.objects.get_or_create(
            personne=p_el3,
            defaults={
                'date_naissance': date(2006, 11, 8),
                'lieu_naissance': 'Korhogo',
                'matricule': 'EL-2025-003',
            }
        )

        # Parent
        p_par1, _ = creer_personne(
            'parent1@academiq.ci', 'BAMBA', 'Ibrahim', 'PARENT'
        )
        Parent.objects.get_or_create(
            personne=p_par1,
            defaults={'telephone': '+225 07 11 22 33', 'profession': 'Commerçant'}
        )
        LienParentEleve.objects.get_or_create(
            parent=p_par1, eleve=p_el1,
            defaults={'lien': 'pere'}
        )

        # ── Classes ───────────────────────────────────────────────────────────
        cls_tc, _ = Classe.objects.get_or_create(
            nom='TERMINALE C', annee=annee,
            defaults={'niveau': 'Terminale', 'cycle': 'second', 'section': 'C', 'effectif_max': 40}
        )
        cls_1ere, _ = Classe.objects.get_or_create(
            nom='PREMIERE D', annee=annee,
            defaults={'niveau': 'Première', 'cycle': 'second', 'section': 'D', 'effectif_max': 38}
        )
        cls_3e, _ = Classe.objects.get_or_create(
            nom='TROISIEME A', annee=annee,
            defaults={'niveau': 'Troisième', 'cycle': 'premier', 'section': 'A', 'effectif_max': 42}
        )

        # ── Inscriptions ─────────────────────────────────────────────────────
        def inscrire(eleve_p, classe):
            Inscription.objects.get_or_create(
                eleve=eleve_p, annee=annee,
                defaults={'classe': classe, 'date_inscription': date(2025, 9, 8), 'statut': 'actif'}
            )

        inscrire(p_el1, cls_tc)
        inscrire(p_el2, cls_tc)
        inscrire(p_el3, cls_1ere)

        # ── Cours ─────────────────────────────────────────────────────────────
        def get_or_create_cours(matiere, classe, enseignant, nb_h):
            c, _ = Cours.objects.get_or_create(
                matiere=matiere, classe=classe, annee=annee,
                defaults={'enseignant': enseignant, 'nb_heures_hebdo': nb_h}
            )
            return c

        c_math_tc   = get_or_create_cours(mat_maths, cls_tc,   p_ens1, 5)
        c_phys_tc   = get_or_create_cours(mat_phys,  cls_tc,   p_ens2, 4)
        c_svt_tc    = get_or_create_cours(mat_svt,   cls_tc,   p_ens3, 3)
        c_fr_tc     = get_or_create_cours(mat_fr,    cls_tc,   p_ens4, 3)
        c_math_1ere = get_or_create_cours(mat_maths, cls_1ere, p_ens1, 5)
        c_phys_1ere = get_or_create_cours(mat_phys,  cls_1ere, p_ens2, 4)

        # ── Emploi du temps (Terminale C / Semestre 1) ────────────────────────
        def creer_creneau(cours, salle, periode, jour, h_deb, h_fin):
            try:
                edt = EmploiDuTemps(
                    cours=cours, salle=salle, periode=periode,
                    jour=jour, heure_debut=h_deb, heure_fin=h_fin
                )
                edt.full_clean()
                edt.save()
            except Exception:
                pass  # ignore conflits si déjà existant

        creer_creneau(c_math_tc, salle_a, sem1, 'lundi',    time(7, 30),  time(9, 30))
        creer_creneau(c_phys_tc, labo,    sem1, 'lundi',    time(10, 0),  time(12, 0))
        creer_creneau(c_svt_tc,  labo,    sem1, 'mardi',    time(7, 30),  time(9, 0))
        creer_creneau(c_fr_tc,   salle_a, sem1, 'mardi',    time(9, 30),  time(11, 0))
        creer_creneau(c_math_tc, salle_a, sem1, 'mercredi', time(7, 30),  time(9, 30))
        creer_creneau(c_phys_tc, labo,    sem1, 'jeudi',    time(10, 0),  time(12, 0))
        creer_creneau(c_fr_tc,   salle_a, sem1, 'vendredi', time(7, 30),  time(9, 0))
        creer_creneau(c_svt_tc,  labo,    sem1, 'vendredi', time(9, 30),  time(11, 0))

        # ── Notes (Semestre 1, désactivation des signaux pour éviter doublons) ──
        def saisir_note(eleve_p, cours, periode, valeur, type_eval):
            Note.objects.get_or_create(
                eleve=eleve_p, cours=cours, periode=periode,
                type_eval=type_eval,
                defaults={'valeur': Decimal(str(valeur))}
            )

        # Élève 1 — TERMINALE C — Semestre 1
        saisir_note(p_el1, c_math_tc, sem1, 15.50, 'devoir_surveille')
        saisir_note(p_el1, c_math_tc, sem1, 13.00, 'interrogation')
        saisir_note(p_el1, c_phys_tc, sem1, 14.00, 'devoir_surveille')
        saisir_note(p_el1, c_phys_tc, sem1, 12.50, 'interrogation')
        saisir_note(p_el1, c_svt_tc,  sem1, 16.00, 'devoir_surveille')
        saisir_note(p_el1, c_fr_tc,   sem1, 11.00, 'devoir_surveille')
        saisir_note(p_el1, c_fr_tc,   sem1, 10.50, 'interrogation')

        # Élève 2 — TERMINALE C — Semestre 1
        saisir_note(p_el2, c_math_tc, sem1, 18.00, 'devoir_surveille')
        saisir_note(p_el2, c_math_tc, sem1, 17.00, 'interrogation')
        saisir_note(p_el2, c_phys_tc, sem1, 16.50, 'devoir_surveille')
        saisir_note(p_el2, c_phys_tc, sem1, 15.00, 'interrogation')
        saisir_note(p_el2, c_svt_tc,  sem1, 17.50, 'devoir_surveille')
        saisir_note(p_el2, c_fr_tc,   sem1, 15.00, 'devoir_surveille')
        saisir_note(p_el2, c_fr_tc,   sem1, 14.50, 'interrogation')

        # Élève 3 — PREMIERE D — Semestre 1
        saisir_note(p_el3, c_math_1ere, sem1, 12.00, 'devoir_surveille')
        saisir_note(p_el3, c_math_1ere, sem1, 10.50, 'interrogation')
        saisir_note(p_el3, c_phys_1ere, sem1, 11.00, 'devoir_surveille')
        saisir_note(p_el3, c_phys_1ere, sem1,  9.50, 'interrogation')

        # ── Résultats par matière (recalcul manuel) ──────────────────────────
        def recalculer_resultats(eleve_p, cours, periode):
            from django.db.models import Avg
            moy = Note.objects.filter(
                eleve=eleve_p, cours=cours, periode=periode
            ).aggregate(m=Avg('valeur'))['m']
            if moy is not None:
                ResultatMatiere.objects.update_or_create(
                    eleve=eleve_p, cours=cours, periode=periode,
                    defaults={'moyenne': round(Decimal(str(moy)), 2)}
                )

        for el in [p_el1, p_el2]:
            for c in [c_math_tc, c_phys_tc, c_svt_tc, c_fr_tc]:
                recalculer_resultats(el, c, sem1)

        for c in [c_math_1ere, c_phys_1ere]:
            recalculer_resultats(p_el3, c, sem1)

        # ── Absences ─────────────────────────────────────────────────────────
        def creer_absence(eleve_p, cours, periode, nb_h, statut, date_abs):
            Absence.objects.get_or_create(
                eleve=eleve_p, cours=cours, periode=periode,
                date_absence=date_abs,
                defaults={'nb_heures': nb_h, 'statut': statut,
                          'motif': 'Maladie' if statut == 'justifiee' else ''}
            )

        creer_absence(p_el1, c_math_tc,   sem1, 2, 'justifiee',     date(2025, 10, 6))
        creer_absence(p_el1, c_phys_tc,   sem1, 2, 'non_justifiee', date(2025, 11, 10))
        creer_absence(p_el2, c_fr_tc,     sem1, 1, 'justifiee',     date(2025, 12, 1))
        creer_absence(p_el3, c_math_1ere, sem1, 4, 'non_justifiee', date(2025, 10, 20))

        # ── Bulletins (Semestre 1 clôturé) ───────────────────────────────────
        def creer_bulletin(eleve_p, periode, classe):
            from django.db.models import Avg
            resultats = ResultatMatiere.objects.filter(eleve=eleve_p, periode=periode)
            if not resultats.exists():
                return

            total_coef = sum(
                float(r.cours.matiere.coefficient) for r in resultats if r.moyenne
            )
            total_points = sum(
                float(r.moyenne) * float(r.cours.matiere.coefficient)
                for r in resultats if r.moyenne
            )
            moy_gen = round(total_points / total_coef, 2) if total_coef else 0

            effectif = Inscription.objects.filter(
                classe=classe, annee=annee, statut='actif'
            ).count()

            Bulletin.objects.get_or_create(
                eleve=eleve_p, periode=periode,
                defaults={
                    'moyenne_generale': Decimal(str(moy_gen)),
                    'rang': 1,
                    'effectif_classe': effectif,
                    'appreciation': self._appreciation(moy_gen),
                }
            )

        creer_bulletin(p_el1, sem1, cls_tc)
        creer_bulletin(p_el2, sem1, cls_tc)
        creer_bulletin(p_el3, sem1, cls_1ere)

        # ── Recalcul des rangs ────────────────────────────────────────────────
        for classe in [cls_tc, cls_1ere]:
            bulletins = Bulletin.objects.filter(
                periode=sem1,
                eleve__inscriptions__classe=classe,
                eleve__inscriptions__annee=annee,
            ).order_by('-moyenne_generale')

            for rang, b in enumerate(bulletins, start=1):
                b.rang = rang
                b.save(update_fields=['rang'])

        # ── Notifications ─────────────────────────────────────────────────────
        def creer_notif(destinataire, message, type_notif):
            Notification.objects.get_or_create(
                destinataire=destinataire,
                message=message,
                type_notif=type_notif,
                defaults={'lu': False}
            )

        creer_notif(
            p_el1,
            f"Votre bulletin du {sem1} est disponible. Moyenne générale : "
            f"{Bulletin.objects.filter(eleve=p_el1, periode=sem1).first().moyenne_generale}/20",
            'bulletin_disponible'
        )
        creer_notif(
            p_el2,
            f"Votre bulletin du {sem1} est disponible. Moyenne générale : "
            f"{Bulletin.objects.filter(eleve=p_el2, periode=sem1).first().moyenne_generale}/20",
            'bulletin_disponible'
        )
        creer_notif(
            p_par1,
            f"Le bulletin de {p_el1.get_full_name()} pour le {sem1} est disponible.",
            'bulletin_disponible'
        )
        creer_notif(
            p_el1,
            "Absence enregistrée en Physique-Chimie (2h).",
            'absence_enregistree'
        )

    @staticmethod
    def _appreciation(moy):
        if moy >= 16:
            return "Excellent travail, continuez ainsi !"
        elif moy >= 14:
            return "Bon travail, persévérez."
        elif moy >= 12:
            return "Travail assez satisfaisant."
        elif moy >= 10:
            return "Travail passable, des efforts sont nécessaires."
        else:
            return "Travail insuffisant, redoublez d'efforts."
