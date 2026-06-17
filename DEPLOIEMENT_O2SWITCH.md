# Déploiement d'ACADEMIQ sur O2Switch (cPanel)

Guide pas-à-pas pour mettre ACADEMIQ en ligne sur un hébergement mutualisé **O2Switch**,
avec **sous-domaine + base MySQL/MariaDB + application Python (Passenger)**.

> Profil ciblé : **accès SSH/Terminal disponible · Python 3.12 · base MySQL**.

---

## 0. Ce qui a déjà été préparé dans le code

| Fichier | Rôle |
|---|---|
| `academiq/academiq/settings.py` | Lit la config depuis des **variables d'environnement** (`.env`) : `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`, base de données, sécurité HTTPS. |
| `academiq/academiq/__init__.py` | Active **PyMySQL** comme connecteur MySQL (pas de compilation). |
| `academiq/academiq/urls.py` | Sert les médias (photos) même en production. |
| `academiq/passenger_wsgi.py` | Point d'entrée **Phusion Passenger** d'O2Switch. |
| `academiq/requirements-prod.txt` | Dépendances de production (sans outils de dev, sans compilation). |
| `academiq/.env.example` | Modèle de configuration à copier en `.env` sur le serveur. |

> ⚠️ La **racine de l'application Django** (celle qui contient `manage.py` et `passenger_wsgi.py`)
> est le dossier **`academiq/academiq`** (le dossier `academiq` *à l'intérieur* du dépôt).

---

## 1. Informations à rassembler avant de commencer

- [ ] Le **domaine** fourni par l'enseignant (ex. `mondomaine.fr`).
- [ ] Le **sous-domaine** souhaité (ex. `academiq` → `academiq.mondomaine.fr`).
- [ ] Tes identifiants **cPanel** O2Switch (et l'accès **SSH**).
- [ ] L'**URL du dépôt Git** du projet (ou les fichiers à téléverser).

---

## 2. Créer le sous-domaine (cPanel)

1. cPanel → **Domaines** (ou « Sous-domaines »).
2. **Créer un sous-domaine** : `academiq` sur `mondomaine.fr`.
3. Laisse le *Document Root* proposé par défaut (ex. `/home/TONCOMPTE/academiq.mondomaine.fr`).

> Le sous-domaine ne servira pas de dossier de fichiers : c'est Passenger qui répondra.
> Mais il doit exister pour pouvoir y rattacher l'application Python.

---

## 3. Créer la base de données MySQL/MariaDB (cPanel)

1. cPanel → **Bases de données MySQL®**.
2. **Créer une base** : ex. `academiq` → nom réel = `TONCOMPTE_academiq`.
3. **Créer un utilisateur** : ex. `academiq` → nom réel = `TONCOMPTE_academiq`, avec un **mot de passe fort**.
4. **Ajouter l'utilisateur à la base** avec **TOUS LES PRIVILÈGES**.

📝 Note bien : **nom de base**, **nom d'utilisateur** (tous deux préfixés par ton compte cPanel),
**mot de passe**. Ils iront dans le `.env`.

---

## 4. Créer l'application Python (cPanel → Setup Python App)

D'abord, **envoyer le code** par SSH (le dossier doit exister avant de créer l'app) :

```bash
# Connexion SSH (identifiants dans cPanel → « Accès SSH »)
ssh TONCOMPTE@mondomaine.fr

# Cloner le projet dans le dossier personnel
cd ~
git clone <URL_DU_DEPOT> academiq
```

> Après clonage, la racine Django est : `~/academiq/academiq`

Ensuite, dans cPanel → **Setup Python App** → **Create Application** :

| Champ | Valeur |
|---|---|
| **Python version** | `3.12` |
| **Application root** | `academiq/academiq` |
| **Application URL** | `academiq.mondomaine.fr` (le sous-domaine) |
| **Application startup file** | `passenger_wsgi.py` |
| **Application Entry point** | `application` |

Clique sur **Create**. cPanel crée alors un **environnement virtuel** dédié.

> 🔎 En haut de la page de l'app, cPanel affiche une commande du type
> `source /home/TONCOMPTE/virtualenv/academiq/academiq/3.12/bin/activate && cd /home/TONCOMPTE/academiq/academiq`
> **Copie-la** : elle active le venv + se place dans le dossier du projet.

> ⚠️ Si cPanel a écrasé `passenger_wsgi.py` avec un fichier vide, restaure son contenu
> (il est versionné dans le dépôt — un simple `git checkout passenger_wsgi.py` suffit).

---

## 5. Créer le fichier `.env` (secrets de production)

En SSH, place-toi dans la racine Django et crée le `.env` à partir du modèle :

```bash
cd ~/academiq/academiq
cp .env.example .env
nano .env
```

Génère une **clé secrète** unique (dans le venv activé — voir étape 6, ou avec le python système) :

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Remplis le `.env` :

```ini
DJANGO_SECRET_KEY=colle-ici-la-cle-generee
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=academiq.mondomaine.fr
DJANGO_CSRF_TRUSTED_ORIGINS=https://academiq.mondomaine.fr
DJANGO_SSL_REDIRECT=False        # passera à True après activation du SSL (étape 9)

DB_ENGINE=mysql
DB_NAME=TONCOMPTE_academiq
DB_USER=TONCOMPTE_academiq
DB_PASSWORD=le_mot_de_passe_de_la_base
DB_HOST=localhost
DB_PORT=3306
```

Enregistre (`Ctrl+O`, `Entrée`) et quitte (`Ctrl+X`).

---

## 6. Installer les dépendances dans le venv

Active le venv (commande copiée à l'étape 4), puis installe :

```bash
# Exemple — utilise TA commande exacte affichée par cPanel :
source /home/TONCOMPTE/virtualenv/academiq/academiq/3.12/bin/activate && cd /home/TONCOMPTE/academiq/academiq

pip install --upgrade pip
pip install -r requirements-prod.txt
```

> Aucune compilation : PyMySQL, WhiteNoise, Django, Pillow, ReportLab s'installent en quelques secondes.

---

## 7. Initialiser la base et les fichiers statiques

Toujours dans le venv activé, à la racine Django (`~/academiq/academiq`) :

```bash
python manage.py migrate
python manage.py init_groupes
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

Données de démonstration (optionnel, pour la soutenance) :

```bash
python create_demo_data.py
python create_notes_demo.py
```

> Le `.env` est lu automatiquement : `migrate` écrit donc directement dans MySQL.

---

## 8. Démarrer / redémarrer l'application

Deux possibilités :

- cPanel → Setup Python App → bouton **Restart**, **ou**
- en SSH :

```bash
mkdir -p ~/academiq/academiq/tmp && touch ~/academiq/academiq/tmp/restart.txt
```

Ouvre ensuite **http://academiq.mondomaine.fr** → la page de connexion ACADEMIQ doit s'afficher,
avec le **style Bootstrap** (preuve que WhiteNoise sert bien les fichiers statiques).

---

## 9. Activer le HTTPS (SSL)

1. cPanel → **SSL/TLS Status** (ou « Let's Encrypt® SSL »).
2. **Lancer AutoSSL** sur `academiq.mondomaine.fr` (certificat gratuit, automatique).
3. Une fois le cadenas actif, passe la redirection HTTPS dans `.env` :

```ini
DJANGO_SSL_REDIRECT=True
```

4. Redémarre l'application (étape 8).

---

## 10. Dépannage (erreurs fréquentes)

| Symptôme | Cause probable / Solution |
|---|---|
| **500 Internal Server Error** | Mets temporairement `DJANGO_DEBUG=True` dans `.env` + restart pour voir l'erreur. **Remets `False` ensuite.** Consulte aussi `~/academiq/academiq/stderr.log` ou les logs cPanel. |
| **DisallowedHost** | `DJANGO_ALLOWED_HOSTS` ne correspond pas exactement au sous-domaine. |
| **CSRF verification failed** (formulaires) | Vérifie `DJANGO_CSRF_TRUSTED_ORIGINS=https://...` (avec `https://`). |
| **Page sans style (CSS absent)** | Tu as oublié `collectstatic`, ou l'app n'a pas redémarré. |
| **Photos de profil non affichées** | Le dossier `media/` doit être accessible en écriture : `mkdir -p ~/academiq/academiq/media && chmod 755 ~/academiq/academiq/media`. |
| **Access denied for user (MySQL)** | Identifiants `.env` incorrects, ou utilisateur non rattaché à la base avec tous les privilèges. |
| **ModuleNotFoundError** | Le venv n'est pas activé / `pip install -r requirements-prod.txt` non exécuté. |
| **Modifications non prises en compte** | Toujours redémarrer (étape 8) après un changement de code ou de `.env`. |

---

## 11. Mettre à jour le site plus tard

```bash
cd ~/academiq/academiq
git pull
source /home/TONCOMPTE/virtualenv/academiq/academiq/3.12/bin/activate
pip install -r requirements-prod.txt        # si dépendances modifiées
python manage.py migrate                    # si nouvelles migrations
python manage.py collectstatic --noinput    # si statiques modifiés
touch tmp/restart.txt                        # redémarrer
```

---

*Guide de déploiement ACADEMIQ — O2Switch / cPanel / Passenger.*
