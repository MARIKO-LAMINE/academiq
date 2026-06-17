from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

urlpatterns = [
    path('', include('accounts.urls', namespace='accounts')),
    path('admin/', admin.site.urls),
    path('personnel/', include('personnel.urls', namespace='personnel')),
    path('enseignant/', include('enseignant.urls', namespace='enseignant')),
    path('eleve/', include('eleve.urls', namespace='eleve')),
    path('parent/', include('parent.urls', namespace='parent')),
]

# Sert les fichiers médias (photos de profil) — y compris en production (DEBUG=False).
# Pour une production à fort trafic, déléguer plutôt /media directement à Apache.
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
