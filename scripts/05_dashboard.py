# Génère dashboard.html autonome (figure base64) pour le livrable Dashboard
import base64, os

OUT = r"C:\Users\souleymane\Desktop\AGENT ia Z\J1\DA_Copilot\output"
DST = r"C:\Users\souleymane\Desktop\AGENT ia Z\J1\DA_Copilot\dashboard.html"

figs = [
    ("fig1_class_imbalance.png",   "Cible : fort déséquilibre de classe"),
    ("fig2_funding_by_status.png", "Financement et nombre de levées par statut"),
    ("fig3_corr_rounds.png",       "Corrélation entre types de rounds"),
    ("fig4_status_by_category.png","Taux d'issue par secteur"),
    ("fig5_status_by_country.png", "Taux d'issue par pays"),
    ("fig6_founded_year.png",      "Année de fondation par statut"),
    ("fig7_confusion_matrix.png",  "Matrice de confusion (Gradient Boosting)"),
    ("fig8_feature_importance.png","Importance des variables (permutation)"),
]

def b64(p):
    return "data:image/png;base64," + base64.b64encode(open(p,"rb").read()).decode()

cards = ""
for fn, cap in figs:
    cards += f'''
    <figure class="card">
      <img src="{b64(os.path.join(OUT, fn))}" alt="{cap}">
      <figcaption>{cap}</figcaption>
    </figure>'''

html = f"""<!DOCTYPE html>
<html lang="fr"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>DA-Copilot — Statut des startups</title>
<style>
  :root {{ color-scheme: dark; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; font-family: -apple-system, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
         background:#0f1216; color:#e6e9ee; padding:40px 24px 80px; line-height:1.5; }}
  .wrap {{ max-width:1080px; margin:0 auto; }}
  h1 {{ font-size:26px; margin:0 0 4px; }}
  .sub {{ color:#8b93a1; margin:0 0 28px; font-size:14px; }}
  h2 {{ font-size:19px; margin:34px 0 12px; border-left:3px solid #2a9d8f; padding-left:10px; }}
  .kpis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin:14px 0; }}
  .kpi {{ background:#171b21; border:1px solid #232a33; border-radius:10px; padding:14px 16px; }}
  .kpi .v {{ font-size:22px; font-weight:600; }} .kpi .l {{ font-size:12.5px; color:#8b93a1; }}
  .acq{{color:#e9c46a}}.clo{{color:#e76f51}}.ope{{color:#2a9d8f}}
  table {{ border-collapse:collapse; width:100%; margin:10px 0; font-size:14px; }}
  th,td {{ text-align:left; padding:8px 10px; border-bottom:1px solid #232a33; }}
  th {{ color:#8b93a1; font-weight:600; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(330px,1fr)); gap:18px; }}
  figure.card {{ margin:0; background:#171b21; border:1px solid #232a33; border-radius:12px;
                overflow:hidden; padding:0 0 10px; }}
  figure.card img {{ width:100%; display:block; }}
  figcaption {{ padding:10px 14px 0; font-size:13px; color:#aeb6c2; }}
  .note {{ background:#1a2119; border:1px solid #2c3a2a; border-radius:10px; padding:14px 18px;
          font-size:14px; color:#c9d4c9; }}
  .warn {{ background:#2a1f1a; border:1px solid #4a3326; border-radius:10px; padding:14px 18px; }}
  code {{ background:#1e242b; padding:1px 5px; border-radius:4px; font-size:13px; }}
</style></head>
<body><div class="wrap">
  <h1>Prédiction du statut des startups</h1>
  <p class="sub">DataAnalyst-Agent (DA-Copilot) · Investments_VC.csv · 48 124 startups étiquetées · 30 septembre 2026</p>

  <div class="kpis">
    <div class="kpi"><div class="v"><span class="ope">86,9 %</span></div><div class="l">operating (41 829)</div></div>
    <div class="kpi"><div class="v"><span class="acq">7,7 %</span></div><div class="l">acquired (3 692)</div></div>
    <div class="kpi"><div class="v"><span class="clo">5,4 %</span></div><div class="l">closed (2 603)</div></div>
    <div class="kpi"><div class="v">8,38 M$</div><div class="l">financement médian « acquired »</div></div>
    <div class="kpi"><div class="v">0,610</div><div class="l">balanced accuracy (meilleur modèle)</div></div>
    <div class="kpi"><div class="v">60,7 %</div><div class="l">rappel « acquired »</div></div>
  </div>

  <h2>Visualisations</h2>
  <div class="grid">{cards}</div>

  <h2>Modèles comparés</h2>
  <table>
    <tr><th>Modèle</th><th>Balanced accuracy</th><th>Macro-F1</th></tr>
    <tr><td>Baseline (majorité)</td><td>0,333</td><td>0,310</td></tr>
    <tr><td>Régression logistique (équilibrée)</td><td>0,582</td><td>0,427</td></tr>
    <tr><td>Forêt aléatoire (équilibrée)</td><td>0,480</td><td>0,477</td></tr>
    <tr><td><b>Gradient Boosting (poids équilibrés)</b></td><td><b>0,610</b></td><td><b>0,450</b></td></tr>
  </table>

  <h2>Recommandations</h2>
  <div class="note">
    <b>Prioriser</b> (signaux « acquired ») : financement élevé, startup récente, basée aux USA,
    première levée tardive après la fondation, secteurs Enterprise Software / Advertising / Software.<br><br>
    <b>Améliorer la donnée</b> : normaliser les codes pays, réconcilier <code>funding_total_usd</code>
    avec la somme des rounds (26 % d'écarts), uniformiser les catégories, compléter les dates de fondation.
  </div>
  <h2>Limites</h2>
  <div class="warn">
    Déséquilibre extrême → précision faible sur les classes rares (outil de tri, pas de décision auto).<br>
    Biais de survivance : <code>founded_year</code> et le délai de financement reflètent en partie
    l'instantané ~2014 (une startup récente n'a pas eu le temps d'être acquise). Corrélation ≠ causalité.<br>
    26 % des totaux de financement ne réconcilient pas avec la somme des rounds ; 29 % des dates de
    fondation manquantes (imputées).
  </div>
</div></body></html>"""

open(DST, "w", encoding="utf-8").write(html)
print("dashboard écrit :", DST, f"({os.path.getsize(DST)/1024:.0f} Ko)")