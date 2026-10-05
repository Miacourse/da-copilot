# DA-Copilot — Étape 2 : Contrôle des données (profilage)
# Question métier : la valeur/présence d'investissements et d'autres critères
# permettent-ils de prédire le statut d'une startup (operating / closed / acquired) ?
import pandas as pd
import numpy as np

CSV = r"C:\Users\souleymane\Desktop\AGENT ia Z\J1\Investments_VC.csv"

raw = pd.read_csv(CSV, dtype=str, keep_default_na=False, encoding="latin-1")
raw.columns = [c.strip() for c in raw.columns]

print("=== 1. FORMES ET TYPES ===")
print("lignes (hors header) :", len(raw))
print("colonnes :", len(raw.columns))
print(raw.columns.tolist())

print("\n=== 2. VALEURS MANQUANTES (chaîne vide = manquant potentiel) ===")
# pour les colonnes non-target : compter les chaînes vides
missing = (raw == "").sum()
missing_pct = ((raw == "").mean() * 100).round(2)
miss_df = pd.DataFrame({"n_vides": missing, "pct": missing_pct}).sort_values("n_vides")
print(miss_df.to_string())

print("\n=== 3. DOUBLONS ===")
print("lignes dupliquées (toutes colonnes) :", raw.duplicated().sum())
print("doublons sur permalink :", raw["permalink"].duplicated().sum())

print("\n=== 4. CIBLE `status` (déséquilibre de classe) ===")
print(raw["status"].value_counts(dropna=False).to_string())
print("proportions :")
print((raw["status"].value_counts(dropna=False, normalize=True) * 100).round(2).to_string())

print("\n=== 5. VALEURS UNIQUES DES COLONNES CATÉGORIELLES ===")
for c in ["country_code", "region", "founded_quarter", "market"]:
    print(f"{c}: {raw[c].nunique()} valeurs uniques")

print("\n=== 6. ÉCHANTILLON DE VALEURS NUMÉRIQUES BRUTES (à nettoyer) ===")
for c in ["funding_total_usd", "funding_rounds", "round_A", "seed", "venture"]:
    vals = raw[c].replace("", np.nan).dropna()
    print(f"{c}: {len(vals)} non-vides | exemples: {list(vals.head(5))}")

print("\n=== 7. CATEGORY_LIST — exemples ===")
print(raw["category_list"].head(8).tolist())