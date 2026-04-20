from django.urls import path
from . import views

app_name = 'enseignant'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('cours/', views.mes_cours, name='mes_cours'),
    path('cours/<int:cours_id>/', views.detail_cours, name='detail_cours'),
    path('cours/<int:cours_id>/notes/ajouter/', views.saisir_note, name='saisir_note'),
    path('notes/<int:note_id>/modifier/', views.modifier_note, name='modifier_note'),
    path('cours/<int:cours_id>/absences/', views.absences_cours, name='absences_cours'),
    path('cours/<int:cours_id>/absences/ajouter/', views.saisir_absence, name='saisir_absence'),
    path('cours/<int:cours_id>/eleve/<int:eleve_id>/notes/', views.notes_eleve, name='notes_eleve'),
    path('notifications/', views.mes_notifications, name='notifications'),
]
