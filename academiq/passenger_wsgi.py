"""
Point d'entrée Phusion Passenger pour O2Switch (cPanel « Setup Python App »).

Ce fichier doit se trouver à la RACINE de l'application Python configurée dans cPanel,
c'est-à-dire le dossier qui contient `manage.py` et le package `academiq/`.
"""
import os
import sys

# Ajoute la racine du projet au PYTHONPATH (dossier contenant ce fichier).
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academiq.settings')

from academiq.wsgi import application  # noqa: E402
