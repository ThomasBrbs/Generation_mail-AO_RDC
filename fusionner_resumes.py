import os

# Dossier contenant les fichiers à fusionner
IN_DIR = 'resume final'
OUT_DIR = 'fusion_final'
os.makedirs(OUT_DIR, exist_ok=True)

# Regroupe les fichiers par préfixe de 6 caractères
files_by_prefix = {}
for fname in os.listdir(IN_DIR):
    if fname.lower().endswith('.txt') and len(fname) >= 6:
        prefix = fname[:6]
        files_by_prefix.setdefault(prefix, []).append(fname)

# Fusionne les fichiers de chaque groupe dans un seul fichier
for prefix, files in files_by_prefix.items():
    output_path = os.path.join(OUT_DIR, f'{prefix}.txt')
    with open(output_path, 'w', encoding='utf-8') as fout:
        for fname in sorted(files):
            file_path = os.path.join(IN_DIR, fname)
            with open(file_path, 'r', encoding='utf-8') as fin:
                content = fin.read().strip()
                if content:
                    fout.write(content + '\n\n')
    print(f'Fichier fusionné créé : {output_path}')
