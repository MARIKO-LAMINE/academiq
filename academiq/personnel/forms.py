from django import forms
from django.core.exceptions import ValidationError
from core.models import (
    AnneeScolaire, Periode, Salle, Matiere, Classe, Cours,
    Personne, Personnel, Enseignant, Eleve, Parent, Inscription,
    EmploiDuTemps,
)


class AnneeScolaireForm(forms.ModelForm):
    class Meta:
        model = AnneeScolaire
        fields = ['libelle', 'date_debut', 'date_fin']
        widgets = {
            'libelle':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': '2025-2026'}),
            'date_debut': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class PeriodeForm(forms.ModelForm):
    class Meta:
        model = Periode
        fields = ['annee', 'nom', 'type_periode', 'date_debut', 'date_fin']
        widgets = {
            'annee':       forms.Select(attrs={'class': 'form-select'}),
            'nom':         forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Trimestre 1'}),
            'type_periode': forms.Select(attrs={'class': 'form-select'}),
            'date_debut':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'date_fin':    forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = ['numero', 'batiment', 'capacite', 'type_salle']
        widgets = {
            'numero':    forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A101'}),
            'batiment':  forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Batiment A'}),
            'capacite':  forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'type_salle': forms.Select(attrs={'class': 'form-select'}),
        }


class MatiereForm(forms.ModelForm):
    class Meta:
        model = Matiere
        fields = ['nom_matiere', 'coefficient', 'description']
        widgets = {
            'nom_matiere':   forms.TextInput(attrs={'class': 'form-control'}),
            'coefficient':   forms.NumberInput(attrs={'class': 'form-control', 'min': 0.5, 'step': '0.5'}),
            'description':   forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class ClasseForm(forms.ModelForm):
    class Meta:
        model = Classe
        fields = ['nom', 'niveau', 'cycle', 'section', 'annee', 'effectif_max']
        widgets = {
            'nom':          forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Terminale A1'}),
            'niveau':       forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Terminale'}),
            'cycle':        forms.Select(attrs={'class': 'form-select'}),
            'section':      forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'A'}),
            'annee':        forms.Select(attrs={'class': 'form-select'}),
            'effectif_max': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }


class CoursForm(forms.ModelForm):
    class Meta:
        model = Cours
        fields = ['matiere', 'classe', 'enseignant', 'annee', 'nb_heures_hebdo']
        widgets = {
            'matiere':        forms.Select(attrs={'class': 'form-select'}),
            'classe':         forms.Select(attrs={'class': 'form-select'}),
            'enseignant':     forms.Select(attrs={'class': 'form-select'}),
            'annee':          forms.Select(attrs={'class': 'form-select'}),
            'nb_heures_hebdo': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # N'afficher que les personnes ayant le rôle enseignant
        self.fields['enseignant'].queryset = Personne.objects.filter(
            enseignant__isnull=False, actif=True
        )
        self.fields['enseignant'].label_from_instance = lambda obj: obj.get_full_name()


class PersonneBaseForm(forms.ModelForm):
    password = forms.CharField(
        label="Mot de passe",
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Laisser vide pour ne pas modifier'}),
        help_text="Laisser vide pour conserver le mot de passe actuel."
    )

    class Meta:
        model = Personne
        fields = ['nom', 'prenom', 'email', 'photo_profil', 'actif']
        widgets = {
            'nom':    forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'email':  forms.EmailInput(attrs={'class': 'form-control'}),
            'photo_profil': forms.FileInput(attrs={'class': 'form-control'}),
            'actif':  forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        pwd = self.cleaned_data.get('password')
        if pwd:
            user.set_password(pwd)
        if commit:
            user.save()
        return user


class PersonnelSubForm(forms.ModelForm):
    class Meta:
        model = Personnel
        fields = ['fonction', 'date_embauche']
        widgets = {
            'fonction':      forms.Select(attrs={'class': 'form-select'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class EnseignantSubForm(forms.ModelForm):
    class Meta:
        model = Enseignant
        fields = ['specialite', 'grade', 'date_embauche']
        widgets = {
            'specialite':    forms.TextInput(attrs={'class': 'form-control'}),
            'grade':         forms.TextInput(attrs={'class': 'form-control'}),
            'date_embauche': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }


class EleveSubForm(forms.ModelForm):
    class Meta:
        model = Eleve
        fields = ['date_naissance', 'lieu_naissance']
        widgets = {
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control'}),
        }


class ParentSubForm(forms.ModelForm):
    class Meta:
        model = Parent
        fields = ['telephone', 'profession']
        widgets = {
            'telephone':  forms.TextInput(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
        }


ROLE_CHOICES = [
    ('personnel', 'Personnel administratif'),
    ('enseignant', 'Enseignant'),
    ('eleve', 'Élève'),
    ('parent', 'Parent'),
]


class RoleChoiceForm(forms.Form):
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label="Rôle",
        widget=forms.Select(attrs={'class': 'form-select'})
    )


class InscriptionForm(forms.ModelForm):
    class Meta:
        model = Inscription
        fields = ['eleve', 'classe', 'annee', 'date_inscription', 'statut']
        widgets = {
            'eleve':             forms.Select(attrs={'class': 'form-select'}),
            'classe':            forms.Select(attrs={'class': 'form-select'}),
            'annee':             forms.Select(attrs={'class': 'form-select'}),
            'date_inscription':  forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'statut':            forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['eleve'].queryset = Personne.objects.filter(eleve__isnull=False, actif=True)
        self.fields['eleve'].label_from_instance = lambda obj: obj.get_full_name()


class EmploiDuTempsForm(forms.ModelForm):
    class Meta:
        model = EmploiDuTemps
        fields = ['cours', 'salle', 'periode', 'jour', 'heure_debut', 'heure_fin']
        widgets = {
            'cours':       forms.Select(attrs={'class': 'form-select'}),
            'salle':       forms.Select(attrs={'class': 'form-select'}),
            'periode':     forms.Select(attrs={'class': 'form-select'}),
            'jour':        forms.Select(attrs={'class': 'form-select'}),
            'heure_debut': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'heure_fin':   forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
        }

    def __init__(self, *args, annee=None, classe=None, **kwargs):
        super().__init__(*args, **kwargs)
        if annee:
            self.fields['cours'].queryset = Cours.objects.filter(
                annee=annee
            ).select_related('matiere', 'classe', 'enseignant')
            self.fields['periode'].queryset = Periode.objects.filter(annee=annee)
        if classe:
            self.fields['cours'].queryset = Cours.objects.filter(
                annee=annee, classe=classe
            ).select_related('matiere', 'enseignant') if annee else Cours.objects.filter(
                classe=classe
            ).select_related('matiere', 'enseignant')
        self.fields['cours'].label_from_instance = lambda obj: (
            f"{obj.matiere.nom_matiere} — {obj.classe.nom} ({obj.enseignant.get_full_name()})"
        )

    def clean(self):
        cleaned = super().clean()
        instance = self.instance if self.instance.pk else EmploiDuTemps()
        for field in ['cours', 'salle', 'periode', 'jour', 'heure_debut', 'heure_fin']:
            setattr(instance, field, cleaned.get(field))
            fk_field = field + '_id'
            val = cleaned.get(field)
            if val and hasattr(val, 'pk'):
                setattr(instance, fk_field, val.pk)
        try:
            instance.clean()
        except forms.ValidationError as e:
            raise forms.ValidationError(e.messages)
        return cleaned
