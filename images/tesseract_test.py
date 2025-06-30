import os
from PIL import Image
import pytesseract

# Configuration automatique du chemin Tesseract sous Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

IMG_DIR = 'c:/Users/ThomasBarbosa/NLP/final/images'
OUT_DIR = 'c:/Users/ThomasBarbosa/NLP/final/tesseract_txt'
os.makedirs(OUT_DIR, exist_ok=True)

all_files = [f for f in os.listdir(IMG_DIR) if f.lower().endswith(('.jpg', '.png', '.jpeg'))]

for fname in sorted(all_files):
    img_path = os.path.join(IMG_DIR, fname)
    print(f"OCR sur : {img_path}")
    try:
        image = Image.open(img_path)
        text = pytesseract.image_to_string(image, lang='fra')
    except Exception as e:
        print(f"Erreur sur {fname} : {e}")
        text = ""
    txt_name = os.path.splitext(fname)[0] + '.txt'
    txt_path = os.path.join(OUT_DIR, txt_name)
    with open(txt_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f"Texte sauvegardé dans {txt_path}\n{'-'*40}")
