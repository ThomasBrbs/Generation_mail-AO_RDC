import json
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Charger les données du fichier JSON
with open('thematique_fusion_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Extraire les thématiques (valeurs du dictionnaire)
thematiques = list(data.values())

# Compter la fréquence de chaque thématique
counter = Counter(thematiques)

# Préparer les données pour le graphique
labels = list(counter.keys())
sizes = list(counter.values())

# Afficher un graphique camembert
plt.figure(figsize=(8, 8))
plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
plt.title("Distribution des thématiques des articles")
plt.axis('equal')
plt.tight_layout()
plt.show()

# Charger les données
with open('resultats_structures_classes.json', encoding='utf-8') as f:
    data = json.load(f)

# Extraire toutes les thématiques (clés de sections)
thematique_counts = {}
for doc in data:
    sections = doc.get('sections', {})
    for thematique in sections.keys():
        thematique_counts[thematique] = thematique_counts.get(thematique, 0) + 1

# Transformer en DataFrame
if thematique_counts:
    df = pd.DataFrame(list(thematique_counts.items()), columns=['Thématique', 'Occurrences'])
    df = df.sort_values('Occurrences', ascending=False)
    plt.figure(figsize=(10, max(6, len(df) * 0.4)))
    sns.barplot(data=df, y='Thématique', x='Occurrences', palette='viridis')
    plt.title('Répartition des thématiques dans tous les fichiers')
    plt.xlabel('Nombre d’occurrences')
    plt.ylabel('Thématique')
    plt.tight_layout()
    plt.show()
else:
    print("Aucune thématique trouvée dans les données.")
