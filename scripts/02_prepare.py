# DA-Copilot — Étapes 3 & 4 : Nettoyage + EDA (avec journal de transformation)
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os, warnings
warnings.filterwarnings("ignore")

CSV = r"C:\Users\souleymane\Desktop\AGENT ia Z\J1\Investments_VC.csv"
OUT = r"C:\Users\souleymane\Desktop\AGENT ia Z\J1\DA_Copilot\output"
os.makedirs(OUT, exist_ok=True)

raw = pd.read_csv(CSV, dtype=str, keep_default_na=False, encoding="latin-1")
raw.columns = [c.strip() for c in raw.columns]

LOG = []  # journal de nettoyage
def log(msg): LOG.append(msg)

log(f"Chargement brut : {len(raw)} lignes x {len(raw.columns)} colonnes (encoding latin-1)")

# --- Nettoyage 1 : colonnes vides exclusivement (lignes poubelles) ---
blank_row = (raw == "").all(axis=1)
n_blank = int(blank_row.sum())
log(f"S1. Suppression de {n_blank} lignes intégralement vides (bruit de fin de fichier)")
df = raw[~blank_row].copy()

# --- Nettoyage 2 : colonnes numériques (format indien "1,50,000" + espaces) ---
num_cols = ["funding_total_usd", "funding_rounds",
            "seed","venture","equity_crowdfunding","undisclosed","convertible_note",
            "debt_financing","angel","grant","private_equity","post_ipo_equity",
            "post_ipo_debt","secondary_market","product_crowdfunding",
            "round_A","round_B","round_C","round_D","round_E","round_F","round_G","round_H"]

for c in num_cols:
    df[c] = (df[c].str.replace(",", "", regex=False)   # séparateur de milliers (format indien)
                  .str.replace("$", "", regex=False)
                  .str.strip()
                  .replace("", np.nan))
    df[c] = pd.to_numeric(df[c], errors="coerce")
log(f"S2. Conversion en numérique de {len(num_cols)} colonnes de montants (suppression virgules/espaces, '' -> NaN)")

# --- Nettoyage 3 : dates ---
for c in ["founded_at", "first_funding_at", "last_funding_at"]:
    df[c] = pd.to_datetime(df[c].str.strip().replace("", np.nan), errors="coerce")
log("S3. Conversion en date de founded_at / first_funding_at / last_funding_at")

# --- Nettoyage 4 : statut (cible) ---
df["status"] = df["status"].str.strip()
n_unlabeled = int((df["status"] == "").sum())
log(f"S4. {n_unlabeled} lignes sans statut (cible manquante) -> exclues du jeu modélisé, conservées en annexe")

labeled = df[df["status"] != ""].copy()
log(f"Jeu final étiqueté : {len(labeled)} lignes")

# Recoupement : somme des rounds vs funding_total_usd
round_cols = ["seed","venture","equity_crowdfunding","undisclosed","convertible_note",
              "debt_financing","angel","grant","private_equity","post_ipo_equity",
              "post_ipo_debt","secondary_market","product_crowdfunding",
              "round_A","round_B","round_C","round_D","round_E","round_F","round_G","round_H"]
sum_rounds = labeled[round_cols].fillna(0).sum(axis=1)
diff = (sum_rounds - labeled["funding_total_usd"].fillna(0)).abs()
tol = labeled["funding_total_usd"].fillna(0) * 0.001 + 1
mismatch = (diff > tol).mean() * 100
corr_val = np.corrcoef(sum_rounds, labeled["funding_total_usd"].fillna(0))[0,1]

# Sauvegarde du jeu nettoyé (preuve reproductible)
labeled.to_csv(os.path.join(OUT, "cleaned_labeled.csv"), index=False)
df.to_csv(os.path.join(OUT, "cleaned_all.csv"), index=False)

print("=========== JOURNAL DE NETTOYAGE ===========")
for m in LOG: print(" •", m)
print(f"\nVérification (recoupement) : somme des rounds ≈ funding_total_usd")
print(f"  corrélation = {corr_val:.4f} | % lignes en écart > tolérance = {mismatch:.2f}%")