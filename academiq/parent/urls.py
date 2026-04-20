from django.urls import path
from . import views

app_name = 'parent'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('enfant/<int:eleve_id>/', views.suivi_enfant, name='suivi_enfant'),
    path('enfant/<int:eleve_id>/bulletin/<int:bulletin_id>/', views.detail_bulletin, name='detail_bulletin'),
    path('enfant/<int:eleve_id>/edt/', views.edt_enfant, name='edt_enfant'),
    path('notifications/', views.mes_notifications, name='notifications'),
]
