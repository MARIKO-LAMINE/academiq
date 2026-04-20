# ACADEMIQ V3
**Système Centralisé de Gestion des Activités Scolaires**

Étudiant : MARIKO Lamine · N° CE : CI0223065023  
Filière : Master 1 — Génie Informatique · Université Nangui Abrogoua  
Encadreur : Dr. ZEZE · Année universitaire : 2025–2026

---

## Stack technique

| Couche | Technologie |
|--------|-------------|
| Backend | Django 6.0.1 (Python 3.14) |
| Base de données | SQLite (développement) |
| Frontend | Bootstrap 5.3 + Bootstrap Icons |
| PDF | ReportLab 4.x |
| Tests | pytest-django |

---

## Installation

### 1. Cloner le projet

```bash
git clone <url-du-repo>
cd academiq
```

### 2. Créer et activer l'environnement virtuel

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate
```

### 3. Installer les dépendances

```bash
pip install django django-crispy-forms crispy-bootstrap5 reportlab pillow pytest-django
```

### 4. Appliquer les migrations

```bash
cd academiq
python manage.py migrate
```

### 5. Créer les groupes et un superuser

```bash
python manage.py init_groupes
python manage.py createsuperuser
```

### 6. Charger les données de démonstration (optionnel)

```bash
python create_demo_data.py
python create_notes_demo.py
```

### 7. Lancer le serveur

```bash
python manage.py runserver
```

Accéder à l'application : http://127.0.0.1:8000/login/

---

## Comptes de démonstration

| Rôle | Email | Mot de passe |
|------|-------|-------------|
| Direction | direction@academiq.ci | Demo@1234 |
| Scolarité | scolarite@academiq.ci | Demo@1234 |
| Enseignant (Maths) | prof.maths@academiq.ci | Demo@1234 |
| Enseignant (Physique) | prof.phys@academiq.ci | Demo@1234 |
| Élève | eleve1@academiq.ci | Demo@1234 |
| Élève | eleve2@academiq.ci | Demo@1234 |
| Parent | parent1@academiq.ci | Demo@1234 |

---

## Fonctionnalités par rôle

### Direction / Scolarité
- Gestion des années scolaires, périodes, classes, matières, salles, cours
- Création et gestion des comptes utilisateurs (5 rôles)
- Gestion des inscriptions (actif / transféré / abandonné — jamais supprimé)
- Validation des absences (justifiée / non justifiée)
- Génération des bulletins après clôture de période
- Export PDF des bulletins (ReportLab)

### Enseignant
- Tableau de bord avec ses cours de l'année active
- Saisie des notes par cours et par période
- Enregistrement des absences
- Consultation des résultats de ses élèves

### Élève
- Tableau de bord personnel (moyenne générale, absences)
- Consultation des notes et résultats par matière
- Bilan des absences
- Téléchargement des bulletins PDF

### Parent
- Suivi de chaque enfant (fratrie multiple supportée)
- Accès aux notes, absences et bulletins de ses enfants

---

## Tests automatisés

```bash
cd academiq
python -m pytest core/tests.py -v
```

**9 tests couvrant :**
- RG-N03 : Contrainte [0 ; 20] sur les notes
- RG-C03 : Unicité inscription élève/année
- RG-T02 : Unicité de l'année scolaire active
- RG-M01 : Recalcul automatique des moyennes via signal
- RG-B01 : Unicité bulletin élève/période
- RG-A03 : Blocage connexion compte inactif
- RG-H03 : Exclusivité des rôles
- Cloisonnement des données enseignant

---

## Structure du projet

```
academiq/                  ← Répertoire racine
├── venv/                  ← Environnement virtuel
└── academiq/              ← Projet Django
    ├── academiq/          ← Configuration (settings, urls)
    ├── core/              ← Modèles, signaux, permissions, tests
    ├── accounts/          ← Authentification
    ├── personnel/         ← Espace DIRECTION/SCOLARITE
    ├── enseignant/        ← Espace ENSEIGNANT
    ├── eleve/             ← Espace ÉLÈVE
    ├── parent/            ← Espace PARENT
    ├── templates/         ← Templates globaux + base layouts
    ├── static/            ← CSS, JS, images
    └── manage.py
```

---

*ACADEMIQ V3 — MARIKO Lamine · CI0223065023 · Master 1 Génie Informatique · Université Nangui Abrogoua · 2025–2026*
