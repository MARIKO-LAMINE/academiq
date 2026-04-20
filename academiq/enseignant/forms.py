from django import forms
from core.models import Note, Absence, Eleve, Cours, Periode


class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['eleve', 'periode', 'type_eval', 'valeur', 'commentaire']
        widgets = {
            'eleve':       forms.Select(attrs={'class': 'form-select'}),
            'periode':     forms.Select(attrs={'class': 'form-select'}),
            'type_eval':   forms.Select(attrs={'class': 'form-select'}),
            'valeur':      forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 20, 'step': 0.25}),
            'commentaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Commentaire optionnel'}),
        }

    def __init__(self, cours, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.models import Personne, Inscription
        eleve_ids = Inscription.objects.filter(
            classe=cours.classe, annee=cours.annee, statut='actif'
        ).values_list('eleve_id', flat=True)
        self.fields['eleve'].queryset = Personne.objects.filter(pk__in=eleve_ids)
        self.fields['eleve'].label_from_instance = lambda obj: obj.get_full_name()
        # Périodes de l'année du cours
        self.fields['periode'].queryset = Periode.objects.filter(annee=cours.annee)
        self.instance.cours = cours


class AbsenceForm(forms.ModelForm):
    class Meta:
        model = Absence
        fields = ['eleve', 'periode', 'date_absence', 'nb_heures']
        widgets = {
            'eleve':        forms.Select(attrs={'class': 'form-select'}),
            'periode':      forms.Select(attrs={'class': 'form-select'}),
            'date_absence': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'nb_heures':    forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

    def __init__(self, cours, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from core.models import Personne, Inscription
        eleve_ids = Inscription.objects.filter(
            classe=cours.classe, annee=cours.annee, statut='actif'
        ).values_list('eleve_id', flat=True)
        self.fields['eleve'].queryset = Personne.objects.filter(pk__in=eleve_ids)
        self.fields['eleve'].label_from_instance = lambda obj: obj.get_full_name()
        self.fields['periode'].queryset = Periode.objects.filter(annee=cours.annee)
        self.instance.cours = cours
