from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


# ─────────────────────────────────────────
# 1. Personne (AbstractBaseUser)
# ─────────────────────────────────────────

class PersonneManager(BaseUserManager):
    def create_user(self, email, nom, prenom, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est obligatoire.")
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

    def get_short_name(self):
        return self.prenom

    def get_role(self):
        for role in ['personnel', 'enseignant', 'eleve', 'parent']:
            if hasattr(self, role):
                return role
        return None

    def __str__(self):
        return self.get_full_name()

    class Meta:
        db_table = 'personne'
        verbose_name = 'Personne'
        verbose_name_plural = 'Personnes'


# ─────────────────────────────────────────
# 2. AnneeScolaire
# ─────────────────────────────────────────

class AnneeScolaire(models.Model):
    libelle = models.CharField(max_length=20, unique=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    active = models.BooleanField(default=False)

    def clean(self):
        if self.date_debut >= self.date_fin:
            raise ValidationError("La date de début doit être antérieure à la date de fin.")

    def __str__(self):
        return self.libelle

    class Meta:
        db_table = 'annee_scolaire'
        verbose_name = 'Année scolaire'
        verbose_name_plural = 'Années scolaires'
        ordering = ['-date_debut']


# ─────────────────────────────────────────
# 3. Periode
# ─────────────────────────────────────────

class Periode(models.Model):
    TYPES = [
        ('trimestre', 'Trimestre'),
        ('semestre', 'Semestre'),
    ]
    annee = models.ForeignKey(AnneeScolaire, on_delete=models.CASCADE, related_name='periodes')
    nom = models.CharField(max_length=50)
    type_periode = models.CharField(max_length=10, choices=TYPES)
    date_debut = models.DateField()
    date_fin = models.DateField()
    cloturee = models.BooleanField(default=False)

    def clean(self):
        if self.date_debut and self.date_fin:
            if self.date_debut >= self.date_fin:
                raise ValidationError("La date de début doit être antérieure à la date de fin.")

        if self.annee_id and self.type_periode and self.date_debut and self.date_fin:
            autres = Periode.objects.filter(annee_id=self.annee_id)
            if self.pk:
                autres = autres.exclude(pk=self.pk)

            # RG: type uniforme pour toute l'année (trimestres OU semestres, jamais mélange)
            if autres.exists():
                type_existant = autres.values_list('type_periode', flat=True).first()
                if type_existant != self.type_periode:
                    raise ValidationError(
                        f"Cette année utilise déjà des {type_existant}s. "
                        f"Impossible de mélanger trimestres et semestres."
                    )

            # RG: max 2 semestres ou 3 trimestres par année
            nb_max = 2 if self.type_periode == 'semestre' else 3
            if autres.count() >= nb_max:
                raise ValidationError(
                    f"Une année scolaire ne peut avoir que {nb_max} "
                    f"{'semestres' if self.type_periode == 'semestre' else 'trimestres'}."
                )

            # RG: pas de chevauchement de dates entre périodes de la même année
            chevauchement = autres.filter(
                date_debut__lt=self.date_fin,
                date_fin__gt=self.date_debut,
            )
            if chevauchement.exists():
                p = chevauchement.first()
                raise ValidationError(
                    f"Ces dates chevauchent avec '{p.nom}' ({p.date_debut} - {p.date_fin})."
                )

    def __str__(self):
        return f"{self.nom} — {self.annee}"

    class Meta:
        db_table = 'periode'
        verbose_name = 'Période'
        verbose_name_plural = 'Périodes'
        ordering = ['date_debut']


# ─────────────────────────────────────────
# 4. Salle
# ─────────────────────────────────────────

class Salle(models.Model):
    TYPES_SALLE = [
        ('salle_de_cours',    'Salle de cours'),
        ('laboratoire',       'Laboratoire'),
        ('salle_informatique','Salle informatique'),
        ('gymnase',           'Gymnase'),
    ]
    numero   = models.CharField(max_length=10, unique=True)
    batiment = models.CharField(max_length=50, blank=True)
    capacite = models.PositiveSmallIntegerField(default=0)
    type_salle = models.CharField(max_length=20, choices=TYPES_SALLE, default='salle_de_cours')

    def __str__(self):
        return f"{self.numero} ({self.get_type_salle_display()})"

    class Meta:
        db_table = 'salle'
        verbose_name = 'Salle'
        verbose_name_plural = 'Salles'


# ─────────────────────────────────────────
# 5. Matiere
# ─────────────────────────────────────────

class Matiere(models.Model):
    nom_matiere = models.CharField(max_length=100, unique=True)
    coefficient = models.DecimalField(max_digits=3, decimal_places=1, default=1.0)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.nom_matiere} (coeff. {self.coefficient})"

    class Meta:
        db_table = 'matiere'
        verbose_name = 'Matière'
        verbose_name_plural = 'Matières'


# ─────────────────────────────────────────
# 6. Personnel
# ─────────────────────────────────────────

class Personnel(models.Model):
    FONCTIONS = [
        ('direction', 'Direction'),
        ('administration', 'Administration'),
        ('scolarite', 'Scolarité'),
        ('finances', 'Finances'),
    ]
    personne = models.OneToOneField(
        Personne, on_delete=models.CASCADE,
        primary_key=True, related_name='personnel'
    )
    fonction = models.CharField(max_length=20, choices=FONCTIONS)
    date_embauche = models.DateField(null=True, blank=True)

    def clean(self):
        if not self.personne_id:
            return
        for role in ['enseignant', 'eleve', 'parent']:
            if hasattr(self.personne, role):
                raise ValidationError(f"Cette personne a déjà le rôle : {role}.")

    def __str__(self):
        return f"{self.personne.get_full_name()} ({self.get_fonction_display()})"

    class Meta:
        db_table = 'personnel'
        verbose_name = 'Personnel'
        verbose_name_plural = 'Personnels'


# ─────────────────────────────────────────
# 7. Enseignant
# ─────────────────────────────────────────

class Enseignant(models.Model):
    personne = models.OneToOneField(
        Personne, on_delete=models.CASCADE,
        primary_key=True, related_name='enseignant'
    )
    specialite = models.CharField(max_length=100)
    grade = models.CharField(max_length=50, blank=True)
    date_embauche = models.DateField(null=True, blank=True)

    def clean(self):
        if not self.personne_id:
            return
        for role in ['personnel', 'eleve', 'parent']:
            if hasattr(self.personne, role):
                raise ValidationError(f"Cette personne a déjà le rôle : {role}.")

    def __str__(self):
        return f"{self.personne.get_full_name()} — {self.specialite}"

    class Meta:
        db_table = 'enseignant'
        verbose_name = 'Enseignant'
        verbose_name_plural = 'Enseignants'


# ─────────────────────────────────────────
# 8. Eleve
# ─────────────────────────────────────────

class Eleve(models.Model):
    personne = models.OneToOneField(
        Personne, on_delete=models.CASCADE,
        primary_key=True, related_name='eleve'
    )
    date_naissance = models.DateField(null=True, blank=True)
    lieu_naissance = models.CharField(max_length=100, blank=True)
    matricule = models.CharField(max_length=30, unique=True, blank=True)

    def clean(self):
        if not self.personne_id:
            return
        for role in ['personnel', 'enseignant', 'parent']:
            if hasattr(self.personne, role):
                raise ValidationError(f"Cette personne a déjà le rôle : {role}.")

    def get_classe_actuelle(self):
        annee = AnneeScolaire.objects.filter(active=True).first()
        if not annee:
            return None
        insc = self.personne.inscriptions.filter(annee=annee, statut='actif').first()
        return insc.classe if insc else None

    def __str__(self):
        return self.personne.get_full_name()

    class Meta:
        db_table = 'eleve'
        verbose_name = 'Élève'
        verbose_name_plural = 'Élèves'


# ─────────────────────────────────────────
# 9. Parent
# ─────────────────────────────────────────

class Parent(models.Model):
    personne = models.OneToOneField(
        Personne, on_delete=models.CASCADE,
        primary_key=True, related_name='parent'
    )
    telephone = models.CharField(max_length=20, blank=True)
    profession = models.CharField(max_length=100, blank=True)

    def clean(self):
        if not self.personne_id:
            return
        for role in ['personnel', 'enseignant', 'eleve']:
            if hasattr(self.personne, role):
                raise ValidationError(f"Cette personne a déjà le rôle : {role}.")

    def __str__(self):
        return self.personne.get_full_name()

    class Meta:
        db_table = 'parent'
        verbose_name = 'Parent'
        verbose_name_plural = 'Parents'


# ─────────────────────────────────────────
# 10. Classe
# ─────────────────────────────────────────

class Classe(models.Model):
    CYCLES = [
        ('premier', 'Premier cycle'),
        ('second', 'Second cycle'),
    ]
    nom = models.CharField(max_length=50)
    niveau = models.CharField(max_length=50, blank=True)
    cycle = models.CharField(max_length=10, choices=CYCLES, default='premier')
    section = models.CharField(max_length=10, blank=True)
    annee = models.ForeignKey(AnneeScolaire, on_delete=models.RESTRICT, related_name='classes')
    effectif_max = models.PositiveSmallIntegerField(default=40)

    def __str__(self):
        return f"{self.nom} — {self.annee}"

    class Meta:
        db_table = 'classe'
        verbose_name = 'Classe'
        verbose_name_plural = 'Classes'
        constraints = [
            models.UniqueConstraint(fields=['nom', 'annee'], name='unique_classe_par_annee')
        ]


# ─────────────────────────────────────────
# 11. Cours
# ─────────────────────────────────────────

class Cours(models.Model):
    matiere = models.ForeignKey(Matiere, on_delete=models.RESTRICT, related_name='cours')
    classe = models.ForeignKey(Classe, on_delete=models.RESTRICT, related_name='cours')
    enseignant = models.ForeignKey(Personne, on_delete=models.RESTRICT, related_name='cours_enseignes')
    annee = models.ForeignKey(AnneeScolaire, on_delete=models.RESTRICT, related_name='cours')
    nb_heures_hebdo = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        return f"{self.matiere.nom_matiere} — {self.classe.nom}"

    class Meta:
        db_table = 'cours'
        verbose_name = 'Cours'
        verbose_name_plural = 'Cours'
        constraints = [
            models.UniqueConstraint(
                fields=['matiere', 'classe', 'annee'],
                name='unique_cours_matiere_classe_annee'
            )
        ]


# ─────────────────────────────────────────
# 12. EmploiDuTemps
# ─────────────────────────────────────────

class EmploiDuTemps(models.Model):
    JOURS = [
        ('lundi', 'Lundi'), ('mardi', 'Mardi'), ('mercredi', 'Mercredi'),
        ('jeudi', 'Jeudi'), ('vendredi', 'Vendredi'), ('samedi', 'Samedi'),
    ]
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='creneaux')
    salle = models.ForeignKey(Salle, on_delete=models.RESTRICT, related_name='creneaux')
    periode = models.ForeignKey(Periode, on_delete=models.RESTRICT, related_name='creneaux')
    jour = models.CharField(max_length=10, choices=JOURS)
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()

    def clean(self):
        if self.heure_debut and self.heure_fin:
            if self.heure_debut >= self.heure_fin:
                raise ValidationError("L'heure de debut doit etre anterieure a l'heure de fin.")

        # RG3: une salle ne peut pas etre affectee a deux cours sur le meme creneau
        if self.salle_id and self.jour and self.heure_debut and self.periode_id:
            conflit = EmploiDuTemps.objects.filter(
                salle=self.salle_id,
                jour=self.jour,
                heure_debut=self.heure_debut,
                periode=self.periode_id,
            )
            if self.pk:
                conflit = conflit.exclude(pk=self.pk)
            if conflit.exists():
                autre = conflit.first()
                raise ValidationError(
                    f"La salle est deja occupee ce creneau par : {autre.cours}."
                )

        # RG-ENS06: un enseignant ne peut pas avoir deux cours en meme temps
        if self.cours_id and self.jour and self.heure_debut and self.periode_id:
            try:
                cours_courant = Cours.objects.get(pk=self.cours_id)
                conflit_ens = EmploiDuTemps.objects.filter(
                    cours__enseignant=cours_courant.enseignant,
                    jour=self.jour,
                    heure_debut=self.heure_debut,
                    periode=self.periode_id,
                ).exclude(cours=self.cours_id)
                if self.pk:
                    conflit_ens = conflit_ens.exclude(pk=self.pk)
                if conflit_ens.exists():
                    autre = conflit_ens.first()
                    raise ValidationError(
                        f"L'enseignant a deja un cours ce creneau : {autre.cours}."
                    )
            except Cours.DoesNotExist:
                pass

        # RG-ENS07: une classe ne peut pas avoir deux cours en meme temps
        if self.cours_id and self.jour and self.heure_debut and self.periode_id:
            try:
                cours_courant = Cours.objects.get(pk=self.cours_id)
                conflit_cls = EmploiDuTemps.objects.filter(
                    cours__classe=cours_courant.classe,
                    jour=self.jour,
                    heure_debut=self.heure_debut,
                    periode=self.periode_id,
                ).exclude(cours=self.cours_id)
                if self.pk:
                    conflit_cls = conflit_cls.exclude(pk=self.pk)
                if conflit_cls.exists():
                    autre = conflit_cls.first()
                    raise ValidationError(
                        f"La classe a deja un cours ce creneau : {autre.cours}."
                    )
            except Cours.DoesNotExist:
                pass

        # RG4: nb eleves inscrit dans la classe <= capacite de la salle
        if self.salle_id and self.cours_id:
            try:
                salle = Salle.objects.get(pk=self.salle_id)
                cours = Cours.objects.select_related('classe', 'annee').get(pk=self.cours_id)
                nb_eleves = Inscription.objects.filter(
                    classe=cours.classe, annee=cours.annee, statut='actif'
                ).count()
                if salle.capacite > 0 and nb_eleves > salle.capacite:
                    raise ValidationError(
                        f"La salle ({salle.capacite} places) est trop petite pour la classe "
                        f"({nb_eleves} eleves inscrits)."
                    )
            except Exception as e:
                if isinstance(e, ValidationError):
                    raise

    def __str__(self):
        return f"{self.cours} - {self.get_jour_display()} {self.heure_debut}"

    class Meta:
        db_table = 'emploi_du_temps'
        verbose_name = 'Emploi du temps'
        verbose_name_plural = 'Emplois du temps'
        constraints = [
            models.UniqueConstraint(
                fields=['salle', 'jour', 'heure_debut', 'periode'],
                name='unique_salle_creneau'
            )
        ]


# ─────────────────────────────────────────
# 13. Inscription
# ─────────────────────────────────────────

class Inscription(models.Model):
    STATUTS = [
        ('actif', 'Actif'),
        ('transfere', 'Transféré'),
        ('abandonne', 'Abandonné'),
    ]
    eleve = models.ForeignKey(Personne, on_delete=models.RESTRICT, related_name='inscriptions')
    classe = models.ForeignKey(Classe, on_delete=models.RESTRICT, related_name='inscriptions')
    annee = models.ForeignKey(AnneeScolaire, on_delete=models.RESTRICT, related_name='inscriptions')
    date_inscription = models.DateField(default=timezone.now)
    statut = models.CharField(max_length=10, choices=STATUTS, default='actif')

    def clean(self):
        # RG: un élève ne peut être inscrit qu'une seule fois par année scolaire
        if self.eleve_id and self.annee_id:
            qs = Inscription.objects.filter(eleve_id=self.eleve_id, annee_id=self.annee_id)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError("Cet élève est déjà inscrit pour cette année scolaire.")

    def __str__(self):
        return f"{self.eleve.get_full_name()} — {self.classe.nom} ({self.annee})"

    class Meta:
        db_table = 'inscription'
        verbose_name = 'Inscription'
        verbose_name_plural = 'Inscriptions'
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'annee'],
                name='unique_eleve_par_annee'  # RG-C03
            )
        ]


# ─────────────────────────────────────────
# 14. LienParentEleve
# ─────────────────────────────────────────

class LienParentEleve(models.Model):
    LIENS = [
        ('pere', 'Père'), ('mere', 'Mère'), ('tuteur', 'Tuteur'),
        ('tutrice', 'Tutrice'), ('autre', 'Autre'),
    ]
    parent = models.ForeignKey(Personne, on_delete=models.RESTRICT, related_name='enfants')
    eleve = models.ForeignKey(Personne, on_delete=models.RESTRICT, related_name='parents_lies')
    lien = models.CharField(max_length=10, choices=LIENS)

    def __str__(self):
        return f"{self.parent.get_full_name()} → {self.eleve.get_full_name()} ({self.get_lien_display()})"

    class Meta:
        db_table = 'lien_parent_eleve'
        verbose_name = 'Lien parent–élève'
        verbose_name_plural = 'Liens parent–élève'
        constraints = [
            models.UniqueConstraint(fields=['parent', 'eleve'], name='unique_lien_parent_eleve')
        ]


# ─────────────────────────────────────────
# 15. Note
# ─────────────────────────────────────────

class Note(models.Model):
    TYPES_EVAL = [
        ('devoir_surveille', 'Devoir surveillé'),
        ('interrogation', 'Interrogation'),
        ('examen_semestriel', 'Examen semestriel'),
    ]
    valeur = models.DecimalField(max_digits=4, decimal_places=2)
    type_eval = models.CharField(max_length=20, choices=TYPES_EVAL)
    commentaire = models.CharField(max_length=200, blank=True)
    date_saisie = models.DateField(auto_now_add=True)
    eleve = models.ForeignKey(Personne, on_delete=models.RESTRICT, related_name='notes')
    cours = models.ForeignKey(Cours, on_delete=models.RESTRICT, related_name='notes')
    periode = models.ForeignKey(Periode, on_delete=models.RESTRICT, related_name='notes')

    def __str__(self):
        return f"{self.eleve.get_full_name()} — {self.cours.matiere.nom_matiere} : {self.valeur}/20"

    class Meta:
        db_table = 'note'
        verbose_name = 'Note'
        verbose_name_plural = 'Notes'
        constraints = [
            models.CheckConstraint(
                condition=models.Q(valeur__gte=0) & models.Q(valeur__lte=20),
                name='note_valeur_entre_0_et_20'  # RG-N03
            )
        ]


# ─────────────────────────────────────────
# 16. ResultatMatiere (CALCULÉ — jamais saisi manuellement)
# ─────────────────────────────────────────

class ResultatMatiere(models.Model):
    eleve = models.ForeignKey(Personne, on_delete=models.RESTRICT, related_name='resultats')
    cours = models.ForeignKey(Cours, on_delete=models.RESTRICT, related_name='resultats')
    periode = models.ForeignKey(Periode, on_delete=models.RESTRICT, related_name='resultats')
    moyenne = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    rang = models.PositiveSmallIntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.eleve.get_full_name()} — {self.cours.matiere.nom_matiere} : {self.moyenne}/20"

    class Meta:
        db_table = 'resultat_matiere'
        verbose_name = 'Résultat matière'
        verbose_name_plural = 'Résultats matières'
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'cours', 'periode'],
                name='unique_resultat_eleve_cours_periode'
            )
        ]


# ─────────────────────────────────────────
# 17. Absence
# ─────────────────────────────────────────

class Absence(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('justifiee', 'Justifiée'),
        ('non_justifiee', 'Non justifiée'),
    ]
    eleve = models.ForeignKey(Personne, on_delete=models.RESTRICT, related_name='absences')
    cours = models.ForeignKey(Cours, on_delete=models.RESTRICT, related_name='absences')
    periode = models.ForeignKey(Periode, on_delete=models.RESTRICT, related_name='absences')
    date_absence = models.DateField()
    nb_heures = models.PositiveSmallIntegerField(default=1)
    statut = models.CharField(max_length=15, choices=STATUTS, default='en_attente')
    motif = models.CharField(max_length=200, blank=True)
    date_saisie = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.eleve.get_full_name()} — {self.date_absence} ({self.get_statut_display()})"

    class Meta:
        db_table = 'absence'
        verbose_name = 'Absence'
        verbose_name_plural = 'Absences'


# ─────────────────────────────────────────
# 18. Bulletin (GÉNÉRÉ après clôture période)
# ─────────────────────────────────────────

class Bulletin(models.Model):
    eleve = models.ForeignKey(Personne, on_delete=models.RESTRICT, related_name='bulletins')
    periode = models.ForeignKey(Periode, on_delete=models.RESTRICT, related_name='bulletins')
    moyenne_generale = models.DecimalField(max_digits=4, decimal_places=2, null=True)
    rang = models.PositiveSmallIntegerField(null=True, blank=True)
    effectif_classe = models.PositiveSmallIntegerField(null=True, blank=True)
    appreciation = models.CharField(max_length=300, blank=True)
    date_generation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bulletin {self.eleve.get_full_name()} — {self.periode}"

    class Meta:
        db_table = 'bulletin'
        verbose_name = 'Bulletin'
        verbose_name_plural = 'Bulletins'
        constraints = [
            models.UniqueConstraint(
                fields=['eleve', 'periode'],
                name='unique_bulletin_eleve_periode'  # RG-B01
            )
        ]


# ─────────────────────────────────────────
# 19. Notification
# ─────────────────────────────────────────

class Notification(models.Model):
    TYPES = [
        ('note_saisie',          'Note saisie'),
        ('absence_enregistree',  'Absence enregistrée'),
        ('depassement_absences', 'Dépassement seuil absences'),
        ('bulletin_disponible',  'Bulletin disponible'),
        ('annonce',              'Annonce générale'),
    ]
    destinataire = models.ForeignKey(
        Personne, on_delete=models.CASCADE, related_name='notifications',
        null=True, blank=True
    )
    message = models.CharField(max_length=500)
    type_notif = models.CharField(max_length=25, choices=TYPES)
    lu = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)
    classe = models.ForeignKey(Classe, on_delete=models.SET_NULL, null=True, blank=True)

    def clean(self):
        # RG-NO03: destinataire individuel XOR classe cible
        if self.destinataire_id and self.classe_id:
            raise ValidationError(
                "Une notification doit avoir soit un destinataire individuel, soit une classe cible, pas les deux."
            )
        if not self.destinataire_id and not self.classe_id:
            raise ValidationError(
                "Une notification doit avoir au moins un destinataire ou une classe cible."
            )

    def __str__(self):
        cible = self.destinataire.get_full_name() if self.destinataire_id else f"Classe {self.classe}"
        return f"[{self.get_type_notif_display()}] → {cible}"

    class Meta:
        db_table = 'notification'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-date_envoi']


# ─────────────────────────────────────────
# 20. HistoriqueActions
# ─────────────────────────────────────────

class Message(models.Model):
    expediteur  = models.ForeignKey(Personne, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(Personne, on_delete=models.CASCADE, related_name='messages_recus')
    sujet   = models.CharField(max_length=150)
    corps   = models.TextField()
    lu      = models.BooleanField(default=False)
    date_envoi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"De {self.expediteur} à {self.destinataire} — {self.sujet}"

    class Meta:
        db_table = 'message'
        ordering = ['-date_envoi']


class EvenementScolaire(models.Model):
    TYPES = [
        ('vacances', 'Vacances scolaires'),
        ('examen', 'Examen / Évaluation'),
        ('reunion', 'Réunion'),
        ('ferie', 'Jour férié'),
        ('autre', 'Autre'),
    ]
    titre       = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    type_event  = models.CharField(max_length=15, choices=TYPES, default='autre')
    date_debut  = models.DateField()
    date_fin    = models.DateField()
    annee       = models.ForeignKey('AnneeScolaire', on_delete=models.CASCADE,
                                    related_name='evenements', null=True, blank=True)
    createur    = models.ForeignKey(Personne, on_delete=models.SET_NULL, null=True,
                                    related_name='evenements_crees')

    def __str__(self):
        return f"{self.titre} ({self.date_debut} → {self.date_fin})"

    class Meta:
        db_table = 'evenement_scolaire'
        ordering = ['date_debut']


class FraisScolarite(models.Model):
    STATUTS = [
        ('en_attente', 'En attente'),
        ('paye', 'Payé'),
        ('partiel', 'Partiellement payé'),
    ]
    eleve       = models.ForeignKey(Personne, on_delete=models.RESTRICT, related_name='frais')
    annee       = models.ForeignKey('AnneeScolaire', on_delete=models.RESTRICT, related_name='frais')
    montant_du  = models.DecimalField(max_digits=10, decimal_places=0)
    montant_paye = models.DecimalField(max_digits=10, decimal_places=0, default=0)
    statut      = models.CharField(max_length=10, choices=STATUTS, default='en_attente')
    date_echeance = models.DateField(null=True, blank=True)
    date_maj    = models.DateTimeField(auto_now=True)

    @property
    def reste_a_payer(self):
        return self.montant_du - self.montant_paye

    def __str__(self):
        return f"Frais {self.eleve.get_full_name()} — {self.annee}"

    class Meta:
        db_table = 'frais_scolarite'
        unique_together = [('eleve', 'annee')]


class Paiement(models.Model):
    frais       = models.ForeignKey(FraisScolarite, on_delete=models.CASCADE, related_name='paiements')
    montant     = models.DecimalField(max_digits=10, decimal_places=0)
    date_paiement = models.DateField()
    recu_numero = models.CharField(max_length=30, unique=True, blank=True)
    mode        = models.CharField(max_length=20, choices=[
        ('especes', 'Espèces'), ('virement', 'Virement'), ('mobile_money', 'Mobile Money')
    ], default='especes')
    saisi_par   = models.ForeignKey(Personne, on_delete=models.SET_NULL, null=True,
                                    related_name='paiements_saisis')

    def save(self, *args, **kwargs):
        if not self.recu_numero:
            import uuid
            self.recu_numero = f"REC-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
        # Recalcul statut frais
        total = self.frais.paiements.aggregate(t=models.Sum('montant'))['t'] or 0
        self.frais.montant_paye = total
        if total >= self.frais.montant_du:
            self.frais.statut = 'paye'
        elif total > 0:
            self.frais.statut = 'partiel'
        else:
            self.frais.statut = 'en_attente'
        self.frais.save()

    def __str__(self):
        return f"Paiement {self.recu_numero} — {self.montant} FCFA"

    class Meta:
        db_table = 'paiement'
        ordering = ['-date_paiement']


class HistoriqueActions(models.Model):
    auteur = models.ForeignKey(Personne, on_delete=models.SET_NULL, null=True, related_name='historique')
    action = models.CharField(max_length=100)
    table_cible = models.CharField(max_length=50)
    id_enreg = models.PositiveIntegerField(null=True, blank=True)
    details = models.TextField(blank=True)
    date_action = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.auteur} — {self.action} sur {self.table_cible} ({self.date_action:%d/%m/%Y %H:%M})"

    class Meta:
        db_table = 'historique_actions'
        verbose_name = "Historique d'action"
        verbose_name_plural = 'Historique des actions'
        ordering = ['-date_action']
