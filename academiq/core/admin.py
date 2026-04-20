from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Personne, AnneeScolaire, Periode, Salle, Matiere,
    Personnel, Enseignant, Eleve, Parent, Classe, Cours,
    EmploiDuTemps, Inscription, LienParentEleve, Note,
    ResultatMatiere, Absence, Bulletin, Notification, HistoriqueActions,
)


@admin.register(Personne)
class PersonneAdmin(UserAdmin):
    model = Personne
    list_display = ('email', 'nom', 'prenom', 'actif', 'is_staff', 'date_creation')
    list_filter = ('actif', 'is_staff', 'groups')
    search_fields = ('email', 'nom', 'prenom')
    ordering = ('nom', 'prenom')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('nom', 'prenom', 'photo_profil')}),
        ('Permissions', {'fields': ('actif', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'nom', 'prenom', 'password1', 'password2', 'actif', 'is_staff'),
        }),
    )


@admin.register(AnneeScolaire)
class AnneeScolaireAdmin(admin.ModelAdmin):
    list_display = ('libelle', 'date_debut', 'date_fin', 'active')
    list_filter = ('active',)


@admin.register(Periode)
class PeriodeAdmin(admin.ModelAdmin):
    list_display = ('nom', 'annee', 'type_periode', 'date_debut', 'date_fin', 'cloturee')
    list_filter = ('annee', 'type_periode', 'cloturee')


@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ('numero', 'batiment', 'capacite', 'type_salle')


@admin.register(Matiere)
class MatiereAdmin(admin.ModelAdmin):
    list_display = ('nom_matiere', 'coefficient')


@admin.register(Personnel)
class PersonnelAdmin(admin.ModelAdmin):
    list_display = ('personne', 'fonction', 'date_embauche')
    list_filter = ('fonction',)


@admin.register(Enseignant)
class EnseignantAdmin(admin.ModelAdmin):
    list_display = ('personne', 'specialite', 'grade', 'date_embauche')
    search_fields = ('personne__nom', 'personne__prenom', 'specialite')


@admin.register(Eleve)
class EleveAdmin(admin.ModelAdmin):
    list_display = ('personne', 'matricule', 'date_naissance', 'lieu_naissance')
    search_fields = ('personne__nom', 'personne__prenom', 'matricule')


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('personne', 'telephone', 'profession')


@admin.register(Classe)
class ClasseAdmin(admin.ModelAdmin):
    list_display = ('nom', 'niveau', 'cycle', 'section', 'annee', 'effectif_max')
    list_filter = ('annee',)


@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('matiere', 'classe', 'enseignant', 'annee', 'nb_heures_hebdo')
    list_filter = ('annee', 'classe')
    search_fields = ('matiere__nom_matiere',)


@admin.register(EmploiDuTemps)
class EmploiDuTempsAdmin(admin.ModelAdmin):
    list_display = ('cours', 'salle', 'jour', 'heure_debut', 'heure_fin', 'periode')
    list_filter = ('jour', 'periode')


@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'classe', 'annee', 'statut', 'date_inscription')
    list_filter = ('annee', 'statut')
    search_fields = ('eleve__nom', 'eleve__prenom')


@admin.register(LienParentEleve)
class LienParentEleveAdmin(admin.ModelAdmin):
    list_display = ('parent', 'eleve', 'lien')


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'cours', 'periode', 'valeur', 'type_eval', 'date_saisie')
    list_filter = ('periode', 'type_eval')
    search_fields = ('eleve__nom', 'eleve__prenom')


@admin.register(ResultatMatiere)
class ResultatMatiereAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'cours', 'periode', 'moyenne', 'rang')
    list_filter = ('periode',)


@admin.register(Absence)
class AbsenceAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'cours', 'date_absence', 'nb_heures', 'statut')
    list_filter = ('statut', 'periode')
    search_fields = ('eleve__nom', 'eleve__prenom')


@admin.register(Bulletin)
class BulletinAdmin(admin.ModelAdmin):
    list_display = ('eleve', 'periode', 'moyenne_generale', 'rang', 'date_generation')
    list_filter = ('periode',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('destinataire', 'type_notif', 'lu', 'date_envoi')
    list_filter = ('type_notif', 'lu')


@admin.register(HistoriqueActions)
class HistoriqueActionsAdmin(admin.ModelAdmin):
    list_display = ('auteur', 'action', 'table_cible', 'id_enreg', 'date_action')
    list_filter = ('table_cible',)
    readonly_fields = ('date_action',)
