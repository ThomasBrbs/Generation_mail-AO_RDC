# Désactiver les avertissements OpenMP pour éviter les conflits de DLL
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import easyocr

IMG_DIR = 'images'
OUT_DIR = 'text_appels_easyocr'
os.makedirs(OUT_DIR, exist_ok=True)

# Initialisation du lecteur pour le français (et anglais si besoin)
reader = easyocr.Reader(['fr', 'en'])  # Tu peux ajouter d'autres langues

for fname in os.listdir(IMG_DIR):
    if fname.lower().endswith('.jpg'):
        img_path = os.path.join(IMG_DIR, fname)
        out_path = os.path.join(OUT_DIR, fname.replace('.jpg', '.txt'))

        try:
            # Extraction du texte (output = liste de tuples)
            result = reader.readtext(img_path, detail=0)
            text = '\n'.join(result)
            with open(out_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"{fname} => {out_path}")
        except Exception as e:
            print(f"Erreur avec {fname} : {e}")
