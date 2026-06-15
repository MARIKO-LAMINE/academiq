from django.urls import path
from . import views

app_name = 'parent'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('enfant/<int:eleve_id>/', views.suivi_enfant, name='suivi_enfant'),
    path('enfant/<int:eleve_id>/bulletin/<int:bulletin_id>/', views.detail_bulletin, name='detail_bulletin'),
    path('enfant/<int:eleve_id>/edt/', views.edt_enfant, name='edt_enfant'),
    path('paiements/', views.mes_paiements, name='mes_paiements'),
    path('annonces/', views.mes_annonces, name='annonces'),
    path('messages/', views.messagerie, name='messagerie'),
    path('messages/nouveau/', views.envoyer_message, name='envoyer_message'),
    path('messages/<int:pk>/', views.lire_message, name='lire_message'),
    path('notifications/', views.mes_notifications, name='notifications'),
]
