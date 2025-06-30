import os
import re
import json
from datetime import datetime

# Dossier contenant les fichiers txt
FOLDER_PATH = 'text_appels_easyocr'

# Fonction pour nettoyer le texte
def nettoyer_texte(texte):
    # Suppression des caractères spéciaux inutiles
    texte = texte.replace('\r', ' ').replace('\n', '\n')
    texte = re.sub(r'[\u202f\u00a0]', ' ', texte)  # espaces spéciaux
    texte = re.sub(r' +', ' ', texte)
    return texte.strip()

# Fonction pour extraire les métadonnées principales
def extraire_metadonnees(texte):
    meta = {}
    # Extractions typiques, à adapter selon structure réelle
    patterns = {
        'numero_avis': r"N[\?°] AVIS\s*[:\-]?\s*([\w/\-]+)",
        'reference_step': r"Référence STEP\s*[:\-]?\s*([\w\-]+)",
        'reference_financement': r"Référence de F[ao]ccord de financ[ea]ment\s*[:\-]?\s*([\w' ]+)",
        'date_publication': r"Dat[ec] d[ec] publication\s*[:\-]?\s*([\d]{1,2} [A-Za-zéû]+ [\d]{4})",
        'date_cloture': r"Date de clôture\s*[:\-]?\s*([\d]{1,2} [A-Za-zéû]+ [\d]{4} à [\d\w: ]+)",
        'province': r"PROVINCE DU ([A-ZÉ\- ]+)",
        'projet': r"NP d'Identification du Projet\s*[:\-]?\s*([\w\d]+)"
    }
    for key, pat in patterns.items():
        m = re.search(pat, texte, re.IGNORECASE)
        if m:
            meta[key] = m.group(1).strip()
    return meta

# Fonction pour séparer les sections (exemple basique)
def separer_sections(texte):
    sections = {}
    # Découpe sur des titres potentiels (ex : tout en majuscules suivi de saut de ligne)
    titres = re.findall(r'(^[A-ZÉÈÀÙÂÊÎÔÛÇ\'\s\-/]+)$', texte, re.MULTILINE)
    if titres:
        for i, titre in enumerate(titres):
            parts = texte.split(titre)
            if len(parts) > 1:
                sections[titre.strip()] = parts[1].strip()
                texte = parts[1]
    else:
        sections['contenu'] = texte
    return sections

# Traitement principal
def traiter_fichiers(folder_path):
    resultats = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.txt'):
            path = os.path.join(folder_path, filename)
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                brut = f.read()
            texte = nettoyer_texte(brut)
            meta = extraire_metadonnees(texte)
            sections = separer_sections(texte)
            resultats.append({
                'fichier': filename,
                'metadonnees': meta,
                'sections': sections
            })
    # Sauvegarde en JSON
    with open('resultats_structures.json', 'w', encoding='utf-8') as f:
        json.dump(resultats, f, ensure_ascii=False, indent=2)
    print(f"Traitement terminé. {len(resultats)} fichiers traités. Résultats dans resultats_structures.json")

if __name__ == '__main__':
    traiter_fichiers(FOLDER_PATH)
