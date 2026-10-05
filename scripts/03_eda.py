# DA-Copilot — Étape 4 : EDA + visualisations clés
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os, warnings
warnings.filterwarnings("ignore")

OUT = r"C:\Users\souleymane\Desktop\AGENT ia Z\J1\DA_Copilot\output"
df = pd.read_csv(os.path.join(OUT, "cleaned_labeled.csv"), low_memory=False)
for c in ["founded_at","first_funding_at","last_funding_at"]:
    df[c] = pd.to_datetime(df[c], errors="coerce")

sns.set_theme(style="whitegrid")
C = {"operating":"#2a9d8f", "acquired":"#e9c46a", "closed":"#e76f51"}

# ---------- 1. Déséquilibre de classe ----------
fig, ax = plt.subplots(figsize=(6.5,4))
vc = df["status"].value_counts()
sns.barplot(x=vc.index, y=vc.values, palette=[C[s] for s in vc.index], ax=ax)
for i,v in enumerate(vc.values):
    ax.text(i, v, f"{v:,}\n({v/len(df)*100:.1f}%)", ha="center", va="bottom", fontsize=9)
ax.set_title("Répartition de la cible `status` (déséquilibre de classe)")
ax.set_ylabel("Nb de startups")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig1_class_imbalance.png"), dpi=110); plt.close(fig)

# ---------- 2. Financement par statut ----------
fund = df["funding_total_usd"].clip(lower=0)
fig, axes = plt.subplots(1,2, figsize=(11,4))
for ax, col, t in zip(axes, ["funding_total_usd","funding_rounds"],
                      ["Financement total (USD)", "Nb de levées de fonds"]):
    order = ["operating","acquired","closed"]
    d = df[(df[col].notna()) & (df[col]>=0)]
    if col=="funding_total_usd":
        sns.boxplot(x="status", y=col, data=d, order=order, palette=C, showfliers=False, ax=ax)
        ax.set_yscale("log")
        ax.set_ylabel("USD (échelle log)")
    else:
        sns.boxplot(x="status", y=col, data=d, order=order, palette=C, showfliers=False, ax=ax)
    ax.set_title(t); ax.set_xlabel("")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig2_funding_by_status.png"), dpi=110); plt.close(fig)

# ---------- 3. Heatmap de corrélation (montants par round) ----------
rounds = ["seed","venture","angel","round_A","round_B","round_C","round_D",
          "grant","debt_financing","private_equity","funding_total_usd"]
corr = df[rounds].corr()
mask = np.triu(np.ones_like(corr, dtype=bool))
fig, ax = plt.subplots(figsize=(9,7))
sns.heatmap(corr, mask=mask, annot=True, fmt=".2f", cmap="RdBu_r", center=0,
            square=True, linewidths=.5, ax=ax, annot_kws={"size":8})
ax.set_title("Corrélation entre les montants par type de round")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig3_corr_rounds.png"), dpi=110); plt.close(fig)

# ---------- 4. Top catégories & taux d'issue ----------
cat = df["category_list"].astype(str).str.strip("|").str.split("|")
expl = df.assign(cat=cat).explode("cat")
expl = expl[expl["cat"].str.len()>0]
top = expl["cat"].value_counts().head(15).index

# taux d'issue par grande catégorie (au moins 50 startups)
cat_stat = expl.groupby("cat")["status"].value_counts(normalize=True).unstack().fillna(0)
big = expl["cat"].value_counts()
big = big[big>=50].index
cat_stat = cat_stat.loc[cat_stat.index.intersection(big)]
cat_stat = cat_stat.reindex(columns=["acquired","closed","operating"]).sort_values("acquired", ascending=False)

fig, ax = plt.subplots(figsize=(8,6))
cat_stat.head(20).plot(kind="barh", stacked=True, color=[C["acquired"],C["closed"],C["operating"]], ax=ax)
ax.axvline(df["status"].eq("acquired").mean(), color="black", ls="--", lw=1)
ax.set_title("Taux d'issue par secteur (top 20 par taux d'acquisition)")
ax.set_xlabel("Proportion"); ax.legend(loc="lower right", fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig4_status_by_category.png"), dpi=110); plt.close(fig)

# ---------- 5. Pays : taux d'acquisition ----------
ct = df[df["country_code"].astype(str).str.len()>=2]
ct_big = ct["country_code"].value_counts()
ct_big = ct_big[ct_big>=100].index
ct_stat = ct[ct["country_code"].isin(ct_big)].groupby("country_code")["status"]\
            .value_counts(normalize=True).unstack().fillna(0)
ct_stat = ct_stat.reindex(columns=["acquired","closed","operating"]).sort_values("acquired", ascending=False)

fig, ax = plt.subplots(figsize=(8,5))
ct_stat.head(15).plot(kind="bar", stacked=True, color=[C["acquired"],C["closed"],C["operating"]], ax=ax)
ax.axhline(df["status"].eq("acquired").mean(), color="black", ls="--", lw=1)
ax.set_title("Taux d'issue par pays (au moins 100 startups)")
ax.set_ylabel("Proportion"); ax.set_xlabel(""); ax.legend(fontsize=8)
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig5_status_by_country.png"), dpi=110); plt.close(fig)

# ---------- 6. Année de fondation ----------
fy = df["founded_year"].astype(str)
fy = pd.to_numeric(fy, errors="coerce")
df["founded_year_n"] = fy
d = df[(fy>=1990)&(fy<=2015)]
fig, ax = plt.subplots(figsize=(8,4))
sns.histplot(data=d, x="founded_year_n", hue="status", multiple="stack",
             palette=C, bins=25, ax=ax)
ax.set_title("Distribution des startups par année de fondation et statut")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig6_founded_year.png"), dpi=110); plt.close(fig)

# ==================== SYNTHÈSE CHIFFRÉE ====================
print("=========== SYNTHÈSE EDA ===========")
print(f"Jeu étiqueté : {len(df):,} startups")
print("\n--- Financement par statut ---")
g = df.groupby("status")[["funding_total_usd","funding_rounds"]].agg(
    n=("funding_total_usd","count"), median_usd=("funding_total_usd","median"),
    mean_usd=("funding_total_usd","mean"), median_rounds=("funding_rounds","median"))
print(g.round(0).to_string())

print("\n--- Top 12 secteurs (fréquence) et leur taux d'acquisition ---")
topfreq = expl["cat"].value_counts().head(12)
acq_rate = simpl2 = expl.assign(is_acq=expl["status"].eq("acquired")).groupby("cat")["is_acq"].mean()
res = pd.DataFrame({"nb": topfreq, "tx_acquisition": acq_rate.reindex(topfreq.index)}).round(3)
print(res.to_string())

print("\n--- Top 10 pays par volume ---")
print(df[df['country_code'].astype(str).str.len()>=2]["country_code"].value_counts().head(10).to_string())

print("\n--- Statut par grande zone (USA vs autre) ---")
usa = df["country_code"].astype(str).eq("USA")
print(pd.crosstab(usa, df["status"], normalize="index").round(3).to_string())

print("\n--- Délai fondation -> 1er financement (médian, jours) ---")
t = (df["first_funding_at"] - df["founded_at"]).dt.days
print(df.assign(t=t).groupby("status")["t"].median().round(0).to_string())
print("\nFigures sauvegardées dans", OUT)