from flask import Flask, render_template_string, request, url_for
import json
import requests
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import random

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

# SMTP CONFIG (à personnaliser)
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
SENDER_EMAIL = ""  # À modifier
SENDER_PASSWORD = ""      # À modifier

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Générer un mail</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .form-container { max-width: 600px; margin: auto; }
        img { display: block; margin: 30px auto 0 auto; max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px #aaa; }
    </style>
</head>
<body>
    <div class="form-container">
        <h2>Générer un mail</h2>
        <form method="post">
            <!-- Ajoute ici tes champs de formulaire -->
            {{ form_html|safe }}
            <button type="submit">Générer</button>
        </form>
        {% if mail_result %}
        <div style="margin-top:30px; padding:15px; border:1px solid #ccc; border-radius:8px; background:#f9f9f9;">
            <h3>Mail généré :</h3>
            <pre style="white-space:pre-wrap;">{{ mail_result }}</pre>
        </div>
        {% endif %}
        <img src="{{ url_for('static', filename='197378.png') }}" alt="Illustration">
    </div>
</body>
</html>
'''

FORM_HTML = '''
<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Générer un mail personnalisé</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    body {
      background: linear-gradient(135deg, #e8f0fe 0%, #f8fafc 100%);
      min-height: 100vh;
    }
    .form-container {
      background: #fff;
      border-radius: 15px;
      box-shadow: 0 4px 24px rgba(80,120,200,0.08);
      padding: 2.5rem 2rem 2rem 2rem;
      max-width: 480px;
      margin: 3rem auto;
    }
    h2 {
      text-align: center;
      color: #2a4d8f;
      margin-bottom: 2rem;
      font-weight: 700;
    }
    label {
      font-weight: 600;
      color: #2a4d8f;
    }
    .btn-primary {
      background: #2a4d8f;
      border: none;
    }
    .mail-preview {
      background: #f4f8fb;
      border-left: 4px solid #2a4d8f;
      padding: 1.5em;
      border-radius: 8px;
      font-family: 'Fira Mono', monospace;
      white-space: pre-wrap;
      margin-top: 1.5em;
    }
    .success-msg {
      color: #198754;
      font-weight: 600;
      margin-top: 1em;
    }
  </style>
</head>
<body>
  <div class="form-container">
    <h2>Générer un mail personnalisé</h2>
    <form method="post">
      <div class="mb-3">
        <label for="profil" class="form-label">Vous êtes :</label>
        <select class="form-select" name="profil" id="profil">
          <option value="particulier">Particulier</option>
          <option value="professionnel">Professionnel</option>
        </select>
      </div>
      <div class="mb-3">
        <label for="thematique" class="form-label">Thématique :</label>
        <select class="form-select" name="thematique" id="thematique">
          {% for t in thematiques %}
            <option value="{{t}}">{{t}}</option>
          {% endfor %}
        </select>
      </div>
      <div class="mb-3">
        <label for="email" class="form-label">Votre e-mail :</label>
        <input type="email" class="form-control" name="email" id="email" required>
      </div>
      <button type="submit" class="btn btn-primary w-100">Générer et envoyer le mail</button>
    </form>
    <img src="{{ url_for('static', filename='197378.png') }}" alt="Illustration" style="display:block; margin:30px auto 0 auto; max-width:100%; height:auto; border-radius:8px; box-shadow:0 2px 8px #aaa;">
    {% if mail_preview %}
      <h4 class="mt-4">Aperçu du mail généré :</h4>
      <div class="mail-preview">{{mail_preview}}</div>
      <div class="success-msg">Mail envoyé à {{dest_email}}</div>
    {% endif %}
  </div>
</body>
</html>
'''


def generer_mail_llm(profil, thematique, email):
    with open('thematique_fusion_final.json', 'r', encoding='utf-8') as f:
        thematique_map = json.load(f)
    fichiers = [k for k, v in thematique_map.items() if v == thematique]
    resume = ""
    contenu = ""
    if fichiers:
        resume_file = random.choice(fichiers)
        try:
            with open(os.path.join('fusion_final', resume_file), 'r', encoding='utf-8') as fin:
                resume = fin.read().strip()
            # Cherche le fichier txt source correspondant (dans tesseract_txt ou dossier d'origine)
            txt_path = os.path.join('tesseract_txt', resume_file.replace('.txt', '.txt'))
            if os.path.exists(txt_path):
                with open(txt_path, 'r', encoding='utf-8') as ftxt:
                    contenu = ftxt.read().strip()
        except Exception:
            resume = ""
            contenu = ""
    prompt = f"""
Tu es un assistant qui génère des mails personnalisés. Rédige un mail professionnel, adapté à un {profil}, qui souhaite obtenir des informations ou un accompagnement sur la thématique suivante : {thematique}.

Dans le mail, présente l'appel d'offres suivant (résumé) :
---
{resume}
---

Puis, donne le contenu complet du fichier texte correspondant à cet appel d'offres :
---
{contenu}
---

Le mail doit être poli, clair, et donner envie de répondre à l'utilisateur. Commence par dire que tu es un robot spécialisé dans les appels d'offres, puis explique la demande, et termine par une formule de politesse.

À la fin du mail, ajoute la phrase suivante, sur une ligne séparée et en affichant le lien en clair :
Pour plus d’informations, consultez le site web :
"https://www.mediacongo.net/appels.html"

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
        return f"Erreur lors de la génération du mail : {e}"

def send_mail(dest_email, subject, body):
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = dest_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls(context=context)
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, dest_email, msg.as_string())
        return True
    except Exception as e:
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    mail_preview = None
    dest_email = None
    if request.method == 'POST':
        profil = request.form['profil']
        thematique = request.form['thematique']
        email = request.form['email']
        mail = generer_mail_llm(profil, thematique, email)
        subject = f"Demande d'information - {thematique}"
        send_mail(email, subject, mail)
        mail_preview = mail
        dest_email = email
    return render_template_string(FORM_HTML, thematiques=THEMATIQUES, mail_preview=mail_preview, dest_email=dest_email)

if __name__ == '__main__':
    app.run(debug=True)
