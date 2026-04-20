import os, django, sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'academiq.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from core.models import Personne, Cours, Periode, Note, AnneeScolaire

annee = AnneeScolaire.objects.filter(active=True).first()
periode = Periode.objects.filter(annee=annee).order_by('date_debut').first()
eleve1 = Personne.objects.get(email='eleve1@academiq.ci')
eleve2 = Personne.objects.get(email='eleve2@academiq.ci')
cours_maths = Cours.objects.get(matiere__nom_matiere__icontains='MATH', annee=annee)
cours_phys  = Cours.objects.get(matiere__nom_matiere__icontains='PHYSIQUE', annee=annee)

notes = [
    (eleve1, cours_maths, 'devoir_surveille',  14.5),
    (eleve1, cours_maths, 'interrogation',     12.0),
    (eleve1, cours_maths, 'examen_semestriel', 15.0),
    (eleve1, cours_phys,  'devoir_surveille',  11.0),
    (eleve1, cours_phys,  'interrogation',     13.5),
    (eleve1, cours_phys,  'examen_semestriel', 10.0),
    (eleve2, cours_maths, 'devoir_surveille',  9.0),
    (eleve2, cours_maths, 'interrogation',     11.0),
    (eleve2, cours_maths, 'examen_semestriel', 8.5),
    (eleve2, cours_phys,  'devoir_surveille',  13.0),
    (eleve2, cours_phys,  'interrogation',     14.0),
    (eleve2, cours_phys,  'examen_semestriel', 12.5),
]

for eleve, cours, type_eval, valeur in notes:
    n, created = Note.objects.get_or_create(
        eleve=eleve, cours=cours, periode=periode, type_eval=type_eval,
        defaults={'valeur': valeur}
    )
    print(f"  {'[+]' if created else '[=]'} {eleve.get_full_name()} | {cours.matiere.nom_matiere} | {type_eval} : {valeur}/20")

print("\nNotes chargees. Le signal a recalcule les ResultatMatiere automatiquement.")
