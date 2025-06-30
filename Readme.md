# 📄 Projet Automatisation de la Veille Appels d’Offres (AO)

Ce projet vise à collecter des AO sur le site https://www.mediacongo.net/appels.html, faire une classification thématique, un résumé intelligent  de générer des emails personnalisés pour chaque AO.

---

## 🚀 Fonctionnalités principales

1. **Scraping automatique des AO**  
   Extraction structurée depuis des plateformes ciblées (API/web scraping).

2. **Classification sémantique**  
   Attribution d’une thématique à chaque AO grâce à un modèle LLM (ex : GPT-4, Mistral, Llama) via prompt.

3. **Résumé intelligent**  
   Génération d’un résumé synthétique (extractif et interprétatif) du contenu de chaque AO avec un LLM (ex : GPT-4, T5, Bart).


5. **Génération dynamique d’emails**  
   Création d’emails personnalisés incluant les AO les plus pertinents (résumés, liens, message d’intro généré).


---


**Requierements**

dans votre environement
- Python 3.8+
- Ollama
- Flask
- Requests
- BeautifulSoup
- Matplotlib
- Seaborn

**A installer au préalable**    
- Ollama (https://ollama.com/download)
    et installer gemma 2b via votre cmd
- Teeseract (https://github.com/UB-Mannheim/tesseract/wiki)

**Ordre d'execution**
1. scrapp.py
2. img_to_txt.py
3. nettoyer_structuration.py
4. reume_gemma.py
5. fusionner_resumes.py
6. classer_ao_thematique.py
7. generer_mail.py ou web_generer_mail.py

Les autres fichier permettent de visualiser les resultats ou des transformer les images en texte via easyocr(peut performant)


**IMPORTANT:**

Avant de run  web_generer_mail.py et generer_mail.py, il faut utiliser seulement une adresse mail **Outlook n'ayant pas de restriction ou de double authentification activé** et rentrer votre identifiant mail et mot de passe dans le fichier puis lancer le serveur flask avec python
