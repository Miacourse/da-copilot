# DA-Copilot — Étapes 5-6 : Modélisation v2 (comparaison équitable, gestion du déséquilibre)
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

# ---------- Feature engineering ----------
round_cols = ["seed","venture","equity_crowdfunding","undisclosed","convertible_note",
              "debt_financing","angel","grant","private_equity","post_ipo_equity",
              "post_ipo_debt","secondary_market","product_crowdfunding",
              "round_A","round_B","round_C","round_D","round_E","round_F","round_G","round_H"]

X = pd.DataFrame(index=df.index)
for c in round_cols:
    X["log_"+c] = np.log1p(pd.to_numeric(df[c], errors="coerce").fillna(0))
X["log_funding_total"] = np.log1p(pd.to_numeric(df["funding_total_usd"], errors="coerce").fillna(0))
X["funding_rounds"] = pd.to_numeric(df["funding_rounds"], errors="coerce").fillna(0)
X["founded_year"] = pd.to_numeric(df["founded_year"], errors="coerce")
X["has_url"] = df["homepage_url"].fillna("").astype(str).str.strip().ne("").astype(int)
X["n_categories"] = df["category_list"].fillna("").astype(str).str.strip("|").map(
    lambda s: 0 if not s else len([x for x in s.split("|") if x]))
X["time_to_first_funding"] = (df["first_funding_at"] - df["founded_at"]).dt.days
X["years_since_founding"] = 2014 - X["founded_year"]

cc = df["country_code"].fillna("").astype(str).str.strip()
cc = cc.where(cc != "", "UNKNOWN")
top_cc = cc.value_counts().head(15).index
for c in top_cc:
    X[f"cc_{c}"] = cc.eq(c).astype(int)
X["cc_OTHER"] = (~cc.isin(top_cc)).astype(int)

def cat_set(s):
    if not isinstance(s, str): return set()
    return set(x for x in s.strip("|").split("|") if x)
allcat = df["category_list"].fillna("").astype(str).map(cat_set)
from collections import Counter
top_cats = [c for c,_ in Counter(c for s in allcat for c in s).most_common(25)]
for c in top_cats:
    X[f"cat_{c}"] = allcat.map(lambda s, c=c: int(c in s))

y = df["status"].map({"operating":0, "acquired":1, "closed":2}).astype(int)
labels = ["operating","acquired","closed"]
print("Features :", X.shape, "| cible :", dict(zip(labels, y.value_counts().sort_index().tolist())))

# ---------- Split stratifié + poids de classe ----------
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
from sklearn.dummy import DummyClassifier
from sklearn.utils.class_weight import compute_sample_weight
from sklearn.metrics import classification_report, balanced_accuracy_score, f1_score, confusion_matrix

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.3, stratify=y, random_state=42)
w_train = compute_sample_weight("balanced", y_train)

num_cols = X.columns.tolist()
pre = Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())])
ct = ColumnTransformer([("num", pre, num_cols)], remainder="passthrough")

def eval_model(name, model, fit_kwargs={}):
    model.fit(X_train, y_train, **fit_kwargs)
    pred = model.predict(X_test)
    bacc = balanced_accuracy_score(y_test, pred)
    mf1 = f1_score(y_test, pred, average="macro")
    print(f"\n========== {name} ==========")
    print(f"Balanced accuracy = {bacc:.3f} | macro-F1 = {mf1:.3f}")
    print(classification_report(y_test, pred, target_names=labels, digits=3))
    return name, bacc, mf1

models = [
    ("Baseline (majorité)", DummyClassifier(strategy="most_frequent"), {}),
    ("Reg. logistique (équilibrée)",
     Pipeline([("ct", ct), ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))]), {}),
    ("Forêt aléatoire (équilibrée)",
     Pipeline([("ct", ct), ("clf", RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                                           n_jobs=-1, random_state=42))]), {}),
    ("Gradient Boosting (poids équilibrés)",
     HistGradientBoostingClassifier(max_iter=300, learning_rate=0.08,
                                    l2_regularization=0.1, random_state=42),
     {"sample_weight": w_train}),
]
results = [eval_model(n, m, kw) for n, m, kw in models]

print("\n========== RÉCAP ==========")
res = pd.DataFrame(results, columns=["modèle","balanced_acc","macro_F1"]).sort_values("balanced_acc", ascending=False)
print(res.round(3).to_string(index=False))

# ---------- Validation croisée 5-fold (meilleur modèle : RL) ----------
skf = StratifiedKFold(5, shuffle=True, random_state=42)
rl = Pipeline([("ct", ct), ("clf", LogisticRegression(max_iter=2000, class_weight="balanced"))])
baccs, mf1s = [], []
for tr, va in skf.split(X, y):
    rl.fit(X.iloc[tr], y.iloc[tr])
    p = rl.predict(X.iloc[va])
    baccs.append(balanced_accuracy_score(y.iloc[va], p))
    mf1s.append(f1_score(y.iloc[va], p, average="macro"))
print(f"\nCV 5-fold (Reg. logistique équilibrée) — balanced acc = {np.mean(baccs):.3f} ± {np.std(baccs):.3f}")
print(f"CV 5-fold (Reg. logistique équilibrée) — macro-F1      = {np.mean(mf1s):.3f} ± {np.std(mf1s):.3f}")

# ---------- Matrice de confusion (RL) ----------
rl.fit(X_train, y_train)
pred = rl.predict(X_test)
cm = confusion_matrix(y_test, pred)
fig, ax = plt.subplots(figsize=(6,5))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", xticklabels=labels, yticklabels=labels, ax=ax)
ax.set_title("Matrice de confusion — Régression logistique équilibrée")
ax.set_xlabel("Prédit"); ax.set_ylabel("Réel")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig7_confusion_matrix.png"), dpi=110); plt.close(fig)

# ---------- Importance des features (permutation, RL) ----------
from sklearn.inspection import permutation_importance
idx = np.random.RandomState(0).choice(len(X_test), 5000, replace=False)
r = permutation_importance(rl, X_test.iloc[idx], y_test.iloc[idx], n_repeats=3,
                           scoring="balanced_accuracy", random_state=0, n_jobs=-1)
imp = pd.DataFrame({"feature": X.columns, "importance": r.importances_mean}).sort_values("importance", ascending=False).head(20)
fig, ax = plt.subplots(figsize=(7,6))
sns.barplot(data=imp, y="feature", x="importance", color="#2a9d8f", ax=ax)
ax.set_title("Top 20 features (importance par permutation) — Reg. logistique")
fig.tight_layout(); fig.savefig(os.path.join(OUT,"fig8_feature_importance.png"), dpi=110); plt.close(fig)
print("\nTop 15 features (importance par permutation) :")
print(imp.head(15).round(4).to_string(index=False))