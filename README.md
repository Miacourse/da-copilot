# DA-Copilot — Agent d'analyse de données

Agent rigoureux et pédagogue qui transforme une question métier et un ou plusieurs jeux de données en une réponse claire, chiffrée et vérifiable : KPI, tendances, anomalies, visualisations et recommandations actionnables.

## Structure

- [`SKILL.md`](SKILL.md) — définition de l'agent (rôle, déclencheurs, workflow en 5 étapes, contraintes, human-gate, critères de succès)
- [`scripts/`](scripts/) — pipeline reproductible, à exécuter dans l'ordre :
  1. `01_profile.py` — profilage & contrôle qualité
  2. `02_prepare.py` — nettoyage + journal de transformation
  3. `03_eda.py` — exploration + visualisations
  4. `04_model.py` — modélisation (comparaison de modèles, validation croisée)
  5. `05_dashboard.py` — génération du dashboard HTML
- [`RAPPORT.md`](RAPPORT.md) — rapport d'analyse complet
- [`dashboard.html`](dashboard.html) — dashboard autonome (graphiques embarqués)
- [`figures/`](figures/) — graphiques clés (PNG)

## Cas d'étude : statut des startups

Prédiction du statut (`operating` / `acquired` / `closed`) d'une startup à partir de ses investissements.

- **Données** : 48 124 startups (après nettoyage de 54 294 lignes brutes)
- **Approche** : classification 3 classes, gestion du déséquilibre (poids de classe + split stratifié)
- **Résultat** : Gradient Boosting — balanced accuracy ≈ 0,61 ; détection ~61 % des « acquired » et ~57 % des « closed »
- **Variables clés** : délai jusqu'au 1er financement, année de fondation, nombre de levées, pays (USA)

## Exécuter

Environnement : `pandas`, `numpy`, `scikit-learn`, `matplotlib`, `seaborn`.

```bash
pip install pandas numpy scikit-learn matplotlib seaborn
python scripts/01_profile.py   # puis 02 → 05 dans l'ordre
```

> Adapter le chemin du CSV en tête de `scripts/01_profile.py` (variable `CSV`).

## Limites (honnêteté du modèle)

- Fort déséquilibre de classes → métriques pondérées (balanced accuracy, macro-F1) ; précision faible sur les classes rares.
- Biais de survivance : année de fondation et délai de financement reflètent en partie l'instantané des données. Corrélation ≠ causalité.