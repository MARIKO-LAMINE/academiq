from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('', views.accueil, name='accueil'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('acces-refuse/', views.acces_refuse, name='acces_refuse'),
    path('profil/', views.mon_profil, name='mon_profil'),
]
