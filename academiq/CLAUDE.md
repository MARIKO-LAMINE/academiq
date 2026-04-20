# ACADEMIQ V3 — Guide d'Implémentation
**Système Centralisé de Gestion des Activités Scolaires**  
Étudiant : MARIKO Lamine · N° CE : CI0223065023  
Filière : Master 1 — Génie Informatique · Université Nangui Abrogoua  
Encadreur : Dr. ZEZE · Année universitaire : 2025–2026

> **Statut du projet :** Phases 1–3 terminées (Règles de gestion ✅ · MCD ✅ · MLD ✅ · MPD/SQL ✅)  
> **Phase courante : Implémentation — Django + HTML/CSS/Bootstrap**

---

## Table des matières

1. [Stack technique](#1-stack-technique)
2. [Structure du projet Django](#2-structure-du-projet-django)
3. [Étape 1 — Configuration initiale](#3-étape-1--configuration-initiale)
4. [Étape 2 — Modèles Django (models.py)](#4-étape-2--modèles-django-modelspy)
5. [Étape 3 — Authentification et permissions](#5-étape-3--authentification-et-permissions)
6. [Étape 4 — Signaux métier (signals.py)](#6-étape-4--signaux-métier-signalspy)
7. [Étape 5 — Vues et URLs (views.py / urls.py)](#7-étape-5--vues-et-urls-viewspy--urlspy)
8. [Étape 6 — Templates HTML/CSS/Bootstrap](#8-étape-6--templates-htmlcssbootstrap)
9. [Étape 7 — Modules fonctionnels par rôle](#9-étape-7--modules-fonctionnels-par-rôle)
10. [Étape 8 — Tests et validation](#10-étape-8--tests-et-validation)
11. [Conventions et règles à respecter](#11-conventions-et-règles-à-respecter)
12. [Checklist d'avancement](#12-checklist-davancement)

---

## 1. Stack technique

| Couche | Technologie | Rôle |
|---|---|---|
| **Backend** | Django 4.x (Python 3.10+) | Logique métier, ORM, routing, authentification |
| **Base de données** | MariaDB 10.x / InnoDB | Stockage persistant, contraintes SQL |
| **Frontend** | HTML5 + CSS3 + Bootstrap 5 | Interfaces utilisateur, responsive design |
| **Templating** | Django Templates | Rendu HTML côté serveur |
| **Formulaires** | Django Forms / ModelForms | Saisie et validation des données |
| **Auth** | Django Auth (AbstractUser) | Sessions, hachage bcrypt, groupes |
| **PDF** | `reportlab` ou `xhtml2pdf` | Export bulletins en PDF |

### Ce qu'on N'utilise PAS dans ce projet
- Pas de Django REST Framework (pas d'API JSON — rendu HTML pur côté serveur)
- Pas de React / Vue / JavaScript framework
- Pas d'AJAX complexe (formulaires Django classiques avec POST)

---

## 2. Structure du projet Django

```
academiq/                          ← Répertoire racine du projet
│
├── academiq/                      ← Package de configuration Django
│   ├── settings.py                ← Configuration (DB, apps, auth...)
│   ├── urls.py                    ← URLs racine
│   ├── wsgi.py
│   └── asgi.py
│
├── core/                          ← App principale : modèles, signaux, permissions
│   ├── models.py                  ← 19 modèles (Personne, Cours, Note, etc.)
│   ├── signals.py                 ← Recalcul moyennes, notifications, historique
│   ├── permissions.py             ← Décorateurs et mixins par rôle
│   ├── admin.py                   ← Interface d'administration Django
│   └── apps.py
│
├── accounts/                      ← App authentification
│   ├── views.py                   ← login, logout, dashboard de redirection
│   ├── forms.py                   ← LoginForm
│   ├── urls.py
│   └── templates/
│       └── accounts/
│           ├── login.html
│           └── profil.html
│
├── personnel/                     ← App espace PERSONNEL (direction, scolarité...)
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/
│       └── personnel/
│
├── enseignant/                    ← App espace ENSEIGNANT
│   ├── views.py
│   ├── forms.py
│   ├── urls.py
│   └── templates/
│       └── enseignant/
│
├── eleve/                         ← App espace ÉLÈVE
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── eleve/
│
├── parent/                        ← App espace PARENT
│   ├── views.py
│   ├── urls.py
│   └── templates/
│       └── parent/
│
├── templates/                     ← Templates globaux partagés
│   ├── base.html                  ← Layout principal avec Bootstrap 5
│   ├── base_personnel.html        ← Layout + sidebar PERSONNEL
│   ├── base_enseignant.html       ← Layout + sidebar ENSEIGNANT
│   ├── base_eleve.html            ← Layout + sidebar ÉLÈVE
│   ├── base_parent.html           ← Layout + sidebar PARENT
│   └── partials/
│       ├── navbar.html
│       ├── messages.html          ← Alertes Django messages framework
│       └── pagination.html
│
├── static/                        ← Fichiers statiques
│   ├── css/
│   │   └── academiq.css           ← Styles personnalisés
│   ├── js/
│   │   └── academiq.js
│   └── img/
│       └── logo.png
│
├── manage.py
└── requirements.txt
```

---

## 3. Étape 1 — Configuration initiale

### 3.1 Installation des dépendances

```bash
pip install django mysqlclient pillow reportlab
```

**`requirements.txt`**
```
django>=4.2
mysqlclient>=2.1
pillow>=10.0
reportlab>=4.0
```

### 3.2 settings.py — Points clés

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps projet
    'core',
    'accounts',
    'personnel',
    'enseignant',
    'eleve',
    'parent',
]

# Modèle utilisateur personnalisé (obligatoire AVANT la première migration)
AUTH_USER_MODEL = 'core.Personne'

# Base de données MariaDB
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'academiq_db',
        'USER': 'academiq_user',
        'PASSWORD': 'mot_de_passe',
        'HOST': 'localhost',
        'PORT': '3306',
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        }
    }
}

# Hachage bcrypt
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]

# Redirection après login/logout
LOGIN_URL = '/login/'
LOGIN_REDIRECT_URL = '/dashboard/'
LOGOUT_REDIRECT_URL = '/login/'

# Fichiers statiques et médias
STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## 4. Étape 2 — Modèles Django (models.py)

### Ordre de création des modèles (respecter les dépendances FK)

```
1.  Personne            ← AbstractBaseUser (super-entité racine)
2.  AnneeScolaire
3.  Periode             → FK AnneeScolaire
4.  Salle
5.  Matiere
6.  Personnel           → OneToOneField Personne
7.  Enseignant          → OneToOneField Personne
8.  Eleve               → OneToOneField Personne
9.  Parent              → OneToOneField Personne
10. Classe              → FK AnneeScolaire
11. Cours               → FK Matiere, Classe, Enseignant, AnneeScolaire
12. EmploiDuTemps       → FK Cours, Salle, Periode
13. Inscription         → FK Eleve, Classe, AnneeScolaire
14. LienParentEleve     → FK Parent, Eleve
15. Note                → FK Eleve, Cours, Periode
16. ResultatMatiere     → FK Eleve, Cours, Periode  ← CALCULÉ, jamais saisi
17. Absence             → FK Eleve, Cours, Periode
18. Bulletin            → FK Eleve, Periode         ← GÉNÉRÉ après clôture période
19. Notification        → FK Personne, Classe
20. HistoriqueActions   → FK Personne
```

### Modèle Personne (AbstractBaseUser)

```python
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class PersonneManager(BaseUserManager):
    def create_user(self, email, nom, prenom, password=None, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, nom=nom, prenom=prenom, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, nom, prenom, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, nom, prenom, password, **extra_fields)

class Personne(AbstractBaseUser, PermissionsMixin):
    nom = models.CharField(max_length=80)
    prenom = models.CharField(max_length=80)
    email = models.EmailField(unique=True)
    photo_profil = models.ImageField(upload_to='profils/', null=True, blank=True)
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nom', 'prenom']

    objects = PersonneManager()

    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

    def get_role(self):
        for role in ['personnel', 'enseignant', 'eleve', 'parent']:
            if hasattr(self, role):
                return role
        return None

    class Meta:
        db_table = 'personne'
```

### Sous-entités (patron OneToOneField)

```python
class Enseignant(models.Model):
    personne = models.OneToOneField(
        'Personne', on_delete=models.CASCADE,
        primary_key=True, related_name='enseignant'
    )
    specialite = models.CharField(max_length=100)
    grade = models.CharField(max_length=50, blank=True)
    date_embauche = models.DateField(null=True, blank=True)

    def clean(self):
        # Exclusivité des rôles (RG-H03)
        for role in ['personnel', 'eleve', 'parent']:
            if hasattr(self.personne, role):
                raise ValidationError(f"Cette personne a déjà le rôle : {role}.")

    class Meta:
        db_table = 'enseignant'
```

### Exemple modèle Note avec contrainte CHECK

```python
class Note(models.Model):
    TYPES_EVAL = [
        ('devoir_surveille', 'Devoir surveillé'),
        ('interrogation', 'Interrogation'),
        ('examen_semestriel', 'Examen semestriel'),
    ]
    valeur = models.DecimalField(max_digits=4, decimal_places=2)
    type_eval = models.CharField(max_length=20, choices=TYPES_EVAL)
    date_saisie = models.DateField(auto_now_add=True)
    eleve = models.ForeignKey('Personne', on_delete=models.RESTRICT, related_name='notes')
    cours = models.ForeignKey('Cours', on_delete=models.RESTRICT, related_name='notes')
    periode = models.ForeignKey('Periode', on_delete=models.RESTRICT, related_name='notes')

    class Meta:
        db_table = 'note'
        constraints = [
            models.CheckConstraint(
                check=models.Q(valeur__gte=0) & models.Q(valeur__lte=20),
                name='note_valeur_entre_0_et_20'  # RG-N03
            )
        ]
```

### Exemple modèle avec contrainte UNIQUE composite

```python
class Inscription(models.Model):
    STATUTS = [
        ('actif', 'Actif'),
        ('transfere', 'Transféré'),
        ('abandonne', 'Abandonné'),
    ]
    eleve = models.ForeignKey('Personne', on_delete=models.RESTRICT, related_name='inscriptions')
    classe = models.ForeignKey('Classe', on_delete=models.RESTRICT)
    annee = models.ForeignKey('AnneeScolaire', on_delete=models.RESTRICT)
    date_inscription = models.DateField()
    statut = models.CharField(max_length=10, choices=STATUTS, default='actif')

    class Meta:
        db_table = 'inscription'
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'annee'],
                name='unique_eleve_par_annee'  # RG-C03
            )
        ]
```

---

## 5. Étape 3 — Authentification et permissions

### 5.1 Groupes Django à créer (une seule fois)

```python
# core/management/commands/init_groupes.py
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        groupes = ['DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES',
                   'ENSEIGNANT', 'ELEVE', 'PARENT']
        for nom in groupes:
            Group.objects.get_or_create(name=nom)
        self.stdout.write("Groupes créés.")
```

```bash
python manage.py init_groupes
```

### 5.2 Décorateur de permission (permissions.py)

```python
from functools import wraps
from django.shortcuts import redirect

def role_required(*roles):
    """
    Usage : @role_required('ENSEIGNANT')
            @role_required('DIRECTION', 'SCOLARITE')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            user_groups = request.user.groups.values_list('name', flat=True)
            if any(r in user_groups for r in roles):
                return view_func(request, *args, **kwargs)
            return redirect('acces_refuse')
        return wrapper
    return decorator
```

### 5.3 Mixin pour les Class-Based Views

```python
class RoleRequiredMixin:
    roles_requis = []  # À définir dans chaque vue

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        user_groups = request.user.groups.values_list('name', flat=True)
        if not any(r in user_groups for r in self.roles_requis):
            return redirect('acces_refuse')
        return super().dispatch(request, *args, **kwargs)
```

### 5.4 Vue de redirection post-login

```python
# accounts/views.py
@login_required
def dashboard(request):
    groupes = request.user.groups.values_list('name', flat=True)
    if any(g in groupes for g in ['DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES']):
        return redirect('personnel:dashboard')
    elif 'ENSEIGNANT' in groupes:
        return redirect('enseignant:dashboard')
    elif 'ELEVE' in groupes:
        return redirect('eleve:dashboard')
    elif 'PARENT' in groupes:
        return redirect('parent:dashboard')
    return redirect('login')
```

---

## 6. Étape 4 — Signaux métier (signals.py)

### Chaîne de recalcul automatique

```
Saisie NOTE (post_save)
    └─► Recalcul ResultatMatiere (moyenne arithmétique du cours sur la période)
            └─► Mise à jour Bulletin si déjà généré
    └─► Création Notification → élève
    └─► Alimentation HistoriqueActions
```

### signals.py

```python
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Avg
from .models import Note, ResultatMatiere, Bulletin, Notification, HistoriqueActions, AnneeScolaire

@receiver(post_save, sender=Note)
def recalculer_resultat_matiere(sender, instance, **kwargs):
    """RG-M01, RG-M03 : Recalcul automatique après saisie de note."""
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

    # Notification à l'élève
    Notification.objects.create(
        message=f"Nouvelle note en {instance.cours.matiere.nom_matiere} : {instance.valeur}/20",
        type_notif='note_saisie',
        destinataire=instance.eleve
    )

    # Traçabilité
    HistoriqueActions.objects.create(
        auteur=instance.cours.enseignant,
        action='Saisie note',
        table_cible='note',
        id_enreg=instance.pk
    )


@receiver(pre_save, sender=AnneeScolaire)
def une_seule_annee_active(sender, instance, **kwargs):
    """RG-T02 : Désactive l'ancienne année active si on active une nouvelle."""
    if instance.active:
        AnneeScolaire.objects.exclude(pk=instance.pk).update(active=False)
```

**Signaux à implémenter :**
- `post_save` sur `Note` → recalcul `ResultatMatiere` + notification élève *(voir ci-dessus)*
- `post_save` sur `Absence` → notification élève + parent + vérification seuil (RG-AB06)
- `post_save` sur `Bulletin` → notification élève + parent (RG-B)
- `pre_save` sur `AnneeScolaire` → désactivation automatique (RG-T02)

---

## 7. Étape 5 — Vues et URLs (views.py / urls.py)

### URLs racine (academiq/urls.py)

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),
    path('personnel/', include('personnel.urls', namespace='personnel')),
    path('enseignant/', include('enseignant.urls', namespace='enseignant')),
    path('eleve/', include('eleve.urls', namespace='eleve')),
    path('parent/', include('parent.urls', namespace='parent')),
]
```

### Patron d'une vue FBV (Function-Based View)

```python
# enseignant/views.py
@role_required('ENSEIGNANT')
def saisir_note(request, cours_id):
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)
    if request.method == 'POST':
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save(commit=False)
            note.cours = cours
            note.save()
            messages.success(request, "Note enregistrée avec succès.")
            return redirect('enseignant:mes_cours')
    else:
        form = NoteForm()
    return render(request, 'enseignant/saisir_note.html', {
        'form': form, 'cours': cours
    })
```

### Tableau complet des vues à développer

| App | Vue | URL | Rôles autorisés |
|---|---|---|---|
| `accounts` | `login_view` | `/login/` | Tous (non authentifiés) |
| `accounts` | `logout_view` | `/logout/` | Tous |
| `accounts` | `dashboard` | `/dashboard/` | Tous (redirection par rôle) |
| `personnel` | `dashboard` | `/personnel/` | DIRECTION, ADMINISTRATION, SCOLARITE, FINANCES |
| `personnel` | `gestion_annees` | `/personnel/annees/` | DIRECTION |
| `personnel` | `gestion_comptes` | `/personnel/comptes/` | DIRECTION |
| `personnel` | `gestion_classes` | `/personnel/classes/` | DIRECTION, SCOLARITE |
| `personnel` | `gestion_cours` | `/personnel/cours/` | DIRECTION, ADMINISTRATION |
| `personnel` | `gestion_edt` | `/personnel/edt/` | DIRECTION, ADMINISTRATION |
| `personnel` | `gestion_inscriptions` | `/personnel/inscriptions/` | SCOLARITE, DIRECTION |
| `personnel` | `validation_absences` | `/personnel/absences/` | SCOLARITE, DIRECTION |
| `personnel` | `generer_bulletin` | `/personnel/bulletins/` | SCOLARITE, DIRECTION |
| `enseignant` | `dashboard` | `/enseignant/` | ENSEIGNANT |
| `enseignant` | `mes_cours` | `/enseignant/cours/` | ENSEIGNANT |
| `enseignant` | `saisir_note` | `/enseignant/cours/<id>/notes/` | ENSEIGNANT |
| `enseignant` | `saisir_absence` | `/enseignant/cours/<id>/absences/` | ENSEIGNANT |
| `eleve` | `dashboard` | `/eleve/` | ELEVE |
| `eleve` | `mes_notes` | `/eleve/notes/` | ELEVE |
| `eleve` | `mes_absences` | `/eleve/absences/` | ELEVE |
| `eleve` | `mes_bulletins` | `/eleve/bulletins/` | ELEVE |
| `parent` | `dashboard` | `/parent/` | PARENT |
| `parent` | `suivi_enfant` | `/parent/enfant/<id>/` | PARENT |

---

## 8. Étape 6 — Templates HTML/CSS/Bootstrap

### 8.1 base.html — Layout principal

```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{% block title %}ACADEMIQ V3{% endblock %}</title>
    <!-- Bootstrap 5 -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <!-- Bootstrap Icons -->
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" rel="stylesheet">
    {% load static %}
    <link rel="stylesheet" href="{% static 'css/academiq.css' %}">
</head>
<body>
    {% include 'partials/navbar.html' %}
    <div class="container-fluid">
        <div class="row">
            {% block sidebar %}{% endblock %}
            <main class="col-md-9 ms-sm-auto col-lg-10 px-md-4 py-4">
                {% include 'partials/messages.html' %}
                {% block content %}{% endblock %}
            </main>
        </div>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    {% block extra_js %}{% endblock %}
</body>
</html>
```

### 8.2 Sidebar ENSEIGNANT (exemple)

```html
<!-- templates/partials/sidebar_enseignant.html -->
<nav class="col-md-3 col-lg-2 d-md-block bg-dark sidebar collapse" id="sidebarMenu">
    <div class="position-sticky pt-3">
        <div class="text-white px-3 py-2 mb-2 border-bottom border-secondary">
            <small class="text-muted">Connecté en tant que</small><br>
            <strong>{{ request.user.get_full_name }}</strong><br>
            <span class="badge bg-info">Enseignant</span>
        </div>
        <ul class="nav flex-column">
            <li class="nav-item">
                <a class="nav-link text-white" href="{% url 'enseignant:dashboard' %}">
                    <i class="bi bi-speedometer2 me-2"></i>Tableau de bord
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link text-white" href="{% url 'enseignant:mes_cours' %}">
                    <i class="bi bi-book me-2"></i>Mes cours
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link text-white" href="{% url 'enseignant:saisir_note' %}">
                    <i class="bi bi-pencil-square me-2"></i>Saisir des notes
                </a>
            </li>
            <li class="nav-item">
                <a class="nav-link text-white" href="{% url 'enseignant:saisir_absence' %}">
                    <i class="bi bi-person-x me-2"></i>Enregistrer une absence
                </a>
            </li>
        </ul>
        <hr class="text-secondary">
        <ul class="nav flex-column mb-2">
            <li class="nav-item">
                <a class="nav-link text-danger" href="{% url 'logout' %}">
                    <i class="bi bi-box-arrow-right me-2"></i>Déconnexion
                </a>
            </li>
        </ul>
    </div>
</nav>
```

### 8.3 Affichage des messages Django

```html
<!-- templates/partials/messages.html -->
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }} alert-dismissible fade show" role="alert">
            <i class="bi bi-{% if message.tags == 'success' %}check-circle{% elif message.tags == 'danger' %}exclamation-triangle{% else %}info-circle{% endif %} me-2"></i>
            {{ message }}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    {% endfor %}
{% endif %}
```

### 8.4 Formulaire Django avec Bootstrap 5

```html
{% extends 'base_enseignant.html' %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0">
                    <i class="bi bi-pencil-square me-2"></i>
                    Saisir une note — {{ cours.matiere.nom_matiere }}
                </h5>
            </div>
            <div class="card-body">
                <form method="post" novalidate>
                    {% csrf_token %}
                    {% for field in form %}
                    <div class="mb-3">
                        <label for="{{ field.id_for_label }}" class="form-label fw-semibold">
                            {{ field.label }}
                        </label>
                        <{{ field.widget_type }}
                            class="form-control {% if field.errors %}is-invalid{% endif %}"
                            ...
                        >
                        {# Rendu manuel recommandé pour contrôle Bootstrap complet #}
                        {{ field }}
                        {% if field.errors %}
                            <div class="invalid-feedback">{{ field.errors|join:", " }}</div>
                        {% endif %}
                    </div>
                    {% endfor %}
                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-check-circle me-1"></i>Enregistrer
                        </button>
                        <a href="{% url 'enseignant:mes_cours' %}" class="btn btn-outline-secondary">
                            Annuler
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### 8.5 Tableau de données Bootstrap

```html
<div class="card shadow-sm">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h6 class="mb-0">Liste des notes</h6>
        <a href="{% url 'enseignant:saisir_note' cours.pk %}" class="btn btn-sm btn-primary">
            <i class="bi bi-plus-circle me-1"></i>Nouvelle note
        </a>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-striped table-hover align-middle mb-0">
                <thead class="table-dark">
                    <tr>
                        <th>Élève</th><th>Valeur</th><th>Type</th><th>Date</th><th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {% for note in notes %}
                    <tr>
                        <td>{{ note.eleve.get_full_name }}</td>
                        <td>
                            <span class="badge fs-6 {% if note.valeur >= 10 %}bg-success{% else %}bg-danger{% endif %}">
                                {{ note.valeur }}/20
                            </span>
                        </td>
                        <td>{{ note.get_type_eval_display }}</td>
                        <td>{{ note.date_saisie|date:"d/m/Y" }}</td>
                        <td>
                            <a href="{% url 'enseignant:modifier_note' note.pk %}"
                               class="btn btn-sm btn-outline-primary">
                                <i class="bi bi-pencil"></i>
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="5" class="text-center text-muted py-4">
                            <i class="bi bi-inbox fs-4 d-block mb-2"></i>
                            Aucune note enregistrée pour ce cours.
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>
```

---

## 9. Étape 7 — Modules fonctionnels par rôle

### Module 1 — Authentification *(priorité absolue, à faire en premier)*
- [ ] `LoginForm` avec champ `email` + `password`
- [ ] Vue `login_view` → vérification `actif=True` avant validation
- [ ] Vue `dashboard` → redirection intelligente selon groupe Django
- [ ] Template `login.html` centré (Bootstrap card)
- [ ] Page `403.html` (accès refusé)

### Module 2 — PERSONNEL : Gestion de l'établissement
- [ ] CRUD `AnneeScolaire` + bouton "Activer" (signal RG-T02)
- [ ] CRUD `Periode` (trimestres ou semestres, validation non-chevauchement)
- [ ] CRUD `Salle`, `Matiere`, `Classe`
- [ ] CRUD `Cours` (matière × classe × enseignant × année)
- [ ] Gestion `EmploiDuTemps` avec détection de conflits de créneaux
- [ ] CRUD comptes Personne + sous-entité — réservé DIRECTION
- [ ] Gestion `Inscription` : créer / transférer / abandonner (jamais supprimer)

### Module 3 — ENSEIGNANT : Saisie pédagogique
- [ ] Dashboard avec résumé de ses cours de l'année active
- [ ] Liste des élèves par cours
- [ ] Saisie notes (filtrage : cours appartenant à l'enseignant connecté)
- [ ] Enregistrement absences (statut initial `en_attente`)
- [ ] Consultation bulletins de ses élèves (lecture seule)

### Module 4 — PERSONNEL : Résultats et bulletins
- [ ] Validation absences (justifiée / non justifiée)
- [ ] Génération bulletins après clôture période (vérification `date_fin <= today`)
- [ ] Calcul et stockage du rang par classe et période
- [ ] Export PDF des bulletins (`reportlab` ou `xhtml2pdf`)

### Module 5 — ÉLÈVE : Espace personnel *(lecture seule)*
- [ ] Dashboard avec carte résumé (moyenne générale, nb absences, dernière note)
- [ ] Tableau notes par cours et période
- [ ] Bilan absences par cours
- [ ] Bulletins disponibles (après clôture)
- [ ] Notifications non lues (badge dans navbar)

### Module 6 — PARENT : Suivi des enfants
- [ ] Sélection enfant si fratrie multiple (via `LienParentEleve`)
- [ ] Mêmes vues que l'élève, filtrées via le lien parent
- [ ] Notifications

### Module 7 — Notifications *(transversal)*
- [ ] Badge compteur dans la navbar (requête `Notification.objects.filter(lu=False, ...)`)
- [ ] Page liste des notifications
- [ ] Vue POST pour marquer comme lu
- [ ] Envoi annonce générale PERSONNEL → toute une classe

---

## 10. Étape 8 — Tests et validation

### Tests critiques à écrire (pytest-django)

```python
# Tests règles de gestion
def test_note_hors_intervalle_rejetee():
    """RG-N03 : valeur > 20 doit lever une ValidationError."""

def test_un_eleve_une_classe_par_annee():
    """RG-C03 : double inscription sur la même année → IntegrityError."""

def test_bulletin_unique_par_eleve_periode():
    """RG-B01 : UNIQUE(eleve, periode) → IntegrityError au doublon."""

def test_enseignant_filtre_ses_cours_uniquement():
    """Cloisonnement : un enseignant ne voit que ses propres cours."""

def test_recalcul_auto_resultat_matiere():
    """Signal : créer une Note → ResultatMatiere mis à jour automatiquement."""

def test_annee_active_unique():
    """RG-T02 : activer une année désactive automatiquement la précédente."""

def test_compte_inactif_ne_peut_pas_se_connecter():
    """RG-A03 : actif=False → accès refusé à la connexion."""
```

### Checklist de validation finale
- [ ] Contraintes UNIQUE actives et testées (inscription, cours, bulletin, résultat)
- [ ] Contrainte CHECK [0;20] active en base MariaDB
- [ ] Groupes Django créés et assignés correctement
- [ ] Cloisonnement des données vérifié pour chaque rôle
- [ ] Chaîne Note → ResultatMatiere → Bulletin fonctionnelle
- [ ] Export PDF bulletins opérationnel
- [ ] Aucune vue accessible sans authentification
- [ ] Compte `actif=False` bloqué à la connexion
- [ ] `HistoriqueActions` alimenté sur les actions sensibles

---

## 11. Conventions et règles à respecter

### Nommage

| Élément | Convention | Exemple |
|---|---|---|
| Modèles Django | PascalCase | `AnneeScolaire`, `ResultatMatiere` |
| Tables DB (`db_table`) | snake_case | `annee_scolaire`, `resultat_matiere` |
| Variables Python | snake_case | `moyenne_generale`, `date_fin` |
| URLs nommées | `namespace:vue` | `enseignant:saisir_note` |
| Templates | `app/nom_vue.html` | `enseignant/saisir_note.html` |
| Formulaires | `NomModelForm` | `NoteForm`, `InscriptionForm` |

### Règles d'intégrité — INTERDICTIONS ABSOLUES

- **JAMAIS** `DELETE` sur `Inscription` → utiliser `statut='transfere'` ou `'abandonne'` (RG-C08)
- **JAMAIS** `DELETE` sur `Personne` → utiliser `actif=False` (RG-A03)
- **JAMAIS** `INSERT` direct sur `ResultatMatiere` → calculé par signal uniquement (RG-M06)
- **JAMAIS** générer un `Bulletin` si `Periode.date_fin > date.today()` (RG-B02)
- **TOUJOURS** tracer les actions sensibles dans `HistoriqueActions` (RG-A06)

### Sécurité des vues — OBLIGATOIRE
- Toute vue doit avoir `@login_required` ou `LoginRequiredMixin` au minimum
- Toute vue sensible doit avoir `@role_required(...)` ou `RoleRequiredMixin`
- Filtrer **systématiquement** les querysets par propriétaire (`request.user`) ou par lien

---

## 12. Checklist d'avancement

### Phase A — Backend (modèles + auth)
- [ ] `Personne` (AbstractBaseUser) créé et migré
- [ ] 4 sous-entités (Personnel, Enseignant, Eleve, Parent) avec `clean()` d'exclusivité
- [ ] Toutes les 19 tables créées avec contraintes `Meta`
- [ ] Migrations exécutées sans erreur sur MariaDB
- [ ] Commande `init_groupes` exécutée
- [ ] Décorateurs `role_required` et `RoleRequiredMixin` opérationnels
- [ ] Signaux `post_save` sur Note et Absence testés
- [ ] Signal `pre_save` sur AnneeScolaire testé
- [ ] Admin Django configuré pour toutes les entités

### Phase B — Frontend (templates + vues)
- [ ] `base.html` avec Bootstrap 5 intégré et responsive
- [ ] Module 1 : Authentification (login / logout / dashboard)
- [ ] Module 2 : Espace PERSONNEL — gestion établissement
- [ ] Module 3 : Espace ENSEIGNANT — saisie pédagogique
- [ ] Module 4 : Espace PERSONNEL — bulletins et résultats
- [ ] Module 5 : Espace ÉLÈVE — consultation
- [ ] Module 6 : Espace PARENT — suivi enfants
- [ ] Module 7 : Notifications
- [ ] Export PDF bulletins

### Phase C — Tests et livraison
- [ ] Tests unitaires écrits et passants
- [ ] Jeu de données de démonstration chargé (`fixtures/`)
- [ ] Application fonctionnelle en local
- [ ] `README.md` rédigé (installation, lancement, comptes de test)

---

*ACADEMIQ V3 — Guide d'Implémentation — 16 avril 2026*  
*MARIKO Lamine · CI0223065023 · Master 1 Génie Informatique · Université Nangui Abrogoua*
