import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from tqdm import tqdm
from PIL import Image

BASE = 'https://www.mediacongo.net/'
INDEX_URL = urljoin(BASE, '/appels.html')
OUTPUT = 'images'
os.makedirs(OUTPUT, exist_ok=True)

res = requests.get(INDEX_URL)
soup = BeautifulSoup(res.text, 'html.parser')

links = [a['href'] for a in soup.select('a[href^="appel-societe-"]')]
links = links[:150]

for idx, link in enumerate(tqdm(links, desc="Appels d'offres")):
    full_link = urljoin(BASE, link)
    page = requests.get(full_link)
    sup = BeautifulSoup(page.text, 'html.parser')

    imgs = sup.select('img')
    for img in imgs:
        src = img.get('src')
        if not src:
            continue
        img_url = urljoin(BASE, src)
        fname = f"{idx+1}{os.path.basename(src).split('?')[0]}"
        out = os.path.join(OUTPUT, fname)
        try:
            img_data = requests.get(img_url).content
            with open(out, 'wb') as f:
                f.write(img_data)
        except Exception as e:
            print(f"Erreur téléchargement {img_url} : {e}")


for filename in os.listdir(OUTPUT):
    filepath = os.path.join(OUTPUT, filename)
    try:
        with Image.open(filepath) as img:
            width, height = img.size
        if width != 711:
            os.remove(filepath)
            print(f"Supprimé (largeur {width} ≠ 711): {filename}")
    except Exception as e:
        print(f"Erreur ouverture image {filename} : {e}")
        # Optionnel : supprimer si impossible d'ouvrir
        os.remove(filepath)
        print(f"Supprimé (impossible d'ouvrir) : {filename}")