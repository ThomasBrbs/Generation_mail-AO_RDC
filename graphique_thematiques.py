import json
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Charger les données
with open('resultats_structures_classes.json', encoding='utf-8') as f:
    data = json.load(f)

# Extraire les thématiques (sections) pour chaque fichier
records = []
for doc in data:
    fichier = doc.get('fichier', 'Inconnu')
    sections = doc.get('sections', {})
    for thematique in sections.keys():
        records.append({'Fichier': fichier, 'Thématique': thematique})

# Créer un DataFrame
if records:
    df = pd.DataFrame(records)
    # Compter les occurrences de chaque thématique par fichier
    pivot = pd.pivot_table(df, index='Fichier', columns='Thématique', aggfunc=len, fill_value=0)

    # Limiter le nombre de fichiers et de thématiques à 20 (les plus fréquents)
    top_fichiers = pivot.sum(axis=1).sort_values(ascending=False).head(20).index
    top_thematiques = pivot.sum(axis=0).sort_values(ascending=False).head(20).index
    pivot_limited = pivot.loc[top_fichiers, top_thematiques]

    # Désactiver annot si la matrice est trop grande
    annot = pivot_limited.shape[0] <= 15 and pivot_limited.shape[1] <= 15

    plt.figure(figsize=(1.5 * len(top_thematiques) + 4, 0.6 * len(top_fichiers) + 4))
    sns.heatmap(pivot_limited, annot=annot, fmt='d', cmap='YlGnBu', cbar_kws={'label': 'Nombre de sections'})
    plt.title('Répartition des thématiques par fichier (top 20)')
    plt.ylabel('Fichier')
    plt.xlabel('Thématique')
    plt.tight_layout()
    plt.show()
else:
    print("Aucune thématique trouvée dans les données.")
