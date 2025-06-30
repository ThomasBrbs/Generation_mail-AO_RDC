import os
import requests

OLLAMA_URL = "http://localhost:11434/api/generate"  # Port par défaut d'Ollama
OLLAMA_MODEL = "gemma:2b"
  # Ou tout autre modèle installé (llama2, etc.)

TXT_DIR = "tesseract_txt"
OUT_DIR = "resume final"
os.makedirs(OUT_DIR, exist_ok=True)
all_files = [f for f in os.listdir(TXT_DIR) if f.lower().endswith(".txt")]

for fname in sorted(all_files):
    print(f"\n--- Début du traitement pour : {fname} ---")
    txt_path = os.path.join(TXT_DIR, fname)
    try:
        with open(txt_path, 'r', encoding='utf-8') as f:
            text = f.read().strip()
        if not text:
            summary = ""
            print(f"Le fichier {fname} est vide, aucun résumé généré.")
        else:
            prompt = f"Résume le texte suivant en français : {text}"
            try:
                try:
                    response = requests.post(OLLAMA_URL, json={
                        "model": OLLAMA_MODEL,
                        "prompt": prompt,
                        "options": {"temperature": 0.2, "num_predict": 80}
                    }, timeout=300)
                except requests.Timeout:
                    print(f"Timeout : le résumé pour {fname} a dépassé 5 minutes.")
                    summary = ""
                    raise  # Pour sortir du bloc try principal
                response.raise_for_status()
                summary = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            import json
                            data = json.loads(line)
                        except Exception as e:
                            print(f"Erreur de parsing JSON sur la ligne : {line} -- {e}")
                            continue
                        if data.get("done"):
                            break
                        summary += data.get("response", "")
                summary = summary.strip()
                print(f"Succès : résumé généré pour {fname}.")
            except Exception as e:
                print(f"Erreur lors du résumé pour {fname} : {e}")
                summary = ""
        resume_name = os.path.splitext(fname)[0] + '_resume.txt'
        resume_path = os.path.join(OUT_DIR, resume_name)
        with open(resume_path, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Résumé pour {fname} :\n{summary}\n{'-'*40}")
    except Exception as e:
        print(f"Erreur inattendue lors du traitement de {fname} : {e}")

print("\nTraitement terminé pour tous les fichiers.")
