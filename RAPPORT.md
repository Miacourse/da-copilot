# Rapport d'analyse — Prédiction du statut des startups

**Agent** : DataAnalyst-Agent (DA-Copilot) · **Date** : 30 septembre 2026
**Source** : `Investments_VC.csv` (54 294 lignes × 39 colonnes)

---

## 1. Question métier

> Peut-on prédire le statut d'une startup — **operating / acquired / closed** — à partir de ses
> investissements (montants, types de rounds) et d'autres critères (secteur, pays, ancienneté) ?

C'est un problème de **classification multi-classe** (cible = `status`), avec un fort déséquilibre
de classes à traiter.

---

## 2. Contrôle & nettoyage des données (journal)

| # | Transformation | Impact |
|---|---|---|
| S1 | Suppression des lignes intégralement vides | − 4 856 lignes |
| S2 | Conversion en numérique de 23 colonnes de montants (format indien `"1,50,000"` + espaces) | virgules/espaces retirés, `"" → NaN` |
| S3 | Conversion en date de `founded_at` / `first_funding_at` / `last_funding_at` | — |
| S4 | Exclusion des lignes sans cible (`status` vide) | − 1 314 lignes |

**Jeu final étiqueté : 48 124 startups.** Encodage fichier : latin-1.

**Vérification (recoupement)** — somme des montants par round vs `funding_total_usd` :
corrélation **0,987** mais **25,96 %** des lignes présentent un écart notable. Le total déclaré
n'est donc pas toujours la somme exacte des rounds (rounds « undisclosed », données incomplètes).

---

## 3. Exploration (EDA) — constats clés

**Déséquilibre de classe (sévère)** : operating 41 829 (86,9 %), acquired 3 692 (7,7 %),
closed 2 603 (5,4 %).

**Le financement discrimine fortement l'issue** :

| Statut | Financement total médian | Levées (médiane) |
|---|---|---|
| acquired | **8,38 M$** | 2 |
| operating | 1,76 M$ | 1 |
| closed | 1,00 M$ | 1 |

**Secteurs** les plus acquis (taux d'acquisition) : Enterprise Software 14,2 % · Advertising 11,9 %
· Curated Web 11,6 % · Software 10,3 % · Mobile 9,1 %. Les plus faibles : Education 3,5 %,
E-Commerce 5,3 %, Biotechnology 5,6 %.

**Géographie** : les USA concentrent 28 233 startups (≈ 59 %). Taux d'acquisition **9,9 % aux USA
vs 4,6 % ailleurs** — les startups américaines sont acquises ~2× plus souvent.

**Délai fondation → 1er financement** (médian) : acquired **733 j** · operating 550 j · closed **238 j**.
Les startups fermées ont été financées vite puis ont périclité ; les acquises ont mis ~2 ans à lever.

---

## 4. Modélisation

Features : montants par round (log1p), financement total, nb de rounds, année de fondation,
délai jusqu'au 1er financement, pays (top 15), secteurs (25 catégories en multi-hot), présence d'URL.
Split stratifié 70/30, gestion du déséquilibre via poids de classe. Cible : 3 classes.

| Modèle | Balanced accuracy | Macro-F1 |
|---|---|---|
| Baseline (majorité) | 0,333 | 0,310 |
| Régression logistique (équilibrée) | 0,582 | 0,427 |
| Forêt aléatoire (équilibrée) | 0,480 | 0,477 |
| **Gradient Boosting (poids équilibrés)** | **0,610** | **0,450** |

**Meilleur équilibre** : Gradient Boosting (balanced acc **0,610**). Rappel (détection) sur les
classes minoritaires : **acquired 60,7 %**, **closed 57,1 %** — mais précision faible (23 % et 15 %),
donc beaucoup de faux positifs. Validation croisée 5-fold de la régression logistique :
balanced acc **0,581 ± 0,006** (stable).

**Variables les plus influentes** (importance par permutation) : délai jusqu'au 1er financement,
année de fondation / ancienneté, nb de rounds, pays (USA), présence d'URL, montants venture / round A.

---

## 5. Recommandations actionnables

1. **Outil de priorisation** : cibler en priorité les startups fortement financées, récentes,
   basées aux USA, ayant levé tardivement après leur fondation, dans les secteurs Enterprise
   Software / Advertising / Software — indicateurs associés à une issue « acquired ».
2. **Améliorer la donnée** : normaliser les codes pays (mélange 2/3 lettres), réconcilier
   `funding_total_usd` avec la somme des rounds (26 % d'écarts), uniformiser la taxonomie des
   catégories, compléter les dates de fondation (29 % manquantes).
3. **Reformuler la cible si besoin** : la classe `closed` (5,4 %) est la plus difficile ; un
   regroupement binaire « encore en activité vs sortie (acquired ∪ closed) » apporte un signal
   plus fiable pour un premier usage décisionnel.

## 6. Limites & hypothèses

- **Déséquilibre extrême** : métriques pondérées (balanced accuracy, macro-F1) ; la précision sur
  les classes rares reste faible — à utiliser comme outil de tri, pas comme décision automatique.
- **Biais de censure / survivance** : `founded_year` et le délai de financement sont très prédictifs
  mais reflètent en partie l'effet de l'instantané (~2014) — une startup récente n'a pas encore eu
  le temps d'être acquise ou fermée. **Corrélation ≠ causalité.**
- **Données de financement partielles** : 26 % des totaux ne réconcilient pas avec la somme des rounds.
- **Valeurs manquantes** imputées (médiane) : année de fondation 29 %, `state_code` 44 %.
- `cc_UNKNOWN` (pays manquant) est lui-même prédictif → signaler une donnée incomplète, pas un effet réel.

---

*Reproductibilité : scripts `01_profile.py` → `04_model.py` dans `DA_Copilot/`, données nettoyées
dans `DA_Copilot/output/cleaned_*.csv`, figures `fig1..fig8` associées.*