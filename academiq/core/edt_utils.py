"""Outils partagés pour l'affichage des emplois du temps (grille hebdomadaire)."""

JOURS_ORDER = ['lundi', 'mardi', 'mercredi', 'jeudi', 'vendredi', 'samedi']

JOURS_LABELS = {
    'lundi': 'Lundi', 'mardi': 'Mardi', 'mercredi': 'Mercredi',
    'jeudi': 'Jeudi', 'vendredi': 'Vendredi', 'samedi': 'Samedi',
}


def construire_grille(creneaux, jours_order=None):
    """Transforme une liste de créneaux en grille hebdomadaire.

    Retourne un dict :
        {
            'jours':  [('lundi', 'Lundi'), ...],   # uniquement les jours utilisés
            'lignes': [
                {'heure_debut': time, 'heure_fin': time,
                 'cellules': [creneau_ou_None, ...]},  # un par jour, dans l'ordre
                ...
            ],
        }
    Les lignes sont triées par heure de début ; les colonnes suivent l'ordre des jours.
    """
    if jours_order is None:
        jours_order = JOURS_ORDER

    creneaux = list(creneaux)

    jours_presents = [j for j in jours_order if any(c.jour == j for c in creneaux)]
    jours = [(j, JOURS_LABELS.get(j, j.capitalize())) for j in jours_presents]

    # Plages horaires distinctes, triées
    plages = sorted({(c.heure_debut, c.heure_fin) for c in creneaux})

    lignes = []
    for hd, hf in plages:
        cellules = []
        for j in jours_presents:
            cell = next(
                (c for c in creneaux
                 if c.jour == j and c.heure_debut == hd and c.heure_fin == hf),
                None,
            )
            cellules.append(cell)
        lignes.append({'heure_debut': hd, 'heure_fin': hf, 'cellules': cellules})

    return {'jours': jours, 'lignes': lignes}
