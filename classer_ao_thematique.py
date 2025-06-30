import os
import json
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma:2b"

# Dossiers
IN_DIR = 'fusion_final'
OUT_JSON = 'thematique_fusion_final.json'

THEMATIQUES = [
    "Santé",
    "Éducation",
    "Infrastructures",
    "Eau et Assainissement",
    "Agriculture",
    "Informatique",
    "Fournitures",
    "Services",
]

PROMPT_TEMPLATE = '''
Tu es un expert en analyse d’appels d’offres publics. À partir du texte ci-dessous, attribue une seule thématique principale à cet appel d’offres parmi la liste suivante :
- Santé
- Éducation
- Infrastructures
- Eau et Assainissement
- Agriculture
- Informatique
- Fournitures
- Services

Si aucune ne correspond parfaitement, choisis la plus proche parmi la liste.
Réponds UNIQUEMENT par le nom exact d'une seule thématique de la liste ci-dessus. N'ajoute rien d'autre.

Texte de l’appel d’offres :
"""{texte_ao}"""

Thématique :
'''

def get_thematique_ollama(texte):
    prompt = PROMPT_TEMPLATE.replace('{texte_ao}', texte[:2000])  # Coupe si trop long
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "options": {"temperature": 0.2, "num_predict": 30}
        }, timeout=180)
        response.raise_for_status()
        thematique = ""
        for line in response.iter_lines():
            if line:
                try:
                    data = json.loads(line)
                except Exception as e:
                    print(f"Erreur de parsing JSON sur la ligne : {line} -- {e}")
                    continue
                if data.get("done"):
                    break
                thematique += data.get("response", "")
        thematique = thematique.strip()
        # Nettoyage : ne garder que la thématique exacte (insensible à la casse)
        for t in THEMATIQUES:
            if t.lower() in thematique.lower():
                return t
        return "Inconnu"
    except Exception as e:
        print(f"Erreur lors de la classification : {e}")
        return "Erreur"

# Liste des thématiques
THEMATIQUES = [
    "Santé",
    "Éducation",
    "Infrastructures",
    "Eau et Assainissement",
    "Agriculture",
    "Informatique",
    "Fournitures",
    "Services",
    
]

PROMPT_TEMPLATE = '''
Tu es un expert en analyse d’appels d’offres publics. À partir du texte ci-dessous, attribue une seule thématique principale à cet appel d’offres parmi la liste suivante :
- Santé
- Éducation
- Infrastructures
- Eau et Assainissement
- Agriculture
- Informatique
- Fournitures
- Services

Si aucune ne correspond parfaitement, choisis la plus proche parmi la liste.
Réponds UNIQUEMENT par le nom exact d'une seule thématique de la liste ci-dessus. N'ajoute rien d'autre.

Texte de l’appel d’offres :
"""{texte_ao}"""

Thématique :
'''


def get_main_text(sections, max_chars=1200):
    # Privilégie les sections clés
    priority_keys = ['objet', 'description', 'but', 'résumé', 'contexte']
    texts = []
    for k, v in sections.items():
        if isinstance(v, str) and len(v) > 30:
            lk = k.lower()
            if any(pk in lk for pk in priority_keys):
                texts.append(v)
    # Si rien de pertinent, prend tout ce qui est assez long
    if not texts:
        texts = [v for v in sections.values() if isinstance(v, str) and len(v) > 30]
    full_text = "\n".join(texts)
    return full_text[:max_chars]

import difflib

def classer_ao(texte):
    prompt = PROMPT_TEMPLATE.format(texte_ao=texte)
    try:
        thematique_brute = query_local_llm(prompt, max_new_tokens=10)
        thematique_brute = thematique_brute.strip().split("\n")[0]
        # Post-traitement : on cherche la première thématique reconnue dans la sortie
        for t in THEMATIQUES:
            if t.lower() in thematique_brute.lower():
                return t, thematique_brute
        # Sinon, on cherche la plus proche
        closest = difflib.get_close_matches(thematique_brute, THEMATIQUES, n=1)
        if closest:
            return closest[0], thematique_brute
        return "Erreur", thematique_brute
    except Exception as e:
        print(f"Erreur Hugging Face : {e}")
        return "Erreur", "Erreur"

def main():
    files = [f for f in os.listdir(IN_DIR) if f.lower().endswith('.txt')]
    results = {}
    for fname in sorted(files):
        txt_path = os.path.join(IN_DIR, fname)
        with open(txt_path, 'r', encoding='utf-8') as f:
            texte = f.read().strip()
        if not texte:
            thematique = "Inconnu"
        else:
            thematique = get_thematique_ollama(texte)
        results[fname] = thematique
    with open(OUT_JSON, 'w', encoding='utf-8') as fout:
        json.dump(results, fout, ensure_ascii=False, indent=2)
    print(f"\nRésultat écrit dans {OUT_JSON}")

if __name__ == '__main__':
    main()
