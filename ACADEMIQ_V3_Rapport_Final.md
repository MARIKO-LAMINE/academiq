## Table des matières

| Chapitre | Titre |
|---|---|
| I | Introduction générale |
| II | Présentation du projet |
| III | Analyse des besoins |
| IV | Règles de gestion |
| V | Modélisation UML |
| VI | Conception de la base de données |
| VII | Architecture du système |
| VIII | Technologies utilisées |
| IX | Implémentation |
| X | Conclusion et perspectives |
| — | Bibliographie |

## I. Introduction générale

### I.1 Contexte général

L'**enseignement secondaire** désigne le second niveau du système éducatif, qui succède à l'enseignement primaire et précède l'enseignement supérieur. En Côte d'Ivoire, il accueille des élèves dont l'âge varie généralement entre onze et dix-neuf ans, répartis dans des **lycées** (établissements préparant au baccalauréat) et des **collèges** (établissements du premier cycle secondaire).

La **gestion administrative** d'un établissement scolaire désigne l'ensemble des activités organisationnelles qui permettent son fonctionnement quotidien : gestion des personnes (élèves, enseignants, personnel), suivi pédagogique (notes, bulletins, absences), planification (cours, emplois du temps), suivi financier (frais de scolarité, paiements) et communication interne.

Dans la grande majorité des établissements secondaires ivoiriens, cette gestion reste aujourd'hui **fragmentée** — c'est-à-dire dispersée entre différents supports sans lien entre eux — et **peu informatisée** :

- Les **notes** (résultats chiffrés des évaluations d'un élève) sont consignées dans des cahiers de texte individuels par chaque enseignant, puis retranscrites manuellement sur les bulletins ;
- Les **absences** (périodes de temps pendant lesquelles un élève n'est pas présent en cours) sont enregistrées sur des feuilles de présence papier ;
- Les **bulletins scolaires** (documents officiels récapitulant les résultats d'un élève pour une période) sont produits manuellement en fin de trimestre, souvent plusieurs semaines après la clôture de la période ;
- La **communication** entre la direction, les enseignants et les parents repose sur des canaux informels ;
- Le **suivi financier** (enregistrement et contrôle des paiements des frais de scolarité) est géré dans des tableurs distincts, sans lien avec les données pédagogiques.

### I.2 Problématique

La **problématique** est la question centrale à laquelle le projet cherche à répondre. Elle peut être formulée ainsi :

> **Comment concevoir et implémenter un système d'information centralisé permettant à tous les acteurs d'un établissement scolaire d'accéder aux informations relevant de leurs attributions, dans le respect d'un contrôle d'accès strict par rôle, tout en automatisant les calculs et traitements métier les plus critiques ?**

Cette problématique soulève trois enjeux :

**Enjeu fonctionnel :** Le système doit couvrir l'intégralité des processus d'un établissement, sans laisser de processus hors périmètre.

**Enjeu de cloisonnement :** Chaque acteur ne doit accéder qu'aux données relevant de son périmètre. Un **cloisonnement** est une séparation stricte qui empêche qu'un utilisateur accède aux données d'un autre utilisateur ou d'un autre service.

**Enjeu technique :** Le système doit être fiable, maintenable et déployable dans un environnement aux ressources informatiques limitées.

### I.3 Objectifs du projet

| N° | Objectif spécifique | Indicateur de réalisation |
|---|---|---|
| OS1 | Modéliser la base de données en troisième forme normale selon Merise | MLD validé, MPD SQL exécutable |
| OS2 | Implémenter le backend avec Django 4.x et MariaDB | Application fonctionnelle |
| OS3 | Développer une interface responsive avec Bootstrap 5 | Rendu correct mobile et desktop |
| OS4 | Garantir le contrôle d'accès par 7 rôles distincts | Aucun accès croisé possible |
| OS5 | Automatiser le calcul des moyennes, rangs et bulletins | Signaux Django opérationnels |
| OS6 | Générer les bulletins en PDF | Export ReportLab fonctionnel |
| OS7 | Implémenter une messagerie interne avec filtrage par rôle | Envoi et réception opérationnels |
| OS8 | Produire un jeu de données de démonstration complet | 840 résultats générés avec rangs |

### I.4 Méthodologie

La **méthodologie** désigne l'ensemble des méthodes et démarches adoptées pour conduire un projet. Ce projet a été conduit en trois phases :

- **Phase A — Analyse et Conception :** Identification des acteurs, formalisation des besoins et des règles de gestion, modélisation selon la méthode Merise, conception UML.
- **Phase B — Implémentation :** Développement du backend Django, des templates HTML/CSS, des signaux applicatifs et du module d'export PDF.
- **Phase C — Tests et Validation :** Tests fonctionnels manuels par rôle, tests d'intégrité en base de données, correction des anomalies identifiées.

### I.5 Plan du rapport

Ce rapport est structuré en dix chapitres. Le chapitre II présente le projet et son contexte. Le chapitre III analyse les besoins. Le chapitre IV formalise les règles de gestion. Le chapitre V décrit la modélisation UML. Le chapitre VI détaille la conception de la base de données. Le chapitre VII présente l'architecture du système. Le chapitre VIII recense les technologies utilisées. Le chapitre IX décrit l'implémentation. Le chapitre X conclut et propose des perspectives.

## II. Présentation du projet

### II.1 Contexte de l'établissement scolaire

Un **établissement scolaire** est une organisation qui emploie plusieurs catégories de personnel aux responsabilités distinctes :

- La **direction** est l'organe décisionnel qui assure la gouvernance de l'établissement.
- L'**administration** désigne le service qui gère l'organisation pédagogique (emplois du temps, salles, matières, cours).
- La **scolarité** est le service chargé des inscriptions des élèves, du suivi des absences et de la production des bulletins.
- Le service **finances** est responsable de la gestion des frais de scolarité, des paiements et du bilan financier.
- Les **enseignants** sont les personnels pédagogiques chargés de dispenser les cours et d'évaluer les élèves.
- Les **élèves** sont les apprenants inscrits dans l'établissement.
- Les **parents** ou tuteurs légaux sont les personnes responsables des élèves, auxquelles l'établissement rend compte du suivi de leurs enfants.

### II.2 Description du projet ACADEMIQ

**ACADEMIQ** est un **logiciel métier** — c'est-à-dire un logiciel conçu pour répondre aux besoins spécifiques d'un secteur d'activité précis, ici l'enseignement secondaire.

Un **système d'information** (SI) est un ensemble organisé de ressources (humaines, matérielles, logicielles et organisationnelles) qui permet de collecter, stocker, traiter et diffuser de l'information au sein d'une organisation. ACADEMIQ est un SI scolaire accessible via un navigateur web standard, sans installation de logiciel particulier côté utilisateur.

### II.3 Périmètre fonctionnel

Le périmètre fonctionnel désigne l'ensemble des fonctions couvertes par le système. ACADEMIQ couvre les seize processus suivants :

| N° | Processus | Description |
|---|---|---|
| P01 | Gestion des années scolaires | Création et activation des années scolaires |
| P02 | Gestion des périodes | Création et clôture des trimestres ou semestres |
| P03 | Gestion des classes | Organisation des groupes d'élèves par niveau |
| P04 | Gestion des salles et matières | Référentiel des locaux et des disciplines |
| P05 | Gestion des cours | Association matière × classe × enseignant × année |
| P06 | Emplois du temps | Planification des créneaux horaires avec détection de conflits |
| P07 | Inscriptions | Enregistrement et suivi des inscriptions des élèves |
| P08 | Saisie des notes | Enregistrement des résultats d'évaluation par les enseignants |
| P09 | Calcul automatique | Calcul des moyennes et des rangs par signal applicatif |
| P10 | Gestion des absences | Enregistrement et validation des absences |
| P11 | Génération des bulletins | Production automatique des bulletins de fin de période |
| P12 | Export PDF | Export des bulletins et du bilan financier en format PDF |
| P13 | Suivi financier | Gestion des frais de scolarité et des paiements |
| P14 | Messagerie interne | Communication sécurisée entre tous les acteurs |
| P15 | Annonces et calendrier | Publication d'informations à destination de l'établissement |
| P16 | Notifications automatiques | Alertes envoyées automatiquement lors d'événements déclencheurs |

### II.4 Les sept acteurs du système

Un **acteur** est toute entité externe (personne ou système) qui interagit avec le système d'information. ACADEMIQ identifie sept acteurs, chacun matérialisé par un **groupe** dans Django — un groupe étant un ensemble d'utilisateurs partageant les mêmes droits d'accès.

| Groupe | Désignation | Périmètre principal |
|---|---|---|
| DIRECTION | Direction | Accès total, gestion des comptes utilisateurs |
| ADMINISTRATION | Administration | Organisation pédagogique : cours, EDT, salles |
| SCOLARITE | Scolarité | Inscriptions, absences, génération des bulletins |
| FINANCES | Finances | Tarification, paiements, bilan financier |
| ENSEIGNANT | Enseignant | Notes et absences de ses propres cours uniquement |
| ELEVE | Elève | Consultation de son propre dossier |
| PARENT | Parent ou Tuteur | Consultation du dossier de ses enfants |

## III. Analyse des besoins

### III.1 Définitions préalables

Avant de décrire les besoins, il convient de définir les termes utilisés.

Un **besoin fonctionnel** est une capacité que le système doit obligatoirement posséder pour permettre à ses utilisateurs d'accomplir leurs tâches.

Un **besoin non-fonctionnel** est une contrainte de qualité que le système doit respecter, indépendamment de ses fonctions : performances, sécurité, maintenabilité, ergonomie.

Une **fonctionnalité** est la mise en œuvre concrète d'un besoin fonctionnel dans le système.

Un **droit d'accès** est l'autorisation accordée à un acteur d'effectuer une opération précise sur une ressource précise.

### III.2 Besoins fonctionnels par acteur

#### DIRECTION

La direction doit pouvoir :

| Fonctionnalité | Description |
|---|---|
| Gestion des comptes utilisateurs | Créer, modifier, désactiver les comptes de tous les utilisateurs et attribuer leurs rôles |
| Activation d'une année scolaire | Activer une nouvelle année scolaire (ce qui désactive automatiquement la précédente) |
| Accès global | Accéder à toutes les fonctionnalités des autres groupes du personnel |
| Consultation de l'historique | Consulter le journal de toutes les actions sensibles réalisées dans le système |
| Export du bilan financier | Exporter le bilan financier annuel en format PDF |

#### ADMINISTRATION

L'administration doit pouvoir :

| Fonctionnalité | Description |
|---|---|
| Gestion des cours | Créer et modifier les cours (association matière, classe, enseignant, année) |
| Gestion des emplois du temps | Planifier les créneaux horaires avec détection automatique des conflits de salle |
| Gestion des salles | Créer et gérer le référentiel des salles de l'établissement |
| Gestion des matières | Créer et gérer le référentiel des matières enseignées |

#### SCOLARITE

La scolarité doit pouvoir :

| Fonctionnalité | Description |
|---|---|
| Gestion des classes | Créer et gérer les classes pour chaque année scolaire |
| Gestion des inscriptions | Inscrire les élèves dans une classe, transférer ou archiver les inscriptions |
| Validation des absences | Valider ou rejeter les absences signalées par les enseignants |
| Génération des bulletins | Déclencher la génération des bulletins après clôture d'une période |
| Export PDF des bulletins | Exporter les bulletins scolaires en format PDF |

#### FINANCES

Le service finances doit pouvoir :

| Fonctionnalité | Description |
|---|---|
| Tarification | Définir les montants des frais de scolarité par niveau et par année |
| Gestion des frais | Créer les dossiers financiers des élèves pour chaque année scolaire |
| Enregistrement des paiements | Enregistrer les paiements avec attribution d'un numéro de reçu unique |
| Export du bilan financier PDF | Exporter le bilan complet de l'année en format PDF |

#### ENSEIGNANT

L'enseignant doit pouvoir :

| Fonctionnalité | Description |
|---|---|
| Consultation de ses cours | Voir uniquement les cours qui lui sont attribués |
| Saisie des notes | Saisir les notes uniquement pour ses propres cours |
| Enregistrement des absences | Signaler les absences lors de ses propres cours |
| Validation des absences | Valider (justifiée ou non justifiée) les absences de ses propres cours |
| Consultation des bulletins | Consulter les bulletins des élèves de ses classes |
| Messagerie | Envoyer des messages à tout utilisateur actif du système |
| Emploi du temps | Consulter son emploi du temps personnel |

#### ÉLÈVE

L'élève doit pouvoir :

| Fonctionnalité | Description |
|---|---|
| Mes notes | Consulter ses propres notes par cours et par période |
| Mes absences | Consulter son historique et son bilan d'absences |
| Mes bulletins | Consulter et télécharger ses propres bulletins en PDF |
| Mon emploi du temps | Consulter l'emploi du temps de sa classe |
| Messagerie | Envoyer des messages au personnel administratif et aux enseignants |
| Notifications | Recevoir les alertes de nouvelles notes, absences ou bulletins |

#### PARENT

Le parent doit pouvoir :

| Fonctionnalité | Description |
|---|---|
| Suivi de ses enfants | Accéder aux notes, absences et bulletins de chaque enfant lié à son compte |
| Emploi du temps | Consulter l'emploi du temps des enfants dont il est responsable |
| Situation financière | Consulter (en lecture seule) le dossier de frais de scolarité de ses enfants |
| Messagerie | Envoyer des messages au personnel administratif et aux enseignants |
| Notifications | Recevoir les alertes concernant ses enfants |

### III.3 Matrice des permissions

La **matrice des permissions** est un tableau à double entrée qui synthétise, pour chaque fonctionnalité et chaque rôle, les opérations autorisées.

**Légende :** C = Créer · L = Lire · M = Modifier · S = Supprimer · — = Aucun accès · (R) = restreint à ses propres données

| Fonctionnalité | DIR | ADM | SCO | FIN | ENS | ELV | PAR |
|---|---|---|---|---|---|---|---|
| Comptes utilisateurs | CLMS | — | — | — | — | — | — |
| Annees scolaires | CLMS | — | L | L | L | L | L |
| Periodes | CLMS | CLM | CLM | L | L | L | L |
| Classes | CLMS | CLM | CLM | L | L | L | L |
| Salles | CLMS | CLMS | L | L | L | — | — |
| Matieres | CLMS | CLMS | L | L | L | — | — |
| Cours | CLMS | CLMS | L | L | L (R) | — | — |
| Emploi du temps | CLMS | CLMS | L | L | L (R) | L | L |
| Inscriptions | CLMS | — | CLMS | L | — | L (R) | L (R) |
| Saisie des notes | — | — | — | — | CLM (R) | — | — |
| Consultation notes | LM | L | L | — | L (R) | L (R) | L (R) |
| Enreg. absences | — | — | — | — | C (R) | — | — |
| Validation absences | — | — | CLM | — | CLM (R) | L | L (R) |
| Generation bulletins | CL | — | CL | — | — | — | — |
| Export PDF bulletin | L | L | L | — | L (R) | L (R) | L (R) |
| Tarifs scolarite | CLMS | — | — | CLMS | — | — | — |
| Frais scolarite | CLMS | — | — | CLMS | — | — | L (R) |
| Paiements | CLMS | — | — | CLMS | — | — | — |
| Export PDF bilan | L | — | — | L | — | — | — |
| Messagerie | CLM | CLM | CLM | CLM | CLM | CLM | CLM |
| Annonces | CLM | CLM | CLM | CLM | L | L | L |
| Calendrier | CLMS | CLM | L | L | L | L | L |
| Notifications | L | L | L | L | L | L | L |
| Historique actions | L | L | — | — | — | — | — |

Tableau 1 — Matrice des permissions  (R) = restreint selon le role : enseignant limité a ses cours, élève et parent limités à leur dossier

### III.4 Besoins non-fonctionnels

| Type | Contrainte | Priorité |
|---|---|---|
| Sécurité | Authentification par email + mot de passe haché (bcrypt) | Critique |
| Cloisonnement | Chaque vue filtre les données par propriétaire (request.user) | Critique |
| Intégrité | Suppression logique uniquement — les données ne sont jamais effacées physiquement | Critique |
| Traçabilité | Toute action sensible est enregistrée dans un journal | Haute |
| Disponibilité | Accessible depuis tout navigateur web standard, sans installation cliente | Haute |
| Performance | Temps de réponse inférieur à 2 secondes pour les pages courantes | Moyenne |
| Maintenabilité | Code organisé en 6 applications Django indépendantes | Haute |
| Ergonomie | Interface adaptative (mobile, tablette, ordinateur) via Bootstrap 5 | Moyenne |

Tableau 2 — Besoins non-fonctionnels

## IV. Règles de gestion

### IV.1 Définitions du domaine métier

Avant d'énoncer les règles de gestion, il est indispensable de définir précisément chaque concept du domaine scolaire utilisé dans ces règles.

Une **règle de gestion** est une contrainte métier que le système d'information doit impérativement respecter. Elle traduit une loi, une politique interne ou une logique métier en une obligation de traitement vérifiable.

Une **année scolaire** est la période annuelle d'enseignement, identifiée par un libellé unique (exemple : « 2025-2026 »). Elle est définie par une date de début et une date de fin.

Une **période** est une subdivision d'une année scolaire correspondant à un trimestre ou un semestre. Elle possède une date de début, une date de fin et un statut : ouverte (les notes peuvent être saisies) ou clôturée (les notes sont gelées et les bulletins peuvent être générés).

Une **classe** est un groupe d'élèves inscrits dans le même niveau pédagogique pour une année scolaire donnée. Elle est caractérisée par un nom (exemple : « Terminale A »), un niveau, un cycle et un effectif maximum.

Une **matière** est une discipline d'enseignement (exemple : Mathématiques, Français). Elle possède un coefficient — c'est-à-dire un poids multiplicateur utilisé lors du calcul de la moyenne générale.

Un **cours** est l'instanciation d'une matière dans une classe, pour une année scolaire donnée, sous la responsabilité d'un enseignant précis. Un cours est le cadre dans lequel les notes et les absences sont enregistrées.

Une **salle** est un local de l'établissement dans lequel un cours peut se tenir. Elle est caractérisée par un numéro unique, un bâtiment et une capacité d'accueil.

Un **emploi du temps** est l'ensemble des créneaux horaires planifiés pour un cours dans une salle, pendant une période.

Une **inscription** est l'acte administratif par lequel un élève est affecté à une classe pour une année scolaire. Elle possède un statut : active, transférée ou abandonnée.

Une **note** est la valeur numérique (comprise entre 0 et 20) attribuée à un élève à l'issue d'une évaluation (devoir surveillé, interrogation, examen). Elle est rattachée à un cours et à une période.

Une **évaluation** désigne l'acte d'apprécier les connaissances d'un élève par un exercice formalisé (devoir surveillé, interrogation ou examen). Le résultat de l'évaluation est la note.

Une **moyenne** est la valeur arithmétique obtenue en divisant la somme de toutes les notes d'un élève pour un cours et une période par le nombre de ces notes.

Un **résultat matière** est l'enregistrement synthétique stockant la moyenne calculée d'un élève pour un cours et une période, ainsi que son rang dans ce cours.

Un **rang** est la position d'un élève dans le classement de son groupe pour un cours et une période, établi par ordre décroissant des moyennes. L'élève ayant la plus haute moyenne obtient le rang 1.

Un **bulletin scolaire** est le document officiel récapitulant l'ensemble des résultats d'un élève pour une période. Il comporte la moyenne dans chaque matière, le coefficient de chaque matière, le rang par matière, la moyenne générale et le rang général dans la classe.

Une **absence** est un événement enregistrant qu'un élève n'était pas présent lors d'un cours. Elle est caractérisée par une date, un nombre d'heures et un statut : en attente de validation, justifiée ou non justifiée.

Un **frais de scolarité** est le montant financier que l'élève doit verser à l'établissement pour une année scolaire. Il est calculé selon un tarif qui dépend du niveau de la classe.

Un **paiement** est le versement d'une somme d'argent par l'élève (ou ses parents) au titre de ses frais de scolarité. Il est associé à un numéro de reçu unique servant de justificatif.

Un **message** est une communication privée envoyée d'un utilisateur à un autre via la messagerie interne du système.

Une **notification** est une alerte automatique ou manuelle envoyée à un ou plusieurs utilisateurs pour les informer d'un événement (nouvelle note, absence, bulletin disponible).

Un **signal applicatif** est un mécanisme du framework Django qui déclenche automatiquement l'exécution d'une fonction (appelée récepteur) en réponse à un événement déterminé dans la base de données (création, modification ou suppression d'un enregistrement).

Un **hachage** de mot de passe est une transformation cryptographique irréversible appliquée au mot de passe avant son stockage, de sorte qu'il est impossible de retrouver le mot de passe original à partir du hachage stocké.

### IV.2 Règles de gestion par domaine

#### Domaine Temporel (RG-T)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-T01 | Une ANNEE_SCOLAIRE est identifiée par un libellé unique dans le système | Contrainte UNIQUE sur la colonne libelle |
| RG-T02 | Une seule ANNEE_SCOLAIRE peut être active à la fois. L'activation d'une nouvelle année désactive automatiquement toutes les autres | Signal pre_save sur le modèle AnneeScolaire |
| RG-T03 | Une PERIODE est obligatoirement rattachée à une ANNEE_SCOLAIRE | Clé étrangère NOT NULL vers AnneeScolaire |
| RG-T04 | Les dates de début et de fin d'une PERIODE doivent être comprises dans les dates de l'ANNEE_SCOLAIRE parente | Validation dans la méthode clean() du modèle |
| RG-T05 | Une PERIODE ne peut pas être rouverte une fois clôturée | Blocage en vue si cloturee = True |

#### Domaine Classe et Inscription (RG-C)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-C01 | Une CLASSE est rattachée à exactement une ANNEE_SCOLAIRE | Clé étrangère NOT NULL sur AnneeScolaire |
| RG-C02 | Le nom d'une CLASSE est unique au sein d'une même ANNEE_SCOLAIRE | Contrainte UNIQUE (nom, annee) |
| RG-C03 | Un ELEVE ne peut être inscrit que dans une seule CLASSE par ANNEE_SCOLAIRE | Contrainte UNIQUE (eleve, annee) sur Inscription |
| RG-C04 | Le nombre d'élèves inscrits dans une CLASSE ne peut pas dépasser l'effectif maximum | Validation avant enregistrement en vue |
| RG-C05 | Statut inscription : actif, transféré ou abandonné | Champ ENUM (3 valeurs) |
| RG-C06 | Les INSCRIPTIONS ne sont jamais supprimées physiquement ; seul le statut change | Suppression logique — pas de DELETE SQL |
| RG-C07 | Un ELEVE ne peut être inscrit que s'il possède un compte actif dans le système | Vérification eleve.actif = True avant inscription |

#### Domaine Cours et Emploi du temps (RG-E)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-E01 | Un COURS est uniquement défini par une combinaison (matière, classe, année) | Contrainte UNIQUE (matiere, classe, annee) |
| RG-E02 | Un enseignant ne peut pas assurer deux cours en même temps | Vérification de chevauchement horaire en vue |
| RG-E03 | Une SALLE ne peut pas accueillir deux cours simultanément | Contrainte UNIQUE (salle, periode, jour, heure_debut) |
| RG-E04 | La capacité d'une SALLE ne peut pas être inférieure à l'effectif de la CLASSE qui l'utilise | Vérification salle.capacite >= classe.effectif en vue |

#### Domaine Note et Évaluation (RG-N)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-N01 | Une NOTE est obligatoirement rattachée à un élève, un cours et une période | Clés étrangères NOT NULL sur les trois champs |
| RG-N02 | Le type d'une évaluation est l'un des trois suivants : devoir surveillé, interrogation, examen semestriel | Champ ENUM avec trois valeurs |
| RG-N03 | La valeur d'une NOTE est comprise dans l'intervalle [0 ; 20]. Toute valeur hors intervalle est rejetée | Contrainte CHECK (valeur >= 0 AND valeur <= 20) en SQL |
| RG-N04 | Un enseignant ne peut saisir des notes que pour les cours qui lui sont attribués | Filtrage queryset par cours.enseignant = request.user |
| RG-N05 | Un enseignant ne peut modifier une note que si la période correspondante n'est pas clôturée | Blocage en vue si periode.cloturee = True |
| RG-N06 | La saisie de notes est bloquée pour toute période dont la date de fin est dépassée | Vérification periode.date_fin >= date.today() en vue |

#### Domaine Moyenne et Résultat (RG-M)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-M01 | La moyenne d'un élève pour un cours et une période est la moyenne arithmétique de toutes ses notes dans ce cours sur cette période | Calcul automatique via signal post_save sur Note |
| RG-M02 | Le rang d'un élève pour un cours est sa position dans le classement par ordre décroissant des moyennes de tous les élèves du même cours sur la même période | Tri et numérotation automatique après chaque mise à jour de moyenne |
| RG-M03 | Il ne peut exister qu'un seul RESULTAT_MATIERE par triplet (élève, cours, période) | Contrainte UNIQUE (eleve, cours, periode) |
| RG-M04 | Un RESULTAT_MATIERE n'est jamais saisi directement ; il est alimenté uniquement par les signaux applicatifs | Absence de formulaire de saisie directe ; calcul automatique exclusivement |
| RG-M05 | La suppression d'une NOTE déclenche le recalcul de la moyenne et du rang | Signal post_delete sur le modèle Note |

#### Domaine Bulletin (RG-B)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-B01 | Il ne peut exister qu'un seul BULLETIN par paire (élève, période) | Contrainte UNIQUE (eleve, periode) sur Bulletin |
| RG-B02 | Un BULLETIN ne peut être généré que si la PERIODE est clôturée | Vérification periode.cloturee = True avant génération |
| RG-B03 | La moyenne générale d'un bulletin est la somme des produits (moyenne × coefficient) de chaque matière divisée par la somme des coefficients | Calcul avant stockage : Σ(moy × coeff) / Σ(coeff) |
| RG-B04 | Un bulletin généré est immuable : ses données ne peuvent plus être modifiées | Absence de formulaire d'édition du bulletin |
| RG-B05 | La génération d'un bulletin déclenche l'envoi automatique d'une notification à l'élève et à chaque parent lié | Signal post_save sur le modèle Bulletin |

#### Domaine Absence (RG-AB)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-AB01 | Une ABSENCE est enregistrée par l'enseignant titulaire du cours concerné uniquement | Filtrage queryset par cours.enseignant = request.user |
| RG-AB02 | Le statut initial d'une ABSENCE est « en attente ». La validation (justifiée ou non justifiée) est de la compétence de l'enseignant titulaire du cours | Signal et vérification en vue |
| RG-AB03 | La scolarité peut valider ou rejeter toute absence, indépendamment du cours | Droit CLM accordé au groupe SCOLARITE |
| RG-AB04 | Une ABSENCE appartient obligatoirement à un cours et à une période | Clés étrangères NOT NULL |
| RG-AB05 | Le nombre d'heures d'une absence est un entier strictement positif | Contrainte CHECK (nb_heures > 0) |
| RG-AB06 | Lorsque le cumul des absences non justifiées d'un élève dépasse 20 heures sur une période, une notification est automatiquement envoyée à la scolarité et aux parents | Signal post_save calculant le cumul après chaque validation |

#### Domaine Finances (RG-FIN)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-FIN01 | Un seul tarif peut être défini par combinaison (niveau, année scolaire) | Contrainte UNIQUE (niveau, annee) sur TarifNiveau |
| RG-FIN02 | Un seul dossier de FRAIS_SCOLARITE peut exister par paire (élève, année) | Contrainte UNIQUE (eleve, annee) sur FraisScolarite |
| RG-FIN03 | Un PAIEMENT possède un numéro de reçu unique dans tout le système | Contrainte UNIQUE sur la colonne recu_numero |
| RG-FIN04 | Le montant payé est la somme de tous les paiements liés aux frais d'un élève pour une année | Calcul automatique : Σ(paiements) |
| RG-FIN05 | Statut dossier : en_regle (paye>=du), partiel (0<paye<du), non_paye | Propriété calculée sur FraisScolarite |
| RG-FIN09 | L'export PDF du bilan financier annuel est accessible uniquement aux groupes FINANCES et DIRECTION | Décorateur @role_required('FINANCES', 'DIRECTION') |

#### Domaine Messagerie (RG-MSG)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-MSG01 | Un MESSAGE possède un expéditeur unique et un destinataire unique | Clés étrangères non nulles vers Personne |
| RG-MSG02 | Le personnel administratif peut écrire à tout utilisateur actif | Liste destinataires sans restriction pour DIR, ADMIN, SCOL, FIN |
| RG-MSG03 | Un ENSEIGNANT peut écrire à tout utilisateur actif, y compris les élèves et les parents | Liste destinataires complète pour le groupe ENSEIGNANT |
| RG-MSG04 | Un ELEVE peut écrire uniquement au personnel administratif et aux enseignants | Filtrage de la liste des destinataires selon le rôle |
| RG-MSG05 | Un PARENT peut écrire uniquement au personnel administratif et aux enseignants | Filtrage de la liste des destinataires selon le rôle |
| RG-MSG06 | Les pièces jointes sont limitées aux fichiers au format PDF | Validation du type MIME côté serveur |

#### Domaine Sécurité et Accès (RG-A)

| Code | Règle de gestion | Traduction technique |
|---|---|---|
| RG-A01 | Tout accès au système requiert une authentification par email et mot de passe | Décorateur @login_required sur toutes les vues protégées |
| RG-A02 | Le mot de passe est stocké sous forme hachée (bcrypt) ; il n'est jamais stocké en clair | Mécanisme natif de Django via AbstractBaseUser |
| RG-A03 | Tout accès à une ressource non autorisée affiche un message d'erreur explicite et redirige vers le tableau de bord propre au rôle de l'utilisateur connecté | Fonction _redirect_to_dashboard() dans permissions.py |
| RG-A04 | Un compte désactivé (actif = False) ne peut pas se connecter au système | Vérification eleve.actif = True dans le processus d'authentification |
| RG-A05 | Toute action sensible est enregistrée dans un journal d'audit avec l'identité de l'auteur, la table concernée et la date | Signal post_save sur les modèles sensibles → HistoriqueActions |

## V. Modélisation UML

### V.1 Définitions UML

**UML** (Unified Modeling Language, ou Langage de Modélisation Unifié) est un langage visuel standardisé utilisé pour décrire, spécifier et documenter les systèmes logiciels. Il propose plusieurs types de diagrammes, dont les plus utilisés dans ce projet sont :

- Le **diagramme de cas d'utilisation**, qui représente les interactions entre les acteurs et le système.
- Le **diagramme de classes**, qui représente la structure statique du système : les entités (classes), leurs attributs, leurs opérations et leurs relations.
- Le **diagramme de séquence**, qui représente les interactions dans le temps entre les composants du système pour réaliser un cas d'utilisation précis.

Un **cas d'utilisation** est une description d'une interaction entre un acteur et le système, conduisant à un résultat observable et utile pour cet acteur.

Une **classe** en UML est un concept qui regroupe un ensemble d'objets partageant les mêmes caractéristiques (attributs) et les mêmes comportements (opérations).

Un **attribut** est une propriété d'une classe, caractérisée par un nom et un type de donnée.

Une **association** est un lien sémantique entre deux classes.

Une **cardinalité** (ou multiplicité) exprime le nombre d'instances d'une classe pouvant être associées à une instance de l'autre classe. Elle se note sous la forme « minimum..maximum » (exemple : 1..* signifie « au moins un »).

### V.2 Diagramme de cas d'utilisation — Vue générale

Le diagramme de cas d'utilisation d'ACADEMIQ identifie les interactions de chaque acteur avec le système.

```
+------------------------------------------ SYSTEME ACADEMIQ --+
|                                                                 |
|  [Gérer les comptes]         [Activer année scolaire]          |
|  [Voir historique]           [Accès total]                     |
|                           <------- DIRECTION                   |
|                                                                 |
|  [Gérer cours/EDT]           [Gérer salles/matières]          |
|                           <------- ADMINISTRATION               |
|                                                                 |
|  [Gérer inscriptions]        [Générer bulletins]               |
|  [Valider absences]          [Export bulletins PDF]            |
|                           <------- SCOLARITE                   |
|                                                                 |
|  [Gérer tarifs]              [Enregistrer paiements]          |
|  [Export bilan financier]                                       |
|                           <------- FINANCES                    |
|                                                                 |
|  [Saisir notes]              [Enregistrer absences]           |
|  [Valider absences]          [Voir son EDT]                    |
|                           <------- ENSEIGNANT                  |
|                                                                 |
|  [Voir mes notes]            [Voir mes bulletins PDF]          |
|  [Voir mes absences]         [Messagerie]                       |
|                           <------- ELEVE                       |
|                                                                 |
|  [Voir dossier enfants]      [Messagerie]                      |
|  [Voir situation financière]                                    |
|                           <------- PARENT                      |
|                                                                 |
|  [Messagerie]  [Notifications]  [Calendrier]  <-- TOUS        |
+-----------------------------------------------------------------+
```

### V.3 Diagramme de classes — Structure principale

Le diagramme de classes présente les entités du système et leurs relations.

#### Entité centrale : Personne (super-entité)

```
+------------------------------+
|         Personne             |
+------------------------------+
| - id : Integer (PK)         |
| - nom : String(80)          |
| - prenom : String(80)       |
| - email : String(150) UNIQ  |
| - password : String(255)    |
| - photo_profil : Image      |
| - actif : Boolean           |
| - date_creation : DateTime  |
+------------------------------+
| + get_full_name() : String  |
| + check_password() : bool   |
+------------------------------+
       ^         ^         ^         ^
       |1        |1        |1        |1
  1..1 |    1..1 |    1..1 |    1..1 |
+----------+ +-----------+ +--------+ +--------+
|Personnel | |Enseignant | | Eleve  | | Parent |
+----------+ +-----------+ +--------+ +--------+
| fonction | |specialite | |matric. | |teleph. |
| date_emb | |grade      | |date_n. | |profess.|
+----------+ +-----------+ +--------+ +--------+
```

#### Relations pédagogiques principales

```
AnneeScolaire 1 ----< * Periode
AnneeScolaire 1 ----< * Classe
AnneeScolaire 1 ----< * Cours

Classe    * >---- 1 Matiere  (via Cours)
Classe    * >---- 1 Enseignant (via Cours)

Cours 1 ----< * EmploiDuTemps
Cours 1 ----< * Note
Cours 1 ----< * Absence
Cours 1 ----< * ResultatMatiere

Eleve 1 ----< * Inscription
Eleve 1 ----< * Note
Eleve 1 ----< * Absence
Eleve 1 ----< * ResultatMatiere
Eleve 1 ----< * Bulletin
Eleve 1 ----< 1 FraisScolarite (par an)

Parent * >------< * Eleve  (via LienParentEleve)

Periode 1 ----< * Note
Periode 1 ----< * Absence
Periode 1 ----< * ResultatMatiere
Periode 1 ----< * Bulletin
Periode 1 ----< * EmploiDuTemps
```

#### Classes des 24 entités du système

| N° | Entité | Attributs clés | Cardinalités principales |
|---|---|---|---|
| 1 | Personne | id, nom, prenom, email UNIQ, actif | Super-entité de toutes les personnes |
| 2 | Personnel | #personne(1..1), fonction | 1 Personnel pour 1 Personne |
| 3 | Enseignant | #personne(1..1), specialite, grade | 1 Enseignant pour 1 Personne |
| 4 | Eleve | #personne(1..1), matricule UNIQ | 1 Eleve pour 1 Personne |
| 5 | Parent | #personne(1..1), telephone | 1 Parent pour 1 Personne |
| 6 | LienParentEleve | #parent(N..1), #eleve(N..1) | N Parents pour N Elèves |
| 7 | AnneeScolaire | id, libelle UNIQ, active | 1 active à la fois |
| 8 | Periode | id, nom, cloturee, #annee(N..1) | N Périodes pour 1 Année |
| 9 | Classe | id, nom, niveau, #annee(N..1) | N Classes pour 1 Année |
| 10 | Salle | id, numero UNIQ, capacite | Indépendante des classes |
| 11 | Matiere | id, nom UNIQ, coefficient | Catalogue global |
| 12 | Cours | id, #matiere, #classe, #ens, #annee | UNIQ(mat,cl,an) |
| 13 | EmploiDuTemps | id, jour, heure_debut, #cours, #salle | UNIQ(salle,per,jour,h) |
| 14 | Inscription | id, statut, #eleve, #classe, #annee | UNIQ(eleve,annee) |
| 15 | Note | id, valeur[0-20], type, #eleve, #cours, #periode | N Notes par (eleve,cours,per) |
| 16 | ResultatMatiere | id, moyenne, rang, #eleve, #cours, #periode | UNIQ(eleve,cours,per) |
| 17 | Bulletin | id, moy_gen, rang, #eleve, #periode | UNIQ(eleve,periode) |
| 18 | Absence | id, nb_heures, statut, #eleve, #cours, #periode | N Absences par (eleve,cours) |
| 19 | TarifNiveau | id, niveau, montant, #annee | UNIQ(niveau,annee) |
| 20 | FraisScolarite | id, montant_du, montant_paye, #eleve, #annee | UNIQ(eleve,annee) |
| 21 | Paiement | id, montant, recu_numero UNIQ, #frais | N Paiements par 1 Frais |
| 22 | Message | id, sujet, corps, lu, #expediteur, #destinataire | N Messages entre Personnes |
| 23 | Notification | id, message, type, lu, #destinataire | N Notifications par Personne |
| 24 | HistoriqueActions | id, action, table_cible, #auteur | N Actions par Personne |

Tableau 3 — Les 24 entités du système

### V.4 Diagramme de séquence — Saisie d'une note et calcul automatique du rang

Ce diagramme montre les interactions entre les composants du système lors de la saisie d'une note par un enseignant.

```
Enseignant    Vue Django        Base de données    Signal Django
    |              |                  |                  |
    |--POST /note->|                  |                  |
    |              |--Vérif. période->|                  |
    |              |<--période OK-----|                  |
    |              |--Vérif. cours--->|                  |
    |              |<--cours ens.-----|                  |
    |              |--INSERT Note---->|                  |
    |              |                  |--post_save------>|
    |              |                  |                  |--Calcul moy.-->BD
    |              |                  |                  |<--moy. calculée-|
    |              |                  |--UPDATE/INSERT-->|  ResultatMat.
    |              |                  |                  |--Tri rangs------>
    |              |                  |<--rangs triés----|
    |              |                  |--bulk_update()-->|
    |              |<--Succès---------|                  |
    |<--Redirect---|                  |                  |
    |  (message OK)|                  |                  |
```

### V.5 Diagramme de séquence — Génération d'un bulletin PDF

```
Scolarité     Vue Django        Base de données    ReportLab
    |              |                  |                  |
    |--GET /bull-->|                  |                  |
    |              |--Vérif. clôture->|                  |
    |              |<--période clôt.--|                  |
    |              |--GET résultats-->|                  |
    |              |<--ResultatMat.---|                  |
    |              |--Calcul moy.gén.>|                  |
    |              |--Calcul rang---->(tous bulletins)   |
    |              |--INSERT Bulletin->|                 |
    |              |                  |--post_save: NOTIFICATION
    |              |--PDF request-----|----------------->|
    |              |                  |                  |--build PDF-->
    |              |<--io.BytesIO-----|<-----------------|
    |<--PDF file---|                  |                  |
    | (télécharge) |                  |                  |
```

## VI. Conception de la base de données

### VI.1 Définitions — Méthode Merise et concepts de base de données

Une **base de données** est un ensemble structuré et organisé de données stockées et accessibles de manière persistante, gérées par un **Système de Gestion de Base de Données** (SGBD).

Un **SGBD** est un logiciel qui assure le stockage, l'organisation, la sécurité et l'accès aux données. Le SGBD utilisé dans ce projet est **MariaDB**, un SGBD relationnel open source dérivé de MySQL.

Une **table** (dans une base de données relationnelle) est une structure de données organisée en lignes et en colonnes, représentant une entité du monde réel.

Un **attribut** (ou colonne) est une caractéristique d'une entité, associée à un type de données (texte, nombre, date, booléen).

Une **clé primaire** (PK, Primary Key) est un attribut ou un ensemble d'attributs dont la valeur identifie de manière unique chaque ligne d'une table.

Une **clé étrangère** (FK, Foreign Key) est un attribut d'une table dont la valeur correspond à la clé primaire d'une autre table, établissant ainsi une relation entre les deux tables.

Une **contrainte d'intégrité** est une règle imposée à la base de données pour garantir la cohérence et la validité des données. Les principales contraintes utilisées sont : UNIQUE (unicité des valeurs), NOT NULL (valeur obligatoire), CHECK (valeur dans un intervalle défini), et FOREIGN KEY (référence à une table parente).

La **méthode Merise** est une méthode française de conception des systèmes d'information, qui propose trois niveaux de modélisation successifs :

| Niveau | Modèle | Objet | Contenu |
|---|---|---|---|
| Conceptuel | MCD (Modèle Conceptuel de Données) | Entités, associations, cardinalités | Représentation sémantique, indépendante de tout SGBD |
| Logique | MLD (Modèle Logique de Données) | Tables, clés primaires, clés étrangères | Traduction du MCD en schéma relationnel |
| Physique | MPD (Modèle Physique de Données) | Script SQL | Script adapté au SGBD cible (MariaDB/InnoDB) |

La **normalisation** est le processus qui consiste à organiser les tables d'une base de données pour éliminer les redondances et les anomalies. Le niveau de référence est la **troisième forme normale** (3FN) :

- **1FN** : tous les attributs sont atomiques (une seule valeur par cellule).
- **2FN** : tout attribut non-clé dépend de la totalité de la clé primaire (pas de dépendances partielles).
- **3FN** : aucun attribut non-clé ne dépend d'un autre attribut non-clé (pas de dépendances transitives).

### VI.2 Modèle Logique de Données (MLD)

```
PERSONNE        (id_personne PK, nom, prenom, email UNIQUE, password,
                 photo_profil, actif, date_creation)

PERSONNEL       (id_personne PK=FK->PERSONNE, fonction ENUM, date_embauche)
ENSEIGNANT      (id_personne PK=FK->PERSONNE, specialite, grade, date_embauche)
ELEVE           (id_personne PK=FK->PERSONNE, matricule UNIQUE, date_naissance)
PARENT          (id_personne PK=FK->PERSONNE, telephone, profession)

LIEN_PARENT_ELEVE (id PK, parent_id FK->PERSONNE, eleve_id FK->PERSONNE)
                   UNIQUE (parent_id, eleve_id)

ANNEE_SCOLAIRE  (id PK, libelle UNIQUE, date_debut, date_fin, active)

PERIODE         (id PK, nom, type_periode ENUM, date_debut, date_fin,
                 cloturee, annee_id FK->ANNEE_SCOLAIRE)

SALLE           (id PK, numero UNIQUE, batiment, capacite, type_salle)

MATIERE         (id PK, nom_matiere UNIQUE, coefficient)

CLASSE          (id PK, nom, niveau, cycle, section, effectif_max,
                 annee_id FK->ANNEE_SCOLAIRE)
                UNIQUE (nom, annee_id)

COURS           (id PK, nb_heures_hebdo, matiere_id FK->MATIERE,
                 classe_id FK->CLASSE, enseignant_id FK->PERSONNE,
                 annee_id FK->ANNEE_SCOLAIRE)
                UNIQUE (matiere_id, classe_id, annee_id)

EMPLOI_DU_TEMPS (id PK, jour ENUM, heure_debut TIME, heure_fin TIME,
                 cours_id FK->COURS, salle_id FK->SALLE,
                 periode_id FK->PERIODE)
                UNIQUE (salle_id, periode_id, jour, heure_debut)

INSCRIPTION     (id PK, date_inscription, statut ENUM, eleve_id FK->PERSONNE,
                 classe_id FK->CLASSE, annee_id FK->ANNEE_SCOLAIRE)
                UNIQUE (eleve_id, annee_id)

NOTE            (id PK, valeur DECIMAL(4,2) CHECK[0,20], type_eval ENUM,
                 date_saisie, eleve_id FK->PERSONNE, cours_id FK->COURS,
                 periode_id FK->PERIODE)

RESULTAT_MATIERE (id PK, moyenne DECIMAL(5,2), rang INT,
                  eleve_id FK->PERSONNE, cours_id FK->COURS,
                  periode_id FK->PERIODE)
                 UNIQUE (eleve_id, cours_id, periode_id)

BULLETIN        (id PK, moyenne_generale DECIMAL(5,2), rang INT,
                 effectif_classe INT, appreciation TEXT, date_generation,
                 eleve_id FK->PERSONNE, periode_id FK->PERIODE)
                UNIQUE (eleve_id, periode_id)

ABSENCE         (id PK, date_absence DATE, nb_heures INT, statut ENUM,
                 motif TEXT, date_saisie, eleve_id FK->PERSONNE,
                 cours_id FK->COURS, periode_id FK->PERIODE)

TARIF_NIVEAU    (id PK, niveau VARCHAR, montant DECIMAL, date_echeance,
                 annee_id FK->ANNEE_SCOLAIRE)
                UNIQUE (niveau, annee_id)

FRAIS_SCOLARITE (id PK, montant_du DECIMAL, montant_paye DECIMAL,
                 statut ENUM, date_echeance, eleve_id FK->PERSONNE,
                 annee_id FK->ANNEE_SCOLAIRE)
                UNIQUE (eleve_id, annee_id)

PAIEMENT        (id PK, montant DECIMAL, recu_numero VARCHAR UNIQUE,
                 mode ENUM, date_paiement, frais_id FK->FRAIS_SCOLARITE)

MESSAGE         (id PK, sujet VARCHAR, corps TEXT, lu BOOLEAN,
                 date_envoi, piece_jointe, expediteur_id FK->PERSONNE,
                 destinataire_id FK->PERSONNE)

NOTIFICATION    (id PK, message TEXT, type_notif ENUM, lu BOOLEAN,
                 date_envoi, destinataire_id FK->PERSONNE,
                 classe_id FK->CLASSE)

EVENEMENT_SCOLAIRE (id PK, titre, description, type_event, date_debut,
                    date_fin, annee_id FK->ANNEE_SCOLAIRE,
                    createur_id FK->PERSONNE)

HISTORIQUE_ACTIONS (id PK, action, table_cible, id_enregistrement,
                    details TEXT, date_action, auteur_id FK->PERSONNE)
```

### VI.3 Les 38 clés étrangères

| N° | Table source | Colonne FK | Table cible | ON DELETE |
|---|---|---|---|---|
| 1 | PERSONNEL | personne_id | PERSONNE | CASCADE |
| 2 | ENSEIGNANT | personne_id | PERSONNE | CASCADE |
| 3 | ELEVE | personne_id | PERSONNE | CASCADE |
| 4 | PARENT | personne_id | PERSONNE | CASCADE |
| 5 | LIEN_PE | parent_id | PERSONNE | RESTRICT |
| 6 | LIEN_PE | eleve_id | PERSONNE | RESTRICT |
| 7 | PERIODE | annee_id | ANNEE_SCOLAIRE | RESTRICT |
| 8 | CLASSE | annee_id | ANNEE_SCOLAIRE | RESTRICT |
| 9 | COURS | matiere_id | MATIERE | RESTRICT |
| 10 | COURS | classe_id | CLASSE | RESTRICT |
| 11 | COURS | enseignant_id | PERSONNE | RESTRICT |
| 12 | COURS | annee_id | ANNEE_SCOLAIRE | RESTRICT |
| 13 | EMPLOI_DU_TEMPS | cours_id | COURS | RESTRICT |
| 14 | EMPLOI_DU_TEMPS | salle_id | SALLE | RESTRICT |
| 15 | EMPLOI_DU_TEMPS | periode_id | PERIODE | RESTRICT |
| 16 | INSCRIPTION | eleve_id | PERSONNE | RESTRICT |
| 17 | INSCRIPTION | classe_id | CLASSE | RESTRICT |
| 18 | INSCRIPTION | annee_id | ANNEE_SCOLAIRE | RESTRICT |
| 19 | NOTE | eleve_id | PERSONNE | RESTRICT |
| 20 | NOTE | cours_id | COURS | RESTRICT |
| 21 | NOTE | periode_id | PERIODE | RESTRICT |
| 22 | RESULTAT_MATIERE | eleve_id | PERSONNE | RESTRICT |
| 23 | RESULTAT_MATIERE | cours_id | COURS | RESTRICT |
| 24 | RESULTAT_MATIERE | periode_id | PERIODE | RESTRICT |
| 25 | BULLETIN | eleve_id | PERSONNE | RESTRICT |
| 26 | BULLETIN | periode_id | PERIODE | RESTRICT |
| 27 | ABSENCE | eleve_id | PERSONNE | RESTRICT |
| 28 | ABSENCE | cours_id | COURS | RESTRICT |
| 29 | ABSENCE | periode_id | PERIODE | RESTRICT |
| 30 | TARIF_NIVEAU | annee_id | ANNEE_SCOLAIRE | RESTRICT |
| 31 | FRAIS_SCOLARITE | eleve_id | PERSONNE | RESTRICT |
| 32 | FRAIS_SCOLARITE | annee_id | ANNEE_SCOLAIRE | RESTRICT |
| 33 | PAIEMENT | frais_id | FRAIS_SCOLARITE | RESTRICT |
| 34 | MESSAGE | expediteur_id | PERSONNE | RESTRICT |
| 35 | MESSAGE | destinataire_id | PERSONNE | RESTRICT |
| 36 | NOTIFICATION | destinataire_id | PERSONNE | SET NULL |
| 37 | NOTIFICATION | classe_id | CLASSE | SET NULL |
| 38 | HISTORIQUE | auteur_id | PERSONNE | SET NULL |

Tableau 4 — Les 38 clés étrangères du modèle

### VI.4 Extrait du script SQL (MPD)

```sql
-- Création de la base de données
CREATE DATABASE IF NOT EXISTS academiq_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE academiq_db;

-- Table PERSONNE (super-entité de tous les utilisateurs)
CREATE TABLE personne (
    id_personne   INT AUTO_INCREMENT PRIMARY KEY,
    nom           VARCHAR(80)  NOT NULL,
    prenom        VARCHAR(80)  NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    password      VARCHAR(255) NOT NULL,
    photo_profil  VARCHAR(255),
    actif         BOOLEAN      NOT NULL DEFAULT TRUE,
    date_creation DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Table ENSEIGNANT (sous-entité par héritage ON DELETE CASCADE)
CREATE TABLE enseignant (
    id_personne   INT          PRIMARY KEY,
    specialite    VARCHAR(100) NOT NULL,
    grade         VARCHAR(50),
    date_embauche DATE,
    FOREIGN KEY (id_personne)
        REFERENCES personne(id_personne)
        ON DELETE CASCADE
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Table NOTE avec contrainte CHECK [0 ; 20]
CREATE TABLE note (
    id_note     INT AUTO_INCREMENT PRIMARY KEY,
    valeur      DECIMAL(4,2)  NOT NULL
                CHECK (valeur >= 0 AND valeur <= 20),
    type_eval   ENUM('devoir_surveille','interrogation','examen_semestriel')
                NOT NULL,
    date_saisie DATE          NOT NULL,
    eleve_id    INT           NOT NULL,
    cours_id    INT           NOT NULL,
    periode_id  INT           NOT NULL,
    FOREIGN KEY (eleve_id)   REFERENCES personne(id_personne),
    FOREIGN KEY (cours_id)   REFERENCES cours(id_cours),
    FOREIGN KEY (periode_id) REFERENCES periode(id_periode)
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Table INSCRIPTION avec contrainte UNIQUE (un élève par classe par an)
CREATE TABLE inscription (
    id_inscription INT  AUTO_INCREMENT PRIMARY KEY,
    date_inscription DATE NOT NULL,
    statut         ENUM('actif','transfere','abandonne') DEFAULT 'actif',
    eleve_id       INT  NOT NULL,
    classe_id      INT  NOT NULL,
    annee_id       INT  NOT NULL,
    FOREIGN KEY (eleve_id)  REFERENCES personne(id_personne),
    FOREIGN KEY (classe_id) REFERENCES classe(id_classe),
    FOREIGN KEY (annee_id)  REFERENCES annee_scolaire(id_annee),
    UNIQUE KEY uk_inscription_eleve_annee (eleve_id, annee_id)
) ENGINE=InnoDB CHARSET=utf8mb4;

-- Table RESULTAT_MATIERE (jamais saisie directement, alimentée par signaux)
CREATE TABLE resultat_matiere (
    id_resultat INT  AUTO_INCREMENT PRIMARY KEY,
    moyenne     DECIMAL(5,2),
    rang        INT,
    eleve_id    INT  NOT NULL,
    cours_id    INT  NOT NULL,
    periode_id  INT  NOT NULL,
    FOREIGN KEY (eleve_id)   REFERENCES personne(id_personne),
    FOREIGN KEY (cours_id)   REFERENCES cours(id_cours),
    FOREIGN KEY (periode_id) REFERENCES periode(id_periode),
    UNIQUE KEY uk_resultat (eleve_id, cours_id, periode_id)
) ENGINE=InnoDB CHARSET=utf8mb4;
```

## VII. Architecture du système

### VII.1 Définitions

L'**architecture logicielle** désigne l'organisation structurelle d'un système informatique, c'est-à-dire la manière dont ses composants sont agencés, leurs rôles et leurs interactions.

Un **framework** est un ensemble d'outils, de bibliothèques et de conventions préfabriquées qui facilitent le développement d'applications d'un type donné. Django est le framework web Python utilisé dans ce projet.

Un **patron d'architecture** est une solution générique et réutilisable à un problème récurrent d'organisation logicielle. ACADEMIQ suit le patron **MVT** (Modèle-Vue-Template), propre à Django.

Le patron **MVT** (Model-View-Template) organise le code en trois couches :
- Le **Modèle** (Model) gère les données et leur persistance en base de données. Il correspond aux classes Python déclarées dans `models.py`.
- La **Vue** (View) contient la logique métier et orchestre les traitements. Elle reçoit les requêtes HTTP, interagit avec les modèles et renvoie une réponse.
- Le **Template** est le fichier HTML qui définit la présentation visuelle renvoyée à l'utilisateur.

Une **requête HTTP** (HyperText Transfer Protocol) est un message envoyé par le navigateur du client vers le serveur web pour demander une ressource (page, image, fichier).

Un **ORM** (Object-Relational Mapper) est un composant logiciel qui traduit automatiquement les opérations effectuées sur des objets Python en requêtes SQL pour la base de données. Django fournit un ORM intégré.

Un **signal applicatif** (défini plus haut dans les règles de gestion) est ici le mécanisme Django utilisé pour déclencher automatiquement le recalcul des moyennes et des rangs.

Une **application Django** (au sens du framework) est un composant autonome du projet qui regroupe un périmètre fonctionnel précis : ses modèles, ses vues, ses URLs et ses templates. Un projet Django est composé d'une ou plusieurs applications.

Un **namespace** est un préfixe d'espace de noms utilisé pour éviter les conflits entre des noms de vues appartenant à différentes applications. Par exemple, `enseignant:dashboard` désigne la vue `dashboard` de l'application `enseignant`.

### VII.2 Architecture globale — Trois couches

ACADEMIQ suit une architecture **client-serveur web à trois couches** :

```
COUCHE PRESENTATION
  Navigateur web  (Chrome, Firefox, Safari, Edge)
  HTML5 + CSS3 + Bootstrap 5 + Bootstrap Icons + Chart.js
  Rendu HTML produit entièrement côté serveur (pas de framework JS)
              |
              |  HTTP/HTTPS  (requêtes et réponses)
              |
COUCHE APPLICATIVE
  Serveur Django 4.x  (Python 3.10+)
  - Routage des URLs avec namespaces par application
  - Vues Function-Based Views (FBV)
  - Décorateurs de permissions @role_required
  - Templates Django (rendu HTML côté serveur)
  - Signaux post_save / pre_save
  - Module ReportLab (génération PDF en mémoire)
              |
              |  ORM Django  (requêtes SQL automatisées)
              |
COUCHE DONNÉES
  MariaDB 10.x avec moteur InnoDB
  - 24 tables, 95 attributs, 38 clés étrangères
  - Contraintes UNIQUE, CHECK, FK avec ON DELETE
  - Encodage UTF-8mb4 (support complet Unicode)
  - Transactions ACID garanties
```

**ACID** est l'acronyme des quatre propriétés qui garantissent la fiabilité des transactions dans une base de données :
- **A**tomicité : une transaction est soit entièrement exécutée, soit entièrement annulée.
- **C**ohérence : chaque transaction amène la base d'un état valide à un autre état valide.
- **I**solation : les transactions concurrentes sont exécutées comme si elles étaient séquentielles.
- **D**urabilité : une transaction confirmée est persistée même en cas de panne.

### VII.3 Structure des applications Django

Le projet est organisé en **six applications Django** aux responsabilités distinctes et cloisonnées :

| Application | Responsabilité | Groupes servis |
|---|---|---|
| `core` | Définition des 24 modèles, signaux, permissions, administration | Tous |
| `accounts` | Authentification (login, logout, redirection post-connexion par rôle) | Tous |
| `personnel` | Espace du personnel administratif : vues, formulaires, templates | DIRECTION, ADMIN, SCOLARITE, FINANCES |
| `enseignant` | Espace enseignant : notes, absences, EDT, messagerie | ENSEIGNANT |
| `eleve` | Espace élève : consultation notes, absences, bulletins, messagerie | ELEVE |
| `parent` | Espace parent : suivi des enfants, messagerie | PARENT |

Tableau 5 — Les six applications Django

### VII.4 Structure des répertoires

```
academiq/                          Répertoire racine du projet
├── academiq/                      Package de configuration Django
│   ├── settings.py                Paramètres : BDD, applications, AUTH_USER_MODEL
│   ├── urls.py                    URLs racine (inclut les 5 namespaces)
│   └── wsgi.py                    Point d'entrée WSGI pour le serveur
│
├── core/                          Noyau métier central
│   ├── models.py                  Les 24 modèles Django (entités)
│   ├── signals.py                 Signaux : calcul moyennes, rangs, notifs
│   ├── permissions.py             @role_required, _redirect_to_dashboard
│   ├── context_processors.py      Variables globales de contexte (rôle, année active)
│   └── management/commands/
│       └── populate_data.py       Génération des données de démonstration
│
├── accounts/                      Authentification
│   └── views.py                   Login, logout, redirection par rôle
│
├── personnel/                     Espace PERSONNEL
│   ├── views.py                   Toutes les vues du personnel
│   ├── forms.py                   Formulaires spécifiques
│   ├── urls.py                    URLs sous le namespace 'personnel'
│   └── templates/personnel/       Templates HTML
│
├── enseignant/                    Espace ENSEIGNANT
├── eleve/                         Espace ELEVE
├── parent/                        Espace PARENT
│
└── templates/
    ├── base_personnel.html        Layout commun + sidebar PERSONNEL
    ├── base_enseignant.html       Layout commun + sidebar ENSEIGNANT
    ├── base_eleve.html            Layout commun + sidebar ELEVE
    └── base_parent.html           Layout commun + sidebar PARENT
```

### VII.5 Flux d'une requête HTTP dans Django

```
1. Navigateur envoie : GET /enseignant/notes/cours/12/
   |
2. Django charge urls.py du projet
   -> inclut enseignant/urls.py (namespace='enseignant')
   |
3. Correspondance trouvée : vue notes_cours(request, cours_id=12)
   |
4. Décorateur @role_required('ENSEIGNANT')
   -> Vérifie : request.user.groups contient 'ENSEIGNANT' ?
   -> Non : redirection vers le bon dashboard (RG-A03)
   -> Oui : exécution de la vue
   |
5. Vue exécute :
   cours = get_object_or_404(Cours, pk=12, enseignant=request.user)
   notes = Note.objects.filter(cours=cours).order_by('-date_saisie')
   |
6. Rendu du template :
   return render(request, 'enseignant/notes/liste.html', {'notes': notes})
   |
7. Template hérite de base_enseignant.html
   -> Génération du HTML final avec Bootstrap 5
   |
8. Réponse HTTP 200 renvoyée au navigateur
```

## VIII. Technologies utilisées

### VIII.1 Définitions générales

Un **langage de programmation** est un langage formel permettant d'écrire des instructions que l'ordinateur peut exécuter. Python est le langage principal de ce projet.

Une **bibliothèque** (library) est un ensemble de fonctions et de classes préécrites que le développeur peut réutiliser dans son code pour ne pas repartir de zéro.

Un **framework** (cadre de travail) fournit, en plus des bibliothèques, une structure et des conventions d'organisation du code que le développeur doit respecter.

Un **moteur de base de données** est le composant interne d'un SGBD qui gère physiquement le stockage des données. Le moteur **InnoDB** de MariaDB offre les transactions ACID et les clés étrangères.

Un **format PDF** (Portable Document Format) est un format de fichier développé par Adobe qui garantit que le document s'affiche de manière identique quel que soit le système d'exploitation ou le logiciel utilisé pour le lire.

Une **interface responsive** est une interface web qui s'adapte automatiquement à la taille de l'écran de l'appareil utilisé (téléphone, tablette, ordinateur).

### VIII.2 Tableau des technologies

| Composant | Technologie | Version | Rôle précis |
|---|---|---|---|
| Langage backend | Python | 3.10+ | Écriture de toute la logique métier |
| Framework web | Django | 4.x | Routing, ORM, authentification, templates, signaux |
| Base de données | MariaDB / InnoDB | 10.x | Stockage persistant, contraintes SQL, transactions ACID |
| Interface CSS | Bootstrap | 5.3 | Mise en page responsive, composants visuels préfabriqués |
| Icônes | Bootstrap Icons | 1.11 | Icônes vectorielles dans l'interface |
| Graphiques | Chart.js | 4.x | Graphiques interactifs dans les tableaux de bord |
| Génération PDF | ReportLab | 4.x | Création des bulletins et du bilan financier en PDF |
| Hachage | bcrypt (via Django) | — | Sécurisation des mots de passe stockés |

Tableau 6 — Technologies utilisées

### VIII.3 Justification des choix

**Pourquoi Python ?** Python est un langage clair, lisible et expressif, avec un écosystème de bibliothèques très riche. Il est enseigné dans la filière Génie Informatique de l'université, ce qui facilite la maintenance future par d'autres étudiants.

**Pourquoi Django ?** Django est un framework web Python mature, sécurisé par défaut et très complet. Il fournit nativement : un ORM, un système d'authentification, un panneau d'administration, un système de templates et un mécanisme de signaux. Il évite d'avoir à réimplémenter ces composants critiques.

**Pourquoi MariaDB ?** MariaDB est open source, performant et entièrement compatible MySQL. Le moteur InnoDB qu'il propose offre les transactions ACID et les clés étrangères, indispensables pour garantir l'intégrité des données scolaires.

**Pourquoi Bootstrap ?** Bootstrap est le framework CSS le plus utilisé au monde. Il fournit une grille responsive et des composants prêts à l'emploi (boutons, tableaux, formulaires, alertes), permettant de produire rapidement une interface professionnelle et compatible tous navigateurs.

**Pourquoi ReportLab ?** ReportLab est la bibliothèque Python de référence pour la génération de fichiers PDF. Elle permet un contrôle précis de la mise en page, du positionnement des éléments et de la typographie, ce qui est essentiel pour des bulletins scolaires officiels.

## IX. Implémentation

### IX.1 Définitions préalables

L'**implémentation** (ou développement) est la phase au cours de laquelle le code source du système est écrit, en traduisant les spécifications de la phase de conception en instructions exécutables.

Un **modèle Django** est une classe Python qui hérite de `django.db.models.Model` et qui représente une table de la base de données. Chaque attribut de classe correspond à une colonne de la table.

Un **formulaire Django** (Form ou ModelForm) est une classe qui gère la validation des données soumises par l'utilisateur via un formulaire HTML, avant leur enregistrement en base de données.

Une **vue Django** (View) est une fonction Python qui reçoit une requête HTTP, effectue des traitements (interaction avec la base de données, calculs) et retourne une réponse HTTP (généralement une page HTML générée à partir d'un template).

Un **template Django** est un fichier HTML qui contient des balises spéciales Django (`{% %}` pour la logique, `{{ }}` pour l'affichage) permettant de générer dynamiquement le contenu à partir des données fournies par la vue.

Un **décorateur Python** est une fonction qui modifie le comportement d'une autre fonction sans en changer le code source. Dans ce projet, `@role_required('ENSEIGNANT')` est un décorateur qui vérifie le rôle de l'utilisateur avant d'autoriser l'accès à la vue.

### IX.2 Modèle utilisateur personnalisé

Le premier choix d'implémentation structurant est l'utilisation d'un **modèle utilisateur personnalisé**, en remplacement du modèle `User` standard fourni par Django.

La classe `AbstractBaseUser` de Django permet de définir un modèle utilisateur entièrement personnalisé, en choisissant l'identifiant de connexion (dans ce projet : l'email au lieu du nom d'utilisateur).

```python
# core/models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin

class PersonneManager(BaseUserManager):
    """Gestionnaire du modèle Personne : définit comment créer un utilisateur."""
    def create_user(self, email, nom, prenom, password=None, **extra):
        if not email:
            raise ValueError("L'email est obligatoire")
        email = self.normalize_email(email)
        user  = self.model(email=email, nom=nom, prenom=prenom, **extra)
        user.set_password(password)   # Hachage bcrypt du mot de passe
        user.save(using=self._db)
        return user

class Personne(AbstractBaseUser, PermissionsMixin):
    """Super-entité de tous les utilisateurs du système."""
    nom           = models.CharField(max_length=80)
    prenom        = models.CharField(max_length=80)
    email         = models.EmailField(unique=True)  # Identifiant de connexion
    photo_profil  = models.ImageField(upload_to='profils/', null=True, blank=True)
    actif         = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    is_staff      = models.BooleanField(default=False)

    USERNAME_FIELD  = 'email'   # L'email est utilisé pour l'authentification
    REQUIRED_FIELDS = ['nom', 'prenom']
    objects         = PersonneManager()

    def get_full_name(self):
        return f"{self.prenom} {self.nom}"

    class Meta:
        db_table = 'personne'
```

Ce paramètre doit être déclaré dans le fichier de configuration avant la première migration :

```python
# academiq/settings.py
AUTH_USER_MODEL = 'core.Personne'
```

### IX.3 Signaux applicatifs — Calcul automatique des moyennes et rangs

#### Signal post_save sur Note : recalcul de la moyenne

À chaque création ou modification d'une note, le signal suivant est déclenché automatiquement :

```python
# core/signals.py
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.db.models import Avg
from .models import Note, ResultatMatiere, AnneeScolaire

@receiver(post_save, sender=Note)
def recalculer_resultat_matiere(sender, instance, **kwargs):
    """
    Déclenché après chaque sauvegarde d'une Note.
    1. Recalcule la moyenne de l'élève pour le cours et la période.
    2. Recalcule les rangs de tous les élèves du même cours.
    """
    # Étape 1 : calcul de la moyenne arithmétique
    agregat = Note.objects.filter(
        eleve=instance.eleve,
        cours=instance.cours,
        periode=instance.periode
    ).aggregate(Avg('valeur'))
    nouvelle_moyenne = agregat['valeur__avg']

    # Étape 2 : création ou mise à jour du résultat matière
    ResultatMatiere.objects.update_or_create(
        eleve=instance.eleve,
        cours=instance.cours,
        periode=instance.periode,
        defaults={'moyenne': nouvelle_moyenne}
    )

    # Étape 3 : recalcul des rangs pour tous les élèves de ce cours
    tous_resultats = list(
        ResultatMatiere.objects.filter(
            cours=instance.cours,
            periode=instance.periode
        ).order_by('-moyenne')  # Tri décroissant (meilleure note = rang 1)
    )
    for rang, resultat in enumerate(tous_resultats, start=1):
        resultat.rang = rang
    if tous_resultats:
        ResultatMatiere.objects.bulk_update(tous_resultats, ['rang'])
```

#### Signal pre_save sur AnneeScolaire : unicité de l'année active (RG-T02)

```python
@receiver(pre_save, sender=AnneeScolaire)
def une_seule_annee_active(sender, instance, **kwargs):
    """
    Intercepte toute activation d'une année scolaire.
    Désactive automatiquement toutes les autres années.
    """
    if instance.active:
        AnneeScolaire.objects.exclude(pk=instance.pk).update(active=False)
```

### IX.4 Contrôle d'accès par rôle

Le décorateur `@role_required` vérifie que l'utilisateur connecté appartient à l'un des groupes requis :

```python
# core/permissions.py
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect

def _redirect_to_dashboard(request):
    """
    Affiche un message d'erreur et redirige vers le bon tableau de bord
    selon le rôle de l'utilisateur connecté (RG-A03).
    """
    messages.error(request, "Vous n'avez pas accès à cette page.")
    groupes = list(request.user.groups.values_list('name', flat=True))
    if any(g in groupes for g in ('DIRECTION','ADMINISTRATION','SCOLARITE','FINANCES')):
        return redirect('personnel:dashboard')
    if 'ENSEIGNANT' in groupes:
        return redirect('enseignant:dashboard')
    if 'ELEVE' in groupes:
        return redirect('eleve:dashboard')
    if 'PARENT' in groupes:
        return redirect('parent:dashboard')
    return redirect('accounts:login')

def role_required(*roles):
    """
    Décorateur qui protège une vue en vérifiant que l'utilisateur
    appartient à au moins l'un des groupes spécifiés.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('accounts:login')
            groupes_user = request.user.groups.values_list('name', flat=True)
            if any(r in groupes_user for r in roles):
                return view_func(request, *args, **kwargs)
            return _redirect_to_dashboard(request)
        return wrapper
    return decorator
```

**Exemple d'utilisation dans une vue :**

```python
# enseignant/views.py
from core.permissions import role_required
from core.models import Cours, Note
from django.shortcuts import get_object_or_404, render

@role_required('ENSEIGNANT')
def saisir_note(request, cours_id):
    """
    Vue de saisie des notes — accessible uniquement au groupe ENSEIGNANT.
    Double cloisonnement : décorateur (vue) + get_object_or_404 (queryset).
    """
    # Cloisonnement queryset : l'enseignant ne peut accéder qu'à SES cours
    cours = get_object_or_404(Cours, pk=cours_id, enseignant=request.user)

    if request.method == 'POST':
        periode_id = request.POST.get('periode')
        periode    = Periode.objects.get(pk=periode_id)

        # Vérification RG-N06 : période non clôturée
        if periode.cloturee:
            messages.error(request, f"La période '{periode.nom}' est clôturée.")
            return redirect('enseignant:notes_cours', cours_id=cours_id)

        # Enregistrement de la note (déclenche post_save → signal recalcul)
        Note.objects.create(
            valeur     = request.POST['valeur'],
            type_eval  = request.POST['type_eval'],
            date_saisie= date.today(),
            eleve_id   = request.POST['eleve'],
            cours      = cours,
            periode    = periode
        )
        messages.success(request, "Note enregistrée et rangs recalculés.")
    ...
```

### IX.5 Module de messagerie avec recherche dynamique

La messagerie interne repose sur un sélecteur de destinataires enrichi. Le problème identifié lors du développement est que la technique CSS `style.display='none'` sur des balises `<option>` HTML n'est pas fiable selon les navigateurs.

**Solution retenue :** injection d'un tableau JavaScript (DEST_DATA) dans la page, puis reconstruction dynamique du sélecteur à chaque frappe dans la zone de recherche.

```python
# personnnel/views.py et enseignant/views.py
ORDRE_ROLES = ['DIRECTION','ADMINISTRATION','SCOLARITE','FINANCES',
               'ENSEIGNANT','PARENT','ELEVE']

@role_required('ENSEIGNANT')
def envoyer_message(request):
    qs = Personne.objects.filter(actif=True).exclude(pk=request.user.pk)
    groupes_dest = {}
    for role in ORDRE_ROLES:
        membres = list(qs.filter(groups__name=role).order_by('nom','prenom'))
        if membres:
            groupes_dest[role] = membres
    return render(request, 'enseignant/messagerie/nouveau.html',
                  {'groupes_dest': groupes_dest})
```

```javascript
// Dans le template HTML : reconstruction dynamique
const DEST_DATA = [
    {% for categorie, membres in groupes_dest.items %}
    {% for p in membres %}
    { v:"{{ p.pk }}", t:"{{ p.get_full_name|escapejs }}", g:"{{ categorie }}" },
    {% endfor %}{% endfor %}
];

function rebuildSelect(query) {
    const sel = document.getElementById('selectDest');
    const q   = query.toLowerCase().trim();
    sel.innerHTML = '<option value="">— Choisir —</option>';
    const groupes = {};
    DEST_DATA.forEach(d => {
        if (!q || d.t.toLowerCase().includes(q)) {
            if (!groupes[d.g]) groupes[d.g] = [];
            groupes[d.g].push(d);
        }
    });
    Object.keys(groupes).forEach(grp => {
        const og = document.createElement('optgroup');
        og.label = grp;
        groupes[grp].forEach(d => {
            const o   = document.createElement('option');
            o.value   = d.v;
            o.textContent = d.t;
            og.appendChild(o);
        });
        sel.appendChild(og);
    });
}
document.getElementById('searchDest').addEventListener('input', function() {
    rebuildSelect(this.value);
});
```

### IX.6 Anomalie identifiée et corrigée : bulk_create et signaux Django

**Contexte :** La commande de peuplement des données de démonstration (`populate_data`) utilise `bulk_create` pour insérer en une seule opération SQL plusieurs centaines de notes, pour des raisons de performance.

**Anomalie :** La méthode `bulk_create` de Django **ne déclenche pas** les signaux `post_save`. Par conséquent, le signal de recalcul des moyennes et des rangs n'était pas exécuté lors de l'initialisation des données. Résultat : 840 enregistrements RESULTAT_MATIERE avec la colonne `rang` à NULL.

**Solution :** Appel explicite du calcul des rangs après chaque `bulk_create`, en regroupant les résultats par cours avec `itertools.groupby` :

```python
# core/management/commands/populate_data.py
from itertools import groupby
from core.models import ResultatMatiere

# Après le bulk_create des notes pour un trimestre :
all_rm = list(
    ResultatMatiere.objects.filter(periode=t1)
    .order_by('cours_id', '-moyenne')
)
to_update = []
for _, groupe in groupby(all_rm, key=lambda r: r.cours_id):
    for rang, res in enumerate(list(groupe), start=1):
        res.rang = rang
        to_update.append(res)
if to_update:
    ResultatMatiere.objects.bulk_update(to_update, ['rang'])
```

**Résultat :** 840 enregistrements RESULTAT_MATIERE générés, 840 avec rang calculé, 0 valeur NULL.

### IX.7 Bilan des modules implémentés

| Module | Fonctionnalités livrées | Statut |
|---|---|---|
| Authentification et accès | 7 rôles, redirections intelligentes, hachage bcrypt | Complet |
| Gestion temporelle | Années scolaires, périodes, activation unique, clôture | Complet |
| Organisation pédagogique | Classes, salles, matières, cours, EDT, détection conflits | Complet |
| Inscriptions | Création, transfert, archivage (suppression logique) | Complet |
| Notes et évaluations | Saisie, calcul automatique moyennes, rangs, période clôturée | Complet |
| Absences | Enregistrement, validation, seuil 20h, notification automatique | Complet |
| Bulletins scolaires | Génération, moyenne pondérée, rang classe, immuabilité | Complet |
| Export PDF bulletins | ReportLab, accessible selon rôle | Complet |
| Suivi financier | Tarifs, frais, paiements, calcul statut automatique | Complet |
| Export PDF bilan financier | Accessible à FINANCES et DIRECTION uniquement | Complet |
| Messagerie interne | Recherche dynamique JS, filtrage rôle, pièce jointe PDF | Complet |
| Annonces et calendrier | Publication personnel, lecture seule enseignants/élèves | Complet |
| Notifications automatiques | Notes, absences, bulletins, seuil absences | Complet |
| Tableaux de bord | Indicateurs clés + graphiques Chart.js par rôle | Complet |
| Historique des actions | Journal d'audit pour les actions sensibles | Complet |
| Données de démonstration | 840 résultats, rangs, absences, paiements | Complet |

Tableau 7 — Bilan des 16 modules implémentés

### IX.8 Comptes de démonstration

| Rôle | Email | Mot de passe |
|---|---|---|
| DIRECTION | direction@academiq.ci | academiq2026 |
| SCOLARITE | scolarite@academiq.ci | academiq2026 |
| FINANCES | finances@academiq.ci | academiq2026 |
| ENSEIGNANT | prof.kone@academiq.ci | academiq2026 |
| ELEVE | eleve1@academiq.ci | academiq2026 |
| PARENT | parent1@academiq.ci | academiq2026 |

## X. Conclusion et perspectives

### X.1 Bilan du projet

Ce projet de fin d'études de Master 1 a permis de concevoir et d'implémenter un système d'information scolaire complet, couvrant l'intégralité des processus d'un établissement d'enseignement secondaire. La démarche adoptée — de l'analyse des besoins à l'implémentation, en passant par la modélisation Merise et la conception UML — illustre la chaîne complète du génie logiciel.

Le système repose sur une base de données relationnelle normalisée en troisième forme normale, avec 24 tables, 59 règles de gestion formalisées et 7 rôles utilisateurs distincts garantissant un cloisonnement strict des accès. L'ensemble des fonctionnalités — gestion pédagogique, suivi financier, communication interne, génération de bulletins en PDF — a été livré et validé fonctionnellement sur un jeu de données de démonstration complet.

### X.2 Perspectives d'évolution

**Court terme (3 à 6 mois) :**
- Import en masse des listes d'élèves et des historiques de notes via des fichiers CSV ou Excel ;
- Tests unitaires automatisés avec le framework `pytest-django` pour les règles métier critiques ;
- Audit d'accessibilité selon les normes WCAG 2.1 (contraste, navigation au clavier).

**Moyen terme (6 à 18 mois) :**
- Développement d'une **API REST** (Interface de Programmation d'Application à architecture REST) avec Django REST Framework, pour exposer les données à une application mobile iOS/Android ;
- Notifications en temps réel avec **Django Channels** (WebSockets — protocole permettant une communication bidirectionnelle permanente entre le navigateur et le serveur) ;
- Tableau de bord analytique : évolution des moyennes sur plusieurs périodes, taux d'absentéisme, comparaisons inter-classes.

**Long terme (plus de 18 mois) :**
- Architecture **multi-établissements** : un réseau d'établissements géré depuis une console d'administration centrale unique ;
- Déploiement **cloud** : conteneurisation avec Docker (outil qui encapsule une application et ses dépendances dans un conteneur portable), orchestration avec Nginx et Gunicorn.

### X.4 Conclusion générale

ACADEMIQ démontre qu'avec des technologies open source maîtrisées — Python, Django, MariaDB, Bootstrap — il est possible de produire un système d'information scolaire robuste, sécurisé et ergonomique, répondant aux besoins réels d'un établissement d'enseignement secondaire en Côte d'Ivoire.

Ce projet a été l'occasion d'appliquer concrètement les compétences acquises en Master 1 : analyse des besoins, modélisation Merise et UML, conception de base de données relationnelle normalisée, développement backend avec un framework moderne, conception d'interfaces web responsive et implémentation de mécanismes de sécurité par rôle.

## Bibliographie

**Ouvrages de référence :**

- TARDIEU H., ROCHFELD A., COLLETTI R. — *La méthode Merise, Tome 1 : Principes et outils*, Éditions d'Organisation, 1983.
- CODD E.F. — *A Relational Model of Data for Large Shared Data Banks*, Communications of the ACM, Vol. 13, N°6, 1970.
- ELMASRI R., NAVATHE S. — *Fundamentals of Database Systems*, Pearson, 7e édition, 2015.
- GREENFELD D. & A. — *Two Scoops of Django 3.x*, Two Scoops Press, 2020.

**Documentation technique :**

- Django Software Foundation — Documentation officielle Django 4.x
- MariaDB Foundation — Documentation MariaDB 10.x
- Bootstrap Team — Documentation Bootstrap 5.3
- ReportLab — Documentation PDF Library 4.x
- Chart.js — Documentation Chart.js 4.x


*ACADEMIQ — Rapport de Projet de Fin d'Études — Juin 2026*
*MARIKO Lamine · CI0223065023 · Master 1 Génie Informatique · Université Nangui Abrogoua*
*Encadreur : Dr. ZEZE*
