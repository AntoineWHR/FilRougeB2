# Analyse de donnees YOps

Ce dossier contient un petit module Python qui exploite la base SQLite de l'application.

Commandes :

```bash
cd app-yops-portal
python3 run.py
python3 analytics/analyze_yops.py
```

Sorties generees dans `storage/reports/` :

- `summary.json` : synthese globale lisible rapidement.
- `severity.csv` : repartition par criticite.
- `client_risk.csv` : score de risque par client.
- `overdue_tickets.csv` : tickets en retard.
- `monthly_trend.csv` : evolution mensuelle.
- `top_assets.csv` : actifs les plus touches.

Le but n'est pas de faire une IA de prediction. Le but est de montrer une vraie manipulation de donnees en Python : extraction SQL, agregation, indicateurs et exports exploitables.
