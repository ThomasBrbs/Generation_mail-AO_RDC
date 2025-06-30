import smtplib
import ssl
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "gemma:2b"

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

def ask_user():
    print("Êtes-vous :\n1. Particulier\n2. Professionnel")
    while True:
        profil = input("Votre choix (1 ou 2) : ").strip()
        if profil == '1':
            profil = "particulier"
            break
        elif profil == '2':
            profil = "professionnel"
            break
        else:
            print("Réponse invalide. Veuillez entrer 1 ou 2.")

    print("\nVeuillez choisir une thématique parmi :")
    for i, t in enumerate(THEMATIQUES, 1):
        print(f"{i}. {t}")
    while True:
        idx = input(f"Votre choix (1-{len(THEMATIQUES)}) : ").strip()
        if idx.isdigit() and 1 <= int(idx) <= len(THEMATIQUES):
            thematique = THEMATIQUES[int(idx)-1]
            break
        else:
            print("Choix invalide.")

    email = input("\nVeuillez entrer votre adresse e-mail : ").strip()
    return profil, thematique, email

import json
import random

def generer_mail_llm(profil, thematique, email):
    # Charger la correspondance fichier <-> thématique
    with open('thematique_fusion_final.json', 'r', encoding='utf-8') as f:
        thematique_map = json.load(f)
    # Trouver tous les fichiers correspondant à la thématique
    fichiers = [k for k, v in thematique_map.items() if v == thematique]
    resume = ""
    if fichiers:
        # Prendre un fichier au hasard (ou le premier)
        resume_file = fichiers[0]
        try:
            with open(f'fusion_final/{resume_file}', 'r', encoding='utf-8') as fin:
                resume = fin.read().strip()
        except Exception as e:
            resume = ""
    # Préparer le prompt
    prompt = f"""
Tu es un assistant qui génère des mails personnalisés. Rédige un mail professionnel, adapté à un {profil}, qui souhaite obtenir des informations ou un accompagnement sur la thématique suivante : {thematique}.

Inclue dans le corps du mail le résumé suivant, qui présente un appel d'offres réel dans cette thématique :
---
{resume}
---

Le mail doit être poli, clair, et donner envie de répondre à l'utilisateur. Commence par une formule d'appel adaptée, puis explique la demande, et termine par une formule de politesse.

À la fin du mail, ajoute la phrase suivante, sur une ligne séparée et en affichant le lien en clair :
Pour plus d’informations, consultez le site web :
https://www.mediacongo.net/appels.html

Le mail doit être prêt à être envoyé à l'utilisateur {email}.
"""
    try:
        response = requests.post(OLLAMA_URL, json={
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "options": {"temperature": 0.4, "num_predict": 200}
        }, timeout=120)
        response.raise_for_status()
        mail_content = ""
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if data.get("done"):
                    break
                mail_content += data.get("response", "")
        return mail_content.strip()
    except Exception as e:
        print(f"Erreur lors de la génération du mail : {e}")
        return ""

def send_mail(dest_email, subject, body):
    # CONFIGURATION SMTP POUR OUTLOOK
    smtp_server = "smtp.office365.com"
    smtp_port = 587
    sender_email = "thomas.barbosa@ynov.com"  # À modifier
    sender_password = "Bt18lk09*"      # À modifier

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = dest_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, dest_email, msg.as_string())
        print(f"\nMail envoyé à {dest_email}")
    except Exception as e:
        print(f"Erreur lors de l'envoi du mail : {e}")

def main():
    profil, thematique, email = ask_user()
    print("\nGénération du mail...")
    mail = generer_mail_llm(profil, thematique, email)
    print("\n--- Aperçu du mail généré ---\n")
    print(mail)
    envoyer = input("\nVoulez-vous envoyer ce mail à l'adresse indiquée ? (o/n) : ").strip().lower()
    if envoyer == 'o':
        send_mail(email, f"Demande d'information - {thematique}", mail)
    else:
        print("Mail non envoyé.")

if __name__ == '__main__':
    main()
