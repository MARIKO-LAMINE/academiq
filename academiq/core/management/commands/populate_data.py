"""
python manage.py populate_data
Supprime toutes les données et génère un jeu complet de démonstration.
Produit un PDF des comptes : ACADEMIQ_COMPTES_DEMO.pdf à la racine du projet.
"""

import os
import random
from datetime import date, time
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
from django.db import transaction

from core.models import (
    AnneeScolaire, Periode, Salle, Matiere, Personne,
    Personnel, Enseignant, Eleve, Parent, Classe, Cours,
    EmploiDuTemps, Inscription, LienParentEleve, Note,
    ResultatMatiere, Absence, Bulletin, Notification, Message,
    EvenementScolaire, TarifNiveau, FraisScolarite, Paiement,
    HistoriqueActions,
)

# ─── Données nominatives ────────────────────────────────────────────────────

NOMS = [
    'Coulibaly', 'Koné', 'Traoré', 'Ouattara', 'Diabaté', 'Bamba', 'Camara', 'Touré',
    'Keita', 'Diallo', 'Kouassi', 'Koffi', 'Konan', 'Yao', 'Brou', 'Kassi', 'Kouame',
    'Dié', 'Yapi', 'Tano', 'Ahoussi', 'Gnagnon', 'Zran', 'Kobenan', 'Alla', 'Gueï',
    'Goba', 'Bogui', 'Loba', 'Sako', 'Bini', 'Goli', 'Kouadio', 'N\'Guessan', 'Adou',
    'Anon', 'Atta', 'Gnahore', 'Lobognon', 'Dago',
]

PRENOMS_M = [
    'Kouassi', 'Koffi', 'Konan', 'Yao', 'Adou', 'Brou', 'N\'Dri', 'Dié',
    'Jean-Baptiste', 'Ibrahim', 'Moussa', 'Abou', 'Sékou', 'Hamidou', 'Souleymane',
    'Emmanuel', 'Franck', 'Arnaud', 'Patrick', 'Christian', 'Justin', 'Laurent',
    'Michel', 'Théodore', 'Pétrono', 'Kouamé', 'Ange', 'Rodrigue', 'Serge', 'Marc',
]

PRENOMS_F = [
    'Adjoua', 'Akissi', 'Ama', 'Affoué', 'Bah', 'Constance', 'Délali', 'Edwige',
    'Fatoumata', 'Gnato', 'Henriette', 'Joëlle', 'Laure', 'Marie', 'Nadège',
    'Olivia', 'Priscille', 'Ramatou', 'Aminata', 'Mariam', 'Aïssata', 'Kadiatou',
    'Bintou', 'Nana', 'Thérèse', 'Cécile', 'Victoire', 'Rosine', 'Alice', 'Bernadette',
]

JOURS_EDT = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
HEURES_EDT = [
    (time(7, 0),  time(8, 0)),
    (time(8, 0),  time(9, 0)),
    (time(9, 0),  time(10, 0)),
    (time(10, 0), time(11, 0)),
    (time(11, 0), time(12, 0)),
    (time(13, 0), time(14, 0)),
    (time(14, 0), time(15, 0)),
    (time(15, 0), time(16, 0)),
]

NIVEAUX_DATA = [
    ('6ème',      'premier', 125_000),
    ('5ème',      'premier', 130_000),
    ('4ème',      'premier', 135_000),
    ('3ème',      'premier', 145_000),
    ('2nde',      'second',  155_000),
    ('1ère',      'second',  165_000),
    ('Terminale', 'second',  175_000),
]

MATIERES_DATA = [
    ('Mathématiques',       Decimal('4.0')),
    ('Français',            Decimal('4.0')),
    ('Anglais',             Decimal('3.0')),
    ('Histoire-Géographie', Decimal('3.0')),
    ('SVT',                 Decimal('2.0')),
    ('Physique-Chimie',     Decimal('3.0')),
    ('EPS',                 Decimal('2.0')),
    ('Informatique',        Decimal('2.0')),
]

APPRECIATIONS = [
    (16, 'Excellent travail, félicitations.'),
    (14, 'Très bon trimestre, continuez ainsi.'),
    (12, 'Bon trimestre, des efforts encore nécessaires.'),
    (10, 'Résultats satisfaisants mais des progrès sont attendus.'),
    (8,  'Trimestre difficile, il faut redoubler d\'efforts.'),
    (0,  'Résultats insuffisants, un soutien est nécessaire.'),
]


def _appr(moy):
    for seuil, txt in APPRECIATIONS:
        if moy >= seuil:
            return txt
    return APPRECIATIONS[-1][1]


def _name(idx, female=False):
    prenoms = PRENOMS_F if female else PRENOMS_M
    nom    = NOMS[idx % len(NOMS)]
    prenom = prenoms[(idx // len(NOMS)) % len(prenoms)]
    slug   = prenom.lower().replace(' ', '').replace("'", '').replace('é', 'e').replace('è', 'e').replace('ê', 'e').replace('î', 'i').replace('ô', 'o').replace('ü', 'u').replace('ï', 'i').replace('â', 'a').replace('ç', 'c')
    slug_n = nom.lower().replace("'", '').replace(' ', '').replace('é', 'e').replace('è', 'e').replace('ê', 'e')
    email  = f"{slug}.{slug_n}{idx}@academiq.ci"
    return nom, prenom, email


# ─── Commande principale ────────────────────────────────────────────────────

class Command(BaseCommand):
    help = "Supprime tout et recrée un jeu complet de données + PDF des comptes"

    def handle(self, *args, **options):
        self.creds = []  # liste de dicts pour le PDF

        self.stdout.write(self.style.WARNING("[1/3] Suppression des donnees existantes..."))
        self._clear_all()

        self.stdout.write("[2/3] Creation des donnees...")
        with transaction.atomic():
            annee, t1, t2, t3, salles, matieres = self._base()
            personnels                           = self._personnels(annee)
            enseignants                          = self._enseignants(matieres)
            classes                              = self._classes(annee)
            eleves                               = self._eleves(classes)
            parents                              = self._parents(eleves)
            inscriptions                         = self._inscriptions(eleves, classes, annee)
            cours_map                            = self._cours(classes, matieres, enseignants, annee)
            self._edt(cours_map, salles, t1, classes)
            self._tarifs_frais(annee, classes, eleves)
            self._paiements(eleves, annee, personnels)
            self._notes(eleves, cours_map, t1, t2)
            self._resultats(eleves, cours_map, t1)
            self._bulletins(eleves, cours_map, t1, classes)
            self._absences(eleves, cours_map, t1, t2)
            self._evenements(annee, personnels)
            self._messages(personnels, enseignants)

        self.stdout.write("[3/3] Generation du PDF...")
        pdf = self._pdf()
        self.stdout.write(self.style.SUCCESS(f"TERMINE ! PDF genere : {pdf}"))

    # ────────────────────────────────────────────────────────────────────────
    # 1. Nettoyage
    # ────────────────────────────────────────────────────────────────────────

    def _clear_all(self):
        for M in [
            Paiement, HistoriqueActions, Notification, Message,
            EvenementScolaire, FraisScolarite, TarifNiveau,
            Bulletin, ResultatMatiere, Note, Absence,
            EmploiDuTemps, LienParentEleve, Inscription, Cours, Classe,
            Parent, Eleve, Enseignant, Personnel,
        ]:
            M.objects.all().delete()
        Personne.objects.filter(is_superuser=False).delete()
        AnneeScolaire.objects.all().delete()
        Salle.objects.all().delete()
        Matiere.objects.all().delete()

    # ────────────────────────────────────────────────────────────────────────
    # 2. Données de base
    # ────────────────────────────────────────────────────────────────────────

    def _base(self):
        annee = AnneeScolaire.objects.create(
            libelle='2024-2025',
            date_debut=date(2024, 9, 2),
            date_fin=date(2025, 6, 27),
            active=True,
        )
        t1 = Periode.objects.create(annee=annee, nom='Trimestre 1', type_periode='trimestre',
                                    date_debut=date(2024, 9, 2),  date_fin=date(2024, 12, 20), cloturee=True)
        t2 = Periode.objects.create(annee=annee, nom='Trimestre 2', type_periode='trimestre',
                                    date_debut=date(2025, 1, 6),  date_fin=date(2025, 3, 28), cloturee=False)
        t3 = Periode.objects.create(annee=annee, nom='Trimestre 3', type_periode='trimestre',
                                    date_debut=date(2025, 4, 7),  date_fin=date(2025, 6, 27), cloturee=False)

        salles = []
        for i in range(1, 22):
            salles.append(Salle.objects.create(numero=f'S{i:02d}', batiment='Bât. Principal',
                                               capacite=40, type_salle='salle_de_cours'))
        salles.append(Salle.objects.create(numero='LAB-PC',   batiment='Bât. Sciences', capacite=30, type_salle='laboratoire'))
        salles.append(Salle.objects.create(numero='LAB-SVT',  batiment='Bât. Sciences', capacite=30, type_salle='laboratoire'))
        salles.append(Salle.objects.create(numero='GYMNASE',  batiment='Bât. Sport',    capacite=100, type_salle='gymnase'))
        salles.append(Salle.objects.create(numero='INFO',     batiment='Bât. Principal', capacite=25, type_salle='salle_informatique'))

        matieres = []
        for nom, coeff in MATIERES_DATA:
            matieres.append(Matiere.objects.create(nom_matiere=nom, coefficient=coeff))

        return annee, t1, t2, t3, salles, matieres

    # ────────────────────────────────────────────────────────────────────────
    # 3. Personnel
    # ────────────────────────────────────────────────────────────────────────

    def _personnels(self, annee):
        data = [
            ('DIRECTION',     'direction',     'Koné',      'Ibrahim',   'direction@academiq.ci',   'demo1234'),
            ('ADMINISTRATION','administration', 'Traoré',    'Awa',       'admin@academiq.ci',       'demo1234'),
            ('SCOLARITE',     'scolarite',      'Coulibaly', 'Mariam',    'scolarite@academiq.ci',   'demo1234'),
            ('FINANCES',      'finances',       'Diabaté',   'Moussa',    'finances@academiq.ci',    'demo1234'),
        ]
        result = []
        for grp, fonction, nom, prenom, email, pwd in data:
            Personne.objects.filter(email=email).delete()
            p = Personne.objects.create_user(email=email, nom=nom, prenom=prenom, password=pwd)
            Personnel.objects.create(personne=p, fonction=fonction, date_embauche=date(2020, 9, 1))
            p.groups.add(Group.objects.get(name=grp))
            result.append(p)
            self.creds.append({'role': grp, 'nom': nom, 'prenom': prenom,
                               'email': email, 'mdp': pwd, 'extra': fonction.capitalize()})
        return result

    # ────────────────────────────────────────────────────────────────────────
    # 4. Enseignants (4 par matière × 8 matières = 32)
    # ────────────────────────────────────────────────────────────────────────

    # Slug de matière pour les emails enseignants
    MAT_SLUGS = ['maths', 'francais', 'anglais', 'histgeo', 'svt', 'physchim', 'eps', 'info']

    def _enseignants(self, matieres):
        grp = Group.objects.get(name='ENSEIGNANT')
        ens_map = {}  # matiere_idx → [Personne, ...]
        ens_idx = 0
        for mat_i, mat in enumerate(matieres):
            lst = []
            mat_slug = self.MAT_SLUGS[mat_i] if mat_i < len(self.MAT_SLUGS) else f'mat{mat_i+1}'
            for t in range(4):
                female = (t % 2 == 1)
                nom, prenom, _ = _name(200 + ens_idx, female)
                email = f'prof.{mat_slug}{t+1}@academiq.ci'
                p = Personne.objects.create_user(email=email, nom=nom, prenom=prenom, password='demo1234')
                Enseignant.objects.create(personne=p, specialite=mat.nom_matiere,
                                          grade='Certifié', date_embauche=date(2020, 9, 1))
                p.groups.add(grp)
                lst.append(p)
                self.creds.append({'role': 'ENSEIGNANT', 'nom': nom, 'prenom': prenom,
                                   'email': email, 'mdp': 'demo1234', 'extra': mat.nom_matiere})
                ens_idx += 1
            ens_map[mat_i] = lst
        return ens_map

    # ────────────────────────────────────────────────────────────────────────
    # 5. Classes (3 par niveau × 7 niveaux = 21)
    # ────────────────────────────────────────────────────────────────────────

    def _classes(self, annee):
        classes = []
        for niveau, cycle, _ in NIVEAUX_DATA:
            for lettre in ('A', 'B', 'C'):
                cls = Classe.objects.create(
                    nom=f'{niveau} {lettre}',
                    niveau=niveau,
                    cycle=cycle,
                    section=lettre,
                    annee=annee,
                    effectif_max=40,
                )
                classes.append(cls)
        return classes  # 21 classes, index 0-20

    # ────────────────────────────────────────────────────────────────────────
    # 6. Élèves (5 par classe × 21 classes = 105)
    # ────────────────────────────────────────────────────────────────────────

    def _eleves(self, classes):
        grp = Group.objects.get(name='ELEVE')
        eleves = []  # list of (Personne, Classe)
        eleve_idx = 0
        for cls in classes:
            for j in range(5):
                female = (j % 2 == 1)
                nom, prenom, _ = _name(400 + eleve_idx, female)
                email = f'eleve{eleve_idx+1}@academiq.ci'
                p = Personne.objects.create_user(email=email, nom=nom, prenom=prenom, password='demo1234')
                mat = f'{date(2010 + (eleve_idx % 6), (eleve_idx % 12) + 1, (eleve_idx % 28) + 1)}'
                Eleve.objects.create(personne=p,
                                     date_naissance=date(2010 + (eleve_idx % 6),
                                                        (eleve_idx % 12) + 1,
                                                        min((eleve_idx % 28) + 1, 28)),
                                     lieu_naissance='Abidjan',
                                     matricule=f'MAT-{2024}-{eleve_idx+1:04d}')
                p.groups.add(grp)
                eleves.append((p, cls))
                self.creds.append({'role': 'ELEVE', 'nom': nom, 'prenom': prenom,
                                   'email': email, 'mdp': 'demo1234', 'extra': cls.nom})
                eleve_idx += 1
        return eleves

    # ────────────────────────────────────────────────────────────────────────
    # 7. Parents (20×1 enfant, 20×2 enfants, 15×3 enfants = 55 parents / 105 enfants)
    # ────────────────────────────────────────────────────────────────────────

    def _parents(self, eleves):
        grp = Group.objects.get(name='PARENT')
        parents = []
        parent_idx = 0
        eleve_ptr = 0

        groupes = [(20, 1), (20, 2), (15, 3)]
        liens_choix = ['pere', 'mere', 'tuteur']

        for nb_parents, nb_enfants in groupes:
            for _ in range(nb_parents):
                female = (parent_idx % 3 == 1)
                nom, prenom, _ = _name(700 + parent_idx, female)
                email = f'parent{parent_idx+1}@academiq.ci'
                p = Personne.objects.create_user(email=email, nom=nom, prenom=prenom, password='demo1234')
                Parent.objects.create(personne=p, telephone=f'07{parent_idx:07d}',
                                      profession='Commerçant(e)')
                p.groups.add(grp)

                enfants_noms = []
                for k in range(nb_enfants):
                    if eleve_ptr < len(eleves):
                        eleve_p, _ = eleves[eleve_ptr]
                        lien = 'mere' if female else 'pere'
                        LienParentEleve.objects.create(parent=p, eleve=eleve_p, lien=lien)
                        enfants_noms.append(eleve_p.get_full_name())
                        eleve_ptr += 1
                parents.append(p)
                self.creds.append({'role': 'PARENT', 'nom': nom, 'prenom': prenom,
                                   'email': email, 'mdp': 'demo1234',
                                   'extra': ', '.join(enfants_noms)})
                parent_idx += 1
        return parents

    # ────────────────────────────────────────────────────────────────────────
    # 8. Inscriptions
    # ────────────────────────────────────────────────────────────────────────

    def _inscriptions(self, eleves, classes, annee):
        inscs = []
        for p, cls in eleves:
            inscs.append(Inscription(
                eleve=p, classe=cls, annee=annee,
                date_inscription=date(2024, 9, 2), statut='actif',
            ))
        Inscription.objects.bulk_create(inscs)
        return inscs

    # ────────────────────────────────────────────────────────────────────────
    # 9. Cours (8 matières × 21 classes = 168)
    # ────────────────────────────────────────────────────────────────────────

    def _cours(self, classes, matieres, ens_map, annee):
        cours_map = {}  # (class_idx, mat_idx) → Cours
        cours_list = []
        for c_i, cls in enumerate(classes):
            for m_i, mat in enumerate(matieres):
                enseignant = ens_map[m_i][c_i % 4]
                cours = Cours(matiere=mat, classe=cls, enseignant=enseignant,
                              annee=annee, nb_heures_hebdo=2)
                cours_list.append(cours)
        created = Cours.objects.bulk_create(cours_list)
        # Reconstruire le mapping après bulk_create
        all_cours = Cours.objects.select_related('classe', 'matiere').filter(annee__libelle='2024-2025')
        for co in all_cours:
            c_i = classes.index(co.classe)
            m_i = next(i for i, m in enumerate(matieres) if m.pk == co.matiere_id)
            cours_map[(c_i, m_i)] = co
        return cours_map

    # ────────────────────────────────────────────────────────────────────────
    # 10. EDT (1 créneau par cours, dans T1)
    # Schéma : classe c → jour JOURS_EDT[c//4], matière s → heure HEURES_EDT[s]
    # ────────────────────────────────────────────────────────────────────────

    def _edt(self, cours_map, salles, t1, classes):
        edts = []
        for (c_i, m_i), cours in cours_map.items():
            jour       = JOURS_EDT[c_i // 4]          # 0-5 : lundi-samedi
            h_d, h_f   = HEURES_EDT[m_i]              # 0-7 : 7h-16h
            salle      = salles[c_i]                   # salle dédiée à chaque classe
            edts.append(EmploiDuTemps(
                cours=cours, salle=salle, periode=t1,
                jour=jour, heure_debut=h_d, heure_fin=h_f,
            ))
        EmploiDuTemps.objects.bulk_create(edts)

    # ────────────────────────────────────────────────────────────────────────
    # 11. Tarifs + Frais de scolarité
    # ────────────────────────────────────────────────────────────────────────

    def _tarifs_frais(self, annee, classes, eleves):
        tarifs = {}
        echeance = date(2024, 10, 31)
        for niveau, _, montant in NIVEAUX_DATA:
            tarifs[niveau] = TarifNiveau.objects.create(
                annee=annee, niveau=niveau,
                montant=Decimal(montant), date_echeance=echeance,
            )
        frais_list = []
        for p, cls in eleves:
            tarif = tarifs[cls.niveau]
            frais_list.append(FraisScolarite(
                eleve=p, annee=annee,
                montant_du=tarif.montant,
                montant_paye=Decimal(0),
                statut='en_attente',
                date_echeance=echeance,
            ))
        FraisScolarite.objects.bulk_create(frais_list)

    # ────────────────────────────────────────────────────────────────────────
    # 12. Paiements (mix : payé, partiel, en attente)
    # ────────────────────────────────────────────────────────────────────────

    def _paiements(self, eleves, annee, personnels):
        import uuid
        caissier = personnels[3]  # finances
        frais_qs = {f.eleve_id: f for f in FraisScolarite.objects.filter(annee=annee)}
        modes = ['especes', 'mobile_money', 'virement']
        paiements = []

        for idx, (p, cls) in enumerate(eleves):
            frais = frais_qs.get(p.pk)
            if not frais:
                continue
            montant_du = frais.montant_du
            scenario = idx % 3  # 0=payé, 1=partiel, 2=en_attente

            if scenario == 0:
                # Paiement intégral
                paiements.append(Paiement(
                    frais=frais,
                    montant=montant_du,
                    date_paiement=date(2024, 10, 15),
                    mode=modes[idx % 3],
                    recu_numero=f'PAI-2024-{uuid.uuid4().hex[:8].upper()}',
                    saisi_par=caissier,
                ))
                frais.montant_paye = montant_du
                frais.statut = 'paye'
            elif scenario == 1:
                # Paiement partiel (50 %)
                versement = montant_du // 2
                paiements.append(Paiement(
                    frais=frais,
                    montant=versement,
                    date_paiement=date(2024, 10, 20),
                    mode=modes[idx % 3],
                    recu_numero=f'PAI-2024-{uuid.uuid4().hex[:8].upper()}',
                    saisi_par=caissier,
                ))
                frais.montant_paye = versement
                frais.statut = 'partiel'
            # scenario 2 : en_attente → rien

        Paiement.objects.bulk_create(paiements)
        # Mise à jour en masse des frais
        FraisScolarite.objects.bulk_update(
            [f for f in frais_qs.values()], ['montant_paye', 'statut']
        )

    # ────────────────────────────────────────────────────────────────────────
    # 13. Notes (T1 : 3 notes, T2 : 1 note ; via bulk_create → pas de signal)
    # ────────────────────────────────────────────────────────────────────────

    def _notes(self, eleves, cours_map, t1, t2):
        notes = []
        types_t1 = ['devoir_surveille', 'devoir_surveille', 'examen_semestriel']
        for idx, (p, cls) in enumerate(eleves):
            cls_idx = idx // 5  # 0-20
            for m_i in range(len(MATIERES_DATA)):
                cours = cours_map.get((cls_idx, m_i))
                if not cours:
                    continue
                base = 8 + (idx * 7 + m_i * 3) % 11  # base réaliste 8-18
                for t_idx, type_ev in enumerate(types_t1):
                    valeur = min(20, max(0, base + (t_idx * 2 - 2) + random.randint(-2, 2)))
                    notes.append(Note(
                        valeur=Decimal(valeur), type_eval=type_ev,
                        eleve=p, cours=cours, periode=t1,
                    ))
                # T2 : 1 note
                v2 = min(20, max(0, base + random.randint(-1, 3)))
                notes.append(Note(
                    valeur=Decimal(v2), type_eval='devoir_surveille',
                    eleve=p, cours=cours, periode=t2,
                ))
        Note.objects.bulk_create(notes)

    # ────────────────────────────────────────────────────────────────────────
    # 14. ResultatMatiere (T1 uniquement — moyenne des 3 notes)
    # ────────────────────────────────────────────────────────────────────────

    def _resultats(self, eleves, cours_map, t1):
        from django.db.models import Avg
        from itertools import groupby
        resultats = []
        for idx, (p, cls) in enumerate(eleves):
            cls_idx = idx // 5  # 0-20
            for m_i in range(len(MATIERES_DATA)):
                cours = cours_map.get((cls_idx, m_i))
                if not cours:
                    continue
                moy = Note.objects.filter(eleve=p, cours=cours, periode=t1).aggregate(m=Avg('valeur'))['m']
                if moy is not None:
                    resultats.append(ResultatMatiere(
                        eleve=p, cours=cours, periode=t1,
                        moyenne=Decimal(str(round(float(moy), 2))),
                    ))
        ResultatMatiere.objects.bulk_create(resultats, ignore_conflicts=True)

        # Calcul du rang par matière (groupé par cours, trié par moyenne décroissante)
        all_rm = list(ResultatMatiere.objects.filter(periode=t1).order_by('cours_id', '-moyenne'))
        to_update = []
        for _, group in groupby(all_rm, key=lambda r: r.cours_id):
            for rang_mat, res in enumerate(list(group), start=1):
                res.rang = rang_mat
                to_update.append(res)
        if to_update:
            ResultatMatiere.objects.bulk_update(to_update, ['rang'])

    # ────────────────────────────────────────────────────────────────────────
    # 15. Bulletins T1 (clôturée) — moyenne pondérée + rang
    # ────────────────────────────────────────────────────────────────────────

    def _bulletins(self, eleves, cours_map, t1, classes):
        bulletins = []
        # Regrouper par classe
        for cls_idx, cls in enumerate(classes):
            classe_eleves = [(p, c) for idx, (p, c) in enumerate(eleves) if c.pk == cls.pk]
            moyennes = []
            for p, _ in classe_eleves:
                resultats = ResultatMatiere.objects.filter(eleve=p, periode=t1,
                                                           cours__classe=cls).select_related('cours__matiere')
                if not resultats.exists():
                    moyennes.append((p, Decimal('0')))
                    continue
                total_pts   = sum(r.moyenne * r.cours.matiere.coefficient for r in resultats)
                total_coeff = sum(r.cours.matiere.coefficient for r in resultats)
                moy_gen = total_pts / total_coeff if total_coeff else Decimal('0')
                moyennes.append((p, round(moy_gen, 2)))

            moyennes.sort(key=lambda x: x[1], reverse=True)
            for rang, (p, moy) in enumerate(moyennes, start=1):
                bulletins.append(Bulletin(
                    eleve=p, periode=t1,
                    moyenne_generale=moy,
                    rang=rang,
                    effectif_classe=len(moyennes),
                    appreciation=_appr(float(moy)),
                ))
        Bulletin.objects.bulk_create(bulletins, ignore_conflicts=True)

    # ────────────────────────────────────────────────────────────────────────
    # 16. Absences (quelques-unes par classe)
    # ────────────────────────────────────────────────────────────────────────

    def _absences(self, eleves, cours_map, t1, t2):
        absences = []
        statuts_cycle = ['en_attente', 'justifiee', 'non_justifiee', 'en_attente', 'non_justifiee']
        for idx, (p, cls) in enumerate(eleves):
            if idx % 4 != 0:
                continue  # 1 élève sur 4 a une absence
            cls_idx = idx // 5  # 0-20
            m_i = idx % len(MATIERES_DATA)
            cours = cours_map.get((cls_idx, m_i))
            if not cours:
                continue
            statut = statuts_cycle[idx % 5]
            motif = 'Maladie' if 'justif' in statut else ''
            absences.append(Absence(
                eleve=p, cours=cours, periode=t1,
                date_absence=date(2024, 10, 7 + (idx % 5)),
                nb_heures=2,
                statut=statut,
                motif=motif,
            ))
            # T2 absence
            absences.append(Absence(
                eleve=p, cours=cours, periode=t2,
                date_absence=date(2025, 1, 13 + (idx % 3)),
                nb_heures=1,
                statut='en_attente',
            ))
        Absence.objects.bulk_create(absences)

    # ────────────────────────────────────────────────────────────────────────
    # 17. Événements scolaires
    # ────────────────────────────────────────────────────────────────────────

    def _evenements(self, annee, personnels):
        dir_p = personnels[0]
        evts = [
            ('Rentrée scolaire 2024-2025', 'Accueil des élèves et distribution des emplois du temps.', 'autre',   date(2024, 9, 2),  date(2024, 9, 2)),
            ('Vacances de la Toussaint',   'Congés scolaires.',                                       'vacances', date(2024, 10, 26), date(2024, 11, 4)),
            ('Examens du 1er trimestre',   'Examens semestriels — tous niveaux.',                      'examen',   date(2024, 12, 9),  date(2024, 12, 18)),
            ('Vacances de Noël',           'Congés scolaires.',                                       'vacances', date(2024, 12, 21), date(2025, 1, 5)),
            ('Conseil de classe T1',       'Réunion des professeurs pour la clôture du trimestre 1.', 'reunion',  date(2025, 1, 13),  date(2025, 1, 13)),
            ('Fête Nationale',             'Jour férié — Fête Nationale de Côte d\'Ivoire.',          'ferie',    date(2024, 12, 7),  date(2024, 12, 7)),
        ]
        for titre, desc, type_ev, d1, d2 in evts:
            EvenementScolaire.objects.create(
                titre=titre, description=desc, type_event=type_ev,
                date_debut=d1, date_fin=d2, annee=annee, createur=dir_p,
            )

    # ────────────────────────────────────────────────────────────────────────
    # 18. Messages
    # ────────────────────────────────────────────────────────────────────────

    def _messages(self, personnels, ens_map):
        dir_p   = personnels[0]
        scol_p  = personnels[2]
        fin_p   = personnels[3]
        ens1    = ens_map[0][0]  # 1er prof de maths
        ens2    = ens_map[1][0]  # 1er prof de français

        msgs = [
            (dir_p,  scol_p, 'Planning des conseils de classe',
             'Bonjour, merci de préparer le planning des conseils de classe pour le trimestre 1.'),
            (scol_p, dir_p,  'Re : Planning des conseils de classe',
             'Bonjour, le planning est prêt. Je vous l\'envoie ce soir.'),
            (dir_p,  fin_p,  'Bilan financier T1',
             'Pouvez-vous me transmettre le bilan des paiements pour le trimestre 1 ?'),
            (ens1,   scol_p, 'Liste des absences',
             'Bonjour, veuillez trouver ci-joint la liste des absences du mois d\'octobre.'),
            (ens2,   dir_p,  'Demande de matériel pédagogique',
             'J\'ai besoin de dictionnaires supplémentaires pour mes classes de 6ème.'),
            (dir_p,  ens1,   'Félicitations',
             'Vos résultats en mathématiques sont excellents ce trimestre, félicitations !'),
            (scol_p, ens2,   'Convocation conseil de classe',
             'Vous êtes convoqué(e) au conseil de classe le 13 janvier 2025 à 14h00.'),
        ]
        for exp, dest, sujet, corps in msgs:
            Message.objects.create(expediteur=exp, destinataire=dest, sujet=sujet, corps=corps)

    # ────────────────────────────────────────────────────────────────────────
    # 19. Génération PDF (ReportLab)
    # ────────────────────────────────────────────────────────────────────────

    def _pdf(self):
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.enums import TA_CENTER, TA_LEFT
        from reportlab.platypus import (
            SimpleDocTemplate, Table, TableStyle, Paragraph,
            Spacer, PageBreak, HRFlowable,
        )

        pdf_path = os.path.join(str(settings.BASE_DIR), 'ACADEMIQ_COMPTES_DEMO.pdf')
        doc = SimpleDocTemplate(pdf_path, pagesize=A4,
                                leftMargin=1.5*cm, rightMargin=1.5*cm,
                                topMargin=2*cm, bottomMargin=2*cm)

        styles = getSampleStyleSheet()
        h1 = ParagraphStyle('H1', fontSize=18, fontName='Helvetica-Bold',
                             alignment=TA_CENTER, spaceAfter=6)
        h2 = ParagraphStyle('H2', fontSize=13, fontName='Helvetica-Bold',
                             spaceAfter=4, spaceBefore=12,
                             textColor=colors.HexColor('#1a4f7a'))
        h3 = ParagraphStyle('H3', fontSize=10, fontName='Helvetica-Bold',
                             spaceAfter=3, spaceBefore=6,
                             textColor=colors.HexColor('#2e7d32'))
        normal = ParagraphStyle('N', fontSize=8, fontName='Helvetica', leading=10)
        small  = ParagraphStyle('S', fontSize=7, fontName='Helvetica', leading=9)

        HEADER_COLOR = colors.HexColor('#1a4f7a')
        ALT_COLOR    = colors.HexColor('#e8f4fd')
        WHITE        = colors.white
        GREEN_H      = colors.HexColor('#2e7d32')
        GREEN_ALT    = colors.HexColor('#e8fdf0')
        ORANGE_H     = colors.HexColor('#e65100')
        ORANGE_ALT   = colors.HexColor('#fff3e0')
        PURPLE_H     = colors.HexColor('#6a1b9a')
        PURPLE_ALT   = colors.HexColor('#f3e5f5')

        story = []

        # ── Page de titre ──
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph('ACADEMIQ V3', h1))
        story.append(Paragraph('Système de Gestion des Activités Scolaires', styles['Normal']))
        story.append(Spacer(1, 0.3*cm))
        story.append(HRFlowable(width='100%', thickness=2, color=HEADER_COLOR))
        story.append(Spacer(1, 0.3*cm))
        story.append(Paragraph(f'<b>Comptes de démonstration — Année 2024-2025</b>',
                                ParagraphStyle('TT', fontSize=14, fontName='Helvetica-Bold',
                                               alignment=TA_CENTER, spaceAfter=4)))
        story.append(Paragraph(f'Généré le {date.today().strftime("%d/%m/%Y")}',
                                ParagraphStyle('D', fontSize=10, fontName='Helvetica',
                                               alignment=TA_CENTER, textColor=colors.grey)))
        story.append(Spacer(1, 0.5*cm))

        # Résumé
        creds_by_role = {}
        for c in self.creds:
            creds_by_role.setdefault(c['role'], []).append(c)

        summary_data = [['Rôle', 'Nombre', 'Mot de passe commun']]
        role_info = [
            ('DIRECTION',      'demo1234'),
            ('ADMINISTRATION', 'demo1234'),
            ('SCOLARITE',      'demo1234'),
            ('FINANCES',       'demo1234'),
            ('ENSEIGNANT',     'demo1234'),
            ('ELEVE',          'demo1234'),
            ('PARENT',         'demo1234'),
        ]
        for role, pwd in role_info:
            nb = len(creds_by_role.get(role, []))
            summary_data.append([role, str(nb), pwd])

        t = Table(summary_data, colWidths=[5*cm, 2.5*cm, 5*cm])
        t.setStyle(TableStyle([
            ('BACKGROUND',  (0,0), (-1,0), HEADER_COLOR),
            ('TEXTCOLOR',   (0,0), (-1,0), WHITE),
            ('FONTNAME',    (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',    (0,0), (-1,-1), 9),
            ('ALIGN',       (0,0), (-1,-1), 'CENTER'),
            ('ROWBACKGROUNDS', (0,1), (-1,-1), [WHITE, ALT_COLOR]),
            ('GRID',        (0,0), (-1,-1), 0.5, colors.grey),
            ('TOPPADDING',  (0,0), (-1,-1), 4),
            ('BOTTOMPADDING',(0,0),(-1,-1), 4),
        ]))
        story.append(t)
        story.append(PageBreak())

        # ── Section Personnel ──
        story.append(Paragraph('1. Personnel administratif', h2))
        story.append(HRFlowable(width='100%', thickness=1, color=HEADER_COLOR))
        story.append(Spacer(1, 0.2*cm))
        self._table_section(story, creds_by_role.get('DIRECTION', []) +
                            creds_by_role.get('ADMINISTRATION', []) +
                            creds_by_role.get('SCOLARITE', []) +
                            creds_by_role.get('FINANCES', []),
                            ['Nom', 'Prénom', 'Email', 'Mot de passe', 'Rôle', 'Fonction'],
                            HEADER_COLOR, ALT_COLOR)

        story.append(PageBreak())

        # ── Section Enseignants ──
        story.append(Paragraph('2. Enseignants', h2))
        story.append(HRFlowable(width='100%', thickness=1, color=GREEN_H))
        story.append(Spacer(1, 0.2*cm))
        self._table_section(story, creds_by_role.get('ENSEIGNANT', []),
                            ['Nom', 'Prénom', 'Email', 'Mot de passe', 'Matière'],
                            GREEN_H, GREEN_ALT)

        story.append(PageBreak())

        # ── Section Élèves ──
        story.append(Paragraph('3. Élèves', h2))
        story.append(HRFlowable(width='100%', thickness=1, color=ORANGE_H))
        story.append(Spacer(1, 0.2*cm))
        self._table_section(story, creds_by_role.get('ELEVE', []),
                            ['Nom', 'Prénom', 'Email', 'Mot de passe', 'Classe'],
                            ORANGE_H, ORANGE_ALT)

        story.append(PageBreak())

        # ── Section Parents ──
        story.append(Paragraph('4. Parents', h2))
        story.append(HRFlowable(width='100%', thickness=1, color=PURPLE_H))
        story.append(Spacer(1, 0.2*cm))
        self._table_section(story, creds_by_role.get('PARENT', []),
                            ['Nom', 'Prénom', 'Email', 'Mot de passe', 'Enfant(s)'],
                            PURPLE_H, PURPLE_ALT)

        doc.build(story)
        return pdf_path

    def _table_section(self, story, data, headers, hdr_color, alt_color):
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import Table, TableStyle, Spacer

        WHITE = colors.white
        nb_cols = len(headers)
        # Largeurs dynamiques selon nb colonnes
        if nb_cols == 6:
            col_w = [2.5*cm, 2.5*cm, 5.5*cm, 2.8*cm, 2.5*cm, 2.5*cm]
        elif nb_cols == 5:
            col_w = [2.8*cm, 2.8*cm, 6*cm, 2.8*cm, 4*cm]
        else:
            col_w = None

        rows = [headers]
        for c in data:
            if nb_cols == 6:
                row = [c['nom'], c['prenom'], c['email'], c['mdp'], c['role'], c['extra']]
            else:
                row = [c['nom'], c['prenom'], c['email'], c['mdp'], c['extra']]
            rows.append(row)

        t = Table(rows, colWidths=col_w, repeatRows=1)
        t.setStyle(TableStyle([
            ('BACKGROUND',    (0,0), (-1,0), hdr_color),
            ('TEXTCOLOR',     (0,0), (-1,0), WHITE),
            ('FONTNAME',      (0,0), (-1,0), 'Helvetica-Bold'),
            ('FONTSIZE',      (0,0), (-1,-1), 7),
            ('ALIGN',         (0,0), (-1,-1), 'LEFT'),
            ('VALIGN',        (0,0), (-1,-1), 'MIDDLE'),
            ('ROWBACKGROUNDS',(0,1), (-1,-1), [WHITE, alt_color]),
            ('GRID',          (0,0), (-1,-1), 0.3, colors.lightgrey),
            ('TOPPADDING',    (0,0), (-1,-1), 3),
            ('BOTTOMPADDING', (0,0),(-1,-1), 3),
            ('LEFTPADDING',   (0,0), (-1,-1), 3),
            ('WORDWRAP',      (0,0), (-1,-1), True),
        ]))
        story.append(t)
        story.append(Spacer(1, 0.3*cm))
