from django.urls import path
from . import views

app_name = 'personnel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    # Années
    path('annees/', views.gestion_annees, name='gestion_annees'),
    path('annees/<int:pk>/activer/', views.activer_annee, name='activer_annee'),
    path('annees/<int:pk>/modifier/', views.modifier_annee, name='modifier_annee'),
    # Périodes
    path('periodes/', views.gestion_periodes, name='gestion_periodes'),
    path('periodes/<int:pk>/cloturer/', views.cloturer_periode, name='cloturer_periode'),
    # Salles
    path('salles/', views.gestion_salles, name='gestion_salles'),
    path('salles/<int:pk>/modifier/', views.modifier_salle, name='modifier_salle'),
    path('salles/<int:pk>/supprimer/', views.supprimer_salle, name='supprimer_salle'),
    # Matières
    path('matieres/', views.gestion_matieres, name='gestion_matieres'),
    path('matieres/<int:pk>/modifier/', views.modifier_matiere, name='modifier_matiere'),
    # Classes
    path('classes/', views.gestion_classes, name='gestion_classes'),
    path('classes/<int:pk>/modifier/', views.modifier_classe, name='modifier_classe'),
    # Cours
    path('cours/', views.gestion_cours, name='gestion_cours'),
    path('cours/<int:pk>/modifier/', views.modifier_cours, name='modifier_cours'),
    path('cours/<int:pk>/supprimer/', views.supprimer_cours, name='supprimer_cours'),
    # Comptes
    path('comptes/', views.gestion_comptes, name='gestion_comptes'),
    path('comptes/creer/', views.creer_compte, name='creer_compte'),
    path('comptes/<int:pk>/modifier/', views.modifier_compte, name='modifier_compte'),
    path('comptes/<int:pk>/toggle-actif/', views.toggle_actif_compte, name='toggle_actif_compte'),
    # Demandes d'inscription
    path('comptes/demandes/', views.demandes_inscription, name='demandes_inscription'),
    path('comptes/demandes/<int:pk>/attribuer/', views.attribuer_role, name='attribuer_role'),
    path('comptes/demandes/<int:pk>/rejeter/', views.rejeter_inscription, name='rejeter_inscription'),
    # Emploi du temps
    path('edt/', views.gestion_edt, name='gestion_edt'),
    path('edt/<int:pk>/supprimer/', views.supprimer_creneau, name='supprimer_creneau'),
    # Inscriptions
    path('inscriptions/', views.gestion_inscriptions, name='gestion_inscriptions'),
    path('inscriptions/<int:pk>/statut/', views.changer_statut_inscription, name='changer_statut_inscription'),
    # Absences
    path('absences/', views.validation_absences, name='validation_absences'),
    path('absences/<int:pk>/valider/', views.valider_absence, name='valider_absence'),
    # Bulletins
    path('bulletins/', views.gestion_bulletins, name='gestion_bulletins'),
    path('bulletins/periode/<int:pk>/generer/', views.generer_bulletins_periode, name='generer_bulletins_periode'),
    path('bulletins/periode/<int:pk>/', views.liste_bulletins_periode, name='liste_bulletins_periode'),
    path('bulletins/<int:bulletin_id>/pdf/', views.export_bulletin_pdf, name='export_bulletin_pdf'),
    # Export Excel
    path('classes/<int:classe_id>/export-excel/', views.export_liste_classe_excel, name='export_liste_classe_excel'),
    path('classes/<int:classe_id>/periode/<int:periode_id>/notes-excel/', views.export_notes_excel, name='export_notes_excel'),
    # Attestation de scolarité
    path('inscriptions/<int:inscription_id>/attestation/', views.attestation_scolarite_pdf, name='attestation_scolarite_pdf'),
    # Historique
    path('historique/', views.historique_actions, name='historique_actions'),
    # Messagerie
    path('messages/', views.messagerie, name='messagerie'),
    path('messages/nouveau/', views.envoyer_message, name='envoyer_message'),
    path('messages/<int:pk>/', views.lire_message, name='lire_message'),
    # Annonces
    path('annonces/', views.gestion_annonces, name='gestion_annonces'),
    # Finances
    path('finances/', views.gestion_finances, name='gestion_finances'),
    path('finances/creer/', views.creer_frais, name='creer_frais'),
    path('finances/<int:frais_id>/paiement/', views.enregistrer_paiement, name='enregistrer_paiement'),
    path('finances/paiement/<int:paiement_id>/recu/', views.recu_paiement_pdf, name='recu_paiement_pdf'),
    # Calendrier
    path('calendrier/', views.calendrier_scolaire, name='calendrier_scolaire'),
    path('calendrier/creer/', views.creer_evenement, name='creer_evenement'),
    path('calendrier/<int:pk>/supprimer/', views.supprimer_evenement, name='supprimer_evenement'),
]
