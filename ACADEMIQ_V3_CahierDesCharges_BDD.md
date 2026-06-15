## Table des matières

| Chapitre | Titre |
|---|---|
| I | Introduction et contexte |
| II | Acteurs et fonctions |
| III | Règles de gestion |
| IV | Dictionnaire des données |
| V | Modèle Logique de Données |
| VI | Modèle Physique de Données |
| VII | Bilan et conclusion |

---

## I. Introduction et contexte

### 1.1 Présentation du projet

**ACADEMIQ** est un système centralisé de gestion des activités scolaires destiné aux établissements d'enseignement secondaire (collèges et lycées). Il couvre l'ensemble du cycle de vie scolaire : de l'inscription d'un élève à la délivrance de son bulletin de notes, en passant par la planification des cours, la gestion des absences, la communication interne et le suivi financier.

Ce document constitue le cahier des charges mis à jour de la base de données du système. Il remplace la version précédente en intégrant cinq nouvelles entités et de nombreuses modifications apportées aux entités existantes, à la suite des analyses fonctionnelles conduites durant la phase d'implémentation.

### 1.2 Objectifs du système

Le système doit permettre de :

- Gérer les années scolaires, les périodes (trimestres ou semestres), les classes et les inscriptions des élèves ;
- Planifier les cours et les emplois du temps avec détection des conflits de créneaux ;
- Saisir et calculer automatiquement les notes, les moyennes et les rangs ;
- Enregistrer et suivre les absences des élèves ;
- Générer les bulletins de notes à la clôture de chaque période ;
- Gérer la communication interne via une messagerie privée et un système d'annonces ;
- Consulter le calendrier scolaire (vacances, examens, réunions, jours fériés) ;
- Suivre la situation financière (frais de scolarité et paiements) de chaque élève ;
- Enregistrer un historique de toutes les actions sensibles réalisées dans le système.

### 1.3 Environnement technique

| Couche | Technologie |
|---|---|
| Langage backend | Python 3.10+ |
| Framework web | Django 4.x |
| Base de données | MariaDB 10.x / InnoDB |
| Frontend | HTML5, CSS3, Bootstrap 5 |
| Génération PDF | ReportLab |
| Authentification | Django Auth (AbstractBaseUser, groupes) |

---

## II. Acteurs et fonctions

### 2.1 Identification des acteurs

Le système distingue sept (7) rôles d'utilisateurs, matérialisés par des groupes Django. Chaque utilisateur appartient à **un seul groupe** à la fois.

| Groupe | Désignation | Description |
|---|---|---|
| `DIRECTION` | Direction | Responsable général de l'établissement. Accès total. |
| `ADMINISTRATION` | Administration | Gestion administrative quotidienne (cours, EDT). |
| `SCOLARITE` | Scolarité | Gestion des inscriptions, absences, bulletins. |
| `FINANCES` | Finances | Gestion des frais de scolarité et des paiements. |
| `ENSEIGNANT` | Enseignant | Saisie des notes et des absences pour ses cours. |
| `ELEVE` | Élève | Consultation de son dossier scolaire personnel. |
| `PARENT` | Parent / Tuteur | Consultation du dossier des enfants qui lui sont liés. |

> **Note :** Les groupes `DIRECTION`, `ADMINISTRATION`, `SCOLARITE` et `FINANCES` sont collectivement désignés **Personnel administratif** (abrégé **PERSONNEL**) dans la suite du document.

### 2.2 Description des fonctions par acteur

#### DIRECTION
- Toutes les fonctions du personnel administratif ;
- Création et modification des comptes utilisateurs ;
- Activation d'une année scolaire ;
- Attribution des rôles aux comptes ;
- Accès complet à l'historique des actions.

#### ADMINISTRATION
- Création et gestion des cours (matière × classe × enseignant × année) ;
- Création et gestion des emplois du temps ;
- Gestion des salles et des matières ;
- Consultation des tableaux de bord et statistiques.

#### SCOLARITE
- Création et gestion des classes ;
- Inscription des élèves ;
- Validation des absences (justifiée / non justifiée) ;
- Génération des bulletins après clôture d'une période ;
- Export PDF des bulletins.

#### FINANCES
- Définition des tarifs de scolarité par niveau et par année ;
- Création des dossiers de frais de scolarité pour chaque élève ;
- Enregistrement des paiements (espèces, virement, mobile money) ;
- Consultation du tableau de bord financier.

#### ENSEIGNANT
- Consultation de ses cours et de son emploi du temps ;
- Saisie des notes pour ses propres cours uniquement ;
- Enregistrement des absences pour ses propres cours uniquement ;
- **Validation des absences (justifiée / non justifiée) pour ses propres cours uniquement ;**
- Consultation des bulletins des élèves de ses classes ;
- Envoi et réception de messages (vers **tout utilisateur actif** du système — personnel, enseignants, élèves, parents) ;
- Consultation des annonces (lecture seule) ;
- Consultation du calendrier scolaire.

#### ELEVE
- Consultation de ses propres notes et moyennes ;
- Consultation de ses absences ;
- Consultation de ses bulletins disponibles ;
- Consultation de son emploi du temps ;
- Envoi et réception de messages (vers le personnel et les enseignants uniquement — **pas les autres élèves ni les parents**) ;
- Réception des notifications et des annonces qui le concernent.

#### PARENT
- Consultation des notes, absences et bulletins de ses enfants ;
- Consultation de l'emploi du temps de ses enfants ;
- Consultation de la situation des frais de scolarité de ses enfants (lecture seule) ;
- Envoi et réception de messages (vers le personnel et les enseignants uniquement — **pas les élèves ni les autres parents**) ;
- Réception des notifications et des annonces concernant les classes de ses enfants.

### 2.3 Matrice des permissions

Le tableau ci-dessous récapitule les droits accordés à chaque groupe sur les principales fonctions du système. **C** = Créer, **L** = Lire, **M** = Modifier, **S** = Supprimer/Désactiver.

| Fonction | DIRECTION | ADMIN | SCOLARITE | FINANCES | ENSEIGNANT | ELEVE | PARENT |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Gestion comptes | CLMS | — | — | — | — | — | — |
| Gestion années scolaires | CLMS | — | L | L | L | L | L |
| Gestion périodes | CLMS | CLM | CLM | L | L | L | L |
| Gestion classes | CLMS | CLM | CLM | L | L | L | L |
| Gestion salles | CLMS | CLMS | L | L | L | — | — |
| Gestion matières | CLMS | CLMS | L | L | L | — | — |
| Gestion cours | CLMS | CLMS | L | L | L (ses cours) | — | — |
| Emploi du temps | CLMS | CLMS | L | L | L (son EDT) | L (son EDT) | L (EDT enfant) |
| Inscriptions élèves | CLMS | — | CLMS | L | — | L (sa fiche) | L (fiche enfant) |
| Saisie notes | — | — | — | — | CLM (ses cours) | — | — |
| Consultation notes | LM | L | L | — | L (ses cours) | L (ses notes) | L (notes enfant) |
| Enregistrement absences | — | — | — | — | C (ses cours) | — | — |
| Validation absences | — | — | CLM | — | CLM (ses cours) | L (ses abs.) | L (abs. enfant) |
| Génération bulletins | CL | — | CL | — | — | — | — |
| Consultation bulletins | L | L | L | — | L (ses élèves) | L (ses bulletins) | L (bulletins enfant) |
| Export PDF bulletin | L | L | L | — | L (ses élèves) | L (son bulletin) | L (bulletins enfant) |
| Tarifs scolarité | CLMS | — | — | CLMS | — | — | — |
| Frais scolarité | CLMS | — | — | CLMS | — | — | L (enfants) |
| Paiements | CLMS | — | — | CLMS | — | — | — |
| Messagerie (envoi) | CLM | CLM | CLM | CLM | CLM (tout le monde) | CLM (pers.+ens.) | CLM (pers.+ens.) |
| Annonces | CLM | CLM | CLM | CLM | L seul | L (ses classes) | L (classes enfants) |
| Calendrier scolaire | CLMS | CLM | L | L | L | L | L |
| Notifications | L | L | L | L | L | L | L |
| Historique actions | L | L | — | — | — | — | — |

---

## III. Règles de gestion

> **Convention de lecture :** Chaque règle est identifiée par un code `RG-XX-NN` où `XX` désigne le groupe thématique et `NN` le numéro séquentiel. Les termes utilisés dans les règles de gestion sont définis dans le **Dictionnaire des données** (Section IV) avant tout emploi.

### Définitions préalables

Les termes techniques suivants sont définis ici pour être utilisés sans ambiguïté dans les règles de gestion qui suivent.

- **Année scolaire (ANNEE_SCOLAIRE)** : période de 12 mois délimitée par une date de début et une date de fin, identifiée par un libellé unique (ex. : « 2025–2026 »). Une seule année peut être **active** à un instant donné.
- **Période (PERIODE)** : subdivision d'une année scolaire, de type *trimestre* (3 par an) ou *semestre* (2 par an). Elle possède une date de début, une date de fin, et un indicateur de **clôture**. Une période est dite **clôturée** lorsque son indicateur `cloturee` est à `Vrai`.
- **Classe (CLASSE)** : groupe d'élèves rattaché à une année scolaire, identifié par un nom unique pour cette année (ex. : « 3ème A »). Elle possède un **effectif maximum** et appartient à un **cycle** (premier ou second).
- **Cours (COURS)** : association entre une matière, une classe, un enseignant et une année scolaire. Un cours est unique pour la combinaison (matière, classe, année).
- **Inscription (INSCRIPTION)** : acte d'enregistrement d'un élève dans une classe pour une année scolaire. Son **statut** peut être *actif*, *transféré* ou *abandonné*. Un élève ne peut avoir qu'une seule inscription par année scolaire.
- **Note (NOTE)** : valeur numérique décimale entre 0 et 20 attribuée à un élève pour un cours et une période donnée, lors d'une **évaluation** de type *devoir surveillé*, *interrogation* ou *examen semestriel*.
- **Résultat matière (RESULTAT_MATIERE)** : entité calculée automatiquement représentant la **moyenne des notes** d'un élève pour un cours sur une période. Cette valeur n'est jamais saisie manuellement.
- **Bulletin (BULLETIN)** : document de synthèse généré automatiquement après la clôture d'une période, récapitulant la **moyenne générale** et le **rang** d'un élève dans sa classe. Il est unique pour la combinaison (élève, période).
- **Absence (ABSENCE)** : constat de non-présence d'un élève lors d'un cours. Elle est définie par une date, un nombre d'heures, un statut (*en_attente*, *justifiée*, *non_justifiée*) et un motif facultatif.
- **Emploi du temps (EMPLOI_DU_TEMPS)** : **créneau horaire** affectant un cours à une salle, un jour et une heure de début et de fin, pour une période donnée.
- **Salle (SALLE)** : local physique de l'établissement disposant d'une capacité d'accueil et d'un type (salle de cours, laboratoire, salle informatique, gymnase).
- **Matière (MATIERE)** : discipline académique caractérisée par un nom unique et un **coefficient** utilisé dans le calcul des moyennes pondérées.
- **Notification (NOTIFICATION)** : message système automatique envoyé à un destinataire individuel **ou** à tous les membres d'une classe. Une notification est soit individuelle, soit collective, jamais les deux.
- **Message (MESSAGE)** : communication privée entre deux utilisateurs identifiés, composée d'un sujet, d'un corps de texte et d'une pièce jointe optionnelle au format PDF.
- **Événement scolaire (EVENEMENT_SCOLAIRE)** : fait inscrit au calendrier de l'établissement avec une date de début et une date de fin. Son **type** peut être *vacances*, *examen*, *réunion*, *jour férié* ou *autre*.
- **Tarif de niveau (TARIF_NIVEAU)** : montant des frais de scolarité fixé par l'administration pour un niveau d'enseignement donné et une année scolaire. Il est unique pour la combinaison (année, niveau).
- **Frais de scolarité (FRAIS_SCOLARITE)** : dossier financier individuel d'un élève pour une année scolaire, contenant le montant dû, le montant payé et un statut (*en_attente*, *partiellement payé*, *payé*). Il est unique pour la combinaison (élève, année).
- **Paiement (PAIEMENT)** : enregistrement d'un versement effectué par un parent au titre des frais de scolarité. Chaque paiement est associé à un numéro de reçu unique.
- **Personne (PERSONNE)** : super-entité racine du système, représentant tout utilisateur humain quelle que soit son rôle. Elle est identifiée par son adresse **email** unique et possède un indicateur **actif**.
- **Historique des actions (HISTORIQUE_ACTIONS)** : journal de traçabilité enregistrant automatiquement toute action sensible effectuée dans le système (auteur, nature de l'action, table cible, identifiant de l'enregistrement affecté).

---

### RG-T — Temps scolaire

**RG-T01** — Une **ANNEE_SCOLAIRE** est définie par un **libellé** unique (ex. : « 2025–2026 »), une **date_debut** et une **date_fin**. La **date_debut** doit être strictement antérieure à la **date_fin**.

**RG-T02** — Une seule **ANNEE_SCOLAIRE** peut avoir le statut **active = Vrai** à un instant donné. L'activation d'une nouvelle année désactive automatiquement toute année précédemment active.

**RG-T03** — La suppression d'une **ANNEE_SCOLAIRE** est interdite si des entités lui sont rattachées (classes, périodes, cours, inscriptions).

**RG-T04** — Une **PERIODE** appartient obligatoirement à une **ANNEE_SCOLAIRE**. Son type est soit *trimestre*, soit *semestre*, et ce type doit être **uniforme** pour toutes les périodes d'une même année (on ne peut pas mélanger trimestres et semestres dans la même année).

**RG-T05** — Une année scolaire ne peut contenir que **3 trimestres au maximum** ou **2 semestres au maximum**.

**RG-T06** — Les périodes d'une même **ANNEE_SCOLAIRE** ne peuvent pas se chevaucher dans le temps. Si les intervalles [date_debut_A, date_fin_A] et [date_debut_B, date_fin_B] se croisent, la création est rejetée.

**RG-T07** — Une **PERIODE** ne peut être **clôturée** que si sa **date_fin** est inférieure ou égale à la date du jour. La clôture est irréversible.

---

### RG-C — Classes et inscriptions

**RG-C01** — Une **CLASSE** est identifiée par son **nom** et son **ANNEE_SCOLAIRE** de rattachement. La combinaison (nom, annee) doit être unique.

**RG-C02** — L'**effectif_max** d'une **CLASSE** définit le nombre maximal d'élèves pouvant y être inscrits avec le statut *actif* simultanément.

**RG-C03** — Un **ELEVE** (voir définition dans RG-H) ne peut avoir qu'une seule **INSCRIPTION** par **ANNEE_SCOLAIRE**, quelle que soit la **CLASSE**.

**RG-C04** — Une **INSCRIPTION** ne peut jamais être supprimée physiquement de la base. En cas de départ, son **statut** est mis à jour : *transféré* (changement d'établissement) ou *abandonné* (fin de scolarité).

**RG-C05** — Seules les inscriptions dont le **statut** est *actif* sont comptabilisées dans l'effectif d'une classe et dans les calculs de moyennes.

**RG-C06** — La suppression physique d'une **CLASSE** est interdite si des **INSCRIPTIONS** ou des **COURS** lui sont rattachés.

---

### RG-H — Hiérarchie des acteurs

**RG-H01** — Tout utilisateur du système est représenté par une **PERSONNE**. La **PERSONNE** est identifiée par son **email** unique.

**RG-H02** — Une **PERSONNE** joue **exactement un rôle** parmi : *PERSONNEL*, *ENSEIGNANT*, *ELEVE*, *PARENT*. Elle ne peut pas cumuler deux rôles.

**RG-H03** — Chaque rôle est représenté par une sous-entité reliée à **PERSONNE** par une relation un-à-un exclusive (OneToOneField avec primary_key) : **PERSONNEL**, **ENSEIGNANT**, **ELEVE**, **PARENT**.

**RG-H04** — La désactivation d'une **PERSONNE** (passage de **actif** à *Faux*) lui interdit toute connexion au système. La suppression physique d'une **PERSONNE** est interdite.

**RG-H05** — Un **PARENT** peut être lié à plusieurs **ELEVE** via l'entité **LIEN_PARENT_ELEVE**. Un **ELEVE** peut avoir plusieurs parents ou tuteurs. Le **lien** qui les unit est précisé (père, mère, tuteur, tutrice, autre). La combinaison (parent, élève) est unique.

**RG-H06** — Seule la **DIRECTION** (groupe Django `DIRECTION`) peut créer ou désactiver des comptes **PERSONNE** et attribuer des groupes.

---

### RG-E — Emploi du temps

**RG-E01** — Un **EMPLOI_DU_TEMPS** (créneau) est défini par un **COURS**, une **SALLE**, une **PERIODE**, un **jour** de la semaine (lundi à samedi), une **heure_debut** et une **heure_fin**. L'**heure_debut** doit être strictement antérieure à l'**heure_fin**.

**RG-E02** — Une **SALLE** ne peut pas accueillir deux cours différents sur le même créneau (même salle, même jour, même heure_debut, même période). La combinaison (salle, jour, heure_debut, periode) est unique.

**RG-E03** — Un **ENSEIGNANT** ne peut pas être affecté à deux cours différents sur le même créneau (même enseignant, même jour, même heure_debut, même période).

**RG-E04** — Une **CLASSE** ne peut pas avoir deux cours différents sur le même créneau (même classe, même jour, même heure_debut, même période).

**RG-E05** — La capacité d'une **SALLE** doit être supérieure ou égale au nombre d'élèves actifs inscrits dans la **CLASSE** du cours affecté à ce créneau.

**RG-E06** — Lors de l'attribution d'un créneau, une notification de type `edt_attribue` est automatiquement envoyée à l'enseignant concerné.

---

### RG-N — Notes et évaluations

**RG-N01** — Une **NOTE** est associée à un **ELEVE**, un **COURS**, une **PERIODE** et un **type_eval**. Les types d'évaluation autorisés sont : *devoir surveillé*, *interrogation*, *examen semestriel*.

**RG-N02** — L'**ELEVE** noté doit avoir une **INSCRIPTION** active dans la **CLASSE** du **COURS** pour la même **ANNEE_SCOLAIRE**.

**RG-N03** — La **valeur** d'une **NOTE** doit être comprise dans l'intervalle fermé [0 ; 20]. Cette contrainte est vérifiée en base de données par une contrainte CHECK.

**RG-N04** — Seul l'**ENSEIGNANT** titulaire du **COURS** peut saisir ou modifier une note pour ce cours.

**RG-N05** — Après toute saisie ou modification de note, le **RESULTAT_MATIERE** correspondant est **recalculé automatiquement** par un déclencheur applicatif (signal Django).

**RG-N06** — La saisie d'une **NOTE** est **interdite** si la **PERIODE** ciblée est **clôturée** (indicateur `cloturee = Vrai`) ou si sa **date_fin** est dépassée.

---

### RG-M — Moyennes et résultats matières

**RG-M01** — Un **RESULTAT_MATIERE** représente la **moyenne arithmétique** de toutes les notes d'un élève pour un cours donné sur une période donnée. Il est unique pour la combinaison (élève, cours, période).

**RG-M02** — La **moyenne** d'un **RESULTAT_MATIERE** est arrondie à deux décimales.

**RG-M03** — Le **RESULTAT_MATIERE** est recalculé automatiquement à chaque saisie ou modification de note, sans intervention manuelle.

**RG-M04** — Le **rang** d'un **RESULTAT_MATIERE** représente la position de l'élève par rapport aux autres élèves actifs de la même classe pour ce cours sur cette période. Il est calculé après tri décroissant des moyennes.

**RG-M05** — La **moyenne générale** d'un **BULLETIN** est la **moyenne pondérée** des **RESULTAT_MATIERE** de l'élève pour la période, pondérée par les **coefficients** des matières.

**RG-M06** — L'entité **RESULTAT_MATIERE** est exclusivement alimentée par des signaux applicatifs. Toute insertion ou modification manuelle directe est interdite.

---

### RG-AB — Absences

**RG-AB01** — Une **ABSENCE** est associée à un **ELEVE**, un **COURS**, une **PERIODE** et une **date_absence**. Elle comporte un **nb_heures** (nombre d'heures d'absence, entier positif), un **statut** et un **motif** facultatif.

**RG-AB02** — Le **statut** initial d'une **ABSENCE** enregistrée par un **ENSEIGNANT** est *en_attente*. La validation (passage à *justifiée* ou *non_justifiée*) est de la compétence de l'**ENSEIGNANT titulaire du cours**. La **SCOLARITE** peut également valider les absences à des fins de régularisation administrative.

**RG-AB03** — L'**ELEVE** absent doit avoir une **INSCRIPTION** active dans la **CLASSE** du **COURS** pour la même **ANNEE_SCOLAIRE**.

**RG-AB04** — Seul l'**ENSEIGNANT** titulaire du **COURS** peut enregistrer une **ABSENCE** pour ce cours.

**RG-AB05** — Après enregistrement d'une **ABSENCE**, une **NOTIFICATION** de type `absence_enregistree` est automatiquement envoyée à l'élève et à ses parents.

**RG-AB06** — Si le nombre total d'heures d'absence non justifiées d'un élève dépasse le seuil de **20 heures** sur la période, une **NOTIFICATION** de type `depassement_absences` est automatiquement envoyée à la scolarité et aux parents.

---

### RG-B — Bulletins

**RG-B01** — Un **BULLETIN** est unique pour la combinaison (élève, période). La contrainte UNIQUE est appliquée en base de données.

**RG-B02** — La génération d'un **BULLETIN** est interdite si la **PERIODE** ciblée n'est pas encore **clôturée** (indicateur `cloturee = Faux`) ou si sa **date_fin** est postérieure à la date du jour.

**RG-B03** — Lors de la génération d'un **BULLETIN**, les champs calculés **moyenne_generale**, **rang** et **effectif_classe** sont calculés et stockés de manière immuable. Ils ne sont plus recalculés après la clôture.

**RG-B04** — Après génération d'un **BULLETIN**, une **NOTIFICATION** de type `bulletin_disponible` est automatiquement envoyée à l'élève et à ses parents.

**RG-B05** — Un élève peut consulter son propre **BULLETIN**. Un parent peut consulter les bulletins de ses enfants. Un enseignant peut consulter les bulletins des élèves de ses classes. Un personnel administratif peut consulter tous les bulletins.

**RG-B06** — L'export PDF d'un **BULLETIN** est soumis aux mêmes restrictions d'accès que la consultation (RG-B05).

---

### RG-NO — Notifications

**RG-NO01** — Une **NOTIFICATION** peut être adressée soit à un **destinataire individuel** (une PERSONNE), soit à une **classe** (tous les membres de la CLASSE). Elle ne peut pas avoir les deux à la fois.

**RG-NO02** — Le **type_notif** d'une **NOTIFICATION** prend l'une des valeurs suivantes : *note_saisie*, *absence_enregistree*, *depassement_absences*, *bulletin_disponible*, *annonce*, *edt_attribue*.

**RG-NO03** — Une **NOTIFICATION** de type *annonce* est adressée à une **CLASSE** (pas à un individu). Les enseignants peuvent la consulter ; seul le **PERSONNEL** peut en créer.

**RG-NO04** — Toute **NOTIFICATION** est initialement **non lue** (`lu = Faux`). Le passage à *lu = Vrai* est effectué automatiquement à la première consultation par le destinataire.

---

### RG-MSG — Messagerie

**RG-MSG01** — Un **MESSAGE** est une communication privée d'un **expéditeur** (une PERSONNE) vers un **destinataire** (une PERSONNE). Il est composé d'un **sujet**, d'un **corps** et d'une **pièce_jointe** optionnelle.

**RG-MSG02** — La **pièce_jointe** d'un **MESSAGE**, si elle est fournie, doit être un fichier au format **PDF** exclusivement.

**RG-MSG03** — Les règles de filtrage des destinataires selon le rôle de l'expéditeur sont les suivantes :
  - Un **ENSEIGNANT** peut écrire à tout utilisateur actif du système : **PERSONNEL** (direction, administration, scolarité, finances), tout autre **ENSEIGNANT**, tout **PARENT** et tout **ELEVE**. La liste est présentée groupée par rôle et triée alphabétiquement, avec une barre de recherche.
  - Un **ELEVE** peut écrire à tout **PERSONNEL** et à tout **ENSEIGNANT** ; il ne peut pas écrire à d'autres **ELEVE** ni à des **PARENT**.
  - Un **PARENT** peut écrire à tout **PERSONNEL** et à tout **ENSEIGNANT** ; il ne peut pas écrire à des **ELEVE** ni à d'autres **PARENT**.
  - Un **PERSONNEL** peut écrire à tout utilisateur actif du système.

**RG-MSG04** — Un utilisateur ne peut lire un **MESSAGE** que s'il en est l'**expéditeur** ou le **destinataire**.

**RG-MSG05** — Un **MESSAGE** reçu est marqué **lu** (`lu = Vrai`) automatiquement lors de sa première consultation par le destinataire.

**RG-MSG06** — Un **MESSAGE** ne peut pas être supprimé par un utilisateur ; seul un administrateur système peut procéder à une suppression.

---

### RG-CAL — Calendrier scolaire

**RG-CAL01** — Un **EVENEMENT_SCOLAIRE** est défini par un **titre**, une **date_debut**, une **date_fin** et un **type_event**. Les types autorisés sont : *vacances*, *examen*, *réunion*, *jour_ferié*, *autre*.

**RG-CAL02** — La **date_debut** d'un **EVENEMENT_SCOLAIRE** doit être antérieure ou égale à sa **date_fin**.

**RG-CAL03** — Un **EVENEMENT_SCOLAIRE** peut être associé à une **ANNEE_SCOLAIRE** (optionnel). S'il n'est pas associé à une année, il est considéré comme permanent (ex. : jour férié récurrent).

**RG-CAL04** — Seul le **PERSONNEL** (direction et administration) peut créer ou modifier un **EVENEMENT_SCOLAIRE**. Tous les autres acteurs peuvent le consulter en lecture seule.

**RG-CAL05** — Le champ **createur** d'un **EVENEMENT_SCOLAIRE** enregistre la **PERSONNE** qui a créé l'événement. Ce champ est positionné à `NULL` si la personne créatrice est supprimée (SET NULL).

---

### RG-FIN — Finances et scolarité

**RG-FIN01** — Un **TARIF_NIVEAU** définit le montant des frais de scolarité pour un **niveau** donné dans une **ANNEE_SCOLAIRE** donnée. La combinaison (annee, niveau) est unique.

**RG-FIN02** — Un **FRAIS_SCOLARITE** est créé pour chaque élève inscrit, une fois par **ANNEE_SCOLAIRE**. La combinaison (élève, année) est unique.

**RG-FIN03** — Le **statut** d'un **FRAIS_SCOLARITE** est calculé automatiquement à partir du **montant_paye** et du **montant_du** :
  - Si **montant_paye** = 0 → statut = *en_attente*
  - Si 0 < **montant_paye** < **montant_du** → statut = *partiellement payé*
  - Si **montant_paye** ≥ **montant_du** → statut = *payé*

**RG-FIN04** — À chaque enregistrement d'un **PAIEMENT**, le **montant_paye** du **FRAIS_SCOLARITE** correspondant est **recalculé automatiquement** par sommation de tous les paiements associés. Le **statut** est mis à jour en conséquence.

**RG-FIN05** — Chaque **PAIEMENT** est associé à un **numéro de reçu** (recu_numero) unique dans toute la base de données. Ce numéro est généré automatiquement si non fourni (format : `REC-XXXXXXXX`).

**RG-FIN06** — Le **mode de paiement** d'un **PAIEMENT** peut être : *espèces*, *virement*, *mobile_money*.

**RG-FIN07** — Seul le **PERSONNEL** du groupe **FINANCES** (ou la **DIRECTION**) peut créer des **PAIEMENTS** et des **FRAIS_SCOLARITE**. Un **PARENT** peut consulter la situation de ses enfants en lecture seule. Les autres acteurs n'ont aucun accès financier.

**RG-FIN08** — Un **PAIEMENT** ne peut pas être supprimé. En cas d'erreur, un **PERSONNEL FINANCES** procède à une correction par ajout d'un paiement négatif avec justification dans le motif.

**RG-FIN09** — L'export PDF du **bilan financier** (récapitulatif des paiements et soldes de l'année active) est accessible au **groupe FINANCES** et à la **DIRECTION**. Les autres groupes n'ont pas accès à cet export.

---

### RG-A — Accès et sécurité

**RG-A01** — Toute accès au système requiert une authentification préalable. L'identifiant de connexion est l'**email** de la **PERSONNE** et le mot de passe est haché par l'algorithme **bcrypt**.

**RG-A02** — Une **PERSONNE** dont l'indicateur **actif** est *Faux* ne peut pas se connecter au système, même si elle dispose d'un mot de passe valide.

**RG-A03** — Chaque vue du système vérifie que l'utilisateur connecté appartient au groupe Django autorisé. Tout accès non autorisé donne lieu à un message d'erreur explicite et une redirection vers une page appropriée. Aucune erreur HTTP 403 (accès interdit) brute n'est affichée à l'utilisateur.

**RG-A04** — Un **ENSEIGNANT** ne peut accéder qu'aux données (notes, absences) des **COURS** dont il est le titulaire. Tout accès croisé est bloqué au niveau applicatif.

**RG-A05** — Un **ELEVE** ne peut accéder qu'à ses propres données. Un **PARENT** ne peut accéder qu'aux données des **ELEVE** liés à lui par un **LIEN_PARENT_ELEVE**.

**RG-A06** — Toute action sensible (création, modification, suppression d'un compte, activation d'une année, clôture d'une période, génération d'un bulletin) est enregistrée dans **HISTORIQUE_ACTIONS** avec l'identité de l'auteur, la nature de l'action, la table cible et l'identifiant de l'enregistrement affecté.

---

## IV. Dictionnaire des données

Le système ACADEMIQ repose sur **24 tables** (entités). Elles sont présentées dans l'ordre de création imposé par les dépendances de clés étrangères.

---

### Table 1 — PERSONNE

Super-entité racine. Tout utilisateur du système, quel que soit son rôle, est d'abord une PERSONNE.

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique unique |
| nom | VARCHAR(80) | NOT NULL | Nom de famille |
| prenom | VARCHAR(80) | NOT NULL | Prénom |
| email | VARCHAR(254) | NOT NULL, UNIQUE | Adresse email (identifiant de connexion) |
| password | VARCHAR(128) | NOT NULL | Mot de passe haché (bcrypt) |
| photo_profil | VARCHAR(100) | NULL | Chemin vers la photo de profil |
| actif | TINYINT(1) | NOT NULL, DEFAULT 1 | 1 = compte actif, 0 = compte désactivé |
| date_creation | DATETIME | NOT NULL, AUTO | Date et heure de création du compte |
| is_staff | TINYINT(1) | NOT NULL, DEFAULT 0 | Accès interface d'administration Django |
| is_superuser | TINYINT(1) | NOT NULL, DEFAULT 0 | Superutilisateur Django |

---

### Table 2 — ANNEE_SCOLAIRE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| libelle | VARCHAR(20) | NOT NULL, UNIQUE | Ex. : « 2025–2026 » |
| date_debut | DATE | NOT NULL | Date de début de l'année |
| date_fin | DATE | NOT NULL | Date de fin de l'année |
| active | TINYINT(1) | NOT NULL, DEFAULT 0 | Une seule année active à la fois (RG-T02) |

**Contrainte applicative :** date_debut < date_fin.

---

### Table 3 — PERIODE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| annee_id | BIGINT | FK → ANNEE_SCOLAIRE, CASCADE | Année scolaire de rattachement |
| nom | VARCHAR(50) | NOT NULL | Nom de la période (ex. : « Trimestre 1 ») |
| type_periode | VARCHAR(10) | NOT NULL, ENUM('trimestre','semestre') | Type de découpage |
| date_debut | DATE | NOT NULL | Début de la période |
| date_fin | DATE | NOT NULL | Fin de la période |
| cloturee | TINYINT(1) | NOT NULL, DEFAULT 0 | Indicateur de clôture (irréversible) |

**Contraintes applicatives :** date_debut < date_fin ; type uniforme par année ; pas de chevauchement ; max 3 trimestres ou 2 semestres (RG-T04 à RG-T07).

---

### Table 4 — SALLE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| numero | VARCHAR(10) | NOT NULL, UNIQUE | Numéro ou code de la salle (ex. : « B12 ») |
| batiment | VARCHAR(50) | NULL | Bâtiment de rattachement |
| capacite | SMALLINT UNSIGNED | NOT NULL, DEFAULT 0 | Nombre de places assises |
| type_salle | VARCHAR(20) | NOT NULL, DEFAULT 'salle_de_cours' | ENUM : salle_de_cours, laboratoire, salle_informatique, gymnase |

---

### Table 5 — MATIERE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| nom_matiere | VARCHAR(100) | NOT NULL, UNIQUE | Nom de la matière (ex. : « Mathématiques ») |
| coefficient | DECIMAL(3,1) | NOT NULL, DEFAULT 1.0 | Coefficient utilisé dans les moyennes pondérées |
| description | TEXT | NULL | Description pédagogique de la matière |

---

### Table 6 — PERSONNEL

Sous-entité de PERSONNE pour le personnel administratif.

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| personne_id | BIGINT | PK, FK → PERSONNE (CASCADE) | Clé primaire partagée avec PERSONNE |
| fonction | VARCHAR(20) | NOT NULL | ENUM : direction, administration, scolarite, finances |
| date_embauche | DATE | NULL | Date de prise de poste |

---

### Table 7 — ENSEIGNANT

Sous-entité de PERSONNE pour les enseignants.

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| personne_id | BIGINT | PK, FK → PERSONNE (CASCADE) | Clé primaire partagée avec PERSONNE |
| specialite | VARCHAR(100) | NOT NULL | Discipline principale de l'enseignant |
| grade | VARCHAR(50) | NULL | Grade académique (ex. : « PCEM », « CAPES ») |
| date_embauche | DATE | NULL | Date de prise de poste |

---

### Table 8 — ELEVE

Sous-entité de PERSONNE pour les élèves.

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| personne_id | BIGINT | PK, FK → PERSONNE (CASCADE) | Clé primaire partagée avec PERSONNE |
| date_naissance | DATE | NULL | Date de naissance |
| lieu_naissance | VARCHAR(100) | NULL | Lieu de naissance |
| matricule | VARCHAR(30) | UNIQUE, NULL | Matricule scolaire de l'élève |

---

### Table 9 — PARENT

Sous-entité de PERSONNE pour les parents et tuteurs.

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| personne_id | BIGINT | PK, FK → PERSONNE (CASCADE) | Clé primaire partagée avec PERSONNE |
| telephone | VARCHAR(20) | NULL | Numéro de téléphone |
| profession | VARCHAR(100) | NULL | Profession du parent |

---

### Table 10 — CLASSE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| nom | VARCHAR(50) | NOT NULL | Nom de la classe (ex. : « 3ème A ») |
| niveau | VARCHAR(50) | NULL | Niveau scolaire (ex. : « 3ème », « Terminale ») |
| cycle | VARCHAR(10) | NOT NULL | ENUM : premier, second |
| section | VARCHAR(10) | NULL | Section optionnelle (A, B, C…) |
| annee_id | BIGINT | FK → ANNEE_SCOLAIRE (RESTRICT) | Année scolaire de rattachement |
| effectif_max | SMALLINT UNSIGNED | NOT NULL, DEFAULT 40 | Capacité maximale de la classe |

**Contrainte UNIQUE :** (nom, annee_id).

---

### Table 11 — COURS

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| matiere_id | BIGINT | FK → MATIERE (RESTRICT) | Matière enseignée |
| classe_id | BIGINT | FK → CLASSE (RESTRICT) | Classe concernée |
| enseignant_id | BIGINT | FK → PERSONNE (RESTRICT) | Enseignant titulaire |
| annee_id | BIGINT | FK → ANNEE_SCOLAIRE (RESTRICT) | Année scolaire |
| nb_heures_hebdo | SMALLINT UNSIGNED | NOT NULL, DEFAULT 0 | Volume horaire hebdomadaire |

**Contrainte UNIQUE :** (matiere_id, classe_id, annee_id) — RG-C06 / unicité cours.

---

### Table 12 — EMPLOI_DU_TEMPS

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| cours_id | BIGINT | FK → COURS (CASCADE) | Cours concerné |
| salle_id | BIGINT | FK → SALLE (RESTRICT) | Salle affectée |
| periode_id | BIGINT | FK → PERIODE (RESTRICT) | Période d'application |
| jour | VARCHAR(10) | NOT NULL | ENUM : lundi, mardi, mercredi, jeudi, vendredi, samedi |
| heure_debut | TIME | NOT NULL | Heure de début du créneau |
| heure_fin | TIME | NOT NULL | Heure de fin du créneau |

**Contrainte UNIQUE :** (salle_id, jour, heure_debut, periode_id) — RG-E02.  
**Contraintes applicatives :** heure_debut < heure_fin ; pas de conflit enseignant (RG-E03) ; pas de conflit classe (RG-E04) ; capacité salle (RG-E05).

---

### Table 13 — INSCRIPTION

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| eleve_id | BIGINT | FK → PERSONNE (RESTRICT) | Élève inscrit |
| classe_id | BIGINT | FK → CLASSE (RESTRICT) | Classe d'inscription |
| annee_id | BIGINT | FK → ANNEE_SCOLAIRE (RESTRICT) | Année scolaire |
| date_inscription | DATE | NOT NULL | Date d'inscription |
| statut | VARCHAR(10) | NOT NULL, DEFAULT 'actif' | ENUM : actif, transfere, abandonne |

**Contrainte UNIQUE :** (eleve_id, annee_id) — RG-C03.

---

### Table 14 — LIEN_PARENT_ELEVE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| parent_id | BIGINT | FK → PERSONNE (RESTRICT) | Parent ou tuteur |
| eleve_id | BIGINT | FK → PERSONNE (RESTRICT) | Enfant concerné |
| lien | VARCHAR(10) | NOT NULL | ENUM : pere, mere, tuteur, tutrice, autre |

**Contrainte UNIQUE :** (parent_id, eleve_id) — RG-H05.

---

### Table 15 — NOTE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| valeur | DECIMAL(4,2) | NOT NULL, CHECK(0 ≤ valeur ≤ 20) | Note sur 20 (RG-N03) |
| type_eval | VARCHAR(20) | NOT NULL | ENUM : devoir_surveille, interrogation, examen_semestriel |
| commentaire | VARCHAR(200) | NULL | Commentaire facultatif de l'enseignant |
| date_saisie | DATE | NOT NULL, AUTO | Date de saisie automatique |
| eleve_id | BIGINT | FK → PERSONNE (RESTRICT) | Élève noté |
| cours_id | BIGINT | FK → COURS (RESTRICT) | Cours concerné |
| periode_id | BIGINT | FK → PERIODE (RESTRICT) | Période d'évaluation |

---

### Table 16 — RESULTAT_MATIERE

Entité calculée automatiquement. Jamais saisie manuellement (RG-M06).

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| eleve_id | BIGINT | FK → PERSONNE (RESTRICT) | Élève concerné |
| cours_id | BIGINT | FK → COURS (RESTRICT) | Cours concerné |
| periode_id | BIGINT | FK → PERIODE (RESTRICT) | Période |
| moyenne | DECIMAL(4,2) | NULL | Moyenne calculée (arrondie à 2 décimales) |
| rang | SMALLINT UNSIGNED | NULL | Rang de l'élève dans sa classe pour ce cours |

**Contrainte UNIQUE :** (eleve_id, cours_id, periode_id).

---

### Table 17 — ABSENCE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| eleve_id | BIGINT | FK → PERSONNE (RESTRICT) | Élève absent |
| cours_id | BIGINT | FK → COURS (RESTRICT) | Cours concerné |
| periode_id | BIGINT | FK → PERIODE (RESTRICT) | Période |
| date_absence | DATE | NOT NULL | Date de l'absence |
| nb_heures | SMALLINT UNSIGNED | NOT NULL, DEFAULT 1 | Nombre d'heures d'absence |
| statut | VARCHAR(15) | NOT NULL, DEFAULT 'en_attente' | ENUM : en_attente, justifiee, non_justifiee |
| motif | VARCHAR(200) | NULL | Motif de l'absence (si justifiée) |
| date_saisie | DATETIME | NOT NULL, AUTO | Date et heure de saisie automatique |

---

### Table 18 — BULLETIN

Entité générée après clôture de période. Jamais créée manuellement (RG-B02).

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| eleve_id | BIGINT | FK → PERSONNE (RESTRICT) | Élève concerné |
| periode_id | BIGINT | FK → PERIODE (RESTRICT) | Période clôturée |
| moyenne_generale | DECIMAL(4,2) | NULL | Moyenne générale pondérée (RG-M05) |
| rang | SMALLINT UNSIGNED | NULL | Rang dans la classe |
| effectif_classe | SMALLINT UNSIGNED | NULL | Effectif de la classe au moment de la clôture |
| appreciation | VARCHAR(300) | NULL | Appréciation générale du conseil de classe |
| date_generation | DATETIME | NOT NULL, AUTO | Date et heure de génération automatique |

**Contrainte UNIQUE :** (eleve_id, periode_id) — RG-B01.

---

### Table 19 — NOTIFICATION

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| destinataire_id | BIGINT | FK → PERSONNE (CASCADE), NULL | Destinataire individuel (NULL si classe cible) |
| classe_id | BIGINT | FK → CLASSE (SET NULL), NULL | Classe cible (NULL si destinataire individuel) |
| message | VARCHAR(500) | NOT NULL | Texte de la notification |
| type_notif | VARCHAR(25) | NOT NULL | ENUM : note_saisie, absence_enregistree, depassement_absences, bulletin_disponible, annonce, edt_attribue |
| lu | TINYINT(1) | NOT NULL, DEFAULT 0 | 0 = non lue, 1 = lue |
| date_envoi | DATETIME | NOT NULL, AUTO | Date et heure d'envoi automatique |

**Contrainte applicative :** destinataire_id XOR classe_id (exactement l'un des deux) — RG-NO01.

---

### Table 20 — MESSAGE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| expediteur_id | BIGINT | FK → PERSONNE (CASCADE) | Expéditeur du message |
| destinataire_id | BIGINT | FK → PERSONNE (CASCADE) | Destinataire du message |
| sujet | VARCHAR(150) | NOT NULL | Objet du message |
| corps | TEXT | NOT NULL | Corps du message |
| lu | TINYINT(1) | NOT NULL, DEFAULT 0 | 0 = non lu, 1 = lu |
| date_envoi | DATETIME | NOT NULL, AUTO | Date et heure d'envoi automatique |
| piece_jointe | VARCHAR(200) | NULL | Chemin vers la pièce jointe PDF (RG-MSG02) |

---

### Table 21 — EVENEMENT_SCOLAIRE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| titre | VARCHAR(150) | NOT NULL | Intitulé de l'événement |
| description | TEXT | NULL | Description détaillée |
| type_event | VARCHAR(15) | NOT NULL, DEFAULT 'autre' | ENUM : vacances, examen, reunion, ferie, autre |
| date_debut | DATE | NOT NULL | Date de début de l'événement |
| date_fin | DATE | NOT NULL | Date de fin de l'événement |
| annee_id | BIGINT | FK → ANNEE_SCOLAIRE (CASCADE), NULL | Année scolaire (NULL = événement permanent) |
| createur_id | BIGINT | FK → PERSONNE (SET NULL), NULL | Auteur de la création (RG-CAL05) |

---

### Table 22 — TARIF_NIVEAU

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| annee_id | BIGINT | FK → ANNEE_SCOLAIRE (CASCADE) | Année scolaire |
| niveau | VARCHAR(50) | NOT NULL | Niveau concerné (ex. : « 3ème », « 2nde ») |
| montant | DECIMAL(10,0) | NOT NULL | Montant des frais en FCFA |
| date_echeance | DATE | NULL | Date d'échéance de paiement |

**Contrainte UNIQUE :** (annee_id, niveau) — RG-FIN01.

---

### Table 23 — FRAIS_SCOLARITE

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| eleve_id | BIGINT | FK → PERSONNE (RESTRICT) | Élève concerné |
| annee_id | BIGINT | FK → ANNEE_SCOLAIRE (RESTRICT) | Année scolaire |
| montant_du | DECIMAL(10,0) | NOT NULL | Montant total dû |
| montant_paye | DECIMAL(10,0) | NOT NULL, DEFAULT 0 | Montant total payé (calculé automatiquement) |
| statut | VARCHAR(10) | NOT NULL, DEFAULT 'en_attente' | ENUM : en_attente, paye, partiel |
| date_echeance | DATE | NULL | Date d'échéance de règlement |
| date_maj | DATETIME | NOT NULL, AUTO_UPDATE | Date de dernière mise à jour automatique |

**Contrainte UNIQUE :** (eleve_id, annee_id) — RG-FIN02.  
**Propriété calculée :** reste_a_payer = montant_du − montant_paye.

---

### Table 24 — PAIEMENT

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| frais_id | BIGINT | FK → FRAIS_SCOLARITE (CASCADE) | Dossier de frais concerné |
| montant | DECIMAL(10,0) | NOT NULL | Montant versé en FCFA |
| date_paiement | DATE | NOT NULL | Date du versement |
| recu_numero | VARCHAR(30) | UNIQUE, NULL | Numéro de reçu unique (RG-FIN05) |
| mode | VARCHAR(20) | NOT NULL, DEFAULT 'especes' | ENUM : especes, virement, mobile_money |
| saisi_par_id | BIGINT | FK → PERSONNE (SET NULL), NULL | Agent ayant saisi le paiement |

---

### Table 25 — HISTORIQUE_ACTIONS

| Attribut | Type SQL | Contraintes | Description |
|---|---|---|---|
| id | BIGINT | PK, AUTO_INCREMENT | Identifiant technique |
| auteur_id | BIGINT | FK → PERSONNE (SET NULL), NULL | Auteur de l'action (NULL si compte supprimé) |
| action | VARCHAR(100) | NOT NULL | Description de l'action (ex. : « Saisie note ») |
| table_cible | VARCHAR(50) | NOT NULL | Nom de la table concernée (ex. : « note ») |
| id_enreg | INT UNSIGNED | NULL | Identifiant de l'enregistrement modifié |
| details | TEXT | NULL | Informations complémentaires |
| date_action | DATETIME | NOT NULL, AUTO | Horodatage automatique de l'action |

> **Bilan du dictionnaire :** 25 tables au total (24 entités métier + la table de jointure des groupes Django gérée par l'ORM). Les 24 entités définissent 95 attributs et 38 clés étrangères.

---

## V. Modèle Logique de Données (MLD)

Le passage du MCD au MLD applique les règles de transformation Merise :
- Toute entité devient une relation (table) ;
- Toute association (0,n)–(1,1) ou (1,n)–(1,1) se traduit par une clé étrangère côté (1,1) ;
- Toute association (0,n)–(0,n) génère une table de jonction avec les deux FK comme clé primaire composite.

Les clés primaires sont soulignées, les clés étrangères sont en italique.

```
ANNEE_SCOLAIRE  (id, libelle, date_debut, date_fin, active)

PERIODE  (id, nom, type_periode, date_debut, date_fin, cloturee, _annee_id#_)

SALLE  (id, numero, batiment, capacite, type_salle)

MATIERE  (id, nom_matiere, coefficient, description)

PERSONNE  (id, nom, prenom, email, password, photo_profil, actif, date_creation,
           is_staff, is_superuser)

PERSONNEL  (_personne_id#_, fonction, date_embauche)
  — personne_id référence PERSONNE(id) ON DELETE CASCADE

ENSEIGNANT  (_personne_id#_, specialite, grade, date_embauche)
  — personne_id référence PERSONNE(id) ON DELETE CASCADE

ELEVE  (_personne_id#_, date_naissance, lieu_naissance, matricule)
  — personne_id référence PERSONNE(id) ON DELETE CASCADE

PARENT  (_personne_id#_, telephone, profession)
  — personne_id référence PERSONNE(id) ON DELETE CASCADE

CLASSE  (id, nom, niveau, cycle, section, effectif_max, _annee_id#_)
  — UNIQUE(nom, annee_id)

COURS  (id, nb_heures_hebdo, _matiere_id#_, _classe_id#_, _enseignant_id#_, _annee_id#_)
  — UNIQUE(matiere_id, classe_id, annee_id)

EMPLOI_DU_TEMPS  (id, jour, heure_debut, heure_fin, _cours_id#_, _salle_id#_, _periode_id#_)
  — UNIQUE(salle_id, jour, heure_debut, periode_id)

INSCRIPTION  (id, date_inscription, statut, _eleve_id#_, _classe_id#_, _annee_id#_)
  — UNIQUE(eleve_id, annee_id)

LIEN_PARENT_ELEVE  (id, lien, _parent_id#_, _eleve_id#_)
  — UNIQUE(parent_id, eleve_id)

NOTE  (id, valeur, type_eval, commentaire, date_saisie, _eleve_id#_, _cours_id#_, _periode_id#_)

RESULTAT_MATIERE  (id, moyenne, rang, _eleve_id#_, _cours_id#_, _periode_id#_)
  — UNIQUE(eleve_id, cours_id, periode_id)

ABSENCE  (id, date_absence, nb_heures, statut, motif, date_saisie,
          _eleve_id#_, _cours_id#_, _periode_id#_)

BULLETIN  (id, moyenne_generale, rang, effectif_classe, appreciation, date_generation,
           _eleve_id#_, _periode_id#_)
  — UNIQUE(eleve_id, periode_id)

NOTIFICATION  (id, message, type_notif, lu, date_envoi,
               _destinataire_id#_, _classe_id#_)

MESSAGE  (id, sujet, corps, lu, date_envoi, piece_jointe,
          _expediteur_id#_, _destinataire_id#_)

EVENEMENT_SCOLAIRE  (id, titre, description, type_event, date_debut, date_fin,
                     _annee_id#_, _createur_id#_)

TARIF_NIVEAU  (id, niveau, montant, date_echeance, _annee_id#_)
  — UNIQUE(annee_id, niveau)

FRAIS_SCOLARITE  (id, montant_du, montant_paye, statut, date_echeance, date_maj,
                  _eleve_id#_, _annee_id#_)
  — UNIQUE(eleve_id, annee_id)

PAIEMENT  (id, montant, date_paiement, recu_numero, mode,
           _frais_id#_, _saisi_par_id#_)

HISTORIQUE_ACTIONS  (id, action, table_cible, id_enreg, details, date_action,
                     _auteur_id#_)
```

**Bilan MLD :** 24 tables, 38 clés étrangères, 12 contraintes UNIQUE composites.

---

## VI. Modèle Physique de Données (MPD)

Script SQL de création des tables pour MariaDB (moteur InnoDB, encodage utf8mb4). Les tables sont créées dans l'ordre des dépendances.

```sql
-- ============================================================
-- ACADEMIQ — Script MPD complet
-- SGBD : MariaDB 10.x / InnoDB / utf8mb4
-- ============================================================

SET FOREIGN_KEY_CHECKS = 0;

-- Table 1 : personne
CREATE TABLE `personne` (
    `id`            BIGINT NOT NULL AUTO_INCREMENT,
    `nom`           VARCHAR(80) NOT NULL,
    `prenom`        VARCHAR(80) NOT NULL,
    `email`         VARCHAR(254) NOT NULL,
    `password`      VARCHAR(128) NOT NULL,
    `photo_profil`  VARCHAR(100) NULL,
    `actif`         TINYINT(1) NOT NULL DEFAULT 1,
    `date_creation` DATETIME NOT NULL,
    `is_staff`      TINYINT(1) NOT NULL DEFAULT 0,
    `is_superuser`  TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_personne_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 2 : annee_scolaire
CREATE TABLE `annee_scolaire` (
    `id`          BIGINT NOT NULL AUTO_INCREMENT,
    `libelle`     VARCHAR(20) NOT NULL,
    `date_debut`  DATE NOT NULL,
    `date_fin`    DATE NOT NULL,
    `active`      TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_annee_libelle` (`libelle`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 3 : periode
CREATE TABLE `periode` (
    `id`           BIGINT NOT NULL AUTO_INCREMENT,
    `annee_id`     BIGINT NOT NULL,
    `nom`          VARCHAR(50) NOT NULL,
    `type_periode` VARCHAR(10) NOT NULL,
    `date_debut`   DATE NOT NULL,
    `date_fin`     DATE NOT NULL,
    `cloturee`     TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_periode_annee`
        FOREIGN KEY (`annee_id`) REFERENCES `annee_scolaire`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 4 : salle
CREATE TABLE `salle` (
    `id`         BIGINT NOT NULL AUTO_INCREMENT,
    `numero`     VARCHAR(10) NOT NULL,
    `batiment`   VARCHAR(50) NULL,
    `capacite`   SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    `type_salle` VARCHAR(20) NOT NULL DEFAULT 'salle_de_cours',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_salle_numero` (`numero`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 5 : matiere
CREATE TABLE `matiere` (
    `id`           BIGINT NOT NULL AUTO_INCREMENT,
    `nom_matiere`  VARCHAR(100) NOT NULL,
    `coefficient`  DECIMAL(3,1) NOT NULL DEFAULT 1.0,
    `description`  TEXT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_matiere_nom` (`nom_matiere`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 6 : personnel
CREATE TABLE `personnel` (
    `personne_id`   BIGINT NOT NULL,
    `fonction`      VARCHAR(20) NOT NULL,
    `date_embauche` DATE NULL,
    PRIMARY KEY (`personne_id`),
    CONSTRAINT `fk_personnel_personne`
        FOREIGN KEY (`personne_id`) REFERENCES `personne`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 7 : enseignant
CREATE TABLE `enseignant` (
    `personne_id`   BIGINT NOT NULL,
    `specialite`    VARCHAR(100) NOT NULL,
    `grade`         VARCHAR(50) NULL,
    `date_embauche` DATE NULL,
    PRIMARY KEY (`personne_id`),
    CONSTRAINT `fk_enseignant_personne`
        FOREIGN KEY (`personne_id`) REFERENCES `personne`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 8 : eleve
CREATE TABLE `eleve` (
    `personne_id`    BIGINT NOT NULL,
    `date_naissance` DATE NULL,
    `lieu_naissance` VARCHAR(100) NULL,
    `matricule`      VARCHAR(30) NULL,
    PRIMARY KEY (`personne_id`),
    UNIQUE KEY `uq_eleve_matricule` (`matricule`),
    CONSTRAINT `fk_eleve_personne`
        FOREIGN KEY (`personne_id`) REFERENCES `personne`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 9 : parent
CREATE TABLE `parent` (
    `personne_id` BIGINT NOT NULL,
    `telephone`   VARCHAR(20) NULL,
    `profession`  VARCHAR(100) NULL,
    PRIMARY KEY (`personne_id`),
    CONSTRAINT `fk_parent_personne`
        FOREIGN KEY (`personne_id`) REFERENCES `personne`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 10 : classe
CREATE TABLE `classe` (
    `id`           BIGINT NOT NULL AUTO_INCREMENT,
    `nom`          VARCHAR(50) NOT NULL,
    `niveau`       VARCHAR(50) NULL,
    `cycle`        VARCHAR(10) NOT NULL,
    `section`      VARCHAR(10) NULL,
    `annee_id`     BIGINT NOT NULL,
    `effectif_max` SMALLINT UNSIGNED NOT NULL DEFAULT 40,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_classe_nom_annee` (`nom`, `annee_id`),
    CONSTRAINT `fk_classe_annee`
        FOREIGN KEY (`annee_id`) REFERENCES `annee_scolaire`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 11 : cours
CREATE TABLE `cours` (
    `id`                BIGINT NOT NULL AUTO_INCREMENT,
    `matiere_id`        BIGINT NOT NULL,
    `classe_id`         BIGINT NOT NULL,
    `enseignant_id`     BIGINT NOT NULL,
    `annee_id`          BIGINT NOT NULL,
    `nb_heures_hebdo`   SMALLINT UNSIGNED NOT NULL DEFAULT 0,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_cours` (`matiere_id`, `classe_id`, `annee_id`),
    CONSTRAINT `fk_cours_matiere`
        FOREIGN KEY (`matiere_id`) REFERENCES `matiere`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_cours_classe`
        FOREIGN KEY (`classe_id`) REFERENCES `classe`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_cours_enseignant`
        FOREIGN KEY (`enseignant_id`) REFERENCES `personne`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_cours_annee`
        FOREIGN KEY (`annee_id`) REFERENCES `annee_scolaire`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 12 : emploi_du_temps
CREATE TABLE `emploi_du_temps` (
    `id`          BIGINT NOT NULL AUTO_INCREMENT,
    `cours_id`    BIGINT NOT NULL,
    `salle_id`    BIGINT NOT NULL,
    `periode_id`  BIGINT NOT NULL,
    `jour`        VARCHAR(10) NOT NULL,
    `heure_debut` TIME NOT NULL,
    `heure_fin`   TIME NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_salle_creneau` (`salle_id`, `jour`, `heure_debut`, `periode_id`),
    CONSTRAINT `fk_edt_cours`
        FOREIGN KEY (`cours_id`) REFERENCES `cours`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_edt_salle`
        FOREIGN KEY (`salle_id`) REFERENCES `salle`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_edt_periode`
        FOREIGN KEY (`periode_id`) REFERENCES `periode`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 13 : inscription
CREATE TABLE `inscription` (
    `id`                BIGINT NOT NULL AUTO_INCREMENT,
    `eleve_id`          BIGINT NOT NULL,
    `classe_id`         BIGINT NOT NULL,
    `annee_id`          BIGINT NOT NULL,
    `date_inscription`  DATE NOT NULL,
    `statut`            VARCHAR(10) NOT NULL DEFAULT 'actif',
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_eleve_annee` (`eleve_id`, `annee_id`),
    CONSTRAINT `fk_inscription_eleve`
        FOREIGN KEY (`eleve_id`) REFERENCES `personne`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_inscription_classe`
        FOREIGN KEY (`classe_id`) REFERENCES `classe`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_inscription_annee`
        FOREIGN KEY (`annee_id`) REFERENCES `annee_scolaire`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 14 : lien_parent_eleve
CREATE TABLE `lien_parent_eleve` (
    `id`        BIGINT NOT NULL AUTO_INCREMENT,
    `parent_id` BIGINT NOT NULL,
    `eleve_id`  BIGINT NOT NULL,
    `lien`      VARCHAR(10) NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_lien_parent_eleve` (`parent_id`, `eleve_id`),
    CONSTRAINT `fk_lien_parent`
        FOREIGN KEY (`parent_id`) REFERENCES `personne`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_lien_eleve`
        FOREIGN KEY (`eleve_id`) REFERENCES `personne`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 15 : note
CREATE TABLE `note` (
    `id`          BIGINT NOT NULL AUTO_INCREMENT,
    `valeur`      DECIMAL(4,2) NOT NULL,
    `type_eval`   VARCHAR(20) NOT NULL,
    `commentaire` VARCHAR(200) NULL,
    `date_saisie` DATE NOT NULL,
    `eleve_id`    BIGINT NOT NULL,
    `cours_id`    BIGINT NOT NULL,
    `periode_id`  BIGINT NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `chk_note_valeur`
        CHECK (`valeur` >= 0 AND `valeur` <= 20),
    CONSTRAINT `fk_note_eleve`
        FOREIGN KEY (`eleve_id`) REFERENCES `personne`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_note_cours`
        FOREIGN KEY (`cours_id`) REFERENCES `cours`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_note_periode`
        FOREIGN KEY (`periode_id`) REFERENCES `periode`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 16 : resultat_matiere (CALCULÉ — jamais inséré manuellement)
CREATE TABLE `resultat_matiere` (
    `id`         BIGINT NOT NULL AUTO_INCREMENT,
    `eleve_id`   BIGINT NOT NULL,
    `cours_id`   BIGINT NOT NULL,
    `periode_id` BIGINT NOT NULL,
    `moyenne`    DECIMAL(4,2) NULL,
    `rang`       SMALLINT UNSIGNED NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_resultat` (`eleve_id`, `cours_id`, `periode_id`),
    CONSTRAINT `fk_resultat_eleve`
        FOREIGN KEY (`eleve_id`) REFERENCES `personne`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_resultat_cours`
        FOREIGN KEY (`cours_id`) REFERENCES `cours`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_resultat_periode`
        FOREIGN KEY (`periode_id`) REFERENCES `periode`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 17 : absence
CREATE TABLE `absence` (
    `id`            BIGINT NOT NULL AUTO_INCREMENT,
    `eleve_id`      BIGINT NOT NULL,
    `cours_id`      BIGINT NOT NULL,
    `periode_id`    BIGINT NOT NULL,
    `date_absence`  DATE NOT NULL,
    `nb_heures`     SMALLINT UNSIGNED NOT NULL DEFAULT 1,
    `statut`        VARCHAR(15) NOT NULL DEFAULT 'en_attente',
    `motif`         VARCHAR(200) NULL,
    `date_saisie`   DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_absence_eleve`
        FOREIGN KEY (`eleve_id`) REFERENCES `personne`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_absence_cours`
        FOREIGN KEY (`cours_id`) REFERENCES `cours`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_absence_periode`
        FOREIGN KEY (`periode_id`) REFERENCES `periode`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 18 : bulletin (GÉNÉRÉ — jamais créé manuellement)
CREATE TABLE `bulletin` (
    `id`               BIGINT NOT NULL AUTO_INCREMENT,
    `eleve_id`         BIGINT NOT NULL,
    `periode_id`       BIGINT NOT NULL,
    `moyenne_generale` DECIMAL(4,2) NULL,
    `rang`             SMALLINT UNSIGNED NULL,
    `effectif_classe`  SMALLINT UNSIGNED NULL,
    `appreciation`     VARCHAR(300) NULL,
    `date_generation`  DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_bulletin_eleve_periode` (`eleve_id`, `periode_id`),
    CONSTRAINT `fk_bulletin_eleve`
        FOREIGN KEY (`eleve_id`) REFERENCES `personne`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_bulletin_periode`
        FOREIGN KEY (`periode_id`) REFERENCES `periode`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 19 : notification
CREATE TABLE `notification` (
    `id`               BIGINT NOT NULL AUTO_INCREMENT,
    `destinataire_id`  BIGINT NULL,
    `classe_id`        BIGINT NULL,
    `message`          VARCHAR(500) NOT NULL,
    `type_notif`       VARCHAR(25) NOT NULL,
    `lu`               TINYINT(1) NOT NULL DEFAULT 0,
    `date_envoi`       DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_notif_destinataire`
        FOREIGN KEY (`destinataire_id`) REFERENCES `personne`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_notif_classe`
        FOREIGN KEY (`classe_id`) REFERENCES `classe`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 20 : message
CREATE TABLE `message` (
    `id`               BIGINT NOT NULL AUTO_INCREMENT,
    `expediteur_id`    BIGINT NOT NULL,
    `destinataire_id`  BIGINT NOT NULL,
    `sujet`            VARCHAR(150) NOT NULL,
    `corps`            TEXT NOT NULL,
    `lu`               TINYINT(1) NOT NULL DEFAULT 0,
    `date_envoi`       DATETIME NOT NULL,
    `piece_jointe`     VARCHAR(200) NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_message_expediteur`
        FOREIGN KEY (`expediteur_id`) REFERENCES `personne`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_message_destinataire`
        FOREIGN KEY (`destinataire_id`) REFERENCES `personne`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 21 : evenement_scolaire
CREATE TABLE `evenement_scolaire` (
    `id`          BIGINT NOT NULL AUTO_INCREMENT,
    `titre`       VARCHAR(150) NOT NULL,
    `description` TEXT NULL,
    `type_event`  VARCHAR(15) NOT NULL DEFAULT 'autre',
    `date_debut`  DATE NOT NULL,
    `date_fin`    DATE NOT NULL,
    `annee_id`    BIGINT NULL,
    `createur_id` BIGINT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_event_annee`
        FOREIGN KEY (`annee_id`) REFERENCES `annee_scolaire`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_event_createur`
        FOREIGN KEY (`createur_id`) REFERENCES `personne`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 22 : tarif_niveau
CREATE TABLE `tarif_niveau` (
    `id`             BIGINT NOT NULL AUTO_INCREMENT,
    `annee_id`       BIGINT NOT NULL,
    `niveau`         VARCHAR(50) NOT NULL,
    `montant`        DECIMAL(10,0) NOT NULL,
    `date_echeance`  DATE NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_tarif_annee_niveau` (`annee_id`, `niveau`),
    CONSTRAINT `fk_tarif_annee`
        FOREIGN KEY (`annee_id`) REFERENCES `annee_scolaire`(`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 23 : frais_scolarite
CREATE TABLE `frais_scolarite` (
    `id`             BIGINT NOT NULL AUTO_INCREMENT,
    `eleve_id`       BIGINT NOT NULL,
    `annee_id`       BIGINT NOT NULL,
    `montant_du`     DECIMAL(10,0) NOT NULL,
    `montant_paye`   DECIMAL(10,0) NOT NULL DEFAULT 0,
    `statut`         VARCHAR(10) NOT NULL DEFAULT 'en_attente',
    `date_echeance`  DATE NULL,
    `date_maj`       DATETIME NOT NULL ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_frais_eleve_annee` (`eleve_id`, `annee_id`),
    CONSTRAINT `fk_frais_eleve`
        FOREIGN KEY (`eleve_id`) REFERENCES `personne`(`id`) ON DELETE RESTRICT,
    CONSTRAINT `fk_frais_annee`
        FOREIGN KEY (`annee_id`) REFERENCES `annee_scolaire`(`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 24 : paiement
CREATE TABLE `paiement` (
    `id`             BIGINT NOT NULL AUTO_INCREMENT,
    `frais_id`       BIGINT NOT NULL,
    `montant`        DECIMAL(10,0) NOT NULL,
    `date_paiement`  DATE NOT NULL,
    `recu_numero`    VARCHAR(30) NULL,
    `mode`           VARCHAR(20) NOT NULL DEFAULT 'especes',
    `saisi_par_id`   BIGINT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uq_paiement_recu` (`recu_numero`),
    CONSTRAINT `fk_paiement_frais`
        FOREIGN KEY (`frais_id`) REFERENCES `frais_scolarite`(`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_paiement_saisi_par`
        FOREIGN KEY (`saisi_par_id`) REFERENCES `personne`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table 25 : historique_actions
CREATE TABLE `historique_actions` (
    `id`           BIGINT NOT NULL AUTO_INCREMENT,
    `auteur_id`    BIGINT NULL,
    `action`       VARCHAR(100) NOT NULL,
    `table_cible`  VARCHAR(50) NOT NULL,
    `id_enreg`     INT UNSIGNED NULL,
    `details`      TEXT NULL,
    `date_action`  DATETIME NOT NULL,
    PRIMARY KEY (`id`),
    CONSTRAINT `fk_historique_auteur`
        FOREIGN KEY (`auteur_id`) REFERENCES `personne`(`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
```

---

## VII. Bilan et conclusion

Ce cahier des charges présente la conception complète de la base de données du système ACADEMIQ, élaborée selon la méthode Merise. La base repose sur 24 tables relationnelles normalisées en troisième forme normale, 38 clés étrangères, 12 contraintes UNIQUE composites et 59 règles de gestion couvrant l'ensemble des domaines fonctionnels : gestion temporelle, pédagogie, évaluation des élèves, suivi des absences, édition des bulletins, finances et communication interne.

Les choix de conception retenus — suppression logique uniquement, données calculées en lecture seule via les signaux applicatifs Django, unicité de l'année scolaire active et traçabilité systématique dans HISTORIQUE_ACTIONS — garantissent l'intégrité, la cohérence et la sécurité des données scolaires sur le long terme.

Ce document constitue la référence technique pour toute évolution ou maintenance du système ACADEMIQ.

---

*Document rédigé selon la méthode Merise (MCD → MLD → MPD, normalisation 3FN).*  
*ACADEMIQ — Cahier des charges BDD — Juin 2026*  
*MARIKO Lamine · CI0223065023 · Master 1 Génie Informatique · Université Nangui Abrogoua*  
*Encadreur : Dr. ZEZE*
