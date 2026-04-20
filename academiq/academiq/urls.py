from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [   
    path('', include('accounts.urls', namespace='accounts')),
    path('admin/', admin.site.urls),
    path('personnel/', include('personnel.urls', namespace='personnel')),
    path('enseignant/', include('enseignant.urls', namespace='enseignant')),
    path('eleve/', include('eleve.urls', namespace='eleve')),
    path('parent/', include('parent.urls', namespace='parent')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
