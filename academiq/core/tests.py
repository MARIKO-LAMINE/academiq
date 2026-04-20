import pytest
from datetime import date
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from core.models import (
    Personne, AnneeScolaire, Periode, Matiere, Classe, Cours,
    Enseignant, Eleve, Parent, Personnel, Inscription,
    Note, ResultatMatiere, Bulletin, Absence,
)


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture
def annee(db):
    return AnneeScolaire.objects.create(
        libelle='2025-2026', active=True,
        date_debut=date(2025, 9, 1), date_fin=date(2026, 7, 31)
    )


@pytest.fixture
def periode(annee):
    return Periode.objects.create(
        nom='Semestre 1', annee=annee,
        date_debut=date(2025, 9, 1), date_fin=date(2026, 1, 31)
    )


@pytest.fixture
def matiere(db):
    return Matiere.objects.create(nom_matiere='Mathematiques', coefficient=5)


@pytest.fixture
def classe(annee):
    return Classe.objects.create(nom='Terminale C', annee=annee, effectif_max=40)


@pytest.fixture
def personne_enseignant(db):
    g, _ = Group.objects.get_or_create(name='ENSEIGNANT')
    p = Personne.objects.create_user(
        email='ens@test.ci', nom='Diallo', prenom='Moussa', password='test1234'
    )
    p.groups.add(g)
    return p


@pytest.fixture
def personne_eleve(db):
    g, _ = Group.objects.get_or_create(name='ELEVE')
    p = Personne.objects.create_user(
        email='elv@test.ci', nom='Bamba', prenom='Youssouf', password='test1234'
    )
    p.groups.add(g)
    return p


@pytest.fixture
def enseignant(personne_enseignant):
    return Enseignant.objects.create(
        personne=personne_enseignant, specialite='Maths'
    )


@pytest.fixture
def eleve(personne_eleve):
    return Eleve.objects.create(personne=personne_eleve, matricule='ELV-001')


@pytest.fixture
def cours(matiere, classe, personne_enseignant, annee, enseignant):
    return Cours.objects.create(
        matiere=matiere, classe=classe,
        enseignant=personne_enseignant, annee=annee
    )


@pytest.fixture
def inscription(personne_eleve, classe, annee, eleve):
    return Inscription.objects.create(
        eleve=personne_eleve, classe=classe, annee=annee,
        date_inscription=date(2025, 9, 2), statut='actif'
    )


# ── Tests regles de gestion ───────────────────────────────────────────────────

@pytest.mark.django_db
def test_note_valeur_valide(cours, personne_eleve, periode, inscription, eleve):
    """RG-N03 : note entre 0 et 20 acceptee."""
    note = Note(eleve=personne_eleve, cours=cours, periode=periode,
                type_eval='devoir_surveille', valeur=15)
    note.full_clean()
    note.save()
    assert Note.objects.filter(pk=note.pk).exists()


@pytest.mark.django_db
def test_note_hors_intervalle_rejetee(cours, personne_eleve, periode, inscription, eleve):
    """RG-N03 : valeur > 20 doit lever une exception."""
    note = Note(eleve=personne_eleve, cours=cours, periode=periode,
                type_eval='devoir_surveille', valeur=25)
    with pytest.raises(Exception):
        note.full_clean()


@pytest.mark.django_db
def test_un_eleve_une_classe_par_annee(personne_eleve, classe, annee, eleve, inscription):
    """RG-C03 : double inscription sur la meme annee -> IntegrityError."""
    with pytest.raises(IntegrityError):
        Inscription.objects.create(
            eleve=personne_eleve, classe=classe, annee=annee,
            date_inscription=date(2025, 9, 3), statut='actif'
        )


@pytest.mark.django_db
def test_annee_active_unique(annee):
    """RG-T02 : activer une nouvelle annee desactive automatiquement la precedente."""
    annee2 = AnneeScolaire.objects.create(
        libelle='2026-2027', active=True,
        date_debut=date(2026, 9, 1), date_fin=date(2027, 7, 31)
    )
    annee.refresh_from_db()
    assert annee.active is False
    assert annee2.active is True


@pytest.mark.django_db
def test_recalcul_auto_resultat_matiere(cours, personne_eleve, periode, inscription, eleve):
    """RG-M01 : creer une Note declenche le recalcul automatique de ResultatMatiere."""
    Note.objects.create(
        eleve=personne_eleve, cours=cours, periode=periode,
        type_eval='devoir_surveille', valeur=14
    )
    Note.objects.create(
        eleve=personne_eleve, cours=cours, periode=periode,
        type_eval='interrogation', valeur=16
    )
    resultat = ResultatMatiere.objects.get(
        eleve=personne_eleve, cours=cours, periode=periode
    )
    assert float(resultat.moyenne) == 15.0


@pytest.mark.django_db
def test_bulletin_unique_par_eleve_periode(personne_eleve, periode, eleve):
    """RG-B01 : UNIQUE(eleve, periode) -> IntegrityError au doublon."""
    Bulletin.objects.create(eleve=personne_eleve, periode=periode, moyenne_generale=12)
    with pytest.raises(IntegrityError):
        Bulletin.objects.create(eleve=personne_eleve, periode=periode, moyenne_generale=13)


@pytest.mark.django_db
def test_compte_inactif_bloque(client):
    """RG-A03 : actif=False -> connexion refusee."""
    Personne.objects.create_user(
        email='inactif@test.ci', nom='Test', prenom='Inactif',
        password='test1234', actif=False
    )
    response = client.post('/login/', {'email': 'inactif@test.ci', 'password': 'test1234'})
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_exclusivite_roles(personne_eleve, eleve):
    """RG-H03 : une Personne deja Eleve ne peut pas devenir Enseignant."""
    ens = Enseignant(personne=personne_eleve, specialite='Maths')
    with pytest.raises(ValidationError):
        ens.clean()


@pytest.mark.django_db
def test_enseignant_filtre_ses_cours(client, personne_enseignant, enseignant, cours):
    """Cloisonnement : un enseignant ne voit que ses propres cours."""
    client.force_login(personne_enseignant)
    response = client.get('/enseignant/')
    assert response.status_code == 200
    for c in response.context.get('mes_cours', []):
        assert c.enseignant == personne_enseignant
