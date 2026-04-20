"""
Script de creation des donnees de demonstration pour ACADEMIQ V3.
Lance avec : python manage.py shell < create_demo_data.py
OU          : python create_demo_data.py (depuis le repertoire du projet)
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academiq.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import Group
from django.utils import timezone
from datetime import date, timedelta

from core.models import (
    Personne, AnneeScolaire, Periode, Matiere, Classe,
    Personnel, Enseignant, Eleve, Parent, Cours,
    Inscription, LienParentEleve,
)

print("=== ACADEMIQ V3 — Chargement des donnees de demo ===\n")

# ── Récupérer l'année et les périodes déjà créées ──────────────────────────
annee = AnneeScolaire.objects.filter(active=True).first()
if not annee:
    annee = AnneeScolaire.objects.create(libelle='2025-2026', active=True)
    print(f"  Annee creee : {annee}")
else:
    print(f"  Annee existante : {annee}")

periode1 = Periode.objects.filter(annee=annee).order_by('date_debut').first()
if not periode1:
    periode1 = Periode.objects.create(
        nom='Semestre 1', annee=annee,
        date_debut=date(2025, 9, 1), date_fin=date(2026, 1, 31)
    )
    print(f"  Periode creee : {periode1}")
else:
    print(f"  Periode existante : {periode1}")

# ── Récupérer classe et matières déjà créées ──────────────────────────────
classe = Classe.objects.filter(annee=annee).first()
if not classe:
    classe = Classe.objects.create(nom='TERMINALE C', annee=annee, effectif_max=40)
    print(f"  Classe creee : {classe}")
else:
    print(f"  Classe existante : {classe}")

maths = Matiere.objects.filter(nom_matiere__icontains='MATH').first()
if not maths:
    maths = Matiere.objects.create(nom_matiere='MATHEMATIQUE', coefficient=5)
    print(f"  Matiere creee : {maths}")
else:
    print(f"  Matiere existante : {maths}")

phys = Matiere.objects.filter(nom_matiere__icontains='PHYSIQUE').first()
if not phys:
    phys = Matiere.objects.create(nom_matiere='PHYSIQUE CHIMIE', coefficient=4)
    print(f"  Matiere creee : {phys}")
else:
    print(f"  Matiere existante : {phys}")

# ── Groupes ────────────────────────────────────────────────────────────────
groupes = {}
for nom in ['DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES', 'ENSEIGNANT', 'ELEVE', 'PARENT']:
    g, _ = Group.objects.get_or_create(name=nom)
    groupes[nom] = g

print("\n  Groupes OK")

# ── Helper creation compte ─────────────────────────────────────────────────
def creer_personne(email, nom, prenom, password='Demo@1234', groupes_list=None, is_staff=False, is_superuser=False):
    p, created = Personne.objects.get_or_create(email=email, defaults={
        'nom': nom, 'prenom': prenom, 'actif': True,
        'is_staff': is_staff, 'is_superuser': is_superuser,
    })
    if created:
        p.set_password(password)
        p.save()
        print(f"  [+] Personne : {p.get_full_name()} ({email})")
    else:
        print(f"  [=] Personne existante : {p.get_full_name()} ({email})")
    if groupes_list:
        for g in groupes_list:
            p.groups.add(groupes[g])
    return p

# ── Comptes ────────────────────────────────────────────────────────────────
print("\n--- Comptes ---")
p_direction = creer_personne(
    'direction@academiq.ci', 'COULIBALY', 'Adama',
    groupes_list=['DIRECTION'], is_staff=True
)
p_scolarite = creer_personne(
    'scolarite@academiq.ci', 'TRAORE', 'Fatoumata',
    groupes_list=['SCOLARITE']
)
p_prof1 = creer_personne(
    'prof.maths@academiq.ci', 'DIABATE', 'Moussa',
    groupes_list=['ENSEIGNANT']
)
p_prof2 = creer_personne(
    'prof.phys@academiq.ci', 'KONE', 'Aminata',
    groupes_list=['ENSEIGNANT']
)
p_eleve1 = creer_personne(
    'eleve1@academiq.ci', 'BAMBA', 'Youssouf',
    groupes_list=['ELEVE']
)
p_eleve2 = creer_personne(
    'eleve2@academiq.ci', 'OUATTARA', 'Mariam',
    groupes_list=['ELEVE']
)
p_parent1 = creer_personne(
    'parent1@academiq.ci', 'BAMBA', 'Ibrahim',
    groupes_list=['PARENT']
)

# ── Sous-entités ───────────────────────────────────────────────────────────
print("\n--- Sous-entites ---")

# Personnel direction
pers_dir, c = Personnel.objects.get_or_create(
    personne=p_direction,
    defaults={'fonction': 'direction', 'date_embauche': date(2018, 9, 1)}
)
print(f"  {'[+]' if c else '[=]'} Personnel : {p_direction.get_full_name()}")

# Personnel scolarité
pers_sco, c = Personnel.objects.get_or_create(
    personne=p_scolarite,
    defaults={'fonction': 'scolarite', 'date_embauche': date(2019, 9, 1)}
)
print(f"  {'[+]' if c else '[=]'} Personnel : {p_scolarite.get_full_name()}")

# Enseignants
ens1, c = Enseignant.objects.get_or_create(
    personne=p_prof1,
    defaults={'specialite': 'Mathématiques', 'grade': 'Professeur certifié', 'date_embauche': date(2020, 9, 1)}
)
print(f"  {'[+]' if c else '[=]'} Enseignant : {p_prof1.get_full_name()}")

ens2, c = Enseignant.objects.get_or_create(
    personne=p_prof2,
    defaults={'specialite': 'Physique-Chimie', 'grade': 'Professeur certifié', 'date_embauche': date(2021, 9, 1)}
)
print(f"  {'[+]' if c else '[=]'} Enseignant : {p_prof2.get_full_name()}")

# Élèves
elv1, c = Eleve.objects.get_or_create(
    personne=p_eleve1,
    defaults={'date_naissance': date(2007, 3, 15), 'lieu_naissance': 'Abidjan', 'matricule': 'ELV-2025-001'}
)
print(f"  {'[+]' if c else '[=]'} Eleve : {p_eleve1.get_full_name()}")

elv2, c = Eleve.objects.get_or_create(
    personne=p_eleve2,
    defaults={'date_naissance': date(2007, 7, 22), 'lieu_naissance': 'Bouaké', 'matricule': 'ELV-2025-002'}
)
print(f"  {'[+]' if c else '[=]'} Eleve : {p_eleve2.get_full_name()}")

# Parent
par1, c = Parent.objects.get_or_create(
    personne=p_parent1,
    defaults={'profession': 'Commerçant', 'telephone': '+225 07 00 00 00'}
)
print(f"  {'[+]' if c else '[=]'} Parent : {p_parent1.get_full_name()}")

# ── Lien parent-élève ──────────────────────────────────────────────────────
lien, c = LienParentEleve.objects.get_or_create(
    parent=p_parent1, eleve=p_eleve1,
    defaults={'lien': 'pere'}
)
print(f"\n  {'[+]' if c else '[=]'} Lien parent-eleve : {p_parent1.get_full_name()} -> {p_eleve1.get_full_name()}")

# ── Cours ──────────────────────────────────────────────────────────────────
print("\n--- Cours ---")
cours_maths, c = Cours.objects.get_or_create(
    matiere=maths, classe=classe, enseignant=p_prof1, annee=annee,
    defaults={'nb_heures_hebdo': 4}
)
print(f"  {'[+]' if c else '[=]'} Cours : {maths} — {classe}")

cours_phys, c = Cours.objects.get_or_create(
    matiere=phys, classe=classe, enseignant=p_prof2, annee=annee,
    defaults={'nb_heures_hebdo': 3}
)
print(f"  {'[+]' if c else '[=]'} Cours : {phys} — {classe}")

# ── Inscriptions ───────────────────────────────────────────────────────────
print("\n--- Inscriptions ---")
insc1, c = Inscription.objects.get_or_create(
    eleve=p_eleve1, annee=annee,
    defaults={'classe': classe, 'date_inscription': date(2025, 9, 2), 'statut': 'actif'}
)
print(f"  {'[+]' if c else '[=]'} Inscription : {p_eleve1.get_full_name()} -> {classe}")

insc2, c = Inscription.objects.get_or_create(
    eleve=p_eleve2, annee=annee,
    defaults={'classe': classe, 'date_inscription': date(2025, 9, 2), 'statut': 'actif'}
)
print(f"  {'[+]' if c else '[=]'} Inscription : {p_eleve2.get_full_name()} -> {classe}")

# ── Résumé ─────────────────────────────────────────────────────────────────
print("""
=== DONE ===

Comptes de test (mot de passe : Demo@1234)
------------------------------------------
  DIRECTION  : direction@academiq.ci
  SCOLARITE  : scolarite@academiq.ci
  ENSEIGNANT : prof.maths@academiq.ci
  ENSEIGNANT : prof.phys@academiq.ci
  ELEVE      : eleve1@academiq.ci
  ELEVE      : eleve2@academiq.ci
  PARENT     : parent1@academiq.ci
""")
