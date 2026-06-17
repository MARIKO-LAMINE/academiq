"""
Générateur de données de test À GRANDE ÉCHELLE pour ACADEMIQ.

Remplit TOUTES les tables en respectant la logique métier :
 - rôles exclusifs (Personne = 1 seul rôle)
 - unicités (inscription/an, cours, bulletin, résultat, salle/créneau…)
 - moyennes par matière + rangs (calculés), bulletins des périodes clôturées
 - notifications (élève + parents) et historique des actions

Usage :
    python manage.py generer_donnees                 # gros volume par défaut
    python manage.py generer_donnees --eleves 40     # 40 élèves / classe
    python manage.py generer_donnees --sections 4    # 4 classes / niveau
    python manage.py generer_donnees --no-clear      # n'efface pas avant

Mot de passe commun à TOUS les comptes générés : demo1234
"""

import random
import uuid
from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth.hashers import make_password
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

# ── Données nominatives (contexte ivoirien) ─────────────────────────────────
NOMS = [
    'Coulibaly', 'Koné', 'Traoré', 'Ouattara', 'Diabaté', 'Bamba', 'Camara', 'Touré',
    'Keita', 'Diallo', 'Kouassi', 'Koffi', 'Konan', 'Yao', 'Brou', 'Kassi', 'Kouamé',
    'Yapi', 'Tano', 'Ahoussi', 'Gnagnon', 'Kobenan', 'Alla', 'Gueï', 'Goba', 'Sako',
    'Kouadio', "N'Guessan", 'Adou', 'Atta', 'Dago', 'Cissé', 'Fofana', 'Sangaré',
    'Doumbia', 'Bakayoko', 'Soro', 'Koffi', 'Aka', 'Assi',
]
PRENOMS_M = [
    'Kouassi', 'Koffi', 'Konan', 'Yao', 'Adou', 'Brou', "N'Dri", 'Ibrahim', 'Moussa',
    'Abou', 'Sékou', 'Hamidou', 'Souleymane', 'Emmanuel', 'Franck', 'Arnaud', 'Patrick',
    'Christian', 'Justin', 'Laurent', 'Michel', 'Kouamé', 'Ange', 'Rodrigue', 'Serge',
    'Marc', 'Jean', 'Olivier', 'Cédric', 'Boubacar',
]
PRENOMS_F = [
    'Adjoua', 'Akissi', 'Affoué', 'Constance', 'Edwige', 'Fatoumata', 'Henriette',
    'Joëlle', 'Laure', 'Marie', 'Nadège', 'Olivia', 'Priscille', 'Ramatou', 'Aminata',
    'Mariam', 'Aïssata', 'Kadiatou', 'Bintou', 'Nana', 'Thérèse', 'Cécile', 'Victoire',
    'Rosine', 'Alice', 'Bernadette', 'Grace', 'Estelle', 'Carine', 'Sandrine',
]

JOURS_EDT = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']
HEURES_EDT = [
    (time(7, 0), time(8, 0)), (time(8, 0), time(9, 0)), (time(9, 0), time(10, 0)),
    (time(10, 0), time(11, 0)), (time(11, 0), time(12, 0)), (time(13, 0), time(14, 0)),
    (time(14, 0), time(15, 0)), (time(15, 0), time(16, 0)),
]

NIVEAUX_DATA = [  # (niveau, cycle, montant scolarité FCFA)
    ('6ème', 'premier', 125_000), ('5ème', 'premier', 130_000),
    ('4ème', 'premier', 135_000), ('3ème', 'premier', 145_000),
    ('2nde', 'second', 155_000), ('1ère', 'second', 165_000),
    ('Terminale', 'second', 175_000),
]
MATIERES_DATA = [
    ('Mathématiques', Decimal('4.0')), ('Français', Decimal('4.0')),
    ('Anglais', Decimal('3.0')), ('Histoire-Géographie', Decimal('3.0')),
    ('SVT', Decimal('2.0')), ('Physique-Chimie', Decimal('3.0')),
    ('EPS', Decimal('2.0')), ('Informatique', Decimal('2.0')),
]
MAT_SLUGS = ['maths', 'francais', 'anglais', 'histgeo', 'svt', 'physchim', 'eps', 'info']
APPRECIATIONS = [
    (16, 'Excellent travail, félicitations.'),
    (14, 'Très bon trimestre, continuez ainsi.'),
    (12, 'Bon trimestre, des efforts encore nécessaires.'),
    (10, 'Résultats satisfaisants mais des progrès sont attendus.'),
    (8, 'Trimestre difficile, il faut redoubler d\'efforts.'),
    (0, 'Résultats insuffisants, un soutien est nécessaire.'),
]


def _appr(moy):
    for seuil, txt in APPRECIATIONS:
        if moy >= seuil:
            return txt
    return APPRECIATIONS[-1][1]


def _slug(s):
    table = str.maketrans('àâäéèêëîïôöùûüç', 'aaaeeeeiioouuuc')
    return s.lower().replace("'", '').replace(' ', '').translate(table)


class Command(BaseCommand):
    help = "Génère un GROS jeu de données de test cohérent (toutes les tables)."

    def add_arguments(self, parser):
        parser.add_argument('--eleves', type=int, default=30,
                            help='Nombre d\'élèves par classe (défaut 30)')
        parser.add_argument('--sections', type=int, default=3,
                            help='Nombre de classes par niveau (défaut 3 : A, B, C)')
        parser.add_argument('--no-clear', action='store_true',
                            help='Ne pas effacer les données existantes avant de générer')

    def handle(self, *args, **opt):
        random.seed(42)
        self.HASH = make_password('demo1234')
        self.n_eleves = max(1, opt['eleves'])
        self.n_sections = max(1, min(opt['sections'], 6))

        if not opt['no_clear']:
            self.stdout.write(self.style.WARNING('[0/12] Nettoyage des données existantes…'))
            self._clear()

        with transaction.atomic():
            self.stdout.write('[1/12] Année, périodes, salles, matières…')
            self._base()
            self.stdout.write('[2/12] Personnel administratif…')
            self._personnel()
            self.stdout.write('[3/12] Enseignants…')
            self._enseignants()
            self.stdout.write('[4/12] Classes…')
            self._classes()
            self.stdout.write(f'[5/12] Élèves ({self.n_eleves}/classe)…')
            self._eleves()
            self.stdout.write('[6/12] Parents + liens…')
            self._parents()
            self.stdout.write('[7/12] Cours, emploi du temps, inscriptions…')
            self._cours_edt_inscriptions()
            self.stdout.write('[8/12] Tarifs, frais, paiements…')
            self._finances()
            self.stdout.write('[9/12] Notes -> resultats -> rangs…')
            self._notes_resultats()
            self.stdout.write('[10/12] Bulletins (périodes clôturées)…')
            self._bulletins()
            self.stdout.write('[11/12] Absences, notifications, historique…')
            self._absences_notifs_histo()
            self.stdout.write('[12/12] Événements + messages…')
            self._evenements_messages()

        self._resume()

    # ──────────────────────────────────────────────────────────────────────
    def _clear(self):
        for M in (Paiement, HistoriqueActions, Notification, Message,
                  EvenementScolaire, FraisScolarite, TarifNiveau, Bulletin,
                  ResultatMatiere, Note, Absence, EmploiDuTemps,
                  LienParentEleve, Inscription, Cours, Classe,
                  Parent, Eleve, Enseignant, Personnel):
            M.objects.all().delete()
        Personne.objects.filter(is_superuser=False).delete()
        for M in (AnneeScolaire, Salle, Matiere):
            M.objects.all().delete()

    # ──────────────────────────────────────────────────────────────────────
    def _base(self):
        self.groupes = {n: Group.objects.get_or_create(name=n)[0] for n in (
            'DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES',
            'ENSEIGNANT', 'ELEVE', 'PARENT')}

        # Année passée → toutes les périodes sont clôturables (bulletins valides)
        self.annee = AnneeScolaire.objects.create(
            libelle='2024-2025', date_debut=date(2024, 9, 2),
            date_fin=date(2025, 6, 27), active=True)
        self.t1 = Periode.objects.create(annee=self.annee, nom='Trimestre 1',
            type_periode='trimestre', date_debut=date(2024, 9, 2),
            date_fin=date(2024, 12, 20), cloturee=True)
        self.t2 = Periode.objects.create(annee=self.annee, nom='Trimestre 2',
            type_periode='trimestre', date_debut=date(2025, 1, 6),
            date_fin=date(2025, 3, 28), cloturee=True)
        self.t3 = Periode.objects.create(annee=self.annee, nom='Trimestre 3',
            type_periode='trimestre', date_debut=date(2025, 4, 7),
            date_fin=date(2025, 6, 27), cloturee=False)
        self.periodes_closes = [self.t1, self.t2]

        self.matieres = [Matiere.objects.create(nom_matiere=n, coefficient=c)
                         for n, c in MATIERES_DATA]

        # Assez de salles : 1 dédiée par classe + labos (évite tout conflit de créneau)
        n_classes = len(NIVEAUX_DATA) * self.n_sections
        self.salles = [Salle.objects.create(
            numero=f'S{i:02d}', batiment='Bâtiment principal',
            capacite=45, type_salle='salle_de_cours') for i in range(1, n_classes + 1)]
        for num, typ, cap in [('LAB-PC', 'laboratoire', 35), ('LAB-SVT', 'laboratoire', 35),
                              ('GYMNASE', 'gymnase', 120), ('INFO', 'salle_informatique', 30)]:
            self.salles.append(Salle.objects.create(numero=num, batiment='Annexe',
                                                    capacite=cap, type_salle=typ))

    # ──────────────────────────────────────────────────────────────────────
    def _new_personne(self, email, nom, prenom):
        """Crée une Personne (mot de passe pré-haché) et renvoie l'objet avec pk."""
        return Personne.objects.create(email=email, nom=nom, prenom=prenom,
                                       actif=True, password=self.HASH)

    def _add_group(self, personnes, groupe):
        Through = Personne.groups.through
        Through.objects.bulk_create(
            [Through(personne_id=p.pk, group_id=groupe.pk) for p in personnes],
            ignore_conflicts=True)

    def _personnel(self):
        data = [
            ('DIRECTION', 'direction', 'Koné', 'Ibrahim', 'direction@academiq.ci'),
            ('ADMINISTRATION', 'administration', 'Traoré', 'Awa', 'admin@academiq.ci'),
            ('SCOLARITE', 'scolarite', 'Coulibaly', 'Mariam', 'scolarite@academiq.ci'),
            ('FINANCES', 'finances', 'Diabaté', 'Moussa', 'finances@academiq.ci'),
        ]
        self.staff = {}
        for grp, fonction, nom, prenom, email in data:
            p = self._new_personne(email, nom, prenom)
            Personnel.objects.create(personne=p, fonction=fonction,
                                     date_embauche=date(2019, 9, 1))
            self._add_group([p], self.groupes[grp])
            self.staff[fonction] = p

    def _enseignants(self):
        self.ens_map = {}  # matiere_idx -> [Personne, ...] (4 profs par matière)
        idx = 0
        profs = []
        for m_i, (nom_mat, _) in enumerate(MATIERES_DATA):
            lst = []
            for k in range(4):
                female = (k % 2 == 1)
                nom = random.choice(NOMS)
                prenom = random.choice(PRENOMS_F if female else PRENOMS_M)
                email = f'prof.{MAT_SLUGS[m_i]}{k + 1}@academiq.ci'
                p = self._new_personne(email, nom, prenom)
                Enseignant.objects.create(personne=p, specialite=nom_mat,
                                          grade='Certifié', date_embauche=date(2020, 9, 1))
                lst.append(p)
                profs.append(p)
                idx += 1
            self.ens_map[m_i] = lst
        self._add_group(profs, self.groupes['ENSEIGNANT'])

    def _classes(self):
        self.classes = []
        lettres = ['A', 'B', 'C', 'D', 'E', 'F'][:self.n_sections]
        for niveau, cycle, _ in NIVEAUX_DATA:
            for lettre in lettres:
                self.classes.append(Classe.objects.create(
                    nom=f'{niveau} {lettre}', niveau=niveau, cycle=cycle,
                    section=lettre, annee=self.annee, effectif_max=max(40, self.n_eleves)))

    def _eleves(self):
        rows, meta = [], []
        compteur = 0
        for cls in self.classes:
            for j in range(self.n_eleves):
                compteur += 1
                female = (j % 2 == 1)
                nom = random.choice(NOMS)
                prenom = random.choice(PRENOMS_F if female else PRENOMS_M)
                email = f'eleve{compteur}@academiq.ci'
                rows.append(Personne(email=email, nom=nom, prenom=prenom,
                                     actif=True, password=self.HASH))
                annee_naiss = 2006 + (compteur % 7)
                meta.append((email, cls, date(annee_naiss, (compteur % 12) + 1,
                                              (compteur % 27) + 1), compteur))
        Personne.objects.bulk_create(rows, batch_size=500)

        pmap = {p.email: p for p in Personne.objects.filter(
            email__in=[m[0] for m in meta])}
        self.eleves = []          # [(personne, classe)]
        self.classe_eleves = {}   # classe.pk -> [personne]
        subs, through, inscs = [], Personne.groups.through, []
        through_rows = []
        for email, cls, naiss, num in meta:
            p = pmap[email]
            self.eleves.append((p, cls))
            self.classe_eleves.setdefault(cls.pk, []).append(p)
            subs.append(Eleve(personne=p, date_naissance=naiss,
                              lieu_naissance='Abidjan', matricule=f'MAT-2024-{num:05d}'))
            through_rows.append(through(personne_id=p.pk,
                                        group_id=self.groupes['ELEVE'].pk))
            inscs.append(Inscription(eleve=p, classe=cls, annee=self.annee,
                                     date_inscription=date(2024, 9, 2), statut='actif'))
        Eleve.objects.bulk_create(subs, batch_size=500)
        through.objects.bulk_create(through_rows, batch_size=500, ignore_conflicts=True)
        Inscription.objects.bulk_create(inscs, batch_size=500)

    def _parents(self):
        # ~1 parent pour 1 à 3 élèves (fratries)
        rows, meta = [], []
        idx = 0
        i = 0
        self.parent_enfants = []  # (parent_meta_index, [eleve_personne,...])
        while i < len(self.eleves):
            nb_enfants = random.choice([1, 1, 2, 2, 3])
            enfants = [self.eleves[i + k][0] for k in range(nb_enfants)
                       if i + k < len(self.eleves)]
            i += nb_enfants
            idx += 1
            female = (idx % 2 == 0)
            nom = enfants[0].nom  # même nom que l'aîné (réalisme)
            prenom = random.choice(PRENOMS_F if female else PRENOMS_M)
            email = f'parent{idx}@academiq.ci'
            rows.append(Personne(email=email, nom=nom, prenom=prenom,
                                 actif=True, password=self.HASH))
            meta.append((email, female, enfants))
        Personne.objects.bulk_create(rows, batch_size=500)

        pmap = {p.email: p for p in Personne.objects.filter(
            email__in=[m[0] for m in meta])}
        through = Personne.groups.through
        through_rows, liens = [], []
        self.parents_enfants = {}  # eleve.pk -> [parent_personne]
        parents = []
        for email, female, enfants in meta:
            p = pmap[email]
            parents.append(p)
            Parent.objects.create(personne=p, telephone=f'07{random.randint(10**6, 10**7 - 1)}',
                                  profession=random.choice(
                                      ['Commerçant', 'Enseignant', 'Fonctionnaire',
                                       'Infirmier', 'Agriculteur', 'Artisan']))
            through_rows.append(through(personne_id=p.pk,
                                        group_id=self.groupes['PARENT'].pk))
            for e in enfants:
                liens.append(LienParentEleve(parent=p, eleve=e,
                                             lien='mere' if female else 'pere'))
                self.parents_enfants.setdefault(e.pk, []).append(p)
        through.objects.bulk_create(through_rows, batch_size=500, ignore_conflicts=True)
        LienParentEleve.objects.bulk_create(liens, batch_size=500, ignore_conflicts=True)

    def _cours_edt_inscriptions(self):
        cours_list = []
        for c_i, cls in enumerate(self.classes):
            for m_i, mat in enumerate(self.matieres):
                cours_list.append(Cours(matiere=mat, classe=cls,
                                        enseignant=self.ens_map[m_i][c_i % 4],
                                        annee=self.annee, nb_heures_hebdo=2))
        Cours.objects.bulk_create(cours_list, batch_size=500)

        # Reconstruire la carte (c_i, m_i) -> Cours (pk fiables après requête)
        mat_pk_to_i = {m.pk: i for i, m in enumerate(self.matieres)}
        cls_pk_to_i = {c.pk: i for i, c in enumerate(self.classes)}
        self.cours_map = {}
        self.coeff_cours = {}
        for co in Cours.objects.filter(annee=self.annee).select_related('matiere'):
            key = (cls_pk_to_i[co.classe_id], mat_pk_to_i[co.matiere_id])
            self.cours_map[key] = co
            self.coeff_cours[co.pk] = co.matiere.coefficient

        # Emploi du temps (T1) : 1 salle dédiée par classe → aucun conflit possible
        edts = []
        for (c_i, m_i), co in self.cours_map.items():
            edts.append(EmploiDuTemps(
                cours=co, salle=self.salles[c_i], periode=self.t1,
                jour=JOURS_EDT[(c_i // 4) % len(JOURS_EDT)],
                heure_debut=HEURES_EDT[m_i][0], heure_fin=HEURES_EDT[m_i][1]))
        EmploiDuTemps.objects.bulk_create(edts, batch_size=500)

    def _finances(self):
        tarifs = {}
        echeance = date(2024, 10, 31)
        for niveau, _, montant in NIVEAUX_DATA:
            tarifs[niveau] = TarifNiveau.objects.create(
                annee=self.annee, niveau=niveau, montant=Decimal(montant),
                date_echeance=echeance)
        frais_list = []
        for p, cls in self.eleves:
            frais_list.append(FraisScolarite(
                eleve=p, annee=self.annee, montant_du=tarifs[cls.niveau].montant,
                montant_paye=Decimal(0), statut='en_attente', date_echeance=echeance))
        FraisScolarite.objects.bulk_create(frais_list, batch_size=500)

        frais_map = {f.eleve_id: f for f in FraisScolarite.objects.filter(annee=self.annee)}
        caissier = self.staff['finances']
        paiements = []
        for idx, (p, cls) in enumerate(self.eleves):
            frais = frais_map[p.pk]
            scenario = idx % 3  # 0 payé, 1 partiel, 2 en attente
            if scenario == 0:
                montant = frais.montant_du
                frais.montant_paye, frais.statut = montant, 'paye'
            elif scenario == 1:
                montant = frais.montant_du // 2
                frais.montant_paye, frais.statut = montant, 'partiel'
            else:
                continue
            paiements.append(Paiement(
                frais=frais, montant=montant, date_paiement=date(2024, 10, 15),
                mode=random.choice(['especes', 'mobile_money', 'virement']),
                recu_numero=f'PAI-2024-{uuid.uuid4().hex[:8].upper()}', saisi_par=caissier))
        Paiement.objects.bulk_create(paiements, batch_size=500)
        FraisScolarite.objects.bulk_update(list(frais_map.values()),
                                           ['montant_paye', 'statut'], batch_size=500)

    def _notes_resultats(self):
        notes = []
        # accumulateur : (eleve, cours, periode) -> [somme, nb]
        self.res_acc = {}
        plan = [(self.t1, ['devoir_surveille', 'devoir_surveille', 'examen_semestriel']),
                (self.t2, ['devoir_surveille', 'interrogation'])]
        for p, cls in self.eleves:
            c_i = self.classes.index(cls)
            niveau_base = 9 + (p.pk % 8)  # niveau moyen propre à l'élève (9-16)
            for m_i, mat in enumerate(self.matieres):
                co = self.cours_map[(c_i, m_i)]
                for periode, types in plan:
                    for type_ev in types:
                        val = niveau_base + random.randint(-4, 4)
                        val = max(0, min(20, val))
                        notes.append(Note(valeur=Decimal(val), type_eval=type_ev,
                                          eleve=p, cours=co, periode=periode))
                        k = (p.pk, co.pk, periode.pk)
                        acc = self.res_acc.setdefault(k, [0, 0, p, co, periode])
                        acc[0] += val
                        acc[1] += 1
        Note.objects.bulk_create(notes, batch_size=1000)

        # ResultatMatiere (moyenne par matière) + rang par cours/période
        resultats = []
        par_cours_periode = {}
        for (e_pk, c_pk, p_pk), (somme, nb, p, co, periode) in self.res_acc.items():
            moy = Decimal(str(round(somme / nb, 2)))
            rm = ResultatMatiere(eleve=p, cours=co, periode=periode, moyenne=moy)
            resultats.append(rm)
            par_cours_periode.setdefault((c_pk, p_pk), []).append(rm)
        for lst in par_cours_periode.values():
            lst.sort(key=lambda r: r.moyenne, reverse=True)
            for rang, r in enumerate(lst, start=1):
                r.rang = rang
        ResultatMatiere.objects.bulk_create(resultats, batch_size=1000)

    def _bulletins(self):
        # Moyenne générale pondérée par coefficient, par (élève, période close)
        agg = {}  # (eleve_pk, periode_pk) -> [pts, coeffs, personne, periode]
        for (e_pk, c_pk, p_pk), (somme, nb, p, co, periode) in self.res_acc.items():
            if periode not in self.periodes_closes:
                continue
            moy = Decimal(str(round(somme / nb, 2)))
            coeff = self.coeff_cours[co.pk]
            a = agg.setdefault((e_pk, p_pk), [Decimal(0), Decimal(0), p, periode])
            a[0] += moy * coeff
            a[1] += coeff

        # Regrouper par (classe, période) pour le rang
        classe_de = {p.pk: cls for p, cls in self.eleves}
        groupes = {}
        for (e_pk, p_pk), (pts, coeffs, p, periode) in agg.items():
            moy_gen = (pts / coeffs).quantize(Decimal('0.01')) if coeffs else Decimal(0)
            groupes.setdefault((classe_de[p.pk].pk, p_pk), []).append((p, periode, moy_gen))

        bulletins = []
        for (cls_pk, p_pk), lst in groupes.items():
            lst.sort(key=lambda x: x[2], reverse=True)
            effectif = len(lst)
            for rang, (p, periode, moy_gen) in enumerate(lst, start=1):
                bulletins.append(Bulletin(
                    eleve=p, periode=periode, moyenne_generale=moy_gen, rang=rang,
                    effectif_classe=effectif, appreciation=_appr(float(moy_gen))))
        Bulletin.objects.bulk_create(bulletins, batch_size=500)
        self.bulletins = bulletins

    def _absences_notifs_histo(self):
        notifs, histo, absences = [], [], []

        # Absences : ~1 élève sur 3, 1 à 3 absences chacun
        statuts = ['en_attente', 'justifiee', 'non_justifiee']
        for idx, (p, cls) in enumerate(self.eleves):
            if idx % 3 != 0:
                continue
            c_i = self.classes.index(cls)
            for _ in range(random.randint(1, 3)):
                m_i = random.randrange(len(self.matieres))
                co = self.cours_map[(c_i, m_i)]
                statut = random.choice(statuts)
                absences.append(Absence(
                    eleve=p, cours=co, periode=self.t1,
                    date_absence=date(2024, 10, 1) + timedelta(days=random.randint(0, 60)),
                    nb_heures=random.choice([1, 2, 2, 4]), statut=statut,
                    motif='Maladie' if statut == 'justifiee' else ''))
                notifs.append(Notification(
                    destinataire=p, type_notif='absence_enregistree',
                    message=f"Absence enregistrée en {co.matiere.nom_matiere}.", lu=False))
                for parent in self.parents_enfants.get(p.pk, []):
                    notifs.append(Notification(
                        destinataire=parent, type_notif='absence_enregistree',
                        message=f"Votre enfant {p.get_full_name()} a été absent.", lu=False))
        Absence.objects.bulk_create(absences, batch_size=1000)

        # Notifications de bulletin (élève + parents) + historique
        for b in self.bulletins:
            notifs.append(Notification(
                destinataire=b.eleve, type_notif='bulletin_disponible',
                message=f"Votre bulletin du {b.periode.nom} est disponible "
                        f"(moyenne {b.moyenne_generale}/20, rang {b.rang}/{b.effectif_classe}).",
                lu=bool(random.getrandbits(1))))
            for parent in self.parents_enfants.get(b.eleve.pk, []):
                notifs.append(Notification(
                    destinataire=parent, type_notif='bulletin_disponible',
                    message=f"Le bulletin de {b.eleve.get_full_name()} ({b.periode.nom}) est disponible.",
                    lu=False))
            histo.append(HistoriqueActions(
                auteur=self.staff['scolarite'], action='Génération bulletin',
                table_cible='bulletin',
                details=f"{b.eleve.get_full_name()} — {b.periode.nom} : {b.moyenne_generale}/20"))

        # Annonces générales à chaque classe (destinataire XOR classe)
        for cls in self.classes:
            notifs.append(Notification(
                classe=cls, type_notif='annonce',
                message=f"Réunion de classe {cls.nom} prévue prochainement.", lu=False))

        # Historique : inscriptions + création des comptes
        for p, cls in self.eleves:
            histo.append(HistoriqueActions(
                auteur=self.staff['scolarite'], action='Inscription élève',
                table_cible='inscription',
                details=f"{p.get_full_name()} inscrit(e) en {cls.nom}"))

        Notification.objects.bulk_create(notifs, batch_size=1000)
        HistoriqueActions.objects.bulk_create(histo, batch_size=1000)

    def _evenements_messages(self):
        dir_p, scol_p, fin_p = self.staff['direction'], self.staff['scolarite'], self.staff['finances']
        evts = [
            ('Rentrée scolaire 2024-2025', 'Accueil des élèves.', 'autre', date(2024, 9, 2), date(2024, 9, 2)),
            ('Vacances de la Toussaint', 'Congés scolaires.', 'vacances', date(2024, 10, 26), date(2024, 11, 4)),
            ('Composition du 1er trimestre', 'Évaluations — tous niveaux.', 'examen', date(2024, 12, 9), date(2024, 12, 18)),
            ('Conseil de classe T1', 'Clôture du 1er trimestre.', 'reunion', date(2025, 1, 13), date(2025, 1, 13)),
            ('Vacances de Noël', 'Congés scolaires.', 'vacances', date(2024, 12, 21), date(2025, 1, 5)),
            ('Composition du 2e trimestre', 'Évaluations — tous niveaux.', 'examen', date(2025, 3, 10), date(2025, 3, 21)),
            ('Fête de l\'école', 'Kermesse annuelle.', 'autre', date(2025, 5, 24), date(2025, 5, 24)),
        ]
        EvenementScolaire.objects.bulk_create([EvenementScolaire(
            titre=t, description=d, type_event=te, date_debut=d1, date_fin=d2,
            annee=self.annee, createur=dir_p) for t, d, te, d1, d2 in evts])

        ens1 = self.ens_map[0][0]
        msgs = [
            (dir_p, scol_p, 'Conseils de classe', 'Merci de préparer le planning des conseils.'),
            (scol_p, dir_p, 'Re : Conseils de classe', 'Le planning est prêt.'),
            (dir_p, fin_p, 'Bilan financier T1', 'Pouvez-vous transmettre le bilan des paiements ?'),
            (ens1, scol_p, 'Liste des absences', 'Voici la liste des absences d\'octobre.'),
            (dir_p, ens1, 'Félicitations', 'Excellents résultats ce trimestre !'),
        ]
        Message.objects.bulk_create([Message(expediteur=e, destinataire=d, sujet=s, corps=c)
                                     for e, d, s, c in msgs])

    def _resume(self):
        lignes = [
            ('Personnes', Personne.objects.count()),
            ('  — Personnel', Personnel.objects.count()),
            ('  — Enseignants', Enseignant.objects.count()),
            ('  — Élèves', Eleve.objects.count()),
            ('  — Parents', Parent.objects.count()),
            ('Classes', Classe.objects.count()),
            ('Cours', Cours.objects.count()),
            ('Emplois du temps', EmploiDuTemps.objects.count()),
            ('Inscriptions', Inscription.objects.count()),
            ('Liens parent-élève', LienParentEleve.objects.count()),
            ('Notes', Note.objects.count()),
            ('Résultats matière', ResultatMatiere.objects.count()),
            ('Bulletins', Bulletin.objects.count()),
            ('Absences', Absence.objects.count()),
            ('Notifications', Notification.objects.count()),
            ('Historique actions', HistoriqueActions.objects.count()),
            ('Frais scolarité', FraisScolarite.objects.count()),
            ('Paiements', Paiement.objects.count()),
            ('Tarifs niveau', TarifNiveau.objects.count()),
            ('Événements', EvenementScolaire.objects.count()),
            ('Messages', Message.objects.count()),
        ]
        self.stdout.write(self.style.SUCCESS('\n=== DONNÉES GÉNÉRÉES ==='))
        for nom, n in lignes:
            self.stdout.write(f'  {nom:.<26} {n:>7}')
        self.stdout.write(self.style.SUCCESS(
            '\nMot de passe commun : demo1234\n'
            '  Direction  : direction@academiq.ci\n'
            '  Scolarité  : scolarite@academiq.ci\n'
            '  Finances   : finances@academiq.ci\n'
            '  Enseignant : prof.maths1@academiq.ci\n'
            '  Élève      : eleve1@academiq.ci\n'
            '  Parent     : parent1@academiq.ci\n'))
