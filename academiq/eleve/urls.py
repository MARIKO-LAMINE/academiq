from django.urls import path
from . import views

app_name = 'eleve'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('notes/', views.mes_notes, name='mes_notes'),
    path('absences/', views.mes_absences, name='mes_absences'),
    path('bulletins/', views.mes_bulletins, name='mes_bulletins'),
    path('bulletins/<int:bulletin_id>/', views.detail_bulletin, name='detail_bulletin'),
    path('annonces/', views.mes_annonces, name='annonces'),
    path('edt/', views.mon_edt, name='mon_edt'),
    path('notifications/', views.mes_notifications, name='notifications'),
]
