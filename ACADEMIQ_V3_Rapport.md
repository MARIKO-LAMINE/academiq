# ACADEMIQ V3
## Conception et Implémentation d'un Système Centralisé de Gestion des Activités Scolaires

---

**Étudiant :** MARIKO Lamine  
**Numéro de carte d'étudiant :** CI0223065023  
**Filière :** Master 1 — Génie Informatique  
**Université :** Nangui Abrogoua  
**Encadreur :** Dr. ZEZE  
**Année universitaire :** 2025–2026  
**Date de soutenance :** Juin 2026

---

## Dédicace

*À ma famille, pour son soutien indéfectible tout au long de ce parcours académique.*

---

## Remerciements

Mes remerciements vont en premier lieu à **Dr. ZEZE**, mon encadreur, pour sa disponibilité, ses conseils avisés et son suivi rigoureux tout au long de ce projet. Sa rigueur scientifique et ses orientations ont été déterminantes dans la réussite de ce travail.

Je remercie également l'ensemble du corps enseignant du département de Génie Informatique de l'**Université Nangui Abrogoua** pour la qualité des enseignements dispensés au cours de ces deux années de Master.

Enfin, je remercie mes camarades de promotion pour les échanges constructifs et l'entraide qui ont marqué cette année universitaire.

---

## Résumé

Les établissements d'enseignement secondaire en Côte d'Ivoire font face à une gestion administrative fragmentée : les notes sont consignées dans des cahiers, les absences sur des fiches papier, les bulletins produits manuellement et les communications internes transmises oralement. Cette dispersion entraîne des erreurs, des délais et une traçabilité insuffisante.

**ACADEMIQ V3** est un système d'information centralisé développé pour répondre à ces problèmes. Il couvre l'intégralité du cycle de vie scolaire : inscription des élèves, planification des cours, saisie des notes, gestion des absences, génération automatique des bulletins, suivi financier et communication interne.

Le système repose sur un backend **Django 4.x** (Python), une base de données **MariaDB** respectant la troisième forme normale, une interface **Bootstrap 5** responsive, et une architecture orientée rôles (7 groupes d'utilisateurs aux droits strictement cloisonnés). Il intègre des mécanismes de calcul automatique des moyennes et des rangs via des signaux applicatifs, ainsi qu'un export PDF des bulletins.

Ce rapport présente la démarche méthodologique adoptée — analyse des besoins, modélisation Merise (MLD, MPD), puis implémentation — et détaille les choix techniques et architecturaux effectués.

**Mots-clés :** système d'information scolaire, Django, MariaDB, Merise, gestion des notes, bulletins, Bootstrap 5, contrôle d'accès par rôle.

---

## Abstract

Secondary schools in Côte d'Ivoire face fragmented administrative management: grades are recorded in notebooks, absences on paper forms, report cards produced manually, and internal communications conveyed orally. This fragmentation leads to errors, delays and insufficient traceability.

**ACADEMIQ V3** is a centralised information system developed to address these issues. It covers the complete school lifecycle: student enrolment, course scheduling, grade entry, absence management, automatic report card generation, financial tracking and internal communication.

The system is built on a **Django 4.x** (Python) backend, a **MariaDB** database normalised to third normal form, a responsive **Bootstrap 5** interface, and a role-based architecture (7 strictly isolated user groups). It incorporates automatic average and rank calculation through application signals, as well as PDF export of report cards.

This report presents the methodological approach adopted — requirements analysis, Merise modelling (LDM, PDM), then implementation — and details the technical and architectural choices made.

**Keywords:** school information system, Django, MariaDB, Merise, grade management, report cards, Bootstrap 5, role-based access control.

---

## Table des matières

1. [Introduction générale](#1-introduction-générale)
2. [Chapitre 1 — Analyse et spécification des besoins](#chapitre-1--analyse-et-spécification-des-besoins)
3. [Chapitre 2 — Conception du système](#chapitre-2--conception-du-système)
4. [Chapitre 3 — Implémentation et développement](#chapitre-3--implémentation-et-développement)
5. [Chapitre 4 — Tests, validation et résultats](#chapitre-4--tests-validation-et-résultats)
6. [Conclusion et perspectives](#6-conclusion-et-perspectives)
7. [Bibliographie et webographie](#7-bibliographie-et-webographie)
8. [Annexes](#8-annexes)

---

## 1. Introduction générale

### 1.1 Contexte

L'école joue un rôle central dans le développement économique et social d'une nation. En Côte d'Ivoire, le système éducatif secondaire regroupe des centaines d'établissements publics et privés accueillant des milliers d'élèves chaque année. Malgré cette envergure, la gestion interne de ces établissements reste majoritairement manuelle ou partiellement informatisée : les informations sont éparpillées entre des tableurs Excel, des registres papier et des logiciels métier incompatibles entre eux.

Cette réalité engendre plusieurs problèmes concrets :

- **Erreurs de saisie** lors de la retranscription manuelle des notes sur les bulletins ;
- **Pertes d'information** en cas de perte de documents physiques ;
- **Délais de production** des bulletins, parfois distribués plusieurs semaines après la clôture des périodes ;
- **Absence de traçabilité** sur les modifications apportées aux données sensibles ;
- **Cloisonnement** de l'information entre les services (pédagogie, scolarité, finances) ;
- **Communication interne déficiente**, reposant sur des canaux informels.

### 1.2 Problématique

Comment concevoir et implémenter un système d'information centralisé qui permette à tous les acteurs d'un établissement scolaire — direction, personnel administratif, enseignants, élèves et parents — d'accéder à l'information dont ils ont besoin, au moment où ils en ont besoin, dans le respect strict de leurs attributions respectives ?

Cette problématique soulève trois enjeux fondamentaux :

1. **L'enjeu fonctionnel :** le système doit couvrir tous les processus métier de l'établissement, de l'inscription à la remise du bulletin ;
2. **L'enjeu de sécurité :** chaque acteur ne doit accéder qu'aux données relevant de son périmètre ; aucune donnée sensible ne doit être exposée à un utilisateur non habilité ;
3. **L'enjeu technique :** le système doit être fiable, maintenable et deployable dans un environnement aux ressources informatiques limitées.

### 1.3 Objectifs du projet

L'objectif principal est de développer **ACADEMIQ V3**, un système d'information scolaire complet répondant aux besoins identifiés. Les objectifs spécifiques sont :

- Modéliser la base de données selon la méthode Merise jusqu'au Modèle Physique de Données (MPD) ;
- Implémenter le backend avec Django 4.x et MariaDB ;
- Développer une interface web responsive avec Bootstrap 5 ;
- Garantir un contrôle d'accès strict par rôle (7 groupes d'utilisateurs) ;
- Automatiser les calculs de moyennes, de rangs et de bulletins ;
- Produire des bulletins exportables en PDF.

### 1.4 Plan du rapport

Ce rapport est organisé en quatre chapitres. Le **Chapitre 1** présente l'analyse des besoins et la spécification fonctionnelle. Le **Chapitre 2** détaille la conception de la base de données et l'architecture logicielle. Le **Chapitre 3** décrit l'implémentation technique, les choix effectués et les mécanismes développés. Le **Chapitre 4** présente les tests, la validation et les résultats obtenus. Une conclusion générale clôt le rapport.

---

## Chapitre 1 — Analyse et spécification des besoins

### 1.1 Présentation du domaine

Un établissement d'enseignement secondaire est une organisation complexe qui rassemble plusieurs services aux responsabilités distinctes mais interdépendantes. Pour comprendre les besoins du système, nous avons procédé à une analyse fonctionnelle du domaine scolaire, en identifiant les processus métier et les acteurs impliqués.

Les processus couverts par ACADEMIQ V3 sont :

| Processus | Description |
|---|---|
| Gestion de l'année scolaire | Création des années, des périodes (trimestres/semestres), activation |
| Gestion de l'établissement | Classes, salles, matières, cours, emplois du temps |
| Inscriptions | Inscription, transfert, abandon d'élèves |
| Évaluation | Saisie des notes, calcul des moyennes, calcul des rangs |
| Absences | Enregistrement, validation, suivi du seuil d'alerte |
| Bulletins | Génération à la clôture de période, export PDF |
| Finances | Tarification, suivi des frais de scolarité, enregistrement des paiements |
| Communication | Messagerie privée, annonces, calendrier scolaire, notifications |
| Sécurité | Authentification, contrôle d'accès, historique des actions |

### 1.2 Identification des acteurs

L'analyse a permis d'identifier sept (7) catégories d'acteurs, chacune correspondant à un rôle fonctionnel distinct :

| Acteur | Désignation | Périmètre d'action |
|---|---|---|
| DIRECTION | Direction de l'établissement | Accès total, gestion des comptes et des années scolaires |
| ADMINISTRATION | Service administratif | Gestion pédagogique (cours, EDT, salles, matières) |
| SCOLARITE | Service de scolarité | Inscriptions, absences, bulletins |
| FINANCES | Service financier | Tarifs, frais de scolarité, paiements |
| ENSEIGNANT | Corps enseignant | Saisie notes et absences de ses cours, validation absences |
| ELEVE | Élèves | Consultation de son dossier personnel |
| PARENT | Parents / tuteurs | Consultation du dossier de leurs enfants |

Les quatre premiers acteurs constituent le **personnel administratif** et partagent un espace de travail commun, avec des droits différenciés selon leur service.

### 1.3 Spécification fonctionnelle

#### 1.3.1 Gestion des années scolaires et périodes

L'établissement fonctionne par années scolaires (ex. : 2025–2026). Chaque année est découpée en périodes évaluatives — trimestres ou semestres selon le cycle. Une seule année peut être active à la fois. La clôture d'une période déclenche la possibilité de générer les bulletins correspondants.

#### 1.3.2 Gestion pédagogique

Un cours est défini comme l'intersection d'une matière, d'une classe, d'un enseignant et d'une année scolaire. L'emploi du temps planifie les cours dans des créneaux horaires (jour, heure début/fin, salle). Le système doit détecter les conflits : un même enseignant ne peut pas être affecté à deux créneaux simultanés, et une même salle ne peut pas accueillir deux cours en même temps.

#### 1.3.3 Saisie des notes et calcul des moyennes

Chaque note est saisie par l'enseignant titulaire du cours, pour un élève, dans une période donnée. Elle est caractérisée par sa valeur (entre 0 et 20), son type d'évaluation (devoir surveillé, interrogation, examen semestriel) et la date de saisie. Dès qu'une note est enregistrée, la moyenne de l'élève pour ce cours et cette période est automatiquement recalculée, ainsi que son rang parmi les autres élèves du cours.

#### 1.3.4 Gestion des absences

L'enregistrement des absences relève de l'enseignant pour ses propres cours. Chaque absence comporte le nombre d'heures manquées, un statut (en attente, justifiée, non justifiée) et un motif facultatif. La validation du statut (justifiée / non justifiée) est de la compétence de l'enseignant titulaire, avec possibilité de régularisation par la scolarité. Une alerte automatique est déclenchée lorsque le cumul d'heures non justifiées dépasse 20 heures sur la période.

#### 1.3.5 Génération des bulletins

Le bulletin est généré après clôture d'une période. Il est propre à chaque élève et consigne sa moyenne générale (pondérée par les coefficients des matières), son rang dans la classe et les résultats détaillés par matière. Une fois généré, il est immuable. Il est exportable en PDF par le personnel habilité, l'élève lui-même et ses parents.

#### 1.3.6 Suivi financier

Les frais de scolarité sont définis par niveau et par année. Chaque élève inscrit se voit créer un dossier financier. Les paiements sont enregistrés avec leur mode (espèces, virement, mobile money) et un numéro de reçu unique. Le statut du dossier (en attente, partiellement payé, payé) est recalculé automatiquement à chaque paiement. La DIRECTION et le service FINANCES peuvent exporter le bilan financier de l'année en PDF.

#### 1.3.7 Communication interne

Le système intègre trois canaux de communication :

- **Messagerie privée :** communication individuelle entre utilisateurs, avec pièce jointe PDF optionnelle. Les règles de filtrage permettent à un ENSEIGNANT d'écrire à tout utilisateur actif (y compris les élèves), tandis qu'un ELEVE ou un PARENT ne peut écrire qu'au personnel et aux enseignants.
- **Annonces :** publiées par le personnel, visibles par toute la communauté scolaire. Les enseignants peuvent les consulter en lecture seule.
- **Calendrier scolaire :** événements scolaires (vacances, examens, jours fériés) consultables par tous.

### 1.4 Contraintes et exigences non fonctionnelles

| Type | Contrainte |
|---|---|
| Sécurité | Authentification obligatoire, hachage bcrypt des mots de passe |
| Cloisonnement | Chaque utilisateur n'accède qu'aux données de son périmètre |
| Traçabilité | Toute action sensible est horodatée et enregistrée |
| Intégrité | Suppression logique uniquement (jamais physique pour les entités métier) |
| Disponibilité | Accessible depuis un navigateur web standard, sans installation côté client |
| Maintenabilité | Code structuré en applications Django indépendantes par rôle |
| Portabilité | Déployable sur tout serveur Linux ou Windows disposant de Python 3.10+ |

---

## Chapitre 2 — Conception du système

### 2.1 Choix méthodologique : la méthode Merise

La conception de la base de données a été conduite selon la **méthode Merise**, méthode d'analyse et de conception des systèmes d'information développée en France dans les années 1970 et encore largement enseignée dans les filières informatiques francophones. Elle offre une démarche structurée en trois niveaux de modélisation :

1. Le **Modèle Conceptuel de Données (MCD)** — représentation sémantique des entités et de leurs associations, indépendante de toute technologie ;
2. Le **Modèle Logique de Données (MLD)** — traduction du MCD en tables relationnelles avec clés primaires et étrangères ;
3. Le **Modèle Physique de Données (MPD)** — script SQL de création des tables, adapté au SGBD cible (MariaDB).

Cette démarche garantit une conception rigoureuse et normalisée, indépendante des contraintes d'implémentation lors des premières phases d'analyse.

### 2.2 Architecture générale du système

ACADEMIQ V3 suit une architecture **client-serveur web classique** à trois couches :

```
┌─────────────────────────────────────────────────────────┐
│  COUCHE PRÉSENTATION                                    │
│  Navigateur web — HTML5, CSS3, Bootstrap 5, Chart.js   │
└────────────────────────┬────────────────────────────────┘
                         │ HTTP / HTTPS
┌────────────────────────▼────────────────────────────────┐
│  COUCHE APPLICATIVE                                     │
│  Django 4.x (Python 3.10+)                             │
│  · Routage URLs (namespace par app)                     │
│  · Vues FBV + décorateurs de permissions               │
│  · Templates Django (rendu HTML côté serveur)          │
│  · Signaux post_save (calculs automatiques)            │
│  · ReportLab (génération PDF)                          │
└────────────────────────┬────────────────────────────────┘
                         │ ORM Django
┌────────────────────────▼────────────────────────────────┐
│  COUCHE DONNÉES                                         │
│  MariaDB 10.x / InnoDB                                 │
│  · 24 tables, 95 attributs, 38 clés étrangères        │
│  · Contraintes UNIQUE, CHECK, FK avec ON DELETE        │
│  · Normalisation 3FN                                   │
└─────────────────────────────────────────────────────────┘
```

Ce choix d'architecture **monolithique** (par opposition à une API REST + frontend séparé) s'est imposé pour plusieurs raisons :

- **Simplicité de déploiement :** un seul processus serveur à gérer ;
- **Rendu côté serveur :** performances satisfaisantes pour un usage intranet d'établissement ;
- **Maîtrise technologique :** correspond aux compétences maîtrisées et à l'environnement d'enseignement ;
- **Pas de surcharge d'ingénierie :** évite la complexité d'une architecture découplée (CORS, tokens JWT, etc.) non justifiée pour ce cas d'usage.

### 2.3 Structure des applications Django

Le projet est organisé en six applications Django à responsabilités distinctes :

| Application | Rôle | Groupes servis |
|---|---|---|
| `core` | Modèles, signaux, permissions — noyau métier | Tous |
| `accounts` | Authentification, login, logout, redirection post-login | Tous |
| `personnel` | Espace de travail du personnel administratif | DIRECTION, ADMIN, SCOLARITE, FINANCES |
| `enseignant` | Espace de travail des enseignants | ENSEIGNANT |
| `eleve` | Espace de consultation des élèves | ELEVE |
| `parent` | Espace de suivi des parents | PARENT |

Chaque application possède ses propres vues, URLs (avec namespace), formulaires et templates. Cette séparation garantit l'isolation du code et simplifie l'évolution indépendante de chaque espace.

### 2.4 Modèle de données

#### 2.4.1 Entités principales et relations

Le modèle de données comporte **24 tables** regroupées en six domaines fonctionnels :

**Domaine Référentiel**

La table centrale est `PERSONNE`, qui matérialise le modèle utilisateur personnalisé (AbstractBaseUser Django). Elle est déclinée en quatre sous-entités exclusives — `PERSONNEL`, `ENSEIGNANT`, `ELEVE`, `PARENT` — liées par des relations OneToOneField. Cette exclusivité est garantie par une méthode `clean()` Django qui interdit qu'une personne appartienne à deux rôles simultanément.

```
PERSONNE (id, nom, prenom, email, password_hash, photo_profil, actif, date_creation)
    ├── PERSONNEL    (personne_id PK=FK, fonction, date_embauche)
    ├── ENSEIGNANT   (personne_id PK=FK, specialite, grade, date_embauche)
    ├── ELEVE        (personne_id PK=FK, date_naissance, lieu_naissance, matricule)
    └── PARENT       (personne_id PK=FK, telephone, profession)
```

**Domaine Pédagogique**

```
ANNEE_SCOLAIRE (id, libelle, date_debut, date_fin, active)
PERIODE        (id, nom, type_periode, date_debut, date_fin, cloturee, #annee_id)
CLASSE         (id, nom, niveau, cycle, section, effectif_max, #annee_id)
MATIERE        (id, nom_matiere, coefficient, description)
SALLE          (id, numero, batiment, capacite, type_salle)
COURS          (id, nb_heures_hebdo, #matiere_id, #classe_id, #enseignant_id, #annee_id)
EMPLOI_DU_TEMPS(id, jour, heure_debut, heure_fin, #cours_id, #salle_id, #periode_id)
```

**Domaine Scolarité**

```
INSCRIPTION     (id, date_inscription, statut, #eleve_id, #classe_id, #annee_id)
LIEN_PARENT_ELEVE(id, lien, #parent_id, #eleve_id)
```

**Domaine Évaluation**

```
NOTE            (id, valeur, type_eval, commentaire, date_saisie, #eleve_id, #cours_id, #periode_id)
RESULTAT_MATIERE(id, moyenne, rang, #eleve_id, #cours_id, #periode_id)
BULLETIN        (id, moyenne_generale, rang, effectif_classe, appreciation, date_generation,
                 #eleve_id, #periode_id)
ABSENCE         (id, date_absence, nb_heures, statut, motif, date_saisie, #eleve_id, #cours_id, #periode_id)
```

**Domaine Finances**

```
TARIF_NIVEAU    (id, niveau, montant, date_echeance, #annee_id)
FRAIS_SCOLARITE (id, montant_du, montant_paye, statut, date_echeance, date_maj, #eleve_id, #annee_id)
PAIEMENT        (id, montant, date_paiement, recu_numero, mode, #frais_id, #saisi_par_id)
```

**Domaine Communication et Sécurité**

```
NOTIFICATION    (id, message, type_notif, lu, date_envoi, #destinataire_id, #classe_id)
MESSAGE         (id, sujet, corps, lu, date_envoi, piece_jointe, #expediteur_id, #destinataire_id)
EVENEMENT_SCOLAIRE(id, titre, description, type_event, date_debut, date_fin, #annee_id, #createur_id)
HISTORIQUE_ACTIONS(id, action, table_cible, id_enreg, details, date_action, #auteur_id)
```

#### 2.4.2 Contraintes d'intégrité

Le modèle impose plusieurs contraintes garantissant la cohérence des données :

| Contrainte | Table | Règle |
|---|---|---|
| UNIQUE (eleve, annee) | INSCRIPTION | Un élève ne peut être inscrit qu'une fois par année |
| UNIQUE (eleve, cours, periode) | RESULTAT_MATIERE | Un seul résultat par élève, cours et période |
| UNIQUE (eleve, periode) | BULLETIN | Un seul bulletin par élève et par période |
| UNIQUE (annee, niveau) | TARIF_NIVEAU | Un seul tarif par niveau et par année |
| UNIQUE (eleve, annee) | FRAIS_SCOLARITE | Un seul dossier financier par élève et par année |
| CHECK (valeur BETWEEN 0 AND 20) | NOTE | Valeur de note dans l'intervalle légal |
| UNIQUE (recu_numero) | PAIEMENT | Numéro de reçu unique dans toute la base |

#### 2.4.3 Normalisation

Le modèle respecte la **troisième forme normale (3FN)** :

- **1FN :** Tous les attributs sont atomiques ; aucun attribut multi-valué.
- **2FN :** Tout attribut non-clé dépend de la totalité de la clé primaire. Les tables à clé composite (RESULTAT_MATIERE, BULLETIN) ont été vérifiées en ce sens.
- **3FN :** Aucune dépendance transitive. Par exemple, `statut` de FRAIS_SCOLARITE n'est pas stocké statiquement mais recalculé dynamiquement depuis `montant_paye` et `montant_du`.

### 2.5 Architecture des permissions

Le contrôle d'accès repose sur le système de **groupes Django**. Chaque utilisateur appartient à exactement un groupe parmi les sept définis. L'accès à chaque vue est protégé par un décorateur `@role_required(*roles)` ou le mixin `RoleRequiredMixin` pour les vues orientées classe.

Une innovation importante introduite lors de l'implémentation concerne la gestion des accès non autorisés : plutôt qu'afficher une erreur HTTP 403 (incompréhensible pour un utilisateur non technique), tout accès refusé produit un **message d'erreur explicite et une redirection intelligente** vers le tableau de bord de l'utilisateur connecté.

```python
def _redirect_to_dashboard(request):
    """Redirige vers le bon dashboard selon le rôle, avec message d'erreur."""
    messages.error(request, "Vous n'avez pas accès à cette page.")
    groups = list(request.user.groups.values_list('name', flat=True))
    if any(g in groups for g in ('DIRECTION', 'ADMINISTRATION', 'SCOLARITE', 'FINANCES')):
        return redirect('personnel:dashboard')
    if 'ENSEIGNANT' in groups:
        return redirect('enseignant:dashboard')
    if 'ELEVE' in groups:
        return redirect('eleve:dashboard')
    if 'PARENT' in groups:
        return redirect('parent:dashboard')
    return redirect('accounts:login')
```

---

## Chapitre 3 — Implémentation et développement

### 3.1 Environnement technique

| Composant | Technologie | Version | Rôle |
|---|---|---|---|
| Langage backend | Python | 3.10+ | Logique métier, ORM |
| Framework web | Django | 4.x | Routing, vues, templates, auth |
| Base de données | MariaDB / InnoDB | 10.x | Stockage persistant, contraintes SQL |
| Frontend | Bootstrap 5 + Bootstrap Icons | 5.3 | Interface responsive |
| Génération PDF | ReportLab | 4.x | Export bulletins en PDF |
| Graphiques | Chart.js | 4.x | Visualisations dans les dashboards |
| Authentification | Django Auth | — | Sessions, bcrypt, groupes |

### 3.2 Modèle utilisateur personnalisé

L'un des premiers choix techniques structurants a été l'utilisation d'un modèle utilisateur personnalisé (`AbstractBaseUser`) à la place du `User` standard de Django. Ce choix s'est imposé pour trois raisons :

1. **Identifiant de connexion :** dans un établissement scolaire, l'email est un identifiant plus naturel et universel que le `username` proposé par défaut ;
2. **Champs supplémentaires :** la nécessité d'ajouter `nom`, `prenom`, `photo_profil` et `actif` directement sur l'entité utilisateur ;
3. **Unicité de la table :** regrouper toutes les personnes (personnel, enseignants, élèves, parents) dans une seule table `personne` simplifie les jointures et la messagerie.

Ce choix devant être fait avant la première migration, il constituait un point critique de la phase de démarrage.

### 3.3 Mécanisme des signaux Django

Les signaux Django représentent l'un des mécanismes les plus importants du système. Ils permettent d'exécuter automatiquement de la logique métier en réponse à des événements (création ou modification d'un enregistrement), sans que l'appelant (la vue) n'ait à s'en préoccuper.

#### 3.3.1 Signal post_save sur Note — Calcul des moyennes et rangs

Chaque fois qu'une note est créée ou modifiée, un signal déclenche :

1. Le **recalcul de la moyenne** de l'élève pour ce cours et cette période :

```python
moyenne = Note.objects.filter(
    eleve=instance.eleve,
    cours=instance.cours,
    periode=instance.periode
).aggregate(Avg('valeur'))['valeur__avg']

ResultatMatiere.objects.update_or_create(
    eleve=instance.eleve, cours=instance.cours, periode=instance.periode,
    defaults={'moyenne': moyenne}
)
```

2. Le **recalcul des rangs** pour tous les élèves du même cours et de la même période :

```python
resultats_cours = list(
    ResultatMatiere.objects.filter(
        cours=instance.cours, periode=instance.periode
    ).order_by('-moyenne')
)
for rang, res in enumerate(resultats_cours, start=1):
    res.rang = rang
ResultatMatiere.objects.bulk_update(resultats_cours, ['rang'])
```

Ce mécanisme garantit que les rangs sont toujours cohérents après chaque saisie, sans intervention manuelle.

#### 3.3.2 Signal pre_save sur AnneeScolaire — Unicité de l'année active

Lors de l'activation d'une année scolaire, un signal `pre_save` désactive automatiquement toute autre année précédemment active, garantissant l'unicité de l'année courante.

#### 3.3.3 Limitation identifiée : bulk_create et signaux

Un problème a été identifié lors du développement de la commande de peuplement des données de démo (`populate_data`). La méthode `bulk_create` de Django, utilisée pour des raisons de performance, ne déclenche **pas** les signaux `post_save`. Les rangs n'étaient donc pas calculés lors de l'initialisation.

La solution adoptée a été d'appeler explicitement le calcul des rangs après chaque `bulk_create`, en utilisant `itertools.groupby` pour regrouper les résultats par cours avant d'effectuer la mise à jour :

```python
from itertools import groupby
all_rm = list(ResultatMatiere.objects.filter(periode=t1).order_by('cours_id', '-moyenne'))
to_update = []
for _, group in groupby(all_rm, key=lambda r: r.cours_id):
    for rang, res in enumerate(list(group), start=1):
        res.rang = rang
        to_update.append(res)
ResultatMatiere.objects.bulk_update(to_update, ['rang'])
```

### 3.4 Génération des bulletins PDF

La génération des bulletins PDF utilise la bibliothèque **ReportLab**. Chaque bulletin est produit directement en mémoire (`io.BytesIO`) et retourné comme réponse HTTP avec le type MIME `application/pdf`, sans stockage intermédiaire sur le disque.

Le bulletin PDF contient :
- L'en-tête de l'établissement avec le nom de l'élève, la classe et la période ;
- Un tableau des résultats par matière avec la note, la moyenne, le rang et le coefficient ;
- La moyenne générale pondérée et le rang dans la classe ;
- L'appréciation globale.

### 3.5 Interface utilisateur

#### 3.5.1 Templates de base par rôle

L'interface est construite autour de quatre templates de base, un par espace utilisateur :

| Template | Utilisateurs | Sidebar |
|---|---|---|
| `base_personnel.html` | DIRECTION, ADMIN, SCOLARITE, FINANCES | Liens filtrés par groupe |
| `base_enseignant.html` | ENSEIGNANT | Liens espace enseignant |
| `base_eleve.html` | ELEVE | Liens espace élève |
| `base_parent.html` | PARENT | Liens espace parent |

Cette séparation en quatre templates distincts garantit qu'un utilisateur ne verra jamais une interface destinée à un autre rôle, même en cas de redirection accidentelle.

#### 3.5.2 Tableaux de bord

Chaque rôle dispose d'un tableau de bord personnalisé affichant les indicateurs pertinents. Le tableau de bord de l'ENSEIGNANT, par exemple, présente :

- Le nombre de cours, de notes saisies et d'absences enregistrées ;
- Un graphique en barres (Chart.js) des moyennes par cours ;
- Un graphique en secteurs de la répartition des notes par tranches (< 8, 8-10, 10-14, ≥ 14).

#### 3.5.3 Messagerie avec recherche dynamique

Le module de messagerie a nécessité une attention particulière sur l'ergonomie du sélecteur de destinataires. Avec potentiellement plusieurs centaines d'utilisateurs, un simple `<select>` déroulant est peu pratique.

La solution retenue est un **sélecteur hybride** : une barre de recherche texte combinée à un `<select>` avec `<optgroup>` pour le groupement par rôle, reconstruit dynamiquement en JavaScript sans rechargement de page :

```javascript
const DEST_DATA = [ /* {v: pk, t: nom_complet, g: role} */ ];

function rebuildSelect(query) {
    const sel = document.getElementById('selectDest');
    const q = query.toLowerCase().trim();
    sel.innerHTML = '<option value="">— Choisir un destinataire —</option>';
    const groups = {};
    DEST_DATA.forEach(d => {
        if (!q || d.t.toLowerCase().includes(q)) {
            if (!groups[d.g]) groups[d.g] = [];
            groups[d.g].push(d);
        }
    });
    Object.keys(groups).forEach(grp => {
        const og = document.createElement('optgroup');
        og.label = grp;
        groups[grp].forEach(d => {
            const o = document.createElement('option');
            o.value = d.v; o.textContent = d.t;
            og.appendChild(o);
        });
        sel.appendChild(og);
    });
}
```

Les données sont injectées dans la page via un tableau JSON généré côté serveur, évitant ainsi un appel AJAX supplémentaire.

### 3.6 Points techniques notables

#### 3.6.1 Cloisonnement des données

Le cloisonnement ne repose pas uniquement sur les permissions de vue, mais aussi sur le **filtrage systématique des querysets** :

- Un ENSEIGNANT ne peut accéder qu'aux cours dont il est le titulaire (`Cours.objects.filter(enseignant=request.user)`) ;
- Un ELEVE ne voit que ses propres notes et absences (`Note.objects.filter(eleve=request.user)`) ;
- Un PARENT ne voit que les données des enfants qui lui sont liés via `LIEN_PARENT_ELEVE`.

#### 3.6.2 Commande de peuplement des données

Pour les besoins de démonstration, une commande de gestion Django personnalisée (`python manage.py populate_data`) génère un jeu de données réaliste :

- 1 année scolaire active avec 2 trimestres ;
- 5 classes de différents niveaux ;
- 8 matières avec coefficients ;
- 30 élèves, 5 enseignants, 10 parents ;
- 840 résultats par matière avec moyennes et rangs calculés ;
- Des absences et des paiements de démonstration.

#### 3.6.3 Gestion des périodes clôturées

Le système interdit la saisie de notes pour une période dont la date de fin est dépassée ou dont l'indicateur `cloturee` est actif. Cette vérification est effectuée dans la vue avant validation du formulaire, garantissant l'intégrité des bulletins déjà générés.

### 3.7 Structure du projet

```
academiq/
├── academiq/          ← Configuration Django (settings, urls, wsgi)
├── core/              ← Modèles, signaux, permissions, admin
│   ├── models.py      ← 24 entités métier
│   ├── signals.py     ← Calcul moyennes, rangs, notifications
│   ├── permissions.py ← role_required, RoleRequiredMixin, _redirect_to_dashboard
│   └── management/commands/populate_data.py
├── accounts/          ← Login, logout, redirection post-login
├── personnel/         ← Espace PERSONNEL (vues, forms, templates)
├── enseignant/        ← Espace ENSEIGNANT
├── eleve/             ← Espace ELEVE
├── parent/            ← Espace PARENT
├── templates/         ← Templates globaux (bases, partials)
└── static/            ← CSS, JS, images
```

---

## Chapitre 4 — Tests, validation et résultats

### 4.1 Stratégie de test

La validation du système a été conduite à travers trois niveaux de vérification :

1. **Tests fonctionnels manuels :** parcours complet de chaque flux métier avec les comptes de démonstration, pour chacun des 7 rôles ;
2. **Tests d'intégrité des données :** vérification directe en base de données après les opérations critiques ;
3. **Tests de cloisonnement :** tentatives d'accès croisé entre rôles pour vérifier que les restrictions sont bien appliquées.

### 4.2 Comptes de démonstration

| Rôle | Email | Mot de passe |
|---|---|---|
| DIRECTION | direction@academiq.ci | academiq2026 |
| SCOLARITE | scolarite@academiq.ci | academiq2026 |
| FINANCES | finances@academiq.ci | academiq2026 |
| ENSEIGNANT | prof.koné@academiq.ci | academiq2026 |
| ELEVE | eleve1@academiq.ci | academiq2026 |
| PARENT | parent1@academiq.ci | academiq2026 |

### 4.3 Résultats des tests fonctionnels

#### 4.3.1 Flux d'authentification

| Scénario | Résultat |
|---|---|
| Connexion avec email + mot de passe valides | Redirection vers le bon dashboard selon le rôle |
| Connexion avec compte désactivé (actif=False) | Connexion refusée, message d'erreur |
| Accès à une vue sans être connecté | Redirection vers la page de login |
| Accès à une vue d'un autre rôle | Message d'erreur + redirection vers son propre dashboard |

#### 4.3.2 Flux de saisie des notes et calcul automatique

| Scénario | Résultat |
|---|---|
| Saisie d'une note valide (0-20) | Note enregistrée, moyenne recalculée immédiatement |
| Saisie d'une note hors intervalle | Formulaire rejeté avec message d'erreur |
| Saisie de plusieurs notes pour le même cours | Rang recalculé automatiquement pour tous les élèves |
| Consultation du bulletin | Rang par matière affiché correctement |
| Saisie de note pour une période clôturée | Saisie bloquée avec message explicite |

#### 4.3.3 Flux des absences

| Scénario | Résultat |
|---|---|
| Enregistrement d'une absence par l'enseignant | Statut initial "en attente", notification envoyée à l'élève et au parent |
| Validation justifiée par l'enseignant titulaire | Statut mis à jour, visible dans l'espace élève et parent |
| Tentative de validation par un enseignant tiers | Accès refusé (vérification de propriété du cours) |
| Cumul d'absences dépassant 20h | Notification automatique à la scolarité et aux parents |

#### 4.3.4 Flux financier

| Scénario | Résultat |
|---|---|
| Création d'un dossier de frais | Statut "en attente" |
| Enregistrement d'un paiement partiel | Statut → "partiellement payé", montant_paye recalculé |
| Enregistrement du solde | Statut → "payé" |
| Export PDF du bilan financier (DIRECTION) | PDF généré avec récapitulatif complet |

#### 4.3.5 Flux messagerie

| Scénario | Résultat |
|---|---|
| Envoi d'un message avec pièce jointe PDF | Message reçu, pièce jointe téléchargeable |
| Tentative d'envoi avec fichier non-PDF | Rejet avec message d'erreur |
| Recherche d'un destinataire par nom | Filtrage dynamique sans rechargement de page |
| ENSEIGNANT écrit à un ELEVE | Autorisé (destinataire visible dans la liste) |
| ELEVE tente d'écrire à un autre ELEVE | Destinataire absent de la liste |

### 4.4 Tests d'intégrité

Après exécution de `populate_data`, les vérifications directes en base ont confirmé :

| Vérification | Valeur attendue | Résultat |
|---|---|---|
| Nombre de ResultatMatiere avec rang calculé | 840 / 840 | Conforme |
| Nombre d'élèves avec rang NULL | 0 | Conforme |
| Unicité des bulletins (eleve, periode) | Aucun doublon | Conforme |
| Unicité des numéros de reçu | Aucun doublon | Conforme |
| Contrainte CHECK [0;20] sur les notes | Violation impossible | Conforme |

### 4.5 Bilan des fonctionnalités livrées

| Module | Statut | Remarques |
|---|---|---|
| Authentification et contrôle d'accès | Complet | 7 rôles, redirections intelligentes |
| Gestion années / périodes / classes | Complet | Signal unicité année active |
| Gestion cours et emplois du temps | Complet | Détection conflits de créneaux |
| Inscriptions élèves | Complet | Suppression logique uniquement |
| Saisie notes + calcul moyennes/rangs | Complet | Calcul automatique via signal |
| Gestion absences + validation | Complet | Enseignant valide ses propres cours |
| Génération bulletins + export PDF | Complet | ReportLab, immuabilité après clôture |
| Suivi financier + bilan PDF | Complet | Accessible FINANCES + DIRECTION |
| Messagerie + pièces jointes | Complet | Recherche, groupes, filtrage par rôle |
| Annonces et calendrier scolaire | Complet | Lecture seule pour ENSEIGNANT |
| Notifications automatiques | Complet | Notes, absences, bulletins |
| Historique des actions | Complet | Traçabilité des actions sensibles |
| Tableaux de bord avec graphiques | Complet | Chart.js, indicateurs par rôle |
| Données de démonstration | Complet | 840 résultats, rangs calculés |

---

## 6. Conclusion et perspectives

### 6.1 Bilan du projet

Ce projet a permis de concevoir et d'implémenter un système d'information scolaire complet couvrant l'ensemble des processus d'un établissement d'enseignement secondaire. La démarche Merise a fourni un cadre rigoureux pour la modélisation d'une base de données de 24 tables, normalisée en troisième forme normale, avec 59 règles de gestion formalisées.

L'implémentation avec Django a mis en évidence plusieurs aspects fondamentaux du développement d'applications web professionnelles :

- **L'importance de la conception préalable :** les choix effectués au niveau du modèle de données (AbstractBaseUser, sous-entités exclusives, contraintes UNIQUE) ont des implications durables sur toute l'application ;
- **La puissance des mécanismes du framework :** les signaux Django ont permis d'implémenter les calculs automatiques de manière transparente pour les vues, respectant le principe de séparation des responsabilités ;
- **Les pièges identifiés en phase de test :** la limitation de `bulk_create` vis-à-vis des signaux, le comportement des `<select>` HTML avec `display:none`, les erreurs HTTP 403 brutes présentées à des utilisateurs finaux — autant de problèmes réels résolus pendant l'implémentation.

Sur le plan quantitatif, le système livre :

- **24 tables** en base de données, **95 attributs**, **38 clés étrangères** ;
- **59 règles de gestion** formalisées dans le cahier des charges ;
- **7 espaces utilisateurs** cloisonnés ;
- **15 modules fonctionnels** entièrement opérationnels.

### 6.2 Difficultés rencontrées

| Difficulté | Solution adoptée |
|---|---|
| Calcul du rang non déclenché par `bulk_create` | Appel explicite de `bulk_update` après chaque insertion en masse |
| Sélecteur de destinataires non fonctionnel (`display:none`) | Reconstruction dynamique du DOM en JavaScript |
| Erreurs HTTP 403 brutes pour utilisateurs finaux | Remplacement par des redirections intelligentes avec message d'erreur |
| Annonces ENSEIGNANT chargeant la mauvaise sidebar | Création d'un template dédié `enseignant/annonces.html` |
| Conflits de créneaux EDT | Vérification au niveau de la vue avant enregistrement |

### 6.3 Perspectives d'évolution

ACADEMIQ V3 constitue une base fonctionnelle solide. Plusieurs axes d'amélioration peuvent être envisagés pour les versions futures :

1. **Application mobile :** développement d'une API REST (Django REST Framework) pour exposer les données à une application mobile iOS/Android destinée aux élèves et parents ;
2. **Notifications push :** intégration de WebSockets (Django Channels) pour des notifications en temps réel ;
3. **Tableau de bord analytique avancé :** visualisations statistiques plus poussées (évolution des moyennes sur plusieurs périodes, taux d'absentéisme par classe) ;
4. **Importation en masse :** import CSV/Excel des listes d'élèves et des notes pour les établissements disposant de données historiques ;
5. **Multi-établissements :** extension de l'architecture pour gérer un réseau d'établissements depuis une interface d'administration centrale ;
6. **Accessibilité :** audit et amélioration de la conformité WCAG 2.1 pour les utilisateurs en situation de handicap.

### 6.4 Conclusion générale

Ce projet de Master 1 a représenté une opportunité de mettre en pratique l'ensemble des compétences acquises au cours de la formation : analyse des besoins, modélisation Merise, conception de base de données relationnelle, développement backend avec un framework moderne, et conception d'interfaces web. La complexité fonctionnelle du domaine scolaire — avec ses nombreux acteurs, ses règles métier rigoureuses et ses enjeux de sécurité des données — en fait un sujet d'application idéal pour une étude complète de conception et de développement d'un système d'information.

ACADEMIQ V3 démontre qu'il est possible, avec des technologies open source maîtrisées, de produire un système d'information scolaire robuste, sécurisé et ergonomique, capable de répondre aux besoins réels d'un établissement d'enseignement secondaire.

---

## 7. Bibliographie et webographie

### Ouvrages

- **TARDIEU H., ROCHFELD A., COLLETTI R.** — *La méthode Merise — Tome 1 : Principes et outils*, Éditions d'Organisation, 1983.
- **CODD E.F.** — *A Relational Model of Data for Large Shared Data Banks*, Communications of the ACM, Vol. 13, N°6, 1970.
- **HOFFER J.A., RAMESH V., TOPI H.** — *Modern Database Management*, Pearson, 12e édition, 2016.

### Documentation technique

- **Django Project** — Documentation officielle Django 4.x — [https://docs.djangoproject.com/](https://docs.djangoproject.com/)
- **MariaDB Foundation** — Documentation MariaDB 10.x — [https://mariadb.com/kb/en/documentation/](https://mariadb.com/kb/en/documentation/)
- **Bootstrap** — Documentation Bootstrap 5 — [https://getbootstrap.com/docs/5.3/](https://getbootstrap.com/docs/5.3/)
- **ReportLab** — Documentation ReportLab PDF Library — [https://docs.reportlab.com/](https://docs.reportlab.com/)
- **Chart.js** — Documentation Chart.js 4.x — [https://www.chartjs.org/docs/](https://www.chartjs.org/docs/)

### Articles et ressources en ligne

- **Two Scoops of Django** — GREENFELD D. & A. — Pratiques avancées de développement Django.
- **OWASP Top 10** — Guide des vulnérabilités web les plus critiques — [https://owasp.org/www-project-top-ten/](https://owasp.org/www-project-top-ten/)
- **PEP 8** — Guide de style Python — [https://peps.python.org/pep-0008/](https://peps.python.org/pep-0008/)

---

## 8. Annexes

### Annexe A — Règles de gestion (extrait)

| Code | Intitulé | Règle |
|---|---|---|
| RG-T02 | Unicité de l'année active | Une seule année scolaire peut être active à la fois. L'activation d'une nouvelle année désactive automatiquement la précédente. |
| RG-N03 | Intervalle des notes | La valeur d'une note doit être comprise entre 0 et 20 inclus. |
| RG-M01 | Calcul automatique des moyennes | La moyenne d'un RESULTAT_MATIERE est recalculée automatiquement à chaque saisie ou modification de note. |
| RG-M04 | Calcul du rang | Le rang d'un RESULTAT_MATIERE est calculé par tri décroissant des moyennes pour le même cours et la même période. |
| RG-B02 | Condition de génération du bulletin | Un bulletin ne peut être généré que si la période est clôturée. |
| RG-AB02 | Validation des absences | La validation (justifiée / non justifiée) est de la compétence de l'ENSEIGNANT titulaire du cours. |
| RG-AB06 | Seuil d'alerte absences | Au-delà de 20 heures d'absences non justifiées sur une période, une notification est automatiquement envoyée. |
| RG-MSG03 | Filtrage des destinataires | Un ENSEIGNANT peut écrire à tout utilisateur actif. Un ELEVE ou un PARENT ne peut écrire qu'au personnel et aux enseignants. |
| RG-FIN09 | Export PDF bilan financier | Le bilan financier PDF est accessible au groupe FINANCES et à la DIRECTION. |
| RG-A03 | Redirection accès refusé | Tout accès non autorisé produit un message d'erreur explicite et redirige vers le dashboard de l'utilisateur connecté. |

### Annexe B — Modèle Logique de Données (MLD — extrait principal)

```
PERSONNE        (id, nom, prenom, email, actif, date_creation)
ENSEIGNANT      (personne_id# → PERSONNE, specialite, grade, date_embauche)
ELEVE           (personne_id# → PERSONNE, date_naissance, lieu_naissance, matricule)
ANNEE_SCOLAIRE  (id, libelle, date_debut, date_fin, active)
PERIODE         (id, nom, type_periode, date_debut, date_fin, cloturee, annee_id# → ANNEE_SCOLAIRE)
CLASSE          (id, nom, niveau, cycle, annee_id# → ANNEE_SCOLAIRE)
COURS           (id, matiere_id# → MATIERE, classe_id# → CLASSE,
                 enseignant_id# → PERSONNE, annee_id# → ANNEE_SCOLAIRE)
INSCRIPTION     (id, eleve_id# → PERSONNE, classe_id# → CLASSE,
                 annee_id# → ANNEE_SCOLAIRE, statut)
                UNIQUE(eleve_id, annee_id)
NOTE            (id, valeur CHECK(0-20), type_eval, eleve_id# → PERSONNE,
                 cours_id# → COURS, periode_id# → PERIODE)
RESULTAT_MAT    (id, moyenne, rang, eleve_id# → PERSONNE,
                 cours_id# → COURS, periode_id# → PERIODE)
                UNIQUE(eleve_id, cours_id, periode_id)
BULLETIN        (id, moyenne_generale, rang, effectif_classe,
                 eleve_id# → PERSONNE, periode_id# → PERIODE)
                UNIQUE(eleve_id, periode_id)
ABSENCE         (id, date_absence, nb_heures, statut, eleve_id# → PERSONNE,
                 cours_id# → COURS, periode_id# → PERIODE)
FRAIS_SCOL      (id, montant_du, montant_paye, statut,
                 eleve_id# → PERSONNE, annee_id# → ANNEE_SCOLAIRE)
                UNIQUE(eleve_id, annee_id)
PAIEMENT        (id, montant, recu_numero UNIQUE, mode,
                 frais_id# → FRAIS_SCOL)
MESSAGE         (id, sujet, corps, lu, expediteur_id# → PERSONNE,
                 destinataire_id# → PERSONNE)
```

### Annexe C — Commandes utiles

```bash
# Initialisation de l'environnement
pip install django mysqlclient pillow reportlab

# Migrations
python manage.py makemigrations
python manage.py migrate

# Création des groupes Django
python manage.py init_groupes

# Peuplement des données de démonstration
python manage.py populate_data

# Lancement du serveur de développement
python manage.py runserver

# Création d'un superutilisateur
python manage.py createsuperuser
```

---

*ACADEMIQ V3 — Rapport de projet de fin d'études — Juin 2026*  
*MARIKO Lamine · CI0223065023 · Master 1 Génie Informatique · Université Nangui Abrogoua*  
*Encadreur : Dr. ZEZE*
